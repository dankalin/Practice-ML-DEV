import uvicorn
from fastapi import FastAPI

from src.database import engine, Base, get_session, Model, session_maker
from src.router import router
from sqlalchemy import select

app = FastAPI()
app.include_router(router=router)
Base.metadata.create_all(engine)


def init_models():
    with session_maker() as session:
        if len(session.execute(select(Model)).fetchall()) != 0:
            return
        model = Model(name="base", price=1)
        model1 = Model(name="catboost", price=10)
        model2 = Model(name="tfidf", price=15)
        session.add(model)
        session.add(model1)
        session.add(model2)
        session.commit()


if __name__ == "__main__":
    init_models()
    uvicorn.run("main:app", reload=True)
