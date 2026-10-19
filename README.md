# simple-broker-worker
Tugas 1 - Mata Kuliah Komputasi Jaringan

Client mengirim request ke broker (port 9000), broker meneruskannya ke salah satu dari
3 worker (port 9001-9003), lalu balasan worker dikembalikan ke client.

## Format request
`<app_id> <isi>`
- `1` (LONG)  : worker menghitung jumlah bilangan prima <= n
- `2` (SHORT) : worker membalas `isi` dalam huruf besar

## Strategi broker
- `rr`    : round robin, berurutan worker 1, 2, 3, 1, ...
- `least` : pilih worker dengan request berjalan paling sedikit (seri -> paling sedikit terlayani)

## Menjalankan
Otomatis (3 worker + broker + client):
```
python run.py rr
python run.py least
```
Manual (terminal terpisah):
```
python worker.py 1 9001
python worker.py 2 9002
python worker.py 3 9003
python broker.py rr
python client.py 1 50000
python client.py 2 halo
```
## Bukti
Log hasil jalan ada di `evidence/` (`hasil-rr.txt`, `hasil-least.txt`).
