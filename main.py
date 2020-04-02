from fastapi import FastAPI

from pydantic import BaseModel

app = FastAPI()
# to see what funny will come
app.counter = 0


class HelloResp(BaseModel):
    msg: str

@app.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}



