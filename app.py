from flask import Flask, request, render_template_string
from datetime import datetime

app = Flask(__name__)

# Хранилище для полученных вебхуков
webhooks = []

# Маршрут для получения вебхуков
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        webhooks.append({'timestamp': timestamp, 'data': data})
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
                        <td><pre>{{ webhook.data | tojson(indent=2) }}</pre></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''
    # Передаем функцию enumerate в контекст шаблона
    return render_template_string(template, webhooks=webhooks, enumerate=enumerate)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
