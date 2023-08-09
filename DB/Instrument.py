from sqlalchemy import Column, Integer, String

from .base import Base


class Instrument(Base):
    __tablename__: str = "instruments"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    address = Column(String)
    token = Column(String)

    def __init__(self, name, address, token):
        self.name = name
        self.address = address
        self.token = token
