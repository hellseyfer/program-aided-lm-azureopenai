from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
from langchain.agents import initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentType
from createCloudSource import CreateCloudSourceTool
from createLiveEvent import CreateLiveEventTool
load_dotenv()

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
    temperature=0
)

tools = [CreateCloudSourceTool(), CreateLiveEventTool()]

# conversational agent memory
memory = ConversationBufferMemory(
    memory_key='chat_history',
    return_messages=True
)

# create our off-the-shelf agent class
    #agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
conversational_agent = initialize_agent(
    agent=AgentType.OPENAI_FUNCTIONS,
    tools=tools,
    llm=llm,
    verbose=True,
    max_iterations=6,
    memory=memory,
    handle_parsing_errors=True
)

# Start the conversation loop
while True:
    human_input = input("Human: ")

    if human_input.lower() == "exit":
        break

    # Get AI response
    #result = conversational_agent.invoke({"input": human_input})["output"]
    result = conversational_agent.run(human_input)

    # print result when you only want the response back, don't forget to put verbose=False
    # print(result)
