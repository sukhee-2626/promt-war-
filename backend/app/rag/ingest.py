"""
ChromaDB ingestion script.
Run once: python -m app.rag.ingest
Embeds resources.json and stores with metadata filters.
"""
import json, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DATA    = Path(__file__).parent.parent.parent.parent / "data"
CHROMA  = os.getenv("CHROMA_PATH", "./chroma_db")
EMBED   = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")


def ingest():
    import chromadb
    from sentence_transformers import SentenceTransformer

    resources = json.loads((DATA / "resources.json").read_text())
    model     = SentenceTransformer(EMBED)

    client = chromadb.PersistentClient(path=CHROMA)
    col    = client.get_or_create_collection("resources")

    # Build text for embedding: title + provider + skill_id + level
    texts = [
        f"{r['title']} | {r.get('provider','')} | skill:{r['skill_id']} | level:{r['level']}"
        for r in resources
    ]
    embeddings = model.encode(texts, normalize_embeddings=True).tolist()

    col.upsert(
        ids        = [r["id"] for r in resources],
        embeddings = embeddings,
        documents  = texts,
        metadatas  = [{
            "skill_id": r["skill_id"],
            "level":    r["level"],
            "type":     r["type"],
            "url":      r["url"],
            "title":    r["title"],
            "provider": r.get("provider",""),
            "duration_min": r.get("duration_min", 0),
            "free":     str(r.get("free", True)),
        } for r in resources],
    )
    print(f"Ingested {len(resources)} resources into ChromaDB at {CHROMA}")


if __name__ == "__main__":
    ingest()
