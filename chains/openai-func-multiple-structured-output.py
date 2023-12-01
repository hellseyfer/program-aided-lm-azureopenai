from typing import Optional

from langchain.chains.openai_functions import (
    convert_to_openai_function,
    get_openai_output_parser,
)
from langchain.prompts import ChatPromptTemplate
from langchain.pydantic_v1 import BaseModel, Field
from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
load_dotenv()

llm = AzureChatOpenAI(
    deployment_name="gpt35-16k",
    model_name="gpt-35-turbo-16k",
    temperature=0
)

class RecordPerson(BaseModel):
    """Record some identifying information about a pe."""

    name: str = Field(..., description="The person's name")
    age: int = Field(..., description="The person's age")
    fav_food: Optional[str] = Field(None, description="The person's favorite food")


class RecordDog(BaseModel):
    """Record some identifying information about a dog."""

    name: str = Field(..., description="The dog's name")
    color: str = Field(..., description="The dog's color")
    fav_food: Optional[str] = Field(None, description="The dog's favorite food")


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a world class algorithm for recording entities."),
        (
            "human",
            "Make calls to the relevant function to record the entities in the following input: {input}",
        ),
        ("human", "Tip: Make sure to answer in the correct format"),
    ]
)

openai_functions = [convert_to_openai_function(f) for f in (RecordPerson, RecordDog)]
llm_kwargs = {"functions": openai_functions}
if len(openai_functions) == 1:
    llm_kwargs["function_call"] = {"name": openai_functions[0]["name"]}
output_parser = get_openai_output_parser((RecordPerson, RecordDog))
runnable = prompt | llm.bind(**llm_kwargs) | output_parser

output = runnable.invoke({"input": "Harry was a chubby brown beagle who loved chicken"})
print(output)