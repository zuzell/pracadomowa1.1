from fastapi import FastAPI



app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}

@app.get("/method")
def metoda(method):
    return{"method": "GET"}






