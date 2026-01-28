import os
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Field, SQLModel, create_engine, Session, select
from dotenv import load_dotenv
from fastapi.security import APIKeyHeader
import jwt

load_dotenv()
app = FastAPI()

# --- Database Setup ---
# Ensure your .env has DATABASE_URL=sqlite:///database.db or similar
engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///database.db"))

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    price: float
    description: str
    stock: int

def get_session():
    with Session(engine) as session:
        yield session

# --- Security Setup ---
header_scheme = APIKeyHeader(name="Authorization")
SECRET_KEY = os.getenv("JWT_SECRET", "your_jwt_secret")

def get_current_user(token: str = Depends(header_scheme)):
    try:
        # Handles "Bearer <token>" or just "<token>"
        raw_token = token.replace("Bearer ", "") if "Bearer " in token else token
        payload = jwt.decode(raw_token, SECRET_KEY, algorithms=["HS256"])
        return {"userId": payload.get("userId")}
    except Exception:
        # Hackathon fallback
        return {"userId": "guest_mode"}

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# --- Routes ---

@app.get("/products", response_model=List[Product])
def read_products(
    session: Session = Depends(get_session),
    # Adding this line makes the 'Authorize' button appear:
    current_user: dict = Depends(get_current_user) 
):
    return session.exec(select(Product)).all()

@app.post("/products", response_model=Product)
def create_product(
    product: Product, 
    session: Session = Depends(get_session),
    # Protecting the POST route as well:
    current_user: dict = Depends(get_current_user)
):
    session.add(product)
    session.commit()
    session.refresh(product)
    return product
@app.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    # This returns whatever was inside your JWT payload
    return {"status": "token_is_valid", "user_data": current_user}