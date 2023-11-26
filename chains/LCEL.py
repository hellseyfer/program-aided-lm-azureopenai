from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
load_dotenv()

llm = AzureChatOpenAI(
    deployment_name="gpt35-16k",
    model_name="gpt-35-turbo-16k",
    temperature=0
)

prompt = PromptTemplate.from_template(
    "What is a good name for a company that makes {product}?"
)
runnable = prompt | llm | StrOutputParser()
output = runnable.invoke({"product": "colorful socks"})
print(output)