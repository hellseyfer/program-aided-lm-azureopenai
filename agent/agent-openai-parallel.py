from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import ddg_search # https://python.langchain.com/docs/integrations/tools/ddg
from langchain.tools import BearlyInterpreterTool # ignore no name in module warning
from langchain.tools.render import format_tool_to_openai_function
from dotenv import load_dotenv
import os
from langchain.chat_models import AzureChatOpenAI

load_dotenv()

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
    temperature=0
)

lc_tools = [ddg_search.DuckDuckGoSearchRun(), BearlyInterpreterTool(api_key=os.getenv("BEARLY_API_KEY")).as_tool()]
oai_tools =  llm.bind(functions=[format_tool_to_openai_function(t) for t in lc_tools])

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: openai_functions.format_to_openai_functions(
            x["intermediate_steps"]
        ),
    }
    | prompt
    | oai_tools
    | OpenAIFunctionsAgentOutputParser()
)

agent_executor = AgentExecutor(agent=agent, tools=lc_tools, verbose=True)

agent_executor.invoke(
    {"input": "What's the average of the temperatures in LA, NYC, and SF today?"}
)