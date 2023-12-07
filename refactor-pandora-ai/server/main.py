from typing import Union

from fastapi import FastAPI
import uuid

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/createcloudsource")
def read_root():
    return {"id": str(uuid.uuid4())}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
