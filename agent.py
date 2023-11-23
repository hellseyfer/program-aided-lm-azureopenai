from langchain.chat_models import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.format_scratchpad import openai_functions
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents import AgentExecutor
from langchain.prompts import MessagesPlaceholder
from langchain.schema.messages import AIMessage, HumanMessage
from dotenv import load_dotenv
from langchain.agents import tool

load_dotenv()

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
)

@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)

@tool
def multiplyX2(number: str) -> int:
    """Returns the number multiplied by 2"""
    return number * 2

MEMORY_KEY = "chat_history"
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are very powerful assistant, but bad at calculating lengths of words.",
        ),
        MessagesPlaceholder(variable_name=MEMORY_KEY),  # Notice that we put this ABOVE the new user input (to follow the conversation flow).
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

tools = [get_word_length, multiplyX2]

llm_with_tools = llm.bind(functions=[format_tool_to_openai_function(t) for t in tools])

chat_history = []

agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: openai_functions.format_to_openai_functions(  # agent_scratchpad should be a sequence of messages that contains the previous agent tool invocations and the corresponding tool outputs.
            x["intermediate_steps"]
        ),
        "chat_history": lambda x: x["chat_history"],
    }
    | prompt
    | llm_with_tools
    | OpenAIFunctionsAgentOutputParser()
)


agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

input1 = "how many letters in the word educa?"
result = agent_executor.invoke({"input": input1, "chat_history": chat_history})
chat_history.extend(
    [
        HumanMessage(content=input1),
        AIMessage(content=result["output"]),
    ]
)

input2 = "is that a real word?"
result2 = agent_executor.invoke({"input": input2, "chat_history": chat_history})
chat_history.extend(
    [
        HumanMessage(content=input2),
        AIMessage(content=result2["output"]),
    ]
)

agent_executor.invoke({"input": "what is the double of 4?", "chat_history": chat_history})