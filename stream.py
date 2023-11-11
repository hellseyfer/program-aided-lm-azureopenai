from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
)
for chunk in llm.stream("Write me a song about goldfish on the moon"):
    print(chunk.content, end="", flush=True)