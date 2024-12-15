import json
import _thread
import network
import time
import socket


class Beacon:

    def __init__(self):
        self.CLIENTS = []
        PORT = 1337

        with open('pymakr.conf') as likeENV:
            env = json.load(likeENV)

        wlan = network.WLAN(network.AP_IF)
        wlan.active(True) 
        wlan.config(essid=env['ap_ssid'], password=env['ap_password'])
        print(f"WiFi сеть '{env['ap_ssid']}' создана с паролем '{env['ap_password']}'")
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Используем UDP
        self.server_socket.bind(('0.0.0.0', PORT))
        print(f"Server listening on 0.0.0.0:{PORT}")


    def loop(self):
        while True:
            data, addr = self.server_socket.recvfrom(1024)
            print(f"Read from {addr}: {data.decode('utf-8')}")
            self.CLIENTS.append(addr)

    def broadcast(self, left_level, right_level):
        if self.server_socket:
            message = f"{left_level},{right_level}" + '\n' 
            for client in self.CLIENTS:
                try:
                    self.server_socket.sendto(message.encode('utf-8'), client)
                except OSError as e:
                    self.CLIENTS.remove(client)

