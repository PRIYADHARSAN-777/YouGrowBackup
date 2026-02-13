import socket

class PersonalAIAgent:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_to_lmStudio()

    def connect_to_lmStudio(self):
        try:
            self.socket.connect((self.host, self.port))
            print(f'Connected to LM Studio at {self.host}:{self.port}')
        except Exception as e:
            print(f'Failed to connect to LM Studio: {e}')

    def send_message(self, message):
        try:
            self.socket.sendall(message.encode('utf-8'))
            print('Message sent to LM Studio.')
        except Exception as e:
            print(f'Failed to send message: {e}')

    def close_connection(self):
        self.socket.close()
        print('Connection to LM Studio closed.')

if __name__ == '__main__':
    agent = PersonalAIAgent()