from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Конфигурация Telegram бота
BOT_TOKEN = '7331726032:AAG1mu4u5otoscG5qkIjNHUQ5pNLHG27AuE'
CHAT_ID = '2020086574'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

def send_message_to_telegram(message):
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    response = requests.post(TELEGRAM_API_URL, json=payload)
    return response.status_code == 200

@app.route('/webhook', methods=['POST'])
def webhook():
    # Проверяем, что запрос содержит правильный тип контента
    if request.content_type != 'application/json':
        return jsonify({'error': 'Content-Type must be application/json'}), 415

    # Получаем данные JSON из запроса
    data = request.json
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400

    # Извлекаем сообщение из данных JSON
    message = data['message']

    # Отправляем сообщение в Telegram
    if send_message_to_telegram(message):
        return jsonify({'message': 'Message sent to Telegram'}), 200
    else:
        return jsonify({'error': 'Failed to send message to Telegram'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
