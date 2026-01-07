import pika, json, time

print("Waiting for RabbitMQ to start...")
time.sleep(15)

connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='ride_finished_queue')

def callback(ch, method, properties, body):
    data = json.loads(body)
    print(f" [x] Received Ride ID: {data['ride_id']}")
    print(f" ... Calculating stats for User {data['user_id']} ...")
    # Тут була б складна математика
    print(f" [x] Analytics processed ride: {json.loads(body)}")

channel.basic_consume(queue='ride_finished_queue', on_message_callback=callback, auto_ack=True)
print(' [*] Analytics waiting for messages...')
channel.start_consuming()