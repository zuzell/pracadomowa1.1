import aiosqlite
import sqlite3
from fastapi import FastAPI, APIRouter, status, Response
from pydantic import BaseModel

app = FastAPI()
router = APIRouter()



@router.on_event("startup")
async def startup():
	router.db_connection = await aiosqlite.connect('chinook.db')

@router.on_event("shutdown")
async def shutdown():
	await router.db_connection.close()


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


class Album(BaseModel):
	title: str
	artist_id: int

@router.post("/albums")
async def add_album(response: Response, album: Album):
	router.db_connection.row_factory = None
	cursor = await router.db_connection.execute("SELECT ArtistId FROM artists WHERE ArtistId = ?",
		(album.artist_id, ))
	result = await cursor.fetchone()
	if result is None:
		response.status_code = status.HTTP_404_NOT_FOUND
		return {"detail":{"error":"Artist with that ID does not exist."}}
	cursor = await router.db_connection.execute("INSERT INTO albums (Title, ArtistId) VALUES (?, ?)",
		(album.title, album.artist_id))
	await router.db_connection.commit()
	response.status_code = status.HTTP_201_CREATED
	return {"AlbumId": cursor.lastrowid, "Title": album.title, "ArtistId": album.artist_id}

@router.get("/albums/{album_id}")
async def tracks_composers(response: Response, album_id: int):
	router.db_connection.row_factory = aiosqlite.Row
	cursor = await router.db_connection.execute("SELECT * FROM albums WHERE AlbumId = ?",
		(album_id, ))
	album = await cursor.fetchone()
	if album is None: # Not required by tests, but why not :)
		response.status_code = status.HTTP_404_NOT_FOUND
		return {"detail":{"error":"Album with that ID does not exist."}}
	return album

class Customer(BaseModel):
	company: str = None
	address: str = None
	city: str = None
	state: str = None
	country: str = None
	postalcode: str = None
	fax: str = None

@router.put("/customers/{customer_id}")
async def tracks_composers(response: Response, customer_id: int, customer: Customer):
	cursor = await router.db_connection.execute("SELECT CustomerId FROM customers WHERE CustomerId = ?",
		(customer_id, ))
	result = await cursor.fetchone()
	if result is None:
		response.status_code = status.HTTP_404_NOT_FOUND
		return {"detail":{"error":"Customer with that ID does not exist."}}
	update_customer = customer.dict(exclude_unset=True)
	values = list(update_customer.values())
	if len(values) != 0:
		values.append(customer_id)
		query = "UPDATE customers SET "
		for key, value in update_customer.items():
			key.capitalize()
			if key == "Postalcode":
				key = "PostalCode"
			query += f"{key}=?, "
		query = query[:-2]
		query += " WHERE CustomerId = ?"
		cursor = await router.db_connection.execute(query, tuple(values))
		await router.db_connection.commit()
	router.db_connection.row_factory = aiosqlite.Row
	cursor = await router.db_connection.execute("SELECT * FROM customers WHERE CustomerId = ?",
		(customer_id, ))
	customer = await cursor.fetchone()
	return customer

@router.get("/sales")
async def tracks_composers(response: Response, category: str):
	if category == "customers":
		router.db_connection.row_factory = aiosqlite.Row
		cursor = await router.db_connection.execute(
			"SELECT invoices.CustomerId, Email, Phone, ROUND(SUM(Total), 2) AS Sum "
			"FROM invoices JOIN customers on invoices.CustomerId = customers.CustomerId "
			"GROUP BY invoices.CustomerId ORDER BY Sum DESC, invoices.CustomerId")
		stats = await cursor.fetchall()
		return stats
	if category == "genres":
		router.db_connection.row_factory = aiosqlite.Row
		cursor = await router.db_connection.execute(
			"SELECT genres.Name, SUM(Quantity) AS Sum FROM invoice_items "
			"JOIN tracks ON invoice_items.TrackId = tracks.TrackId "
			"JOIN genres ON tracks.GenreId = genres.GenreId "
			"GROUP BY tracks.GenreId ORDER BY Sum DESC, genres.Name")
		stats = await cursor.fetchall()
		return stats
	else:
		response.status_code = status.HTTP_404_NOT_FOUND
		return {"detail":{"error":"Unsuported category."}}
