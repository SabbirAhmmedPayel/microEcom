import os
import jwt
import psycopg
from typing import List
from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Order Service")

# --- Configuration (Must match Product/Back services) ---
DATABASE_URL = os.getenv("DATABASE_URL")
# This secret must be identical across all services to share user sessions
SECRET_KEY = os.getenv("JWT_SECRET", "your_jwt_secret")
ALGORITHM = "HS256"

def get_db_conn():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)

# --- Schemas ---
class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderCreate(BaseModel):
    items: List[OrderItem]

# --- JWT Authentication ---
def get_user_id(authorization: str = Header(None)):
    """
    Decodes the JWT to get the userId for the order owner.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header")
    try:
        # Standard Bearer token extraction
        token = authorization.replace("Bearer ", "") if "Bearer " in authorization else authorization
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("userId")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# --- Database Setup (Startup) ---
@app.on_event("startup")
def init_db():
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    total_price DECIMAL NOT NULL,
                    payment_status VARCHAR(50) DEFAULT 'unpaid',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id SERIAL PRIMARY KEY,
                    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    price DECIMAL NOT NULL
                );
            """)
            conn.commit()

# --- Updated Route for Payment Integration ---

@app.post("/orders")
async def create_order(order_input: OrderCreate, user_id: str = Depends(get_user_id)):
    """
    Returns order_id, total_amount, and user_id for the Payment Service.
    """
    total = sum(item.price * item.quantity for item in order_input.items)
    
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            # 1. Save the main order record
            cur.execute(
                "INSERT INTO orders (user_id, total_price) VALUES (%s, %s) RETURNING id",
                (user_id, total)
            )
            order_id = cur.fetchone()['id']
            
            # 2. Save product links (Product IDs from your product section)
            for item in order_input.items:
                cur.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                    (order_id, item.product_id, item.quantity, item.price)
                )
            
            conn.commit()
            
            # This response provides exactly what your partner needs for Payment
            return {
                "status": "success",
                "order_id": order_id,
                "total_amount": float(total),
                "user_id": user_id,  # Extracted from JWT
                "message": "Send these details to the Payment Service"
            }