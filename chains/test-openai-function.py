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

json_schema = {
  "title": "ChannelConfig",
  "description": "Identifying information about the channel config.",
  "type": "object",
  "properties": {
    "name": {"type": "string", "default": "Channel1-Primary"},
    "cryptoSetting": {
      "type": "object",
      "properties": {
        "key": {"type": "string"},
        "method": {"type": "string", "default": "NONE"}
      },
      "required": ["key"],
      "default": "null"
    },
    "labels": {
      "type": "array",
      "items": {"type": "string"},
      "default": "null"
    },
    "maxOutputConnections": {"type": "integer", "default": "null"},
    "protocol": {"type": "string", "default": "null"},
    "redundancyMode": {"type": "string", "default": "null"},
    "streamCount": {"type": "integer", "default": "null"}
  },
  "required": [],
}

prompt = ChatPromptTemplate.from_messages([
    ( "system",
     "You are a Media Service AI assistant for a media service."),
       (
            "human",
            "Use the given format to extract information from the following input: {input}",
        ),
        ("human", "Tip: Make sure to answer in the correct format and to return the all the properties even if they are set to null"),
])

inputCreate = "I want to create a cloud source with name Example1, with a number of 2 streams and a maximum of 200 connections"

runnable = create_structured_output_runnable(json_schema, llm, prompt)
output = runnable.invoke({"input": inputCreate})
print(output)
