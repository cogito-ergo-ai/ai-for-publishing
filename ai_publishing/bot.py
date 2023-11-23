import argparse
from langchain.prompts import PromptTemplate
from langchain.llms import CTransformers
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA


custom_prompt_template = """
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

"""

prompt = PromptTemplate(
    template=custom_prompt_template, input_variables=["context", "question"]
)


class BotManager:
    def __init__(self, model, temperature, k):
        self.context = ""
        self.temperature = temperature
        self.k = k
        self.model = model

    def load_model(self):
        # change model here based on your needs
        if self.model == "openai":
            llm = ChatOpenAI(
                model_name="gpt-4-1106-preview",
                temperature=self.temperature
            )
        else:
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
        "--model",
        choices=["openai", "llama2"],
        type=str.lower,
        help="LLM model to use",
        default="openai",
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

    while True:
        user_input = input("prompt> ")
        response = bot_manager.get_response(user_input)
        print("Bot:", response)
