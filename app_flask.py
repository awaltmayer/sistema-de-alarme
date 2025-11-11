from flask import Flask, render_template
from flask_socketio import SocketIO
import pika, threading, sqlite3

app = Flask(__name__)
socketio = SocketIO(app)

# Banco SQLite
conn = sqlite3.connect('alertas.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS alertas (id INTEGER PRIMARY KEY, mensagem TEXT)')
conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

def consume():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='alarme')

    def callback(ch, method, properties, body):
        msg = body.decode()
        print("🔔 Recebido:", msg)
        c.execute("INSERT INTO alertas (mensagem) VALUES (?)", (msg,))
        conn.commit()
        socketio.emit('alerta', {'mensagem': msg})

    channel.basic_consume(queue='alarme', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

# Thread separada para o consumidor
threading.Thread(target=consume, daemon=True).start()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
