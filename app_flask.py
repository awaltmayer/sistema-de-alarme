from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import sqlite3
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# --- Função para inicializar o banco de dados ---
def init_db():
    conn = sqlite3.connect('alertas.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS alertas
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  mensagem TEXT,
                  data TEXT,
                  hora TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- Página principal ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Rota para receber e emitir alertas ---
@app.route('/alerta', methods=['POST'])
def alerta():
    data = request.get_json()
    mensagem = data.get('mensagem', '🚨 Alerta recebido!')

    # Data e hora atuais
    agora = datetime.now()
    data_str = agora.strftime("%Y-%m-%d")
    hora_str = agora.strftime("%H:%M:%S")

    # Salva no banco
    conn = sqlite3.connect('alertas.db')
    c = conn.cursor()
    c.execute("INSERT INTO alertas (mensagem, data, hora) VALUES (?, ?, ?)",
              (mensagem, data_str, hora_str))
    conn.commit()
    conn.close()

    # Emite via Socket.IO
    socketio.emit('alerta', {'mensagem': mensagem, 'data': data_str, 'hora': hora_str})

    return jsonify({'status': 'ok', 'mensagem': mensagem})

# --- Rota para buscar histórico ---
@app.route('/historico')
def historico():
    conn = sqlite3.connect('alertas.db')
    c = conn.cursor()
    c.execute("SELECT mensagem, data, hora FROM alertas ORDER BY id DESC")
    dados = [{'mensagem': m, 'data': d, 'hora': h} for (m, d, h) in c.fetchall()]
    conn.close()
    return jsonify(dados)

# --- Rota para limpar histórico ---
@app.route('/limpar', methods=['POST'])
def limpar():
    conn = sqlite3.connect('alertas.db')
    c = conn.cursor()
    c.execute("DELETE FROM alertas")
    conn.commit()
    conn.close()
    return jsonify({'mensagem': '✅ Histórico apagado com sucesso!'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
