from typing import Union

from fastapi import FastAPI
import uuid

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/live/v1/cloudsources")
def create_cloud_source():
    return {
    "id":  str(uuid.uuid4()),
    "name": "live event 1",
    "state": "RUNNING",
    "version": "1.21.0.0.41",
    "ingress": {
        "protocol": "SRT",
        "platform": "AZURE_VM",
        "region": "westus2",
        "url": "srt://ingress-6498fcb731b0e90059941dba.lrs-preprod.vos360.video:7086",
        "cryptoSetting": "null",
        "streamCount": 0
    },
    "backupIngress": "null",
    "redundancyMode": "NONE",
    "statistics": "null",
    "maxOutputConnections": 9
    }

@app.post('/live/v1/events')
def create_live_event():
    return {
  "id": "34fd01fc-fee6-11ed-be56-0242ac120002",
  "name": "College Football Final 2023",
  "state": "Preview",
  "input": {
      "cloudSourceId": "6498fcb731b0e90059941dba"
  },
  "transcodingProfile": "Standard",
  "liveTranscription": {
    "enableLiveTranscription": "false"
  },
  "inputLossSlate": {
    "enableInputLossSlate": "true",
    "imageUrl": "https://harmonicinc.box.com/s/ihapp8m4hrkpuikprxdi5x5c9081k991"
  },
  "packagingProfile": "Standard",
  "publishName": "footballlFinal2003",
  "output": [
    {
      "encryptionMethod": "Clear",
      "packageType": "cmaf-dash"
    },
    {
      "encryptionMethod": "Clear",
      "packageType": "cmaf-hls"
    }
  ], 
  "addOns": {
  }, 
  "goLiveTime": "2023-08-1T12:23:00+0000",
  "endTime": "2023-08-1T15:33:00+0000" ,
  "playbackUrls": {
    "cdnUrls": {
      "cmafDashUrl": "https://cdn-vos-ppp-01.vos360.video/Content/CMAF/Live/channel(footballlFinal2003)/master.mpd",
      "cmafHlsUrl": "https://cdn-vos-ppp-01.vos360.video/Content/CMAF/Live/channel(footballlFinal2003)/master.m3u8"
    },
    "originUrls": {
      "cmafDashUrl": "https://origin-irp-vos-ppp-01.vos360.video/Content/CMAF/Live/channel(footballlFinal2003)/master.mpd",
      "cmafHlsUrl": "https://origin-irp-vos-ppp-01.vos360.video/Content/CMAF/Live/channel(footballlFinal2003)/master.m3u8"
    }
  }
}
    
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
