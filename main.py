from fastapi import FastAPI

from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}

class GiveMeSomethingRq(BaseModel):
    first_key: str


class GiveMeSomethingResp(BaseModel):
    received: Dict
    constant_data: str = "python jest super"


@app.post("/dej/mi/coś", response_model=GiveMeSomethingResp)
def receive_something(rq: GiveMeSomethingRq):
    return GiveMeSomethingResp(received=rq.dict())



