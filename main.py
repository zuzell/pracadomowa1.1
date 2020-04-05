from fastapi import FastAPI



app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}

@app.get("/method")
def metoda():
    return{"method": "GET"}


@app.post("/method")
def metoda():
    return{"method": "POST"}






