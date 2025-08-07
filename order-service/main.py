from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
import os

app = FastAPI()

# Database config
DB_HOST = os.getenv("DB_HOST", "mysql")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_NAME = os.getenv("DB_NAME", "orderdb")

# Pydantic model
class Order(BaseModel):
    id: int = None
    customer_name: str
    game_title: str
    quantity: int
    order_date: str
    cart_items: str
    total_price: float

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

@app.get("/orders")
def get_orders():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM orders")
    result = cursor.fetchall()
    conn.close()
    return result

@app.post("/orders")
def create_order(order: Order):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (customer_name, game_title, quantity, order_date) VALUES (%s, %s, %s, %s)",
                   (order.customer_name, order.game_title, order.quantity, order.order_date))
    conn.commit()
    conn.close()
    return {"message": "Order placed successfully"}

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    result = cursor.fetchone()
    conn.close()
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return result

@app.put("/orders/{order_id}")
def update_order(order_id: int, order: Order):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET customer_name=%s, game_title=%s, quantity=%s, order_date=%s WHERE id=%s",
                   (order.customer_name, order.game_title, order.quantity, order.order_date, order_id))
    conn.commit()
    conn.close()
    return {"message": "Order updated"}

@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE id=%s", (order_id,))
    conn.commit()
    conn.close()
    return {"message": "Order deleted"}
