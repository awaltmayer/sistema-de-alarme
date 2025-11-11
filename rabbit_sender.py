import serial
import os
import pika
import json
import requests
import time
from datetime import datetime
import pytz

# ==========================================
# 🔧 CONFIGURAÇÕES
# ==========================================

# Porta serial do Arduino (ajuste conforme necessário)
SERIAL_PORT = os.getenv('SERIAL_PORT', '/dev/ttyACM0')
BAUD_RATE = int(os.getenv('BAUD_RATE', 9600))

# Configuração RabbitMQ
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
QUEUE_NAME = 'alarme'

# Configuração do Telegram
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Fuso horário (Brasil)
TZ = pytz.timezone("America/Sao_Paulo")

# ==========================================
# ⚙️ INICIALIZAÇÃO DAS CONEXÕES
# ==========================================

# Conecta ao Arduino
try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"✅ Conectado ao Arduino em {SERIAL_PORT}")
except serial.SerialException:
    print(f"❌ Erro ao conectar na porta serial '{SERIAL_PORT}'. Verifique o cabo e a porta.")
    exit(1)

# Conecta ao RabbitMQ
try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)
    print(f"✅ Conectado ao RabbitMQ em '{RABBITMQ_HOST}'")
except Exception as e:
    print(f"❌ Erro ao conectar ao RabbitMQ: {e}")
    exit(1)

print("\n📡 Aguardando mensagens do Arduino...\n")

# ==========================================
# 🚨 LOOP PRINCIPAL
# ==========================================

while True:
    try:
        if arduino.in_waiting > 0:
            msg = arduino.readline().decode(errors="ignore").strip()

            # Verifica se contém palavra-chave de alerta
            if "ALERTA" in msg:
                # Data e hora local formatada
                # Timestamp em formato ISO para fácil parseamento no backend
                timestamp_iso = datetime.now(TZ).isoformat()
                horario_formatado = datetime.now(TZ).strftime("%d/%m/%Y %H:%M:%S")
                mensagem_telegram = f"🚨 ALERTA ({horario_formatado}): {msg}"
                
                # Objeto estruturado para o RabbitMQ
                payload = {
                    "mensagem": msg,
                    "timestamp": timestamp_iso,
                    "horario_formatado": horario_formatado
                }
                payload_json = json.dumps(payload)

                # Envia ao RabbitMQ
                channel.basic_publish(
                    exchange='',
                    routing_key=QUEUE_NAME,
                    body=payload_json
                )
                print(f"📩 Enviado ao RabbitMQ: {payload_json}")

                # Envia mensagem ao Telegram
                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                payload_telegram = {"chat_id": CHAT_ID, "text": mensagem_telegram}

                try:
                    response = requests.post(url, data=payload_telegram )
                    if response.status_code == 200:
                        print("📲 Mensagem enviada com sucesso no Telegram!")
                    else:
                        print(f"⚠️ Falha ao enviar no Telegram (status {response.status_code})")
                except requests.RequestException as e:
                    print(f"❌ Erro ao enviar para o Telegram: {e}")

            time.sleep(0.1)  # Evita sobrecarga do loop

    except KeyboardInterrupt:
        print("\n🛑 Execução interrompida pelo usuário.")
        break

    except Exception as e:
        print(f"⚠️ Erro inesperado: {e}")
        time.sleep(1)

# ==========================================
# 🔚 ENCERRAMENTO LIMPO
# ==========================================

arduino.close()
connection.close()
print("✅ Conexões encerradas com segurança.")
