# Models
from typing import Dict, List
from pydantic import BaseModel


class Ingress(BaseModel):
    protocol: str
    platform: str
    region: str
    url: str
    cryptoSetting: str
    streamCount: int
class CloudSource(BaseModel):
    id: str
    name: str
    state: str
    version: str
    ingress: Ingress
    backupIngress: str
    redundancyMode: str
    statistics: str
    maxOutputConnections: int

class CryptoSetting(BaseModel):
    key: str
    method: str

class LiveTranscription(BaseModel):
    enableLiveTranscription: bool

class Input(BaseModel):
    cloudSourceId: str

class OutputItem(BaseModel):
    encryptionMethod: str
    packageType: str

class InputLossSlate(BaseModel):
    enableInputLossSlate: bool
    imageUrl: str

class CdnUrls(BaseModel):
    cmafDashUrl: str
    cmafHlsUrl: str

class OriginUrls(BaseModel):
    cmafDashUrl: str
    cmafHlsUrl: str
class PlaybackUrls(BaseModel):
    cdnUrls: CdnUrls
    originUrls: OriginUrls
class LiveEvent(BaseModel):
    id: str
    name: str
    state: str
    input: Input
    transcodingProfile: str
    liveTranscription: LiveTranscription
    inputLossSlate: InputLossSlate
    packagingProfile: str
    publishName: str
    output: List[OutputItem]
    addOns: Dict[str, str]
    goLiveTime: str
    endTime: str
    playbackUrls: PlaybackUrls

class ThreadResponse(BaseModel):
    thread_id: str
    
class BodyMessage(BaseModel):
    message: str
    thread_id: str
    
class MessageResponse(BaseModel):
    message: str