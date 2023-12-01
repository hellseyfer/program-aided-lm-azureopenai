# We can take advantage of OpenAI functions to try and force the model to return a particular kind of structured output. 
# We'll use create_structured_output_runnable to create our chain, which takes the desired structured output either as 
# a Pydantic class or as JsonSchema.
from typing import Optional

from langchain.chains.openai_functions import (
    create_openai_fn_chain,
    create_openai_fn_runnable,
    create_structured_output_chain,
    create_structured_output_runnable,
)
from langchain.prompts import ChatPromptTemplate
from langchain.pydantic_v1 import BaseModel, Field
from typing import Sequence
from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
load_dotenv()

llm = AzureChatOpenAI(
    deployment_name="gpt35-16k",
    model_name="gpt-35-turbo-16k",
    temperature=0
)

class Person(BaseModel):
    # When passing in Pydantic classes to structure our text, we need to make sure to have a docstring description for the class. 
    # It also helps to have descriptions for each of the classes attributes.
    """Identifying information about a person."""

    name: str = Field(..., description="The person's name")
    age: int = Field(..., description="The person's age")
    fav_food: Optional[str] = Field(None, description="The person's favorite food")

class People(BaseModel):
    """Identifying information about all people in a text."""

    people: Sequence[Person] = Field(..., description="The people in the text")
    
# If we pass in a model explicitly, we need to make sure it supports the OpenAI function-calling API.
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a world class algorithm for extracting information in structured formats.",
        ),
        (
            "human",
            "Use the given format to extract information from the following input: {input}",
        ),
        ("human", "Tip: Make sure to answer in the correct format"),
    ]
)

inputPerson = "Sally is 13"
inputPeople = "Sally is 13, Joey just turned 12 and loves spinach. Caroline is 10 years older than Sally."
runnable = create_structured_output_runnable(Person, llm, prompt)
# runnable = create_structured_output_runnable(People, llm, prompt)
#output = runnable.invoke({"input": "Sally is 13"})
# output = runnable.invoke({"input": inputPeople})


# Using JsonSchema

json_schema = {
    "title": "Person",
    "description": "Identifying information about a person.",
    "type": "object",
    "properties": {
        "name": {"title": "Name", "description": "The person's name", "type": "string"},
        "age": {"title": "Age", "description": "The person's age", "type": "integer"},
        "fav_food": {
            "title": "Fav Food",
            "description": "The person's favorite food",
            "type": "string",
        },
    },
    "required": ["name", "age"],
}

runnable = create_structured_output_runnable(json_schema, llm, prompt)
output = runnable.invoke({"input": "Sally is 13"})
print(output)
