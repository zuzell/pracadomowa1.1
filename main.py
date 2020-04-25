from _sha256 import sha256

from typing import Dict

from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from fastapi import FastAPI, Request, Response, status, Depends, HTTPException
from starlette.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.counter: int = 0


class Patient(BaseModel):
    name: str
    surname: str
    id: str = 0


class PatientsResp(BaseModel):
    response: dict


templates = Jinja2Templates(directory="templates")
app.storage: Dict[int, Patient] = {}
app.tokens = []

security = HTTPBasic()
app.secret_key = "3586551867030721809738080201689944348810193121742430128090228167"


def check_login(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "trudnY")
    correct_password = secrets.compare_digest(credentials.password, "PaC13Nt")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username + ":" + credentials.password


@app.get("/")
def root():
    return {"message": "Hello World during the coronavirus pandemic!"}


@app.api_route(path="/welcome", methods=["GET"])
def welcome(request: Request, auth: str = Depends(check_login)):
    return templates.TemplateResponse("greeting.html", {"request": request, "user": auth.split(':', 1)[0]})


@app.post("/patient")
async def add_patient(response: Response, patient: Patient, auth: str = Depends(check_login)):
    patient.id = "id_" + str(app.counter)
    app.storage[app.counter] = patient
    app.counter += 1
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = f"/patient/{app.counter - 1}"


@app.get("/patient")
def get_patients(response: Response, auth: str = Depends(check_login)):
    resp = {}
    for x in app.storage.values():
        resp[x.id] = {'name': x.name, 'surname': x.surname}
    if resp:
        return JSONResponse(resp)
    response.status_code = status.HTTP_204_NO_CONTENT


@app.get("/patient/{pk}")
def get_patient(pk: int, auth: str = Depends(check_login)):
    if pk in app.storage:
        return app.storage.get(pk)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete("/patient/{pk}")
def get_patient(pk: int, response: Response, auth: str = Depends(check_login)):
    if pk in app.storage:
        app.storage.pop(pk, None)
        response.status_code = status.HTTP_204_NO_CONTENT


@app.post("/login")
async def login(response: Response, login_pass: str = Depends(check_login)):
    response.headers["Location"] = "/welcome"
    response.status_code = status.HTTP_302_FOUND
    secret_token = sha256(bytes(f"{login_pass.split(':', 1)[0]}{login_pass.split(':', 1)[1]}{app.secret_key}",
                                encoding='utf8')).hexdigest()
    app.tokens += secret_token
    response.set_cookie(key="session_token", value=secret_token)
    return response


@app.post("/logout")
def logout(response: Response, auth: str = Depends(check_login)):
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = "/"
    response.delete_cookie("session_token")
    return response
