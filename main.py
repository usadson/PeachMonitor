import collections
import itertools
import json
import platform
import psutil
import socket
import sys
import time

SERVER_SOCKET = ("127.0.0.1", 1312)
TIMEOUT = 0.5

isWindows = platform.system() == "Windows"

if len(sys.argv) == 1:
    print("Wachtwoord Vereist")
if len(sys.argv) == 2:
    print("Identifier Vereist")
s = None

def connect():
    global s
    print("Verbinden met " + SERVER_SOCKET[0] + " op poort " + str(SERVER_SOCKET[1]))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect(SERVER_SOCKET)

    s.sendall(bytes("IDENTIFY {identifier}\n".format(identifier = sys.argv[2]), "utf-8"))
    s.sendall(bytes("LOGIN {password}\n".format(password = sys.argv[1]), "utf-8"))
    l = read_line(s)
    print(l)
    if l != "ACCESS GRANTED":
        quit()

def read_line(sock):
    chars = []
    while True:
        a = str(sock.recv(1), 'UTF-8')
        if a == '\n' or a == "":
            return "".join(chars)
        chars.append(a)     

# Warm up psutil
psutil.cpu_percent()

def count_iter_items(iterable):
    counter = itertools.count()
    collections.deque(zip(iterable, counter), maxlen=0)
    return next(counter)

def count_windows_services():
    if not psutil.WINDOWS:
        return 0
    return count_iter_items(psutil.win_service_iter())

def send_data():
    global s
    while True:
#    line = read_line(s)
#    print(line)
#    if line == '':
#        break
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("C:\\" if isWindows else "/")
        io = psutil.net_io_counters()

        #heartbeat = str(psutil.cpu_percent() / 100) + " " + str(mem['used'] / mem[
        heartbeat = {
            "cpu": {
                "percent": int(psutil.cpu_percent() * 10),
                "processes": len(psutil.pids()),
                "windows-services": count_windows_services(),
            },
            "memory": {
                "used": mem.used,
                "total": mem.total,
            },
            "disk": {
                "used": disk.used,
                "total": disk.total,
            },
            "io": {
                "bytes-sent": io.bytes_sent,
                "bytes-received": io.bytes_recv,
            },
        }
        s.send(bytes("HEARTBEAT " + json.dumps(heartbeat) + "\n", 'UTF-8'))

        time.sleep(TIMEOUT)


while True:
    try:
        connect()
        print("Verbonden. Ik zal nu elke " + str(TIMEOUT) + " seconden HEARTBEATs sturen")
        send_data()
    except KeyboardInterrupt:
        break
    except BrokenPipeError:
        print("Verbinding verloren.")
        continue
    except ConnectionRefusedError:
        print("Geen verbinding mogelijk. Ik probeer het over 1 seconde opnieuw...")
        time.sleep(1)
