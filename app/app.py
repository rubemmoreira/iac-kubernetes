from flask import Flask, request, jsonify
import random
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Configuração do banco (via variáveis de ambiente)
DB_HOST = os.getenv('DB_HOST', '192.168.3.37')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'stocks')
DB_USER = os.getenv('DB_USER', 'stockuser')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'stock123')

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Consultor de Ações</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
            input, select, button { padding: 10px; margin: 5px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #4CAF50; color: white; }
            .positive { color: green; }
            .negative { color: red; }
        </style>
    </head>
    <body>
        <h1>📈 Consultor de Ações</h1>
        <p>Banco conectado: <strong>''' + DB_HOST + '''</strong></p>
        <form id="form">
            <div>
                <label>Código da Ação:</label>
                <input type="text" id="symbol" placeholder="PETR4, VALE3, ITUB4" required>
            </div>
            <div>
                <label>Período:</label>
                <select id="period">
                    <option value="7">7 dias</option>
                    <option value="30" selected>30 dias</option>
                    <option value="90">90 dias</option>
                </select>
            </div>
            <button type="submit">Consultar</button>
        </form>
        <div id="resultado" style="margin-top: 20px;"></div>
        <script>
        document.getElementById('form').onsubmit = async (e) => {
            e.preventDefault();
            const symbol = document.getElementById('symbol').value.toUpperCase();
            const period = document.getElementById('period').value;
            const res = await fetch(`/api/stock?symbol=${symbol}&period=${period}`);
            const data = await res.json();
            if (data.error) {
                document.getElementById('resultado').innerHTML = `<p style="color:red">Erro: ${data.error}</p>`;
                return;
            }
            let html = '<h2>' + data.symbol + '</h2>';
            html += '<table>';
            html += '<tr><th>Data</th><th>Abertura</th><th>Máxima</th><th>Mínima</th><th>Fechamento</th><th>Variação</th></tr>';
            data.data.forEach(item => {
                let changeClass = item.change >= 0 ? 'positive' : 'negative';
                let changeSign = item.change >= 0 ? '+' : '';
                html += `<tr>
                    <td>${item.date}</td>
                    <td>R$ ${item.open}</td>
                    <td>R$ ${item.high}</td>
                    <td>R$ ${item.low}</td>
                    <td><strong>R$ ${item.close}</strong></td>
                    <td class="${changeClass}">${changeSign}${item.change}%</td>
                </tr>`;
            });
            html += '</table>';
            html += `<p>📊 Total de registros: ${data.data.length}</p>`;
            document.getElementById('resultado').innerHTML = html;
        };
        </script>
    </body>
    </html>
    '''

@app.route('/api/stock')
def get_stock():
    symbol = request.args.get('symbol', '').upper()
    period = int(request.args.get('period', 30))
    
    if not symbol:
        return jsonify({'error': 'Símbolo obrigatório'}), 400
    
    # Preços base por símbolo (simulação)
    prices = {
        'PETR4': 35.50,
        'VALE3': 68.20,
        'ITUB4': 32.50,
        'BBDC4': 28.30,
        'ABEV3': 14.20,
    }
    
    base_price = prices.get(symbol, 50.00)
    data = []
    
    for i in range(period):
        date = (datetime.now() - timedelta(days=period - i)).strftime('%Y-%m-%d')
        variation = random.uniform(-0.03, 0.03)
        close = round(base_price * (1 + variation), 2)
        open_price = round(close * (1 + random.uniform(-0.02, 0.02)), 2)
        high = round(max(open_price, close) * (1 + random.uniform(0, 0.02)), 2)
        low = round(min(open_price, close) * (1 - random.uniform(0, 0.02)), 2)
        change = round(((close - open_price) / open_price) * 100, 2)
        
        data.append({
            'date': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'change': change
        })
        
        base_price = close  # Próximo dia baseado no fechamento atual
    
    return jsonify({'symbol': symbol, 'data': data})

@app.route('/health')
def health():
    return {'status': 'healthy', 'db_host': DB_HOST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)