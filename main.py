import json
import platform
import psutil
import socket
import sys
import time

isWindows = platform.system() == "Windows"

if len(sys.argv) == 1:
    print("Wachtwoord Vereist")
if len(sys.argv) == 2:
    print("Identifier Vereist")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(("127.0.0.1", 1312))

s.sendall(bytes("IDENTIFY {identifier}\n".format(identifier = sys.argv[2]), "utf-8"))
s.sendall(bytes("LOGIN {password}\n".format(password = sys.argv[1]), "utf-8"))

def read_line(sock):
    chars = []
    while True:
        a = str(sock.recv(1), 'UTF-8')
        if a == '\n' or a == "":
            return "".join(chars)
        chars.append(a)     

# Warm up psutil
psutil.cpu_percent()


while True:
#    line = read_line(s)
#    print(line)
#    if line == '':
#        break
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("C:\\" if isWindows else "/")

    #heartbeat = str(psutil.cpu_percent() / 100) + " " + str(mem['used'] / mem[
    heartbeat = {
        "cpu": {
            "percent": int(psutil.cpu_percent() * 10)
        },
        "memory": {
            "used": mem.used,
            "total": mem.total
        },
        "disk": {
            "used": disk.used,
            "total": disk.total
        }
    }
    s.send(bytes("HEARTBEAT " + json.dumps(heartbeat) + "\n", 'UTF-8'))

    time.sleep(0.5)


