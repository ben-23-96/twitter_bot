from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, Session
from os import getenv
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()


class Birthdays(Base):
    __tablename__ = "birthdays"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), )
    birthday = Column(String(50))

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, birthday={self.birthday!r})"


database_url = getenv('JAWSDB_URL')

engine = create_engine(database_url)

session = Session(engine)

# Base.metadata.create_all(engine)
