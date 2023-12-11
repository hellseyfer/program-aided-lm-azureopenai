from langchain.pydantic_v1 import BaseModel, Field
from typing import Literal

class TopicClassifier(BaseModel):
    "Classify the topic of the Current Conversation. Always prioritize user's last intentions."

    topic: Literal["CreateCloudSource",
                   "CreateLiveEvent",
                   "PreviewLiveEvent",
                   "GoLiveWithLiveEvent",
                   "ListLiveEvents"]
    """The topic of the current conversation. One of 
    'CreateCloudSource', 'CreateLiveEvent', 'GoLiveWithLiveEvent', 'PreviewLiveEvent' or 'ListLiveEvents'."""