# run.py - jalankan semuanya sekaligus (3 worker + broker + beberapa request).
# Pemakaian: python run.py [rr|least]
import subprocess, sys, time

strategi = sys.argv[1] if len(sys.argv) > 1 else "rr"
py = sys.executable
servers = [subprocess.Popen([py, "worker.py", str(i), str(9000 + i)]) for i in (1, 2, 3)]
servers.append(subprocess.Popen([py, "broker.py", strategi]))
time.sleep(1)

for app, isi in [("1", "50000"), ("2", "halo"), ("1", "30000"),
                 ("2", "jaringan"), ("1", "20000"), ("2", "komputasi")]:
    subprocess.run([py, "client.py", app, isi])

# Tahap 2: request bersamaan (1 beban berat + 4 ringan) agar beda rr vs least terlihat
print("--- request bersamaan ---", flush=True)
jobs = [("1", "300000")] + [("2", f"ringan{i}") for i in range(4)]
procs = []
for app, isi in jobs:
    procs.append(subprocess.Popen([py, "client.py", app, isi]))
    time.sleep(0.1)
for p in procs:
    p.wait()

time.sleep(0.5)
for p in servers:
    p.terminate()
