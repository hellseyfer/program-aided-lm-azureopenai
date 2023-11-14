from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import faiss
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv

load_dotenv()
 
llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
)

loader = PyPDFLoader("bitcoin.pdf")
pages = loader.load_and_split()

#print(pages[0])

faiss_index = faiss.FAISS.from_documents(pages, OpenAIEmbeddings())
docs = faiss_index.similarity_search("How will the community be engaged?", k=2)
for doc in docs:
    print(str(doc.metadata["page"]) + ":", doc.page_content[:500])
