from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import pika, threading, sqlite3, json

app = Flask(__name__)
socketio = SocketIO(app)

# Banco SQLite
conn = sqlite3.connect('alertas.db', check_same_thread=False)
c = conn.cursor()
# Tabela atualizada para incluir a coluna 'timestamp'
c.execute('CREATE TABLE IF NOT EXISTS alertas (id INTEGER PRIMARY KEY, mensagem TEXT, timestamp TEXT)')
conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/historico')
def historico():
    # Retorna a mensagem e o timestamp
    c.execute('SELECT mensagem, timestamp FROM alertas ORDER BY id DESC LIMIT 20')
    alertas = [{'mensagem': row[0], 'timestamp': row[1]} for row in c.fetchall()]
    return jsonify(alertas)

def consume():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='alarme')

    def callback(ch, method, properties, body):
        try:
            # Decodifica o payload JSON
            payload = json.loads(body.decode())
            msg = payload.get('mensagem', 'Alerta sem mensagem')
            timestamp = payload.get('timestamp', 'Sem Data')
            
            print(f"🔔 Recebido: {msg} em {timestamp}")
            
            # Salva no SQLite
            c.execute("INSERT INTO alertas (mensagem, timestamp) VALUES (?, ?)", (msg, timestamp))
            conn.commit()
            
            # Emite via SocketIO
            socketio.emit('alerta', {'mensagem': msg, 'timestamp': timestamp})
            
        except json.JSONDecodeError:
            print(f"⚠️ Erro ao decodificar JSON do RabbitMQ: {body.decode()}")
            # Trata como mensagem simples se não for JSON
            msg = body.decode()
            c.execute("INSERT INTO alertas (mensagem, timestamp) VALUES (?, ?)", (msg, 'Sem Data'))
            conn.commit()
            socketio.emit('alerta', {'mensagem': msg, 'timestamp': 'Sem Data'})

    channel.basic_consume(queue='alarme', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

# Thread separada para o consumidor
threading.Thread(target=consume, daemon=True).start()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
