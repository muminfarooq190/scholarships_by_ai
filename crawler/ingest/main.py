import os
import uuid
import time
import re
import requests
from bs4 import BeautifulSoup
from astrapy import DataAPIClient
from dotenv import load_dotenv

load_dotenv()

# ─── Setup Astra client ────────────────────────────────────────────────────────
client = DataAPIClient(os.getenv("ASTRA_TOKEN"))
db = client.get_database_by_api_endpoint(
    os.getenv("ASTRA_ENDPOINT"),
    keyspace=os.getenv("ASTRA_KEYSPACE"),
)
tbl = db.get_collection(os.getenv("ASTRA_TABLE"))  # JSON-collection

# ─── Constants & Helpers ──────────────────────────────────────────────────────
URL = "https://www.scholars4dev.com/category/masters-scholarships/"

def clean(txt: str) -> str:
    return re.sub(r"\s+", " ", txt).strip()

# ─── 1) Crawl function ───────────────────────────────────────────────────────
def crawl(max_items: int = 20) -> list[dict]:
    html = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30).text
    soup = BeautifulSoup(html, "html.parser")
    docs = []

    for post in soup.select("div.post")[:max_items]:
        a     = post.select_one("h2 a[href]")
        title = clean(a.get_text()) if a else "No title"
        url   = a["href"]           if a else None

        entry = post.select_one("div.entry")
        para  = entry.find("p")     if entry else None
        desc  = clean(para.get_text()) if para else ""

        docs.append({
            # use your own UUID as the JSON-doc _id
            "id":            str(uuid.uuid4()),
            "title":         title,
            "short_desc":    desc,
            "url":           url,
            "country":       "International",
            "degree_level":  "Masters",
        })

    return docs

# ─── 2) Batch-embed function ─────────────────────────────────────────────────
def embed_texts(docs: list[dict]) -> list[list[float]]:
    api_url = "https://api.jina.ai/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {os.getenv('JINA_API_KEY')}",
        "Content-Type": "application/json",
    }
    inputs = [{"text": d["short_desc"]} for d in docs]
    payload = {"model": "jina-clip-v2", "input": inputs}

    resp = requests.post(api_url, headers=headers, json=payload)
    resp.raise_for_status()

    data = resp.json().get("data", [])
    # return list of embedding vectors in same order
    return [item["embedding"] for item in data]

# ─── 3) Main pipeline ─────────────────────────────────────────────────────────
def main():
    docs = crawl(max_items=20)
    embeddings = embed_texts(docs)

    # Attach embeddings to each doc
    for doc, emb in zip(docs, embeddings):
        doc["embedding_v1024"] = emb

    # Bulk insert all docs at once
    tbl.insert_many(docs)

    print("Done 🚀")

if __name__ == "__main__":
    main()