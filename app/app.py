from flask import Flask, request, jsonify
import os
import socket

app = Flask(__name__)

@app.route('/')
def index():
    hostname = socket.gethostname()
    return f'''
    <!DOCTYPE html>
    <html>
    <head><title>Todo App no K8s</title></head>
    <body style="font-family: Arial; max-width: 600px; margin: 50px auto;">
        <h1>✅ Todo App Rodando!</h1>
        <p>Pod: {hostname}</p>
        <p>Namespace: {os.getenv('NAMESPACE', 'todo-app')}</p>
        <p>Versão da imagem: {os.getenv('VERSION', 'latest')}</p>
        <hr>
        <h2>Testar API:</h2>
        <ul>
            <li><a href="/health">Health Check</a></li>
            <li><a href="/todos">Ver todos (exemplo)</a></li>
        </ul>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    return {'status': 'healthy', 'pod': socket.gethostname()}

@app.route('/todos')
def todos_exemplo():
    return [
        {'id': '1', 'title': 'Exemplo: Estudar Kubernetes', 'completed': False},
        {'id': '2', 'title': 'Exemplo: Aprender ArgoCD', 'completed': False}
    ]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
