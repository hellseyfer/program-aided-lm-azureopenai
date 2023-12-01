from langchain.agents import AgentType, Tool, initialize_agent
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
from langchain.utilities import google_serper
from langchain.chat_models import AzureChatOpenAI

load_dotenv()

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
    temperature=0
)

search = google_serper.GoogleSerperAPIWrapper()
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

tools = [
    Tool(
        name="Current Search",
        func=search.run,
        description="useful for when you need to answer questions about current events or the current state of the world",
    ),
]

agent_executor = initialize_agent(
    tools,
    llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
)

#agent_executor.invoke({"input": "hi, i am bob"})["output"]
#agent_executor.invoke({"input": "hi, i am bob"})["output"]
#agent_executor.invoke({"input": "what are some movies showing 9/21/2023?"})["output"]

# Start the conversation loop
while True:
    user_input = input("You: ")

    # Invoke the agent with user input
    response = agent_executor.invoke({"input": user_input})["output"]

    # Print the agent's response
    print("Agent:", response)

    # Check if the user wants to close the connection
    if user_input.lower() == "exit":
        break

# Close the connection outside the loop