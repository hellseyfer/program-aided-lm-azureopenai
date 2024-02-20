import html
import io
import os
import time

#from langchain_openai import AzureOpenAI
from openai import AzureOpenAI
from datetime import datetime
from pathlib import Path
from typing import Iterable
from openai.types import FileObject
import yfinance as yf
from openai.types.beta import Thread
from openai.types.beta.threads import Run
from openai.types.beta.threads.message_content_image_file import MessageContentImageFile
from openai.types.beta.threads.message_content_text import MessageContentText
from openai.types.beta.threads.messages import MessageFile
from PIL import Image
# Load the environment variables - These are secrets.


api_endpoint = os.getenv("OPENAI_API_BASE")
api_key = os.getenv("OPENAI_API_KEY")
deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")
api_version = os.getenv("OPENAI_VERSION")
print(deployment_name)
print(api_endpoint)
print(api_key)

# Create an OpenAI Azure client
client = AzureOpenAI(api_key=api_key, api_version=api_version, azure_endpoint=api_endpoint)

# Upload the files
DATA_FOLDER = "assistants/data/"
def upload_file(client: AzureOpenAI, path: str) -> FileObject:
    with Path(path).open("rb") as f:
        return client.files.create(file=f, purpose="assistants")

arr = os.listdir(DATA_FOLDER)
assistant_files = []
for file in arr:
    filePath = DATA_FOLDER + file
    assistant_files.append(upload_file(client, filePath))
print(assistant_files)
file_ids = [file.id for file in assistant_files]

# Send an email using Logic Apps
def send_logic_apps_email(to: str, content: str) -> None:
    try:
        #json_payload = {"to": to, "content": html.unescape(content)}
        #headers = {"Content-Type": "application/json"}
        #response = requests.post("", json=json_payload, headers=headers)
        
        #if response.status_code == 202:
        #    print("Email sent to: " + json_payload["to"])
        print("Email sent to: " + to)
    except:
        print("Failed to send email via Logic Apps")

# Get the latest stock price by ticker symbol
def get_stock_price(symbol: str) -> float:
    stock = yf.Ticker(symbol)
    return stock.history(period="1d")["Close"].iloc[-1]

tools_list = [
    {"type": "code_interpreter"},
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Retrieve the latest closing price of a stock using its ticker symbol.",
            "parameters": {
                "type": "object",
                "properties": {"symbol": {"type": "string", "description": "The ticker symbol of the stock"}},
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Sends an email to a recipient(s).",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "The email(s) the email should be sent to."},
                    "content": {"type": "string", "description": "The content of the email."},
                },
                "required": ["to", "content"],
            },
        },
    },
]

# Create an Asssitant with the code_interpreter tool
assistant = client.beta.assistants.create(
    name="Portfolio Management Assistant",
    instructions="You are a personal securities trading assistant. Please be polite, professional, helpful, and friendly. "
        + "Use the provided portfolio CSV file to answer the questions. If question is not related to the portfolio or you cannot answer the question, say, 'contact a representative for more assistance.'"
        + "If the user asks for help or says 'help', provide a list of sample questions that you can answer.",
    tools=tools_list,
    model=deployment_name,
    file_ids=file_ids
)

# Create a thread
thread = client.beta.threads.create()

# Function calling
def call_functions(client: AzureOpenAI, thread: Thread, run: Run) -> None:
    print("Function Calling")
    required_actions = run.required_action.submit_tool_outputs.model_dump()
    print(required_actions)
    tool_outputs = []
    import json

    for action in required_actions["tool_calls"]:
        func_name = action["function"]["name"]
        arguments = json.loads(action["function"]["arguments"])

        if func_name == "get_stock_price":
            output = get_stock_price(symbol=arguments["symbol"])
            tool_outputs.append({"tool_call_id": action["id"], "output": output})
        elif func_name == "send_email":
            print("Sending email...")
            email_to = arguments["to"]
            email_content = arguments["content"]
            send_logic_apps_email(email_to, email_content)

            tool_outputs.append({"tool_call_id": action["id"], "output": "Email sent"})
        else:
            raise ValueError(f"Unknown function: {func_name}")

    print("Submitting outputs back to the Assistant...")
    client.beta.threads.runs.submit_tool_outputs(thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs)

# Format and display the Assistant messages for text and images

def read_assistant_file(file_id:str):
    response_content = client.files.content(file_id)
    return response_content.read()

# Check the status of a Run
def print_messages(messages: Iterable[MessageFile]) -> None:
    message_list = []

    # Get all the messages till the last user message
    for message in messages:
        message_list.append(message)
        if message.role == "user":
            break

    # Reverse the messages to show the last user message first
    message_list.reverse()

    # Print the user or Assistant messages or images
    for message in message_list:
        for item in message.content:
            # Determine the content type
            if isinstance(item, MessageContentText):
                print(f"{message.role}:\n{item.text.value}\n")
                file_annotations = item.text.annotations
                if file_annotations:
                    for annotation in file_annotations:
                        file_id = annotation.file_path.file_id
                        content = read_assistant_file(file_id)
                        print(f"Annotation Content:\n{str(content)}\n")
            elif isinstance(item, MessageContentImageFile):
                # Retrieve image from file id                
                data_in_bytes = read_assistant_file(item.image_file.file_id)
                # Convert bytes to image
                readable_buffer = io.BytesIO(data_in_bytes)
                image = Image.open(readable_buffer)
                # Resize image to fit in terminal
                width, height = image.size
                image = image.resize((width // 2, height // 2), Image.LANCZOS)
                # Display image
                image.show()

def process_prompt(prompt: str) -> None:
    client.beta.threads.messages.create(thread_id=thread.id, role="user", content=prompt)
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Please address the user as Jane Doe. The user has a premium account. Be assertive, accurate, and polite. Ask if the user has further questions. "
        + "The current date and time is: "
        + datetime.now().strftime("%x %X")
        + ". ",
    )
    print("processing ...")
    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run.status == "completed":
            # Handle completed
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            print_messages(messages)
            break
        if run.status == "failed":
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            answer = messages.data[0].content[0].text.value
            print(f"Failed User:\n{prompt}\nAssistant:\n{answer}\n")
            # Handle failed
            break
        if run.status == "expired":
            # Handle expired
            print(run)
            break
        if run.status == "cancelled":
            # Handle cancelled
            print(run)
            break
        if run.status == "requires_action":
            # Handle function calling and continue processing
            call_functions(client, thread, run)
        else:
            time.sleep(5)

 
#process_prompt("Based on the provided portfolio, what investments do I own?")
#process_prompt("What is the value of my portfolio?")
user_prompt =  "Please send a report to name@contoso.com with the details for each stock based on the latest stock prices, and list the best and worst performing stocks in my portfolio."

process_prompt(user_prompt)
# Cleanup
client.beta.assistants.delete(assistant.id)
client.beta.threads.delete(thread.id)
for file in assistant_files:
    client.files.delete(file.id)