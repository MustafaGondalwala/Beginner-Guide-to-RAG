import os
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

OUTPUT_DIR = "./zomato_technology"
os.makedirs(OUTPUT_DIR, exist_ok=True)

URLS = [
    "https://blog.zomato.com/apache-flink-journey-zomato-from-inception-to-innovation",
    "https://blog.zomato.com/introducing-pos-developer-platform-simplifying-integration-with-easy-to-use-tools",
    "https://blog.zomato.com/migrating-to-victoriametrics-a-complete-overhaul-for-enhanced-observability",
    "https://blog.zomato.com/go-beyond-building-performant-and-reliable-golang-applications",
    "https://blog.zomato.com/zomatos-journey-to-seamless-ios-code-sharing-and-distribution",
    "https://blog.zomato.com/menu-score-how-we-cracked-the-menu-code-and-you-can-too",
    "https://blog.zomato.com/hackoween-elevating-cybersecurity-resilience-at-zomato-through-competitive-challenges",
    "https://blog.zomato.com/a-tale-of-scale-behind-the-scenes-at-zomato-tech-for-nye-2023",
    "https://blog.zomato.com/switching-from-tidb-to-dynamodb",
    "https://blog.zomato.com/how-we-increased-our-zomato-restaurant-partner-app-speed-by-over-90",
    "https://blog.zomato.com/how-we-improved-our-android-app-startup-time-by-over-20-with-baseline-profile",
    "https://blog.zomato.com/introducing-vinifera",
    "https://blog.zomato.com/building-kimchi-for-hack-a-noodle-2022",
    "https://blog.zomato.com/building-a-cost-effective-logging-platform-using-clickhouse-for-petabyte-scale",
    "https://blog.zomato.com/explained-how-zomato-handles-100-million-daily-search-queries-part-three",
    "https://blog.zomato.com/explained-how-we-handle-100million-daily-search-queries-pt2",
    "https://blog.zomato.com/explained-how-zomato-handles-100-million-daily-search-queries-p1",
    "https://blog.zomato.com/hackanoodle",
    "https://blog.zomato.com/how-we-make-our-search-more-conversational-and-inclusive",
    "https://blog.zomato.com/powering-restaurant-ads-on-zomato",
    "https://blog.zomato.com/unique-addresses",
    "https://blog.zomato.com/powering-data-analytics-with-trino",
    "https://blog.zomato.com/predicting-fpt-optimally",
    "https://blog.zomato.com/rethinking-zomato-search-pt-2",
    "https://blog.zomato.com/rethinking-zomato-search-pt-1",
    "https://blog.zomato.com/android-security-part-two",
    "https://blog.zomato.com/android-security-part-one",
    "https://blog.zomato.com/connecting-the-dots-strengthening-recommendations-for-our-customers-part-two",
    "https://blog.zomato.com/connecting-the-dots-strengthening-recommendations-for-our-customers-part-one",
    "https://blog.zomato.com/the-accurate-eta-to-customer-satisfaction-part-two",
    "https://blog.zomato.com/the-accurate-eta-to-customer-satisfaction-part-one",
    "https://blog.zomato.com/increasing-android-app-speed",
    "https://blog.zomato.com/our-learnings-from-nye",
    "https://blog.zomato.com/defining-our-typography-system",
    "https://blog.zomato.com/to-help-us-locate-you-better",
    "https://blog.zomato.com/making-design-collaboration-seamless",
    "https://blog.zomato.com/elements-of-scalable-machine-learning",
    "https://blog.zomato.com/new-ratings",
    "https://blog.zomato.com/restaurant-ratings-v2",
    "https://blog.zomato.com/food-preparation-time",
    "https://blog.zomato.com/all-new-search-and-discovery-on-zomato",
    "https://blog.zomato.com/huddle-diaries-ios",
    "https://blog.zomato.com/architecture-behind-tags",
    "https://blog.zomato.com/ux-teardown",
    "https://blog.zomato.com/reviews-2-0",
    "https://blog.zomato.com/v14-app-update",
    "https://blog.zomato.com/women-in-tech-chapter-3",
    "https://blog.zomato.com/sushi",
    "https://blog.zomato.com/huddle-diaries-product-design",
    "https://blog.zomato.com/women-in-tech-chapter-2",
    "https://blog.zomato.com/women-in-tech-chapter-1",
    "https://blog.zomato.com/ongoing-trial-weeks",
    "https://blog.zomato.com/our-android-app-has-been-eating-but-shedding-weight",
    "https://blog.zomato.com/why-we-switched-to-figma-as-a-primary-design-tool-at-zomato",
    "https://blog.zomato.com/huddle-diaries-devops-and-data-platform",
    "https://blog.zomato.com/ios-compile-time",
    "https://blog.zomato.com/huddle-diaries-android",
    "https://blog.zomato.com/gratitude",
    "https://blog.zomato.com/how-we-cut-the-build-time-for-our-android-app-by-95",
    "https://blog.zomato.com/ios-app-update",
    "https://blog.zomato.com/zomato-pickup",
    "https://blog.zomato.com/zomato-piggybank",
    "https://blog.zomato.com/machine-learning",
    "https://blog.zomato.com/hygiene-ratings",
    "https://blog.zomato.com/learnings-from-the-last-huddle-cybersecurity",
    "https://blog.zomato.com/product-before-pixels-a-product-thinking-workshop-for-designers",
    "https://blog.zomato.com/lessons-in-localisation",
    "https://blog.zomato.com/introducing-pre-ordering-to-zomato",
    "https://blog.zomato.com/project-pixl-creating-a-unique-set-of-icons-for-the-zomato-app",
    "https://blog.zomato.com/say-hello-to-huddle-2",
    "https://blog.zomato.com/our-first-open-source-contribution-stunning-photo-filters-for-your-android-apps",
    "https://blog.zomato.com/our-first-steps-towards-personalisation-on-zomato",
    "https://blog.zomato.com/rewriting-the-network-connection-layer-in-our-android-apps",
    "https://blog.zomato.com/how-we-moved-our-food-feed-from-redis-to-cassandra"
]

def download_file(url, output_path):
    with requests.get(url, stream=True) as response:
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

def save_html(content, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def extract_markdown(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text()
    return text

def create_page_folder(title):
    folder_name = re.sub(r'[^a-zA-Z0-9]+', '_', title).strip('_')
    folder_path = os.path.join(OUTPUT_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def scrape_page(url, session):
    response = session.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.title.string if soup.title else "Untitled"
        page_folder = create_page_folder(title)

        html_path = os.path.join(page_folder, "page.html")
        save_html(str(soup), html_path)

        markdown_path = os.path.join(page_folder, "page.md")
        markdown_content = extract_markdown(response.content)
        save_html(markdown_content, markdown_path)

        images = soup.find_all("img")
        for i, img in enumerate(images):
            img_url = img.get("src")
            if img_url:
                img_url = urljoin(url, img_url)
                img_name = f"image_{i}.jpg"
                img_path = os.path.join(page_folder, img_name)
                download_file(img_url, img_path)
    else:
        print(f"Failed to scrape {url}: {response.status_code}")

def scrape_all_urls(urls):
    session = requests.Session()
    for url in urls:
        print(f"Scraping: {url}")
        scrape_page(url, session)

if __name__ == "__main__":
    scrape_all_urls(URLS)