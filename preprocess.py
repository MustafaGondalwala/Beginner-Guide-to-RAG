import os
import json
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from PIL import Image
from pytesseract import image_to_string
from bs4 import BeautifulSoup

MILVUS_URI = "<url>"
TOKEN = "<token>"
connections.connect("default", uri=MILVUS_URI, token=TOKEN)

collection_name = "knowledge_base"
dim = 384
check_collection = utility.has_collection(collection_name)
if check_collection:
    utility.drop_collection(collection_name)

fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=10000),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
]
schema = CollectionSchema(fields, description="Knowledge base embeddings")
collection = Collection(name=collection_name, schema=schema)

def process_image(file_path):
    try:
        img = Image.open(file_path)
        return image_to_string(img)
    except Exception:
        return ""

def process_html(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            return soup.get_text(separator="\n")
    except Exception:
        return ""

def process_folder(folder_path):
    documents = []
    for sub_folder in os.listdir(folder_path):
        sub_folder_path = os.path.join(folder_path, sub_folder)
        if not os.path.isdir(sub_folder_path):
            continue

        aggregated_content = []
        for root, _, files in os.walk(sub_folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith(".md") or file.endswith(".txt"):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            aggregated_content.append(content)
                elif file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg"):
                    content = process_image(file_path)
                    if content:
                        aggregated_content.append(content)
                elif file.endswith(".html"):
                    content = process_html(file_path)
                    if content:
                        aggregated_content.append(content)

        if aggregated_content:
            combined_content = "\n".join(aggregated_content)
            documents.append(Document(page_content=combined_content, metadata={"source": sub_folder}))
    return documents

folder_to_process = "./zomato_technology"
documents = process_folder(folder_to_process)

if not documents:
    print("No valid documents found in the folder.")
    exit()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
chunks = splitter.split_documents(documents)

if not chunks:
    print("No valid chunks created from the documents.")
    exit()

contents = [chunk.page_content for chunk in chunks]
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
embeddings = embedding_model.embed_documents(contents)

if not contents or not embeddings:
    print("No valid content or embeddings generated.")
    exit()

collection.insert([contents, embeddings])

collection.flush()
index_params = {"index_type": "AUTOINDEX", "metric_type": "IP", "params": {}}
collection.create_index("embedding", index_params)
collection.load()