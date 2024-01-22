import pandas as pd
from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.responses import JSONResponse

from src.auth import get_current_user, authenticate_user, create_access_token, get_password_hash
from src.database import get_session
from src.model_predict import base_model_predict, tfidf_model_predict, catboost_model_predict
from src.repository import get_predictions_by_user_id, subtract_money, get_model_by_name, prediction_create, \
    get_user_by_username, create_user, get_all_models
from src.schemes import PredictionScheme, PredictionItem, AvailableModels, RequestPrediction, Token, SingUpRequest, \
    UserScheme, ModelListScheme, ModelScheme

router = APIRouter()


@router.get("/models")
async def get_models(session=Depends(get_session)) -> ModelListScheme:
    models = get_all_models(session)
    if models is None:
        return ModelListScheme(models=[])
    return ModelListScheme(
        models=[
            ModelScheme(
                id=model.id,
                name=model.name,
                cost=model.price
            )
            for model in models
        ]
    )


@router.get("/predictions")
async def get_user_predictions(session= Depends(get_session), user= Depends(get_current_user)) -> PredictionScheme:
    predictions = get_predictions_by_user_id(user.id, session)
    if predictions is None:
        return PredictionScheme(predictions=[])
    return PredictionScheme(
        predictions=[
            PredictionItem(
                id=prediction.id,
                predicted_model_id=prediction.model_id,
                input_data=prediction.input_data,
                result=prediction.predicted_class_id[0],
            )
            for prediction in predictions
        ]
    )


@router.post("/predict")
async def predict(
        model_name: AvailableModels, data: RequestPrediction, user=Depends(get_current_user),
        session=Depends(get_session)
):
    model = get_model_by_name(model_name, session)
    if model is None:
        raise HTTPException(status_code=400, detail="Model not found")
    subtract_money(user.id, model.price, session)

    df = pd.DataFrame(data.data, columns=[" Cluster Label"])
    match model_name:
        case AvailableModels.base:
            res = base_model_predict(df)
        case AvailableModels.tfidf:
            res = tfidf_model_predict(df)
        case AvailableModels.catboost:
            res = catboost_model_predict(df)
        case _:
            raise ValueError
    prediction = prediction_create(user.id, model.id, data.data, res, session)
    return {"model_id": prediction.model_id, "input_data": prediction.input_data, "predicted_class_id": prediction.predicted_class_id[0]}


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session=Depends(get_session)):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")


@router.post("/signup")
async def signup(user_info: SingUpRequest, session=Depends(get_session)) -> Token:
    user = get_user_by_username(user_info.username, session)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    hashed_password = get_password_hash(user_info.password)
    user = create_user(
        user_info.username,
        hashed_password,
        session,
    )
    token = create_access_token({"sub": user_info.username})
    return Token(access_token=token, token_type="bearer")


@router.get("/me")
async def me(user=Depends(get_current_user)):
    return UserScheme(username=user.username, balance=user.balance)
