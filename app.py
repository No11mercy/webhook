import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Настройки: Ваши токен и ID чата
BOT_TOKEN = '7331726032:AAG1mu4u5otoscG5qkIjNHUQ5pNLHG27AuE'
CHAT_ID = '2020086574'

# Функция для отправки сообщения в Telegram
def send_message(text):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': text}
    response = requests.post(url, data=data)
    return response

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Пытаемся получить данные как JSON
        data = request.get_json()
        
        # Если данные пусты, используем сырые данные (в случае text/plain)
        if not data:
            data = request.get_data(as_text=True)
        
        # Отправляем сообщение в Telegram
        send_message(f"Получены данные: {data}")
        
        return {"status": "ok"}, 200

    except Exception as e:
        # Логирование ошибки
        app.logger.error(f"Произошла ошибка: {str(e)}")
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
