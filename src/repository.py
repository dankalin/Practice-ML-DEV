from src.database import Model, Prediction, User
from sqlalchemy import select, update


def get_model_by_name(name, db):
    return db.scalars(select(Model).where(Model.name == name)).first()


def get_model_by_id(model_id, db):
    return db.scalars(select(Model).where(Model.id == model_id)).first()


def get_all_models(db):
    return db.scalars(select(Model)).all()


def get_predictions_by_user_id(user_id, db):
    return db.scalars(select(Prediction).where(Prediction.user_id == user_id)).all()


def prediction_create(user_id, model_id, data, predicted_class, db):
    predictions = Prediction(user_id=user_id, model_id=model_id, input_data=data[0], predicted_class_id=predicted_class)
    db.add(predictions)
    db.commit()
    return predictions


def get_prediction_by_id(prediction_id, db):
    return db.scalars(select(Prediction).where(Prediction.id == prediction_id)).first()


def get_user_by_username(username, db):
    return db.scalars(select(User).where(User.username == username)).first()


def create_user(username, password, db):
    user = User(username=username, password=password)
    db.add(user)
    db.commit()
    return user


def subtract_money(user_id, cost, db):
    db.execute(update(User).where(User.id == user_id).values(balance=User.balance - cost))
    db.commit()
