# By encapsulating prompts into functions, you can create a series of functions to establish a workflow. 
# Each function represents a specific step or task, and when combined in a particular order, 
# they can automate complex processes or solve problems more efficiently. This approach allows for 
# a more structured and streamlined interaction with GPT, ultimately enhancing its capabilities 
# and making it a powerful tool to accomplish a wide range of tasks.

from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
from langchain.schema import (
    SystemMessage,
    HumanMessage
)

load_dotenv()

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
)



META_PROMPT=""" Hello, ChatGPT! I hope you are doing well. I am reaching out to you for assistance with a specific function. I understand that you have the capability to process information and perform various tasks based on the instructions provided. In order to help you understand my request more easily, I will be using a template to describe the function, input, and instructions on what to do with the input. Please find the details below:

function_name: [Function Name]
input: [Input]
rule: [Instructions on how to process the input]

I kindly request you to provide the output for this function, based on the details I have provided. Your assistance is greatly appreciated. Thank you!
I will replace the text inside the brackets with the relevant information for the function I want you to perform. This detailed introduction should help you understand my request more efficiently and provide the desired output. The format is function_name(input) If you understand, just answer one word with ok.
 """

 # English study assistant #
 ###########################

 # tans_word function
FUNCTION_TRANS_WORD="""
function_name: [trans_word]
input: ["text"]
rule: [I want you to act as an English translator, spelling corrector and improver. 
I will provide you with input forms including "text" in any language and you will detect the language, 
translate it and answer in the corrected of my text, in English.] """

FUNCTION_EXPAND_WORD=""" function_name: [expand_word]
input: ["text"]
rule: [Please serve as a Chatterbox, spelling corrector, and language enhancer. 
I will provide you with input forms including "text" in any language, and output the original language.
I want you to Keep the meaning same, but make them more literary.] """

FIX_ENGLISH=""" function_name: [fix_english]
input: ["text"]
rule: [Please serve as an English master, spelling corrector, and language enhancer. 
I will provide you with input forms including "text", I want you to improve the text's vocabulary and 
sentences with more natural and elegent. Keep the meaning same.] """

USER_PROMPT=""" trans_word('婆罗摩火山处于享有“千岛之国”美称的印度尼西亚. 多岛之国印尼有4500座之多的火山, 世界著名的十大活火山有三座在这里.')
fix_english('Finally, you can run the function independently or chain them together.')
fix_english(expand_word(trans_word('婆罗摩火山处于享有“千岛之国”美称的印度尼西亚. 多岛之国印尼有4500座之多的火山, 世界著名的十大活火山有三座在这里.'))) 
DO NOT SAY THINGS ELSE OK, UNLESS YOU DONT UNDERSTAND THE FUNCTION"""

messages = [
    SystemMessage(content=META_PROMPT)
]
# Add more messages with additional prompts or instructions
messages.append(SystemMessage(content=FUNCTION_TRANS_WORD))
messages.append(SystemMessage(content=FUNCTION_EXPAND_WORD))
messages.append(SystemMessage(content=FIX_ENGLISH))

messages.append(
    HumanMessage(
        content=USER_PROMPT
    )
)


llm_out = llm(messages)
print(llm_out)

# expected output:  "The Bromo volcano, situated in the distinguished \'Country of Thousand Islands\', Indonesia, is 
# truly noteworthy. This archipelagic nation boasts a staggering count of 4500 volcanoes, thereby securing its unique place
#  in the global arena. It is indeed remarkable that three of the world\'s top ten renowned active volcanoes find their home here."'

#output = exec(llm_out)
#print(output) 
