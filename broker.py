import socket, sys, threading

strategi = sys.argv[1] if len(sys.argv) > 1 else "rr"
WORKERS = {1: 9001, 2: 9002, 3: 9003}      # server-id -> port
selesai = {1: 0, 2: 0, 3: 0}               # jumlah request yang sudah dilayani
berjalan = {1: 0, 2: 0, 3: 0}              # request yang sedang diproses tiap worker
counter = 0                                # counter broker (untuk rr)
lock = threading.Lock()

def pilih():
    global counter
    with lock:
        if strategi == "rr":               # berurutan sesuai server-id
            wid = counter % 3 + 1
            counter += 1
        else:                              # least: paling sedikit beban berjalan, lalu paling sedikit terlayani
            wid = min(WORKERS, key=lambda w: (berjalan[w], selesai[w], w))
        berjalan[wid] += 1
        return wid

def layani(client):
    data = client.recv(1024).decode()
    wid = pilih()
    print(f"[Broker] request '{data}' -> worker {wid}")
    try:
        w = socket.socket()
        w.connect(("localhost", WORKERS[wid]))
        w.send(data.encode())
        balasan = w.recv(1024).decode()
        w.close()
    except OSError:
        balasan = f"{wid} ERROR worker tidak merespons"
    with lock:
        berjalan[wid] -= 1
        selesai[wid] += 1
    print(f"[Broker] balasan '{balasan}' | terlayani: {selesai}")
    client.send(balasan.encode())
    client.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("localhost", 9000))
s.listen(5)
print(f"[Broker] siap di port 9000, strategi={strategi}")
while True:
    c, _ = s.accept()
    threading.Thread(target=layani, args=(c,)).start()
