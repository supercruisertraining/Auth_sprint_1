import socket
import time

from core.config import config

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        s.connect((config.DB_HOST, config.DB_PORT))
        s.close()
        break
    except socket.error as ex:
        time.sleep(1)
