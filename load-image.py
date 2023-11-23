from langchain.document_loaders.image import UnstructuredImageLoader
from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
# on Ubuntu sudo apt-get install tesseract-ocr
# on mac brew install tesseract
# dependencies to install: unstructured, unstructured-inference, unstructured.pytesseract, 
# pandas, opencv-python, pdfminer.six, pdf2image, faiss-cpu, tiktoken, pypdf  

load_dotenv()

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
)

loader = UnstructuredImageLoader("librosa-feature-melspectrogram-1.png")
data = loader.load()
print(data[0])
