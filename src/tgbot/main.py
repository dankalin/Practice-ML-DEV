import telebot
import requests
from fastapi import HTTPException

TOKEN = '6828712799:AAEsyacMryknyLPvnn90KbZ9g9e81BFKJS0'
API_URL = 'http://127.0.0.1:8000'  

bot = telebot.TeleBot(TOKEN)
access_tokens = {}  # Dictionary to store access tokens by chat ID

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the FastAPI bot. Now you can use /signup, /login commands.")

@bot.message_handler(commands=['signup'])
def signup_user(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Please enter your username and password in the format: username password")
    bot.register_next_step_handler(message, process_signup_step)

def process_signup_step(message):
    try:
        chat_id = message.chat.id
        username, password = message.text.split(' ', 1)
        response = requests.post(API_URL + '/signup', json={'username': username, 'password': password})
        if response.status_code == 200:
            token = response.json()['access_token']
            access_tokens[chat_id] = token 
            bot.send_message(chat_id, f"Signup successful! Now you can use /me,/models,/predictions,/predict.")
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        bot.send_message(chat_id, f"Error: {e}")

@bot.message_handler(commands=['login'])
def login_user(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Please enter your username and password in the format: username password")
    bot.register_next_step_handler(message, process_login_step)

def process_login_step(message):
    try:
        chat_id = message.chat.id
        username, password = message.text.split(' ', 1)
        response = requests.post(API_URL + '/token', data={'username': username, 'password': password})
        if response.status_code == 200:
            token = response.json()['access_token']
            access_tokens[chat_id] = token  
            bot.send_message(chat_id, f"Login successful! Now you can use /me,/models,/predictions,/predict.")
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        bot.send_message(chat_id, f"Error: {e}")

@bot.message_handler(commands=['predictions'])
def handle_commands_with_token(message):
    chat_id = message.chat.id
    if chat_id not in access_tokens:
        bot.send_message(chat_id, "Please log in or sign up first.")
        return

    command = message.text.split()[0][1:] 
    token = access_tokens[chat_id]
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(API_URL + f'/{command}', headers=headers)

    if response.status_code == 200:
        data = response.json()
        predictions = data['predictions']
        for prediction in predictions:
            model_id = prediction['predicted_model_id']
            result = prediction['result']
            input_data = prediction['input_data']

            # Определить имя модели на основе model_id
            if model_id == 1:
                model_name = 'base'
            elif model_id == 2:
                model_name = 'catboost'
            elif model_id == 3:
                model_name = 'tfidf'
            else:
                model_name = 'Unknown'

            bot.send_message(chat_id, f"Model name: {model_name}")
            bot.send_message(chat_id, f"Predicted class: {result}")
            bot.send_message(chat_id, f"Input data: {input_data}")
    else:
        bot.send_message(chat_id, f"Error: {response.text}")

@bot.message_handler(commands=['models'])
def handle_commands_with_token(message):
    chat_id = message.chat.id
    if chat_id not in access_tokens:
        bot.send_message(chat_id, "Please log in or sign up first.")
        return

    command = message.text.split()[0][1:] 
    token = access_tokens[chat_id]
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(API_URL + f'/{command}', headers=headers)

    if response.status_code == 200:
        data = response.json()
        models = data['models']
        for model in models:
            name = model['name']
            cost = model['cost']
            bot.send_message(chat_id, f"Model {name} cost {cost}")

@bot.message_handler(commands=['me'])
def handle_commands_with_token(message):
    chat_id = message.chat.id
    if chat_id not in access_tokens:
        bot.send_message(chat_id, "Please log in or sign up first.")
        return

    command = message.text.split()[0][1:] 
    token = access_tokens[chat_id]
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(API_URL + f'/{command}', headers=headers)

    if response.status_code == 200:
        data = response.json()
        username = data['username']
        balance = data['balance']
        bot.send_message(chat_id, f"Username: {username}\nBalance: {balance}")
    else:
        bot.send_message(chat_id, f"Error: {response.text}")


@bot.message_handler(commands=['predict'])
def predict_step(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Please enter your model name and input data in the format: model name  data")
    bot.register_next_step_handler(message, process_predict_step)


def process_predict_step(message):
    try:
        chat_id = message.chat.id
        model_name, input_data = message.text.split(' ', 1)
        token = access_tokens.get(chat_id)
        if not token:
            bot.send_message(chat_id, "Please log in or sign up first.")
            return
        headers = {'Authorization': f'Bearer {token}'}
        if model_name not in ['base', 'tfidf', 'catboost']:
            bot.send_message(chat_id, "Invalid model name. Please use 'base', 'tfidf', or 'catboost'.")
            return
        response = requests.post(API_URL + f'/predict?model_name={model_name}', json={'data': [input_data]}, headers=headers)
        if response.status_code == 200:
            prediction = response.json()
            predicted = prediction['predicted_class_id']
            bot.send_message(chat_id, f"Your prediction: {predicted}")
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        bot.send_message(chat_id, f"Error: {e}")


bot.polling()