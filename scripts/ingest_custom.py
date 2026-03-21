import os
import sys

# Ensure backend folder is in path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.ingestion_service import ingest_document

def main():
    file_path = "data/custom_facts.txt"
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found.")
        return

    print(f"📂 Reading {file_path}...")
    with open(file_path, "rb") as f:
        content = f.read()

    print("🧠 Ingesting to Vector DB (FAISS)...")
    try:
        num_chunks = ingest_document(content, "custom_facts.txt")
        print(f"✅ SUCCESS! Added {num_chunks} memory fragments.")
    except Exception as e:
        print(f"❌ Failed to ingest: {e}")

if __name__ == "__main__":
    main()
