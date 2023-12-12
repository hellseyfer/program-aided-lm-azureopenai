from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
from langchain.agents import tool
from langchain.agents import initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentType

load_dotenv()

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
    temperature=0
)

@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)

@tool
def multiply_by_2(number_string: str) -> float:
    """Returns the number multiplied by 2"""
    return float(number_string) * 2

@tool
def meaning_of_life(world_length_multiplied_by_2: float) -> str:
    """ useful when the user ask for the meaning of life. 

    In order to be used, you first need to ask the user for his name. Don't asume user's name, after user input, calculate the length of his name and multiply it by 2.
    That will be the value of <world_length_multiplied_by_2>."""

    return f"the meaning of life is {world_length_multiplied_by_2}"

fixed_prompt = '''Assistant is a large language model trained by OpenAI.

Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

Assistant can ask the user for further information if it's not sure or required to do so.

Assistant doesn't know anything about calculating the length of a word, multiplying numbers by 2 or anything related to the meaning of life and should use a tool for questions about these topics.

Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

Overall, Assistant is a powerful system that can help with a wide range of tasks and provide valuable insights and information'''


tools = [get_word_length, multiply_by_2, meaning_of_life]

# conversational agent memory
memory = ConversationBufferMemory(
    memory_key='chat_history',
    return_messages=True
)

# create our off-the-shelf agent class
conversational_agent = initialize_agent(
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    tools=tools,
    llm=llm,
    verbose=True,
    max_iterations=6,
    early_stopping_method='generate',
    memory=memory
)

# conversational_agent.agent.llm_chain.prompt.messages[0].prompt.template = fixed_prompt

# Start the conversation loop
while True:
    human_input = input("Human: ")

    if human_input.lower() == "exit":
        break

    # Get AI response
    result = conversational_agent.invoke({"input": human_input})["output"]
    # print result when you only want the response back, don't forget to put verbose=False
    # print(result)