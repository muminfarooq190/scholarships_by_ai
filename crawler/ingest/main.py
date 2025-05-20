import os, uuid, time
import requests, openai
from bs4 import BeautifulSoup
from astrapy import DataAPIClient
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY");

client = DataAPIClient(os.getenv("ASTRA_TOKEN"))
db = client.get_database_by_api_endpoint(
    os.getenv("ASTRA_ENDPOINT"),
    keyspace=os.getenv("ASTRA_KEYSPACE"),
)

tbl = db.get_collection(os.getenv("ASTRA_TABLE"))  # works for tables and JSON collections
URL = "https://www.scholars4dev.com/category/masters-scholarships/"
def crawl(max_items: int = 20):
    headers = {"User-Agent": "Mozilla/5.0"}
    html = requests.get(URL, timeout=1500, headers=headers).text
    resp = requests.get(URL, timeout=1500, headers={'User-Agent': 'Mozilla/5.0'})
    print(resp.status_code, len(resp.text))      # 200 and a non-tiny length?
    with open("/scholarship/debug.html", "w", encoding="utf-8") as f:
     f.write(resp.text)
    soup = BeautifulSoup(html, "html.parser")

    posts = soup.select("h3.entry-title > a")   # current selector
    for a in posts[:max_items]:
        title = a.get_text(strip=True)
        url   = a["href"]

        # grab the first paragraph inside the sibling div.td-excerpt
        excerpt_parent = a.find_parent().find_next_sibling("div", class_="td-excerpt")
        short_desc = excerpt_parent.p.get_text(strip=True) if excerpt_parent else ""

        yield {
            "id": str(uuid.uuid4()),
            "title": title,
            "short_desc": short_desc,
            "url": url,
            "country": "International",
            "degree_level": "Masters",
        }

def embed(text: str) -> list[float]:
    r = openai.embeddings.create(model="text-em     bedding-3-small", input=text)
    return r.data[0].embedding

for doc in crawl():
    print("hii")
    doc["embedding"] = embed(doc["short_desc"])
    tbl.insert_one(doc)              # REST call under the hood
    time.sleep(0.8)                  # stay way under OpenAI QPS limits

print("Done 🚀")