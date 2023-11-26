from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import StrOutputParser
from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
load_dotenv()

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
    temperature=0.4
)

prompt = PromptTemplate.from_template(
    """Summarize this text:

{output_text}

Summary:"""
)

with open("IntegrateSpark.md") as f:
    mytextfile = f.read()

runnable = (
    {"output_text": lambda text: "\n\n".join(text.split("\n\n")[:3])}
    | prompt
    | llm
    | StrOutputParser()
)
output = runnable.invoke(mytextfile)
print(output)