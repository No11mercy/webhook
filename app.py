from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# URL, на который будут отправляться вебхуки
FORWARD_URL = 'http://62.113.108.39:5000/'

@app.route('/webhook', methods=['POST'])
def webhook():
    # Получение данных вебхука
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    # Пересылка данных на внешний сервер
    try:
        response = requests.post(FORWARD_URL, json=data)
        response.raise_for_status()  # Выбрасывает исключение для HTTP ошибок
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

    # Возврат ответа, если успешно
    return jsonify({'status': 'success', 'message': 'Webhook forwarded successfully'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
