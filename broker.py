# broker.py
# Server utama (broker).
# Tugasnya: menerima request dari client, memilih salah satu worker,
# meneruskan (forward) request ke worker itu, lalu mengembalikan balasannya ke client.
#
# Contoh menjalankan:
#   python broker.py --strategi rr
#   python broker.py --strategi least --worker 1=192.168.1.10:9001 2=192.168.1.11:9002 3=localhost:9003

import argparse
import socket
import socketserver
import threading


class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    # Server non-blocking berbasis thread: setiap client dilayani thread sendiri.
    allow_reuse_address = True   # sama dengan SO_REUSEADDR
    daemon_threads = True        # thread ikut berhenti saat server dihentikan


def pilih_worker():
    # Memilih worker sesuai strategi. Memakai lock karena banyak thread mengakses data yang sama.
    global counter
    with kunci:
        if STRATEGI == "rr":
            # Strategi 2: berurutan sesuai server-id berdasarkan counter milik broker.
            wid = URUTAN[counter % len(URUTAN)]
            counter += 1
        else:
            # Strategi 1: pemerataan jumlah request yang SUDAH DILAYANI tiap worker.
            # Pilih yang paling sedikit; jika sama, pilih server-id terkecil.
            wid = min(URUTAN, key=lambda w: (terlayani[w], w))
    return wid


class BrokerHandler(socketserver.StreamRequestHandler):
    # handle() dipanggil sekali untuk setiap koneksi dari client.
    def handle(self):
        pesan = self.rfile.readline().decode().strip()    # baca request client: "REQ <app_id> <data>"
        wid = pilih_worker()                              # tentukan worker tujuan
        host, port = WORKERS[wid]
        print(f"[Broker] terima '{pesan}' -> teruskan ke worker {wid} ({host}:{port})")

        try:
            with socket.create_connection((host, port), timeout=60) as w:  # sambung ke worker
                w.sendall((pesan + "\n").encode())                         # teruskan request
                balasan = w.makefile().readline().strip()                  # tunggu satu baris balasan
            with kunci:
                terlayani[wid] += 1          # dihitung hanya jika worker benar-benar membalas
        except OSError:
            balasan = f"ERR worker {wid} tidak merespons"

        print(f"[Broker] balasan '{balasan}' | terlayani: {terlayani}")
        self.wfile.write((balasan + "\n").encode())       # kembalikan balasan ke client


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Broker pada cluster")
    parser.add_argument("--host", default="0.0.0.0", help="0.0.0.0 = bisa diakses dari komputer lain")
    parser.add_argument("--port", type=int, default=9000, help="port broker")
    parser.add_argument("--strategi", choices=["rr", "least"], default="rr", help="strategi alokasi")
    parser.add_argument("--worker", nargs="+", metavar="ID=HOST:PORT",
                        default=["1=localhost:9001", "2=localhost:9002", "3=localhost:9003"],
                        help="daftar alamat worker")
    args = parser.parse_args()

    WORKERS = {}                                     # server-id -> (host, port)
    for item in args.worker:                         # contoh item: "1=localhost:9001"
        wid, alamat = item.split("=")
        host, port = alamat.split(":")
        WORKERS[int(wid)] = (host, int(port))

    STRATEGI = args.strategi
    URUTAN = sorted(WORKERS)                         # urutan server-id: [1, 2, 3]
    terlayani = {w: 0 for w in URUTAN}               # jumlah request yang sudah dilayani tiap worker
    counter = 0                                      # counter milik broker (strategi rr)
    kunci = threading.Lock()                         # pengaman data bersama antar-thread

    server = ThreadedServer((args.host, args.port), BrokerHandler)  # bind + listen
    print(f"[Broker] siap di {args.host}:{args.port} | strategi={STRATEGI} | worker={WORKERS}")
    server.serve_forever()                                           # loop accept() selamanya
