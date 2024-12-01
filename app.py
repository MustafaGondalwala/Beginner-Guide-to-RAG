from flask import Flask, request, jsonify, send_from_directory
from pymilvus import Collection, connections
from transformers import AutoTokenizer, AutoModel
import torch
import subprocess
import json

app = Flask(__name__)

milvus_uri = "<url>"
token = "<token>"
connections.connect("default", uri=milvus_uri, token=token)

collection_name = "knowledge_base"
collection = Collection(collection_name)

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

def embed_text(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        embeddings = model(**inputs).last_hidden_state.mean(dim=1).numpy()
    return embeddings.flatten().tolist()

@app.route('/query', methods=['POST'])
def query():
    try:
        data = request.get_json() 
        if not data or 'query' not in data:
            return jsonify({'error': 'Invalid request. "query" field is required.'}), 400

        user_query = data['query']
        if not isinstance(user_query, str) or not user_query.strip():
            return jsonify({'error': 'The "query" field must be a non-empty string.'}), 400

        query_embedding = embed_text(user_query)

        search_params = {"metric_type": "IP", "params": {"nprobe": 10}}
        results = collection.search(
            [query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=3,
            output_fields=["content"]
        )

        retrieved_docs = []
        for hits in results:
            for hit in hits:
                retrieved_docs.append(hit.get("content"))

        if not retrieved_docs:
            return jsonify({'error': 'No relevant documents found.'}), 404

        context = "\n\n".join(retrieved_docs)
        prompt = f"Context:\n{context}\n\nUser: {user_query}\nAssistant:"
        print(prompt)
        result = subprocess.run(
            ['ollama', 'run', 'llama3.2:3b', prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            return jsonify({'error': result.stderr.strip()}), 500

        assistant_response = result.stdout.strip()
        return jsonify({'response': assistant_response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
