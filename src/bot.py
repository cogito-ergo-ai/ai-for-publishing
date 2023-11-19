import argparse
from langchain import PromptTemplate
from langchain.llms import CTransformers
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA


custom_prompt_template = """Use the following pieces of information to answer the user’s question.
If you don’t know the answer, just say that you don’t know, don’t try to make up an answer.

Context: {context}
Question: {question}

Only return the helpful answer below and nothing else.
Helpful answer:
"""

prompt = PromptTemplate(
    template=custom_prompt_template, input_variables=["context", "question"]
)


class BotManager:
    def __init__(self, temperature, k):
        self.context = ""
        self.temperature = temperature
        self.k = k

    def load_model(self):
        # change model here based on your needs
        llm = CTransformers(
            model="TheBloke/Llama-2-7B-Chat-GGML",
            model_type="llama",
            temperature=self.temperature,
        )
        return llm

    def response_with_qdrant_context(self, query):
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
        )

        client = QdrantClient(url="http://localhost:6333")

        doc_store = Qdrant(
            client=client, collection_name="knowledge_base", embeddings=embeddings
        )

        llm = self.load_model()
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=doc_store.as_retriever(search_kwargs={"k": self.k}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt},
        )

        response = qa({"query": query})
        return response

    def update_context(self, new_context):
        self.context += " " + new_context

    def get_response(self, query):
        self.update_context(query)
        response = self.response_with_qdrant_context(query)
        return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Content generation bot from Knowledge base"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        help="set models's temperature (must be in interval [0, 1])",
        default=0.2,
        required=False,
    )
    parser.add_argument(
        "--k",
        type=int,
        help="How many docs to retrieve from qdrant (must be >= 1)",
        default=2,
        required=False,
    )
    args = parser.parse_args()

    bot_manager = BotManager(args.temperature, args.k)

    while True:
        user_input = input("prompt> ")
        response = bot_manager.get_response(user_input)
        print("Bot:", response)
