# ConversationSummaryBufferMemory combines the two ideas. It keeps a buffer of recent interactions in memory, 
# but rather than just completely flushing old interactions it compiles them into a summary and uses both. 
# It uses token length rather than number of interactions to determine when to flush interactions.

from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
load_dotenv()

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
    temperature=0
)

conversation= ConversationChain(
    llm=llm,
    # We set a very low max_token_limit for the purposes of testing.
    memory=ConversationSummaryBufferMemory(llm=llm, max_token_limit=40),
    verbose=True,
)


while True:
    human_input = input("Human: ")

    if human_input.lower() == "exit":
        break

    # Get AI response
    ai_response = conversation.predict(input=human_input)
    print("AI: ", ai_response)