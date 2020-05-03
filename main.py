import aiosqlite
import sqlite3
from fastapi import FastAPI, APIRouter

app = FastAPI()
router = APIRouter()



@app.on_event("startup")
async def startup():
	app.db_connection = await aiosqlite.connect('chinook.db')

@app.on_event("shutdown")
async def shutdown():
	await app.db_connection.close()

@app.get("/tracks")
async def tracks(page: int = 0, per_page: int = 10):
	app.db_connection.row_factory = aiosqlite.Row
	cursor = await app.db_connection.execute("SELECT * FROM tracks ORDER BY TrackId LIMIT :per_page OFFSET :per_page*:page",
		{'page': page, 'per_page': per_page})
	tracks = await cursor.fetchall()
	return tracks

@app.get("/tracks/composers")
async def tracks(composer_name, response: Response):
	app.db_connection.row_factory = lambda cursor, x: x[0]
	cursor = await app.db_connection.execute("SELECT Name FROM tracks WHERE Composer = ? ORDER BY Name", (composer_name,))
	tracks = await cursor.fetchall()
	if len(tracks) == 0:
		response.status_code = status.HTTP_404_NOT_FOUND
		return {"detail": {"error": "Your error"}}
	return tracks

