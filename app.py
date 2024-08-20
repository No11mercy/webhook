from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Настройки Telegram Bot API
BOT_TOKEN = "7331726032:AAG1mu4u5otoscG5qkIjNHUQ5pNLHG27AuE"  # Ваш токен бота
CHAT_ID = "2020086574"  # Ваш ID чата

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    response = requests.post(url, data=data)
    return response.status_code, response.text

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        try:
            data = request.json
            if data is None:
                raise ValueError("Пустое тело запроса или некорректный формат данных. Ожидался JSON.")

            # Обработка данных от TradingView
            message = f"Получен сигнал от TradingView:\n\n{data}"
            status_code, response_text = send_telegram_message(message)
            
            if status_code == 200:
                return jsonify({"status": "success", "message": "Сообщение отправлено в Telegram"}), 200
            else:
                return jsonify({"status": "error", "message": response_text}), status_code

        except Exception as e:
            # Вывод детализированного сообщения об ошибке
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "Только POST-запросы разрешены"}), 405

if __name__ == '__main__':
    # Запуск Flask сервера
    app.run(host='0.0.0.0', port=5000)
