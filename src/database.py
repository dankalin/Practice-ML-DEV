from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

engine = create_engine("sqlite:///database.db")
session_maker = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Model(Base):
    __tablename__ = "model"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    balance = Column(Float, nullable=False, default=100)


class Prediction(Base):
    __tablename__ = "prediction"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey("model.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    input_data = Column(String(255), nullable=False)
    predicted_class_id = Column(Integer, nullable=False)


def get_session():
    session = session_maker()
    try:
        yield session
    finally:
        session.close()
