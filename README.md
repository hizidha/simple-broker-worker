# simple-broker-worker

Tugas 1 – Socket untuk *Cluster Computing*
Mata Kuliah **Komputasi Berbasis Jaringan** – S2 Informatika UNESA

Simulasi *load balancing* sederhana dengan socket TCP di Python:
**client** mengirim request ke **broker**, broker meneruskannya ke salah satu dari **3 worker**, lalu balasan worker dikembalikan ke client.

```
                        +--> Worker 1 (port 9001)
Client --> Broker (9000) --> Worker 2 (port 9002)
                        +--> Worker 3 (port 9003)
```

---

## 1. Isi Repositori

| File | Fungsi |
|---|---|
| `worker.py` | Server pekerja: menjalankan aplikasi LONG atau SHORT |
| `broker.py` | Server utama: memilih worker dan meneruskan request (*forwarding*) |
| `client.py` | Mengirim satu request ke broker dengan menyebutkan Application ID |
| `run.py` | Menjalankan 3 worker + broker + beberapa client sekaligus |
| `evidence/` | Log hasil percobaan |

---

## 2. Kesesuaian dengan Soal

| Poin soal | Implementasi |
|---|---|
| Broker menerima request client dan mendistribusikannya ke 3 worker | `broker.py`, kelas `BrokerHandler` |
| Alokasi 1: pemerataan jumlah request yang **sudah dilayani** | `--strategi least` → pilih worker dengan `terlayani` paling sedikit |
| Alokasi 2: berurutan sesuai **server-id** berdasarkan **counter broker** | `--strategi rr` → `URUTAN[counter % 3]` |
| Worker punya 2 aplikasi: Long dan Short | `worker.py`: app `1` = hitung bilangan prima, app `2` = echo huruf besar |
| Client menyebutkan Application ID, protokol didefinisikan | Lihat bagian 3 (Protokol) |
| Broker dan worker mencetak informasi ke layar | Baris log `[Broker] ...` dan `[Worker n] ...` |

## 3. Protokol Pesan

Semua pesan berupa **satu baris teks yang diakhiri `\n`** (*newline*). Tanda `\n` menjadi penanda akhir pesan, karena TCP adalah aliran byte dan tidak punya batas pesan sendiri.

**Request** (client → broker → worker):

```
REQ <app_id> <data>
```

| `app_id` | Nama | `data` | Hasil |
|---|---|---|---|
| `1` | LONG (perhitungan kompleks) | bilangan bulat `n` | banyaknya bilangan prima ≤ n |
| `2` | SHORT (echo) | teks bebas | teks yang sama dalam huruf besar |

**Balasan** (worker → broker → client):

```
OK <worker_id> <hasil>      jika berhasil
ERR <alasan>                jika gagal
```

Contoh:

| Request | Balasan |
|---|---|
| `REQ 1 50000` | `OK 1 5133` |
| `REQ 2 halo` | `OK 2 HALO` |
| `REQ 7 salah` | `ERR app_id atau data tidak valid` |
| worker mati | `ERR worker 3 tidak merespons` |

## 4. Konsep dari Materi yang Dipakai

| Konsep di slide | Dipakai di |
|---|---|
| Echo server/client: `bind`, `listen`, `accept`, `sendall`, `SO_REUSEADDR` | `socketserver.TCPServer` (worker, broker), `client.py` |
| `argparse` untuk argumen program | Ketiga file |
| *Non-blocking server* thread-based: `socketserver.ThreadingMixIn` | Kelas `ThreadedServer` di `worker.py` dan `broker.py` |
| *Forwarding*: menerima koneksi lalu meneruskannya ke server lain | `BrokerHandler` di `broker.py` |

---

## 5. Cara Menjalankan

### a. Sekaligus (satu komputer)

```
python run.py rr
python run.py least
```

`run.py` mengirim 7 request satu per satu (termasuk 1 request salah untuk menguji `ERR`), lalu 5 request bersamaan (1 berat + 4 ringan) agar perbedaan kedua strategi terlihat.

### b. Manual (5 terminal)

```
python worker.py --id 1 --port 9001
python worker.py --id 2 --port 9002
python worker.py --id 3 --port 9003
python broker.py --strategi rr          (atau --strategi least)
python client.py --app 1 --data 50000
python client.py --app 2 --data halo
```

### c. Di beberapa komputer (cluster sungguhan)

Misalnya worker 2 berjalan di laptop lain dengan IP `192.168.1.11`:

```
# di laptop lain
python worker.py --id 2 --port 9002

# di laptop broker
python broker.py --strategi rr --worker 1=localhost:9001 2=192.168.1.11:9002 3=localhost:9003

# client (bisa dari laptop mana saja di jaringan yang sama)
python client.py --host <IP-laptop-broker> --app 2 --data halo
```

Izinkan Python di Windows Firewall jika muncul peringatan.

---

## 6. Bukti Percobaan

Log hasil `run.py` disimpan di folder `evidence/`:
- `evidence/hasil-rr.txt`
- `evidence/hasil-least.txt`
