from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
from langchain.agents import initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentType
from createCloudSource import CloudSourceInputSchema, CreateCloudSourceTool
from createLiveEvent import CreateLiveEventInputSchema, CreateLiveEventTool
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.format_scratchpad.openai_functions import (
    format_to_openai_functions
)
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.output_parsers.openai_functions import OpenAIFunctionsAgentOutputParser
from langchain.agents import AgentExecutor
from langchain.schema.messages import AIMessage, HumanMessage
from langchain.utils.openai_functions import convert_pydantic_to_openai_function

load_dotenv()

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
    temperature=0,
    streaming=True
)

lc_tools = [CreateCloudSourceTool(), CreateLiveEventTool()]

oai_tools = [format_tool_to_openai_function(tool) for tool in lc_tools]

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

agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_functions(  # agent_scratchpad should be a sequence of messages that contains the previous agent tool invocations and the corresponding tool outputs.
            x["intermediate_steps"]
        ),
        "chat_history": lambda x: x["chat_history"]
    }
    | prompt
    #| llm.bind(tools=oai_tools)
    | llm.bind(
        functions=oai_tools
    )
    | OpenAIFunctionsAgentOutputParser()
)

agent_executor = AgentExecutor(agent=agent, tools=lc_tools, verbose=True)

# Start the conversation loop
while True:
    human_input = input("Human: ")

    if human_input.lower() == "exit":
        break

    # Get AI response
    result = agent_executor.invoke({"input": human_input, "chat_history": chat_history})
    chat_history.extend(
        [
            HumanMessage(content=human_input),
            AIMessage(content=result["output"]),
        ]
    )

    # print result when you only want the response back, don't forget to put verbose=False
    #print(result)
