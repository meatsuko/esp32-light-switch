import _thread
import machine
import time

class Analyzer:
    ADC_LEFT = None
    ADC_RIGHT = None
    LOW_PASS = 200
    ADC_ATTN = None
    left_level = 0
    right_level = 0
    silent = True
    
    def __init__(self, PIN_LEFT, PIN_RIGHT, lp=0, ATTN=machine.ADC.ATTN_11DB, WDTH=machine.ADC.WIDTH_12BIT):
        self.ADC_LEFT = machine.ADC(machine.Pin(PIN_LEFT, mode=machine.Pin.IN, pull=machine.Pin.PULL_DOWN)) # похоже что pull_up pull_down не работают
        self.ADC_RIGHT = machine.ADC(machine.Pin(PIN_RIGHT, mode=machine.Pin.IN, pull=machine.Pin.PULL_DOWN)) # похоже что pull_up pull_down не работают
        self.attn(ATTN)
        self.width(WDTH)
        self.LOW_PASS = lp  # Устанавливаем LOW_PASS
        self.SILENT_COUNTER = 0

        self.left_level = 0
        self.right_level = 0
        
    def attn(self, ATTN):
        self.ADC_LEFT.atten(ATTN)
        self.ADC_RIGHT.atten(ATTN)
    
    def width(self, WDTH=machine.ADC.WIDTH_12BIT):
        self.ADC_LEFT.width(WDTH)
        self.ADC_RIGHT.width(WDTH)
        
    def loop(self, ticks=80):
        while True:
            max_left_level = 0
            max_right_level = 0

            for _ in range(ticks):  # Считываем уровни звука ticks раз
                loop_left_level = self.ADC_LEFT.read()
                loop_right_level = self.ADC_RIGHT.read()

                if max_left_level < loop_left_level: 
                    max_left_level = loop_left_level
                if max_right_level < loop_right_level: 
                    max_right_level = loop_right_level
            
            # temp for 11db attenuation
            max_left_level = self.__map(max_left_level, self.LOW_PASS, 2720, 0, 4095)
            max_right_level = self.__map(max_right_level, self.LOW_PASS, 2720, 0, 4095)

            self.left_level = max_left_level
            self.right_level = max_right_level

            self.__silentCompute()

    
    def __silentCompute(self):
        if self.left_level < 20 and self.right_level < 20:
            if self.SILENT_COUNTER < 20:
                self.SILENT_COUNTER += 1
            else:
                self.silent = True
        else:
            if self.SILENT_COUNTER > 1:
                self.SILENT_COUNTER = self.SILENT_COUNTER -1
            else:
                self.silent = False
    
        
    def __map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


import network
import socket

class ReAnalyzer(Analyzer):
    def __init__(self ):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.SSID = 'LightSwitch24'  # имя вашей сети
        self.PASSWORD = 'NIO1TRAUTo'  # пароль от сети

        self.__wlan_connect()
        self.__sock_hello()
        _thread.start_new_thread(self.__watchdog, ())

        self.left_level = 0
        self.right_level = 0
        
        self.silent = False
        self.SILENT_COUNTER = 0
        


    def __watchdog(self):
        while True:
            time.sleep(5)
            if not self.wlan.isconnected():
                print("wlan connection lost, reconnecting...")
                self.__wlan_connect()
                self.__sock_hello()
            
            if time.time() - self.sock_time > 5:
                print("socket connection lost, reconnecting...")
                self.__sock_hello()

    def __wlan_connect(self):
        self.wlan.connect(self.SSID)
        print("Подключаемся к сети...")
        while not self.wlan.isconnected():
            print(".")
            time.sleep(1)  # ждем подключения

        print("Подключено к сети!")
        print("IP адрес устройства:", self.wlan.ifconfig()[0])  # выводим IP адрес

    def __sock_hello(self):
        SERVER_IP = "192.168.4.1"  # IP сервера, к которому подключаемся
        SERVER_PORT = 1337          # Порт сервера
        self.sock.sendto("0x00", (SERVER_IP, SERVER_PORT))

    def loop(self, ticks=80):
        while True:
            data, addr = self.sock.recvfrom(1024)  # Максимальный размер буфера - 1024 байта
            message = data.decode('utf-8')
            left_level, right_level = message.strip().split(',')  # Убираем пробелы и разделяем по запятой
            
            left_level = float(left_level)  # Преобразуем в float
            right_level = float(right_level)  #
            
            self.left_level = left_level
            self.right_level = right_level
            

            self.__silentCompute()
            self.sock_time = time.time()

