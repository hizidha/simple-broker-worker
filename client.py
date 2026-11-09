# client.py
# Mengirim satu request ke broker dengan menyebutkan Application ID, lalu menampilkan balasannya.
#
# Contoh menjalankan:
#   python client.py --app 1 --data 50000      (LONG: hitung prima <= 50000)
#   python client.py --app 2 --data halo       (SHORT: echo)

import argparse
import socket

parser = argparse.ArgumentParser(description="Client pengirim request")
parser.add_argument("--host", default="localhost", help="alamat broker")
parser.add_argument("--port", type=int, default=9000, help="port broker")
parser.add_argument("--app", type=int, required=True, help="Application ID: 1 = LONG, 2 = SHORT")
parser.add_argument("--data", required=True, help="LONG: angka n, SHORT: teks")
args = parser.parse_args()

request = f"REQ {args.app} {args.data}"                         # susun pesan sesuai protokol

with socket.create_connection((args.host, args.port)) as s:     # sambung ke broker
    s.sendall((request + "\n").encode())                        # kirim seluruh pesan, diakhiri \n
    balasan = s.makefile().readline().strip()                   # tunggu satu baris balasan

print(f"[Client] kirim '{request}' -> balasan '{balasan}'")
