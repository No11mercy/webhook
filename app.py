from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

def send_message(message):
    # Функция для отправки сообщения или обработки данных
    app.logger.info(f"Сообщение: {message}")
    # Здесь вы можете добавить код для обработки данных или отправки уведомлений

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Логирование заголовков запроса
        app.logger.debug(f"Заголовки запроса: {request.headers}")

        # Получение типа контента
        content_type = request.headers.get('Content-Type')
        app.logger.debug(f"Content-Type: {content_type}")

        # Обработка JSON данных
        if content_type == 'application/json':
            data = request.get_json()
            app.logger.debug(f"Получены данные JSON: {data}")

        # Обработка текстовых данных
        elif content_type == 'text/plain':
            data = request.get_data(as_text=True)
            app.logger.debug(f"Получены данные как текст: {data}")

        # Если тип данных не поддерживается
        else:
            app.logger.error("Unsupported Media Type")
            return jsonify({"error": "Unsupported Media Type"}), 415

        # Обработка данных
        send_message(f"Получены данные: {data}")
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        # Логирование ошибки
        app.logger.error(f"Произошла ошибка: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
