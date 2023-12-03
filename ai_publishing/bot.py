import argparse
from langchain.prompts import PromptTemplate
from langchain.llms import CTransformers
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA


prompt = PromptTemplate.from_template("""
Article Assistant is adept at creating high quality articles for the user according to the content he wants to generate. 
The content should be generated from user-provided context relevant documents, transforming content into engaging, 
well-structured articles while strictly adhering to the document's content. 
It prioritizes accuracy and alignment with the user's intent, asking for clarifications in cases of ambiguous instructions. 
It simplifies complex information while maintaining the integrity and tone of the original content. 
Article Assistant communicates in a conversational and friendly style, making it approachable and easy to interact with.
It avoids altering fundamental meanings or introducing personal opinions and is conscientious about copyright laws.

User input: 
{question}

---
Context Relevant Documents: 

{context}

""")
document_prompt = PromptTemplate.from_template("""{page_content}: 
{content}
""")


class BotManager:
    def __init__(self, model_type, temperature, k):
        self.temperature = temperature
        self.k = k
        self.model_type = model_type
        self.llm = None
        self.embedding_model = None
        self.vector_store = None

    def _load_llm(self):
        if self.llm is not None:
            # model already loaded nothing to do
            return
        if self.model_type == "openai":
            llm = ChatOpenAI(
                model_name="gpt-4-1106-preview",
                temperature=self.temperature
            )
        else:
            llm = CTransformers(
                model="TheBloke/Llama-2-7B-Chat-GGML",
                model_type="llama",
                temperature=self.temperature,
                device="cuda"
            )
        self.llm = llm

    def _load_embedding_model(self):
        if self.embedding_model is not None:
            return
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cuda"},
        )

    def _load_vector_store(self):
        if self.vector_store is not None:
            return
        self._load_embedding_model()
        client = QdrantClient(url="http://localhost:6333")
        self.vector_store = Qdrant(
            client=client, collection_name="knowledge_base", embeddings=self.embedding_model
        )

    def load_model(self):
        # change model here based on your needs
        self._load_llm()
        self._load_embedding_model()
        self._load_vector_store()

    def response_with_qdrant_context(self, query):
        qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": self.k}),
            return_source_documents=True,
            chain_type_kwargs={
                "prompt": prompt,
                "document_prompt": document_prompt
            },
        )
        return qa({"query": query})

    def get_response(self, query):
        res = self.response_with_qdrant_context(query)
        return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Content generation bot from Knowledge base"
    )
    parser.add_argument(
        "--model",
        choices=["openai", "llama2"],
        type=str.lower,
        help="LLM model to use",
        default="llama2",
        required=False
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

    bot_manager = BotManager(args.model, args.temperature, args.k)
    bot_manager.load_model()

    while True:
        command = "Write an article about "
        user_input = input(f"{command}:> ")
        user_input = command + user_input
        response = bot_manager.get_response(user_input)
        # print("Bot:", response["result"])
        from pprint import pprint
        print("Input Source Documents:")
        for x in response["source_documents"]:
            print("*" + x.metadata["title"] + ": " + x.metadata["summary"])
        print("---")
        print("Article:")
        print(response["result"])
