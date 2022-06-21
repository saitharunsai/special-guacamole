from sqlalchemy import Column, Integer, Float, String

from db import Base


class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True, index=True)
    user_address = Column(String)
    user_name = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    postal_code = Column(Integer)
    longitude = Column(Float)
    latitude = Column(Float)
