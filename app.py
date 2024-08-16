from flask import Flask, request, jsonify

app = Flask(__name__)

# Адрес локального сервера, куда будут передаваться вебхуки
LOCAL_SERVER_URL = 'http://127.0.0.1:5000/webhook'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    # Передача данных на локальный сервер
    try:
        response = requests.post(LOCAL_SERVER_URL, json=data)
        response.raise_for_status()  # Проверка на ошибки HTTP
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Webhook received and forwarded'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Настройка сервера Flask на прослушивание всех IP-адресов
