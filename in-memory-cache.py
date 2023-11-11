from langchain.globals import set_llm_cache
from langchain.cache import InMemoryCache
from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
)
set_llm_cache(InMemoryCache())

# The first time, it is not yet in cache, so it should take longer
output = llm.predict("Tell me a joke")
print(output)

# The second time it is, so it goes faster
output = llm.predict("Tell me a joke")
print(output)
