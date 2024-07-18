from pymongo import MongoClient
from pydantic import BaseModel
from datetime import datetime
import os

from database.database import MONGODB_URI

client = MongoClient(MONGODB_URI)
db = client.get_default_database()

class Token(BaseModel):
    name: str
    symbol: str
    launch_date: datetime
    price: float
    volume: float = None
    contract_address: str

class Trade(BaseModel):
    token: str
    trade_time: datetime
    amount: float
    price: float

class User(BaseModel):
    username: str
    email: str
