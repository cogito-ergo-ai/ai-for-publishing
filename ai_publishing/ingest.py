import sys
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings


def get_docs(url):
    if ".pdf" not in url:
        raise Exception("Please pass a url of a PDF file!")

    loader = PyPDFLoader(url)
    pages = loader.load()
    return pages


def ingest_to_qdrant(url):
    print(f"Ingesting from {url}")
    docs = get_docs(url)

    print("Splitting documents...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
    texts = text_splitter.split_documents(docs)

    print("Generating embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",  # choose one based on your hardware
        model_kwargs={"device": "cpu"},  # if you have a GPU you can change this
    )

    print("Ingesting to Qdrant...")
    qdrant = Qdrant.from_documents(
        texts,
        embeddings,
        url="http://localhost:6333",
        collection_name="knowledge_base",
    )


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Specify one or more URLs of PDFs to ingest data")
        sys.exit(1)

    for url in sys.argv[1:]:
        ingest_to_qdrant(url)
