import sys
from typing import List

from langchain.vectorstores import Qdrant
from langchain.schema import Document
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings


def get_docs(document_url: str):
    if ".pdf" not in document_url:
        raise Exception("Please pass a url of a PDF file!")

    loader = PyPDFLoader(document_url)
    pages = loader.load()
    return pages


def ingest_to_qdrant(documents: List[Document]):
    print("Splitting documents...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)

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
        docs = get_docs(url)
        ingest_to_qdrant(docs)
