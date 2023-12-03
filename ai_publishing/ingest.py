import json
import sys

from langchain.vectorstores import Qdrant
from langchain.schema import Document
from langchain.embeddings import HuggingFaceEmbeddings


def ingest_to_qdrant(articles: dict):
    docs = [
        Document(
            page_content=article["title"] + "\n" + article["summary"],
            metadata=article
        )
        for article in articles
    ]
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",  # choose one based on your hardware
        model_kwargs={"device": "cpu"},  # if you have a GPU you can change this
    )

    print("Ingesting to Qdrant...")
    Qdrant.from_documents(
        docs,
        embeddings,
        url="http://localhost:6333",
        collection_name="knowledge_base",
    )


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Specify one or more URLs of PDFs to ingest data")
        sys.exit(1)

    for file_path in sys.argv[1:]:
        with open(file_path, "r") as f:
            d = json.load(f)
        ingest_to_qdrant(d)
