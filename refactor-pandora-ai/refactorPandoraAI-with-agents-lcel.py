from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from createCloudSource import  CreateCloudSourceTool
from createLiveEvent import  CreateLiveEventTool
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.agents.format_scratchpad.openai_functions import (
    format_to_openai_functions
)
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.output_parsers.openai_functions import OpenAIFunctionsAgentOutputParser
from langchain.agents import AgentExecutor
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from langserve import add_routes
from typing import List, Tuple
from pydantic import BaseModel, Field

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

background_tasks = set()
lc_tools = [CreateCloudSourceTool(background_tasks=background_tasks), CreateLiveEventTool()]

oai_tools = [convert_to_openai_function(tool) for tool in lc_tools]

# conversational agent memory
MEMORY_KEY = 'chat_history'

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. But you don't know anything about creating a cloud source or a live event."),
        MessagesPlaceholder(variable_name=MEMORY_KEY),  # Notice that we put this ABOVE the new user input (to follow the conversation flow).
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

chat_history = []

llm = AzureChatOpenAI(
    temperature=0,
    deployment_name="gpt-35-turbo-16k",
    streaming=True,
    #callbacks=[MyCustomAsyncHandler(arg1=chat_history)],
)

agent = (
    {
        "input": lambda x: x["question"],
        "agent_scratchpad": lambda x: format_to_openai_functions(  # agent_scratchpad should be a sequence of messages that contains the previous agent tool invocations and the corresponding tool outputs.
            x["intermediate_steps"]
        ),
        "chat_history": lambda x: x["chat_history"]
    }
    | prompt
    | llm.bind(
        functions=oai_tools
    )
    | OpenAIFunctionsAgentOutputParser()
)

agent_executor = AgentExecutor(agent=agent, tools=lc_tools, verbose=True)

class ChatRequest(BaseModel):
    question: str
    chat_history: List[Tuple[str, str]] = Field(
        ...,
        extra={"widget": {"type": "chat", "input": "question", "output": "answer"}},
    )

add_routes(
    app, agent_executor, path="/chat", input_type=ChatRequest, config_keys=["configurable"]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)