from fastapi import FastAPI



app = FastAPI()

i=0

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
def create_patient(mydict):
    i += 1
    return {"id": i, "patient": f'{mydict}'}






