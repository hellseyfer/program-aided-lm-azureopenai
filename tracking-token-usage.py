from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv

from langchain.callbacks import get_openai_callback

load_dotenv()
 
llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
)

with get_openai_callback() as cb:
    result = llm.invoke("Tell me a joke")
    print(cb)

#    Tokens Used: 24
#        Prompt Tokens: 11
#        Completion Tokens: 13
#    Successful Requests: 1
#    Total Cost (USD): $0.0011099999999999999