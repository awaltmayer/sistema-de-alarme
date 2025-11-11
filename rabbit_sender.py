import serial
import pika
import requests
import time
from datetime import datetime
import pytz

# ==========================================
# 🔧 CONFIGURAÇÕES
# ==========================================

# Porta serial do Arduino (ajuste conforme necessário)
SERIAL_PORT = '/dev/ttyACM0'  # ou '/dev/ttyUSB0'
BAUD_RATE = 9600

# Configuração RabbitMQ
RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'alarme'

# Configuração do Telegram
TOKEN = '8542390575:AAGDZBJkMlG_3GrHknln536TiCNteWTbEfA'
CHAT_ID = '6791074263'

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
    print("❌ Erro ao conectar na porta serial. Verifique o cabo e a porta.")
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
                horario = datetime.now(TZ).strftime("%d/%m/%Y %H:%M:%S")
                mensagem = f"🚨 ALERTA ({horario}): {msg}"

                # Envia ao RabbitMQ
                channel.basic_publish(
                    exchange='',
                    routing_key=QUEUE_NAME,
                    body=mensagem
                )
                print(f"📩 Enviado ao RabbitMQ: {mensagem}")

                # Envia mensagem ao Telegram
                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                payload = {"chat_id": CHAT_ID, "text": mensagem}

                try:
                    response = requests.post(url, data=payload)
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