from flask import Flask, request, render_template_string
from datetime import datetime
import hmac
import hashlib
import time

app = Flask(__name__)

# Хранилище для полученных вебхуков
webhooks = []

# Переменные для хранения последних сигналов
last_indicator_signal = None
last_strategy_signal = None

# Конфигурация торговли
trade_config = {
    "instrument": "BTC-USDT",  # Инструмент для торговли
    "trade_type": "futures",    # Тип торговли: "spot", "margin", "futures"
    "order_type": "limit",      # Тип ордера: "market", "limit"
    "margin_mode": "isolated",  # Режим маржи: "isolated", "cross"
    "position_size_percent": 50 # Размер позиции в процентах от баланса
}

# Ваши данные API
api_key = "e7d3faf8-8b6a-4708-9d45-d842e1050e17"
secret_key = "332D62A8E67767FF68E021CA5CAA5C9C"
api_passphrase = "1459_Malwar_10_000_Go_Far"

# Функция для генерации подписи
def generate_signature(api_secret, timestamp, body):
    message = f"{timestamp}{body}"
    signature = hmac.new(api_secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return signature

# Функция для получения баланса счета
def get_account_balance():
    url = 'https://www.okx.com/api/v5/account/balance'
    timestamp = str(int(time.time()))
    headers = {
        'Content-Type': 'application/json',
        'OK-ACCESS-KEY': api_key,
        'OK-ACCESS-SIGN': generate_signature(secret_key, timestamp, '{"data": {}}'),
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': api_passphrase,
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверка на успешный ответ
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting account balance: {e}")
        return {}

# Функция для отправки ордера на OKX
def place_order_on_okx(action):
    balance_data = get_account_balance()
    if not balance_data or 'data' not in balance_data:
        print("Failed to retrieve balance data")
        return

    try:
        balance = float(balance_data['data'][0]['total'])  # Пример получения общего баланса
    except (IndexError, ValueError) as e:
        print(f"Error parsing balance data: {e}")
        return

    position_size = (balance * trade_config["position_size_percent"] / 100)

    url = 'https://www.okx.com/api/v5/trade/order'
    timestamp = str(int(time.time()))
    headers = {
        'Content-Type': 'application/json',
        'OK-ACCESS-KEY': api_key,
        'OK-ACCESS-SIGN': generate_signature(secret_key, timestamp, '{"data": {}}'),
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': api_passphrase,
    }
    data = {
        "instId": trade_config["instrument"],  # Пара, например, BTC-USDT
        "tdMode": trade_config["margin_mode"],  # Режим маржи
        "side": action,  # "buy" для лонга, "sell" для шорта
        "ordType": trade_config["order_type"],  # Тип ордера
        "sz": str(position_size)  # Размер позиции
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Проверка на успешный ответ
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error placing order: {e}")
        return {}

# Функция для проверки и выполнения действий
def check_and_execute_trade():
    global last_indicator_signal, last_strategy_signal

    if last_indicator_signal and last_strategy_signal:
        indicator_action = last_indicator_signal.get('action')
        strategy_action = last_strategy_signal.get('signal')

        if indicator_action == 'long' and strategy_action == 'signal':
            result = place_order_on_okx('buy')
            print("Вход в лонг на OKX:", result)
        elif indicator_action == 'short' and strategy_action == 'signal':
            result = place_order_on_okx('sell')
            print("Вход в шорт на OKX:", result)

        # Сбрасываем сигналы после выполнения
        last_indicator_signal = None
        last_strategy_signal = None

# Маршрут для получения вебхуков
@app.route('/webhook', methods=['POST'])
def webhook():
    global last_indicator_signal, last_strategy_signal

    data = request.json
    if data:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        webhooks.append({'timestamp': timestamp, 'data': data})

        # Определяем тип сигнала
        if 'action' in data:  # Это сигнал от индикатора
            last_indicator_signal = data
        elif 'signal' in data:  # Это сигнал от стратегии
            last_strategy_signal = data

        # Проверяем и выполняем сделку, если оба сигнала присутствуют
        check_and_execute_trade()

    return 'Webhook received', 200

# Маршрут для отображения вебхуков
@app.route('/')
def index():
    # HTML-шаблон с Bootstrap для стилизации
    template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Webhook Viewer</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h1 class="mb-4">Received Webhooks</h1>
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th scope="col">#</th>
                        <th scope="col">Timestamp</th>
                        <th scope="col">Data</th>
                    </tr>
                </thead>
                <tbody>
                    {% for i, webhook in enumerate(webhooks) %}
                    <tr>
                        <th scope="row">{{ i + 1 }}</th>
                        <td>{{ webhook.timestamp }}</td>
                        <td><pre>{{ webhook.data | default({}) | tojson(indent=2) }}</pre></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''
    return render_template_string(template, webhooks=webhooks)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
