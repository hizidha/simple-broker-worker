# run.py
# Menjalankan semuanya sekaligus di satu komputer: 3 worker + broker + beberapa client.
# Contoh menjalankan:  python run.py rr   atau   python run.py least

import subprocess
import sys
import time

strategi = sys.argv[1] if len(sys.argv) > 1 else "rr"
py = sys.executable                                   # interpreter Python yang sedang dipakai

# Nyalakan 3 worker dan 1 broker. Host 127.0.0.1 agar tidak memicu peringatan firewall.
servers = [subprocess.Popen([py, "worker.py", "--id", str(i), "--host", "127.0.0.1", "--port", str(9000 + i)])
           for i in (1, 2, 3)]
servers.append(subprocess.Popen([py, "broker.py", "--host", "127.0.0.1", "--strategi", strategi]))
time.sleep(1)                                         # beri waktu server untuk siap

# Tahap 1: request dikirim satu per satu.
for app, data in [("1", "50000"), ("2", "halo"), ("1", "30000"),
                  ("2", "jaringan"), ("1", "20000"), ("2", "komputasi"), ("7", "salah")]:
    subprocess.run([py, "client.py", "--app", app, "--data", data])

# Tahap 2: request dikirim bersamaan (1 berat + 4 ringan) agar beda rr dan least terlihat.
print("--- request bersamaan ---", flush=True)
jobs = [("1", "300000")] + [("2", f"ringan{i}") for i in range(4)]
procs = []
for app, data in jobs:
    procs.append(subprocess.Popen([py, "client.py", "--app", app, "--data", data]))
    time.sleep(0.1)
for p in procs:
    p.wait()                                          # tunggu semua client selesai

time.sleep(0.5)
for p in servers:
    p.terminate()                                     # matikan worker dan broker
