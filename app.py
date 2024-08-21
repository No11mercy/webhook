from flask import Flask, request, jsonify
import ccxt
import time

app = Flask(__name__)

# Хранилище состояния для сигналов
state = {
    'pending_signal': None,
    'timestamp': None,
    'symbol': None
}

def execute_trade(signal, symbol):
    # Создайте клиента
    exchange = ccxt.okx({
        'apiKey': 'e7d3faf8-8b6a-4708-9d45-d842e1050e17',
        'secret': '332D62A8E67767FF68E021CA5CAA5C9C',
        'password': '1459_Malwar_10_000_Go_Far',
    })

    # Задайте использование фьючерсного рынка
    exchange.options['defaultType'] = 'futures'

    # Установите плечо
    leverage = 10
    exchange.set_leverage(leverage, symbol)

    # Получите баланс USDT на фьючерсном аккаунте
    balance = exchange.fetch_balance({'type': 'futures'})
    usdt_balance = balance['free']['USDT']
    total_balance = balance['total']['USDT']

    # Получите все открытые позиции
    positions = exchange.fetch_positions()
    used_balance = sum([pos['info']['initialMargin'] for pos in positions if pos['symbol'] == symbol])

    # Если есть открытая позиция, используйте оставшиеся доступные средства
    if used_balance > 0:
        order_amount = (usdt_balance / total_balance) * used_balance * leverage
    else:
        # Если нет позиции, зайдите на 50% от доступного баланса
        order_amount = (usdt_balance * 0.1) * leverage

    # Получите книгу ордеров для нахождения наилучшей цены
    order_book = exchange.fetch_order_book(symbol)
    best_bid = order_book['bids'][0][0] if order_book['bids'] else None  # Лучшая цена на покупку
    best_ask = order_book['asks'][0][0] if order_book['asks'] else None  # Лучшая цена на продажу

    # Выберите наилучшую цену для лимитного ордера
    limit_price = best_ask if best_ask else best_bid

    # В зависимости от сигнала создайте ордер на покупку (лонг) или продажу (шорт)
    if signal == 'long':
        order = exchange.create_limit_buy_order(symbol, order_amount, limit_price)
    elif signal == 'short':
        order = exchange.create_limit_sell_order(symbol, order_amount, limit_price)
    else:
        return {'error': 'Invalid signal'}

    return order

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    signal = data.get('signal')
    symbol = data.get('symbol')

    current_time = time.time()

    if signal and symbol:
        if signal in ['long', 'short']:
            # Сохраните сигнал, инструмент и текущее время в ожидании подтверждения
            state['pending_signal'] = signal
            state['symbol'] = symbol
            state['timestamp'] = current_time
            return jsonify({'message': 'Signal saved, waiting for confirmation'}), 200

        elif signal == 'ACTVE':
            if state['pending_signal'] and state['symbol'] == symbol:
                elapsed_time = current_time - state['timestamp']
                if elapsed_time <= 15:  # Проверка, что прошло не более 15 секунд
                    try:
                        order = execute_trade(state['pending_signal'], state['symbol'])
                        state['pending_signal'] = None  # Сбросьте состояние после выполнения сделки
                        state['timestamp'] = None
                        state['symbol'] = None
                        return jsonify(order), 200
                    except Exception as e:
                        return jsonify({'error': str(e)}), 500
                else:
                    # Время ожидания истекло
                    state['pending_signal'] = None
                    state['timestamp'] = None
                    state['symbol'] = None
                    return jsonify({'message': 'Signal expired'}), 400
            else:
                return jsonify({'message': 'No pending signal to confirm or symbol mismatch'}), 400

        else:
            return jsonify({'message': 'Invalid signal provided'}), 400
    else:
        return jsonify({'message': 'No signal or symbol provided'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
