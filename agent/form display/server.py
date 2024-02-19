import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain.schema.runnable import Runnable
from langserve import add_routes
from returningStructuredOutput import agent_executor
from langchain.pydantic_v1 import BaseModel, Field
from typing import List, Union, Any
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.function import FunctionMessage

origins = [
    "http://localhost:5173"
]

app = FastAPI(debug=False, docs_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="Spin up a simple api server using Langchain's Runnable interfaces",
)

# We need to add these input/output schemas because the current AgentExecutor
# is lacking in schemas.
class Input(BaseModel):
    input: str
    chat_history: List[Union[HumanMessage, AIMessage, FunctionMessage]]


class Output(BaseModel):
    output: Any

def add_route(path: str, chain: Runnable):
    add_routes(
        app,
        runnable=chain,
        path=path,
        enabled_endpoints=["invoke", "stream", "input_schema", "output_schema"],
    )

# Adds routes to the app for using the chain under:
# /invoke
# /batch
# /stream
#add_routes(app, agent_executor.with_types(input_type=Input, output_type=Output))
add_route("/test/stream", agent_executor.with_types(input_type=Input, output_type=Output))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8002)