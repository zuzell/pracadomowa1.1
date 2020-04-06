from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI()

app.counter=0

class PatientRq(BaseModel):
    name: str
    surename: str


class PatientResp(BaseModel):
    id: str
    received: dict


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





@app.post("/patient")
def create_patient(rq: PatientRq):
    app.counter +=1
    return PatientResp(id=str(app.counter), received=rq.dict())

@app.get("/patient/{pk}")
def patient_finder(pk):
    if int(pk) > app.counter:
        raise HTTPException(status_code=204, detail="No content")
    return PatientRq(name="NAME", surename="SURENAME")






