import catboost
import joblib
import pandas as pd
import sklearn

base_model = joblib.load("src/models/base.joblib")
tfidf_model = joblib.load("src/models/tfidf.joblib")
catboost_model = catboost.CatBoostClassifier().load_model("src/models/catboost.model")


def base_model_predict(data: pd.DataFrame):
    return base_model.predict(data)
def tfidf_model_predict(data: pd.DataFrame):
    return tfidf_model.predict(data)

def catboost_model_predict(data: pd.DataFrame):
    return catboost_model.predict(data)
