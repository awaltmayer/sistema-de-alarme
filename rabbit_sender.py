import serial
import time
import sqlite3
import pika
import requests
from datetime import datetime

# ==============================
# ⚙️ CONFIGURAÇÕES
# ==============================
PORTA_SERIAL = "/dev/ttyACM0"   # ou /dev/ttyUSB0 dependendo da placa
BAUD_RATE = 9600
RABBITMQ_SERVER = "localhost"

# 🧩 Telegram (preencher manualmente)
TELEGRAM_TOKEN = "8542390575:AAGDZBJkMlG_3GrHknln536TiCNteWTbEfA"
CHAT_ID = "6791074263"

# ==============================
# 🔌 CONEXÕES
# ==============================
print("Conectando ao Arduino...")
arduino = serial.Serial(PORTA_SERIAL, BAUD_RATE)
time.sleep(2)
print("✅ Conectado ao Arduino!")

# Conexão com RabbitMQ
try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVER))
    channel = connection.channel()
    channel.queue_declare(queue='movimentos')  # deve ser o mesmo nome da fila no app_flask.py
    print("✅ Conectado ao RabbitMQ!")
except Exception as e:
    print(f"❌ Erro ao conectar ao RabbitMQ: {e}")
    exit()

# ==============================
# 🧠 FUNÇÕES
# ==============================
def salvar_alerta():
    """Salva o alerta no banco, envia ao RabbitMQ e Telegram."""
    data = datetime.now().strftime("%Y-%m-%d")
    hora = datetime.now().strftime("%H:%M:%S")
    msg = f"🚨 Movimento detectado!\n📅 {data}\n🕓 {hora}"

    # --- salvar no banco local ---
    try:
        conn = sqlite3.connect("alertas.db")
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS alertas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                hora TEXT NOT NULL
            )
        """)
        c.execute("INSERT INTO alertas (data, hora) VALUES (?, ?)", (data, hora))
        conn.commit()
        conn.close()
        print(f"💾 Alerta salvo no banco ({data} {hora})")
    except Exception as e:
        print(f"⚠ Erro ao salvar no banco: {e}")

    # --- envia mensagem pro RabbitMQ ---
    try:
        channel.basic_publish(exchange='', routing_key='movimentos', body=msg)
        print(f"📩 Enviado ao RabbitMQ: {msg}")
    except Exception as e:
        print(f"⚠ Erro ao enviar ao RabbitMQ: {e}")

    # --- envia mensagem ao Telegram ---
    enviar_telegram(msg)


def enviar_telegram(msg):
    """Envia notificação via Telegram."""
    url = f"https://api.telegram.org/bot8542390575:AAGDZBJkMlG_3GrHknln536TiCNteWTbEfA/sendMessage"
    data = {"chat_id": 6791074263, "text": msg}
    try:
        resposta = requests.post(url, data=data)
        if resposta.status_code == 200:
            print("✅ Mensagem enviada ao Telegram!")
        else:
            print(f"⚠ Erro Telegram: {resposta.text}")
    except Exception as e:
        print(f"⚠ Erro ao enviar Telegram: {e}")

# ==============================
# 🕵️ LOOP PRINCIPAL
# ==============================
print("🕵️ Monitorando sensor...")
while True:
    try:
        if arduino.in_waiting > 0:
            valor = arduino.readline().decode().strip()
            if valor == "1":
                salvar_alerta()
                time.sleep(5)  # evita spam de mensagens
    except KeyboardInterrupt:
        print("\n🛑 Encerrado pelo usuário.")
        break
    except Exception as e:
        print(f"⚠ Erro no loop: {e}")
        time.sleep(2)
