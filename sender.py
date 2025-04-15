import pika
import sys
import os



def send_message(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='hello')
    channel.basic_publish(exchange='', routing_key='hello', body=message)
    print(f"Sent {message}")
    connection.close()

def main():
    user_input = input("Send a message: ")
    send_message(user_input)

if __name__ == '__main__':
    try:
        while True:
            main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)