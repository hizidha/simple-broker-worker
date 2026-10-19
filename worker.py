import socket, sys, threading

wid, port = int(sys.argv[1]), int(sys.argv[2])

def layani(conn):
    # format request: "<app_id> <isi>"  (1 = LONG, 2 = SHORT)
    app, isi = conn.recv(1024).decode().split(" ", 1)
    if app == "1":      # LONG: hitung jumlah bilangan prima <= n
        n = int(isi)
        hasil = sum(all(i % d for d in range(2, int(i ** 0.5) + 1)) for i in range(2, n + 1))
    else:               # SHORT: echo
        hasil = isi.upper()
    print(f"[Worker {wid}] app={app} isi={isi} -> {hasil}")
    conn.send(f"{wid} {hasil}".encode())
    conn.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("localhost", port))
s.listen(5)
print(f"[Worker {wid}] siap di port {port}")
while True:
    conn, _ = s.accept()
    threading.Thread(target=layani, args=(conn,)).start()
