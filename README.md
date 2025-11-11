Sistema de Detecção de Movimento com Sensor Ultrassônico, Alarme, RabbitMQ, Flask, Telegram e Banco SQL
Este projeto usa uma Raspberry Pi 4 para monitorar movimento utilizando um sensor ultrassônico. Quando algo é detectado a uma distância menor que o limite definido, a Raspberry envia um sinal para um Arduino, que aciona um buzzer como alarme sonoro. Além disso, a Raspberry registra a ocorrência no banco de dados e envia alertas para outros serviços.

Como tudo funciona:
- Raspberry Pi 4 + Sensor Ultrassônico

- A Raspberry mede continuamente a distância usando o sensor ultrassônico.
Se algo se aproxima além do limite configurado:

- a Raspberry aciona o Arduino para disparar o buzzer,

- a detecção é registrada com data e hora,

- e o evento é enviado para o sistema usando RabbitMQ.

RabbitMQ

A Raspberry publica uma mensagem na fila do RabbitMQ sempre que acontece uma detecção.
Isso garante que o alerta chegue ao backend mesmo que exista atraso ou processamento paralelo.

Backend em Flask

- O Flask fica ouvindo a fila. Quando chega um alerta:

- grava o registro no banco SQL (incluindo data e hora),

- atualiza a interface web com o novo evento.

Banco SQL

Cada detecção salva contém:

- data

- hora

Isso cria um histórico simples e consultável.

Alertas no Telegram

Além da interface web, o sistema também envia uma notificação para um bot do Telegram sempre que ocorre um novo movimento. Assim dá para acompanhar tudo mesmo à distância.

Recursos principais:

- Sensor ultrassônico para detecção de presença

- Registro em SQL com data/hora

- Alarme sonoro acionado por Arduino usando buzzer

- Comunicação via RabbitMQ

- Interface web com Flask

- Notificações via Telegram
