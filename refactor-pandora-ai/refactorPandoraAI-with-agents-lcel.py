import asyncio
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
from langchain.schema.messages import AIMessage, HumanMessage
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from langchain.schema.runnable import (
    ConfigurableField,
    Runnable,
    RunnableBranch,
    RunnableLambda,
    RunnableMap,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langserve import add_routes
from typing import List, Optional, Sequence, Tuple, Union
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

class ChatRequest(BaseModel):
    question: str
    chat_history: List[Tuple[str, str]] = Field(
        ...,
        extra={"widget": {"type": "chat", "input": "question", "output": "answer"}},
    )


lc_tools = [CreateCloudSourceTool(), CreateLiveEventTool()]

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

# Start the conversation loop
# while True:
#     human_input = input("Human: ")

#     if human_input.lower() == "exit":
#         break

#     # Get AI response
#     result = agent_executor.invoke({"input": human_input, "chat_history": chat_history})
#     chat_history.extend(
#         [
#             HumanMessage(content=human_input),
#             AIMessage(content=result["output"]),
#         ]
#     )

    # print result when you only want the response back, don't forget to put verbose=False
    #print(result)

add_routes(
    app, agent_executor, path="/chat", input_type=ChatRequest, config_keys=["configurable"]
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)