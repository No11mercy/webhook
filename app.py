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
    data = request.json  # Получаем данные JSON из запроса
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400

    message = data['message']  # Извлекаем сообщение из данных JSON
    if send_message_to_telegram(message):
        return jsonify({'message': 'Message sent to Telegram'}), 200
    else:
        return jsonify({'error': 'Failed to send message to Telegram'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
