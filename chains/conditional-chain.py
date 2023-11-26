# Using LCEL
#import langchain
#langchain.debug = True
from typing import Literal
from operator import itemgetter
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableBranch
from langchain.schema.runnable import RunnablePassthrough
from langchain.output_parsers.openai_functions import PydanticAttrOutputFunctionsParser
from langchain.pydantic_v1 import BaseModel
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain.prompts import PromptTemplate
from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
load_dotenv()

physics_template = """You are a very smart physics professor. \
You are great at answering questions about physics in a concise and easy to understand manner. \
When you don't know the answer to a question you admit that you don't know.

Here is a question:
{input}"""
physics_prompt = PromptTemplate.from_template(physics_template)

math_template = """You are a very good mathematician. You are great at answering math questions. \
You are so good because you are able to break down hard problems into their component parts, \
answer the component parts, and then put them together to answer the broader question.

Here is a question:
{input}"""

math_prompt = PromptTemplate.from_template(math_template)

general_prompt = PromptTemplate.from_template(
    "You are a helpful assistant. Answer the question as accurately as you can.\n\n{input}"
)
prompt_branch = RunnableBranch(
    (lambda x: x["topic"] == "math", math_prompt),
    (lambda x: x["topic"] == "physics", physics_prompt),
    general_prompt,
)

class TopicClassifier(BaseModel):
    "Classify the topic of the user question"

    topic: Literal["math", "physics", "general"]
    "The topic of the user question. One of 'math', 'physics' or 'general'."

classifier_function = convert_pydantic_to_openai_function(TopicClassifier)

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
    temperature=0
).bind(
    functions=[classifier_function], function_call={"name": "TopicClassifier"}
)

parser = PydanticAttrOutputFunctionsParser(
    pydantic_schema=TopicClassifier, attr_name="topic"
)

classifier_chain = llm | parser

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
    temperature=0
)

final_chain = (
    RunnablePassthrough.assign(topic=itemgetter("input") | classifier_chain)
    | prompt_branch
    | llm
    | StrOutputParser()
)

# "input": "What is the first prime number greater than 40 such that one plus the prime number is divisible by 3?"
# "input": "Tectonic plates are large segments of the Earth’s crust that move slowly. Suppose that one such plate has an average speed of 4.0 cm/year. (a) What distance does it move in 1 s at this speed? (b) What is its speed in kilometers per million years?"
output = final_chain.invoke(
    {
        "input": "Tectonic plates are large segments of the Earth’s crust that move slowly. Suppose that one such plate has an average speed of 4.0 cm/year. (a) What distance does it move in 1 s at this speed? (b) What is its speed in kilometers per million years?"
    }
)

print(output)
