import os
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import APIKeyHeader
from sqlmodel import SQLModel, Field, create_engine, Session, select
import jwt
from dotenv import load_dotenv

# --- Load environment ---
load_dotenv()

app = FastAPI(title="Payment Service")

# --- Database ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:NewPassword123@localhost/payment_db")
engine = create_engine(DATABASE_URL, echo=True)


class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    order_id: int
    order_price: Decimal
    current_balance: Decimal = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


def get_session():
    with Session(engine) as session:
        yield session


# --- JWT setup ---
header_scheme = APIKeyHeader(name="Authorization")
SECRET_KEY = os.getenv("JWT_SECRET", "your_jwt_secret")


def get_current_user(token: str = Depends(header_scheme)):
    try:
        raw_token = token.replace("Bearer ", "") if "Bearer " in token else token
        payload = jwt.decode(raw_token, SECRET_KEY, algorithms=["HS256"])
        # Extract user and order info from JWT
        return {
            "userId": payload.get("userId"),
            "orderId": payload.get("orderId"),
            "orderPrice": Decimal(payload.get("orderPrice", 0))
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# --- Startup: create tables automatically ---
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


# --- Routes ---

@app.post("/payments", response_model=Payment)
def create_payment(session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    # Create payment directly from JWT info
    payment = Payment(
        user_id=current_user["userId"],
        order_id=current_user["orderId"],
        order_price=current_user["orderPrice"],
        current_balance=current_user["orderPrice"]
    )
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return payment


@app.get("/payments", response_model=List[Payment])
def get_my_payments(session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    statement = select(Payment).where(Payment.user_id == current_user["userId"])
    return session.exec(statement).all()


@app.post("/payments/{payment_id}/deduct")
def deduct_balance(payment_id: int, amount: Decimal, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    payment = session.get(Payment, payment_id)
    if not payment or payment.user_id != current_user["userId"]:
        raise HTTPException(status_code=404, detail="Payment record not found")
    if payment.current_balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    payment.current_balance -= amount
    session.add(payment)
    session.commit()
    session.refresh(payment)
    return {"status": "success", "new_balance": payment.current_balance}


@app.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {"status": "token_valid", "user": current_user}
