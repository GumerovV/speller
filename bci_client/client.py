import socket
import threading

class BCIClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.eeg = []
        self.running = False  # Флаг для управления потоком

    def connect(self):
        """Подключение к серверу ЭЭГ"""
        self.socket.connect((self.host, self.port))

    def start_listening(self):
        """Начало прослушивания данных ЭЭГ в фоновом потоке"""
        self.running = True  # Устанавливаем флаг, чтобы начать слушать
        listening_thread = threading.Thread(target=self.listen_for_eeg)
        listening_thread.daemon = True  # Установим поток как демон, чтобы он завершился при выходе программы
        listening_thread.start()

    def listen_for_eeg(self):
        """Метод для получения данных ЭЭГ"""
        while self.running:
            try:
                data = self.socket.recv(1024).decode('utf-8')  # Получаем данные от сервера
                if not data:
                    break  # Если нет данных, выходим из цикла
                self.eeg.append(data)
                # print(self.eeg)
            except Exception:
                break  # В случае ошибки выходим из цикла

    def get_current_eeg(self):
        """Получение данных ЭЭГ"""
        current_eeg = self.eeg
        self.eeg = []  # Очистка после получения данных
        return current_eeg

    def stop_listening(self):
        """Остановка прослушивания данных ЭЭГ"""
        self.running = False  # Завершаем цикл в потоке
        self.socket.close()  # Закрываем сокет, чтобы завершить соединение
