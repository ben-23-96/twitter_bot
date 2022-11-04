from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()


class Birthdays(Base):
    __tablename__ = "birthdays"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), )
    birthday = Column(String(50))

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, birthday={self.birthday!r})"


engine = create_engine('mysql://{0}:{1}@{2}:{3}/{4}'.format(
    'root', 'Katmando23*', 'localhost', 3306, 'twitter_bot_db'))

session = Session(engine)

# Base.metadata.create_all(engine)
