from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date
import mysql.connector
import os

app = FastAPI()

# Database config
DB_HOST = os.getenv("DB_HOST", "mysql")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_NAME = os.getenv("DB_NAME", "gamedb")

# Pydantic model
class Game(BaseModel):
    id: int = None
    game_name: str
    category: str
    released_date: date
    price: float

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

@app.get("/games")
def get_games():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM games")
    result = cursor.fetchall()
    conn.close()
    return result

@app.post("/games")
def create_game(game: Game):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO games (game_name, category, released_date, price) VALUES (%s, %s, %s, %s)",
        (game.game_name, game.category, game.released_date, game.price)
    )
    conn.commit()
    conn.close()
    return {"message": "Game added successfully"}

@app.get("/games/{game_id}")
def get_game(game_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM games WHERE id = %s", (game_id,))
    result = cursor.fetchone()
    conn.close()
    if not result:
        raise HTTPException(status_code=404, detail="Game not found")
    return result

@app.put("/games/{game_id}")
def update_game(game_id: int, game: Game):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE games SET game_name=%s, category=%s, released_date=%s, price=%s WHERE id=%s",
        (game.game_name, game.category, game.released_date, game.price, game_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Game updated"}

@app.delete("/games/{game_id}")
def delete_game(game_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM games WHERE id=%s", (game_id,))
    conn.commit()
    conn.close()
    return {"message": "Game deleted"}

