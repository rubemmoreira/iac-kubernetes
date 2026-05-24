from flask import Flask, request, jsonify, render_template_string
import yfinance as yf
import psycopg2
import os
import json
from datetime import datetime, timedelta
import hashlib

app = Flask(__name__)

DB_HOST = os.getenv('DB_HOST', '192.168.3.37')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'stocks')
DB_USER = os.getenv('DB_USER', 'stockuser')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'stock123')

cache = {}

def get_db_connection():
    try:
        return psycopg2.connect(
            host=DB_HOST, port=DB_PORT,
            database=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
    except Exception as e:
        print(f"Erro: {e}")
        return None

def init_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS stock_queries (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(10) NOT NULL,
                interval VARCHAR(5) NOT NULL,
                period VARCHAR(10) NOT NULL,
                query_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                result_data JSONB,
                cache_key VARCHAR(64) UNIQUE
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("✅ DB inicializado")

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Consultor de Ações</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        input, select, button { padding: 10px; margin: 5px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
    </style>
    </head>
    <body>
        <h1>📈 Consultor de Ações</h1>
        <form id="form">
            <div><label>Código:</label><input type="text" id="symbol" placeholder="PETR4" required></div>
            <div><label>Timeframe:</label>
                <select id="interval"><option value="1d">1 dia</option><option value="1wk">1 semana</option><option value="1mo">1 mês</option></select>
            </div>
            <div><label>Período:</label>
                <select id="period"><option value="1mo">1 mês</option><option value="3mo">3 meses</option><option value="6mo">6 meses</option><option value="1y">1 ano</option></select>
            </div>
            <button type="submit">Consultar</button>
        </form>
        <div id="resultado"></div>
        <script>
        document.getElementById('form').onsubmit = async (e) => {
            e.preventDefault();
            const symbol = document.getElementById('symbol').value.toUpperCase();
            const interval = document.getElementById('interval').value;
            const period = document.getElementById('period').value;
            const res = await fetch(`/api/stock?symbol=${symbol}&interval=${interval}&period=${period}`);
            const data = await res.json();
            if (data.error) {
                document.getElementById('resultado').innerHTML = `<p style="color:red">Erro: ${data.error}</p>`;
                return;
            }
            let html = '<h2>' + data.symbol + '</h2><table><tr><th>Data</th><th>Abertura</th><th>Máxima</th><th>Mínima</th><th>Fechamento</th></tr>';
            data.data.slice(0, 50).forEach(item => {
                html += `<tr><td>${item.date}</td><td>R$ ${item.open}</td><td>R$ ${item.high}</td><td>R$ ${item.low}</td><td><strong>R$ ${item.close}</strong></td></tr>`;
            });
            html += '</table><p>' + data.data.length + ' registros</p>';
            document.getElementById('resultado').innerHTML = html;
        };
        </script>
    </body>
    </html>
    '''

@app.route('/api/stock')
def get_stock():
    symbol = request.args.get('symbol', '').upper()
    interval = request.args.get('interval', '1d')
    period = request.args.get('period', '1mo')
    if not symbol:
        return jsonify({'error': 'Símbolo obrigatório'}), 400
    try:
        ticker = yf.Ticker(f"{symbol}.SA" if symbol[-1].isdigit() else symbol)
        hist = ticker.history(interval=interval, period=period)
        if hist.empty:
            return jsonify({'error': f'Nenhum dado para {symbol}'}), 404
        result = []
        for date, row in hist.iterrows():
            result.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': round(row['Open'], 2),
                'high': round(row['High'], 2),
                'low': round(row['Low'], 2),
                'close': round(row['Close'], 2)
            })
        return jsonify({'symbol': symbol, 'data': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
