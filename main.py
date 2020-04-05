from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

i=0

class PatientRq(BaseModel):
    name: str
    surename: str


class PatientResp(BaseModel):
    id: int=i
    received: Dict


@app.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}

@app.get("/method")
def metoda():
    return{"method": "GET"}


@app.post("/method")
def metoda():
    return{"method": "POST"}

@app.put("/method")
def metoda():
    return{"method": "PUT"}

@app.delete("/method")
def metoda():
    return{"method": "DELETE"}





@app.post("/patient", response_model=PatientResp)
def create_patient(rq: PatientRq):
    i=i+ 1
    return PatientResp(recived=rq.dict())






