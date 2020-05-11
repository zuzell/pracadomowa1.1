import aiosqlite
import sqlite3
from fastapi import FastAPI, APIRouter, status, Response, Request, HTTPException
from pydantic import BaseModel
import json



app = FastAPI()
router = APIRouter()

	
class AlbumRequest(BaseModel):
    title: str
    artist_id: int

class AlbumResponse(BaseModel):
    AlbumId: int
    Title: str
    ArtistId: int


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect('chinook.db')

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


@app.post("/albums", response_model=AlbumResponse)
async def receive_album(response: Response, request: AlbumRequest):
    exist = app.db_connection.execute("SELECT Name FROM artists WHERE ArtistId = ?", (request.artist_id,)).fetchall()
    if not exist:
        raise HTTPException(status_code=404, detail={"error": "There is no such composer"})
    cursor = app.db_connection.execute("INSERT INTO albums(ArtistId, Title) VALUES (?, ?)", (request.artist_id, request.title))
    app.db_connection.commit()
    new_album_id = cursor.lastrowid
    response.status_code = 201
    return AlbumResponse(AlbumId=new_album_id, Title=request.title, ArtistId=request.artist_id)

@app.get("/albums/{album_id}", response_model=AlbumResponse)
async def show_album(album_id: int):
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute("SELECT * FROM albums WHERE AlbumId = ?", (album_id,)).fetchall()

    if not data:
        raise HTTPException(status_code=404, detail={"errors": "There is no such composer"})
    return AlbumResponse(AlbumId=album_id, Title=data[0]["title"], ArtistId=data[0]["artistId"])

@app.put("/customers/{customer_id}")
async def update_customer(customer_id: int, request: dict={}):
    app.db_connection.row_factory = sqlite3.Row
    customer = app.db_connection.execute("SELECT * FROM customers WHERE CustomerId = ?", (customer_id,)).fetchall()

    if not customer:
        raise HTTPException(status_code=404, detail={"error": "There is no such customer"})
    queue = "UPDATE customers SET "

    if request:
        for key in request:
            queue += f"{key} = \'{request[key]}\', "
        queue = queue[:-2]
        queue += " WHERE CustomerId = " + str(customer_id)
        app.db_connection.execute(queue)
        app.db_connection.commit()
    return app.db_connection.execute("SELECT * FROM customers WHERE CustomerId = ?",(customer_id,)).fetchone()

@app.get("/sales")
async def show_numbers(category: str):
    app.db_connection.row_factory = sqlite3.Row
    
    if category =="customers":
        data = app.db_connection.execute("SELECT customers.CustomerId, Email, Phone, round(sum(Total),2) AS Sum FROM customers \
                                         JOIN invoices ON customers.CustomerId = invoices.CustomerId \
                                         GROUP BY customers.CustomerId \
                                         ORDER BY Sum DESC, customers.CustomerId").fetchall()
    elif category == "genres":
        data = app.db_connection.execute("SELECT genres.Name, sum(Quantity) AS Sum FROM genres \
                                         JOIN tracks ON tracks.GenreId = genres.GenreId \
                                         JOIN invoice_items ON invoice_items.TrackId = tracks.TrackId \
                                         GROUP BY genres.Name \
                                         ORDER BY Sum DESC, genres.Name").fetchall()
    else:
        raise HTTPException(status_code=404, detail={"error": "There is no such category"})
        
    return data


