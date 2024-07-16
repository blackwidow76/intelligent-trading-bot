from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    contract_address = Column(String, unique=True, index=True)
    creation_time = Column(DateTime)

    metadata = relationship("TokenMetadata", back_populates="token", uselist=False)

class TokenMetadata(Base):
    __tablename__ = "token_metadata"

    id = Column(Integer, primary_key=True, index=True)
    token_id = Column(Integer, ForeignKey("tokens.id"))
    name = Column(String)
    symbol = Column(String)
    decimals = Column(Integer)
    total_supply = Column(String)

    token = relationship("Token", back_populates="metadata")
