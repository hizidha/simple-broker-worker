# worker.py
# Server pekerja (worker) di dalam cluster.
# Tugasnya: menerima request dari broker, mengerjakan aplikasi LONG atau SHORT,
# lalu mengirim balasan ke broker.
#
# Contoh menjalankan:  python worker.py --id 1 --port 9001

import argparse
import socketserver

LONG = "1"    # Application ID 1: perhitungan kompleks
SHORT = "2"   # Application ID 2: echo (perhitungan sederhana)


def hitung_prima(n):
    # Aplikasi LONG: menghitung banyaknya bilangan prima dari 2 sampai n.
    # Sengaja dibuat lambat (dicek satu per satu) agar terasa sebagai pekerjaan berat.
    return sum(all(i % d for d in range(2, int(i ** 0.5) + 1)) for i in range(2, n + 1))


class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    # Server non-blocking berbasis thread (resep slide 20: socketserver.ThreadingMixIn).
    # Setiap koneksi yang masuk dilayani oleh thread baru.
    allow_reuse_address = True   # sama dengan SO_REUSEADDR pada contoh echo server
    daemon_threads = True        # thread ikut berhenti saat server dihentikan


class WorkerHandler(socketserver.StreamRequestHandler):
    # handle() dipanggil sekali untuk setiap koneksi dari broker.
    def handle(self):
        wid = self.server.worker_id                       # nomor worker ini
        pesan = self.rfile.readline().decode().strip()    # baca satu baris: "REQ <app_id> <data>"
        bagian = pesan.split(" ", 2)                      # pecah menjadi ["REQ", app_id, data]

        if len(bagian) != 3 or bagian[0] != "REQ":        # format pesan salah
            balasan = "ERR format pesan salah"
        elif bagian[1] == LONG and bagian[2].isdigit():   # LONG: data harus angka
            balasan = f"OK {wid} {hitung_prima(int(bagian[2]))}"
        elif bagian[1] == SHORT:                          # SHORT: kembalikan data dalam huruf besar
            balasan = f"OK {wid} {bagian[2].upper()}"
        else:                                             # Application ID tidak dikenal / data salah
            balasan = "ERR app_id atau data tidak valid"

        print(f"[Worker {wid}] terima '{pesan}' -> balas '{balasan}'")
        self.wfile.write((balasan + "\n").encode())       # kirim balasan, diakhiri \n


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Worker pada cluster")
    parser.add_argument("--id", type=int, required=True, help="nomor worker (server-id)")
    parser.add_argument("--host", default="0.0.0.0", help="0.0.0.0 = bisa diakses dari komputer lain")
    parser.add_argument("--port", type=int, required=True, help="port worker")
    args = parser.parse_args()

    server = ThreadedServer((args.host, args.port), WorkerHandler)  # bind + listen
    server.worker_id = args.id                                       # simpan nomor worker
    print(f"[Worker {args.id}] siap di {args.host}:{args.port}")
    server.serve_forever()                                           # loop accept() selamanya
