from flask import Flask, request, jsonify
import requests
import logging

app = Flask(__name__)

# Конфигурация Telegram бота
BOT_TOKEN = '7331726032:AAG1mu4u5otoscG5qkIjNHUQ5pNLHG27AuE'
CHAT_ID = '2020086574'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

def send_message_to_telegram(message):
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    try:
        response = requests.post(TELEGRAM_API_URL, json=payload)
        response.raise_for_status()  # Поднимет исключение для кода ответа 4xx/5xx
        return response.status_code == 200
    except requests.RequestException as e:
        logging.error(f"Error sending message to Telegram: {e}")
        return False

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        logging.debug(f"Request content type: {request.content_type}")
        logging.debug(f"Request data: {request.data.decode('utf-8')}")

        # Проверяем тип контента и извлекаем данные
        if request.content_type == 'application/json':
            data = request.json
            if not data or 'message' not in data:
                error_msg = 'No message provided in JSON'
                logging.error(error_msg)
                return jsonify({'error': error_msg}), 400
            message = data['message']
        elif request.content_type == 'text/plain':
            message = request.data.decode('utf-8')
        else:
            error_msg = 'Unsupported Content-Type'
            logging.error(error_msg)
            return jsonify({'error': error_msg}), 415

        logging.debug(f"Message extracted: {message}")

        # Отправляем сообщение в Telegram
        if send_message_to_telegram(message):
            return jsonify({'message': 'Message sent to Telegram'}), 200
        else:
            error_msg = 'Failed to send message to Telegram'
            logging.error(error_msg)
            return jsonify({'error': error_msg}), 500

    except Exception as e:
        logging.exception("An unexpected error occurred")
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
