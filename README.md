# Database Hardening & High Availability Cluster — `klinik_db`

Proyek Akhir **Keamanan Sistem Informasi** — Kelompok 4
D-IV Komputasi Statistik, Politeknik Statistik STIS

Lab pengujian keamanan basis data klinik: **MySQL Master–Slave + HAProxy**, dengan lima skenario pengujian yang membuktikan CIA Triad + Accountability.

---

## Daftar Isi

- [Arsitektur](#arsitektur)
- [Struktur Berkas](#struktur-berkas)
- [Skema Basis Data](#skema-basis-data)
- [User & Hak Akses](#user--hak-akses)
- [Cara Menjalankan](#cara-menjalankan)
- [Web Demo Interaktif](#web-demo-interaktif)
- [Lima Skenario Pengujian](#lima-skenario-pengujian)
- [Status Implementasi](#status-implementasi)
- [Yang Masih Perlu Dikerjakan](#yang-masih-perlu-dikerjakan)
- [Catatan Teknis Penting](#catatan-teknis-penting)
- [Troubleshooting](#troubleshooting)

---

## Arsitektur

```
              Klien / Script Demo
                      │
                      ▼
        ┌─────────────────────────────┐
        │  HAProxy  (port 3300)       │
        │  dashboard: port 8900       │
        │  health check tiap 2 detik  │
        └──────────┬──────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
   db-master              db-slave
   host :3305             host :3307
   server-id=1            server-id=2, read_only
        └──── replikasi Binary Log (ROW) ────┘
```

**Peta port**

| Endpoint | Port host | Kegunaan |
|---|---|---|
| HAProxy SQL | **3300** | jalur aplikasi, demo failover |
| HAProxy stats | **8900** | dashboard → http://localhost:8900 |
| db-master | **3305** | akses langsung master |
| db-slave | **3307** | verifikasi replikasi |

> **Catatan:** `prd.md` dan `panduan-pengujian.md` menulis dashboard di port **8404**.
> Nilai yang benar sesuai [config/haproxy.cfg](config/haproxy.cfg) adalah **8900**. Perbaiki di laporan.

**Perilaku load balancer.** `db-slave` ditandai `backup`, artinya **seluruh** trafik diarahkan ke master selama master hidup, dan baru dialihkan ke slave saat master mati. Inilah perilaku yang dibutuhkan Skenario 1 (failover). Baris `balance roundrobin` pada konfigurasi karena itu tidak pernah terpakai.

`option tcp-check` dipakai secara sengaja: health check cukup membuka socket TCP dan tidak mencapai lapisan autentikasi, sehingga tetap lolos meski TLS diwajibkan. `option mysql-check` mengirim paket login polos dan akan ditolak server.

---

## Struktur Berkas

```
docker-compose.yml              3 service: db-master, db-slave, haproxy
config/
  haproxy.cfg                   load balancer + dashboard
  mysql-master.cnf              (TIDAK TERBACA — lihat Catatan Teknis)
  mysql-slave.cnf               (TIDAK TERBACA — lihat Catatan Teknis)
sql/
  01-schema.sql                 4 tabel: users, pasien, rekam_medis, audit_log
  02-users.sql                  3 user + GRANT least privilege
  03-sample-data.sql            data sampel, NIK dienkripsi AES_ENCRYPT
  04-audit-harvest.sql          sp_harvest_audit() — panen forensik
  skenario2-attack.sql          payload injeksi pada tabel pasien
  skenario2-attack-medis.sql    payload injeksi numerik pada rekam_medis
  skenario2-mitigation.sql      mitigasi prepared statement
ssl/                            sertifikat CA, server, client (di-mount ke kedua node)
setup-replikasi.sh              bootstrap replikasi Master -> Slave
aktifkan-tls.sh                 aktifkan require_secure_transport (persisten)
web-demo/                       aplikasi peraga interaktif (port 8080)
  server.py                     backend Python, panggil MySQL via docker exec
  index.html / app.js / style.css
  run-demo.bat                  pintasan jalankan di Windows
user_screenshots/               22 screenshot ASLI — dipakai laporan 40 halaman
screenshots/                    20 gambar hasil render PIL (lihat catatan)
prd.md                          Product Requirements Document
task.md                         checklist pekerjaan (0 / 75 tercentang)
panduan-pengujian.md            panduan eksekusi per skenario
pengujian sementara.docx/.pdf   laporan + panduan screenshot
build_laporan_akhir_40hlm.py    generator laporan akhir → user_screenshots/
build_full_word_report.py       generator laporan lama  → screenshots/
generate_all_screenshots.py     generator gambar terminal (PIL)
generate_doc_helpers.py         helper dokumen
```

> **Dua folder screenshot — jangan tertukar.**
> `user_screenshots/` berisi tangkapan layar **asli** (dimensi bervariasi, RGBA) dan inilah yang dipakai `build_laporan_akhir_40hlm.py`.
> `screenshots/` berisi gambar yang **digambar** oleh `generate_all_screenshots.py` memakai PIL (semua lebar persis 1100px) dengan output di-hardcode — bukan tangkapan layar. Gunakan `user_screenshots/` untuk laporan.

Berkas `sql/*.sql` dengan awalan angka dijalankan otomatis dan berurutan oleh MySQL saat container **pertama kali** dibuat, karena folder `sql/` di-mount ke `/docker-entrypoint-initdb.d`.

---

## Skema Basis Data

Empat tabel di `klinik_db` ([sql/01-schema.sql](sql/01-schema.sql)):

| Tabel | Isi | Catatan keamanan |
|---|---|---|
| `users` | akun internal (admin, dokter, resepsionis) | menyimpan hash password |
| `pasien` | identitas pasien | `nik_encrypted` VARBINARY, dienkripsi `AES_ENCRYPT` |
| `rekam_medis` | diagnosa & resep | FK ke `pasien` dan `users` |
| `audit_log` | jejak percobaan mencurigakan | diisi otomatis oleh `sp_harvest_audit()` |

**Enkripsi at-rest.** Kolom `nik_encrypted` diisi lewat `AES_ENCRYPT(nik, 'kunci_rahasia_klinik')`. Dekripsi dengan kunci benar mengembalikan NIK asli; kunci salah mengembalikan `NULL`. Kunci di-hardcode **hanya untuk demo lab** — di produksi harus lewat KMS (tercatat sebagai batasan di `prd.md`).

---

## User & Hak Akses

Prinsip *least privilege* ([sql/02-users.sql](sql/02-users.sql)):

| User | Password | Hak akses |
|---|---|---|
| `root` | `RootPass123!` | penuh (administratif) |
| `app_user` | `AppPass123!` | SELECT/INSERT/UPDATE `pasien` & `rekam_medis`; INSERT `audit_log` |
| `read_only` | `ReadPass123!` | SELECT `pasien` saja |
| `replicator` | `ReplPass123!` | `REPLICATION SLAVE` (tidak boleh baca data) |

Setiap user sengaja dibatasi agar percobaan di luar wewenang menghasilkan penolakan yang bisa dibuktikan.

---

## Cara Menjalankan

**Prasyarat:** Docker Desktop berjalan. Perintah dijalankan dari **Git Bash**.

```bash
# Bangun dari nol (inisialisasi pertama 2-4 menit)
docker compose down -v
docker compose up -d

# Pantau sampai siap
docker compose ps
docker exec db-master mysql -uroot -pRootPass123! -e "SELECT 1"
```

Buka dashboard: **http://localhost:8900** — kedua node harus hijau (UP).

Lalu jalankan **tiga langkah wajib** ini secara berurutan:

```bash
# 1. Setup replikasi Master -> Slave (Skenario 1)
bash setup-replikasi.sh

# 2. Aktifkan penegakan TLS (Skenario 3)
bash aktifkan-tls.sh

# 3. Muat prosedur audit (Skenario 5)
docker exec -i db-master mysql -uroot -pRootPass123! \
  --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED < sql/04-audit-harvest.sql
```

Setelah `bash setup-replikasi.sh` selesai, pastikan muncul:

```
Replica_IO_Running: Yes
Replica_SQL_Running: Yes
Source_SSL_Allowed: Yes
```

Dan `bash aktifkan-tls.sh` harus menampilkan:

```
ERROR 3159 (HY000): Connections using insecure transport are prohibited...
[OK] TLS diwajibkan -- Skenario 3 siap didemokan.
```

> **Urutannya tidak boleh dibalik.** `setup-replikasi.sh` menyalin data ke slave lewat `mysqldump`; kalau TLS sudah diwajibkan lebih dulu, langkah itu jadi lebih rumit tanpa manfaat.

> **Setelah `docker compose down -v`**, ketiga langkah ini harus diulang — semuanya adalah state runtime, bukan bagian dari image.

---

## Web Demo Interaktif

Aplikasi peraga di [web-demo/](web-demo/) — memanggil MySQL **sungguhan** lewat `docker exec`, bukan simulasi. Cocok dipakai saat presentasi karena kontras before/after terlihat langsung.

```bash
cd web-demo
python server.py          # atau klik run-demo.bat
```

Buka **http://localhost:8080**. Badge di kanan atas menandakan status:

| Badge | Arti |
|---|---|
| 🟢 *Live Docker Cluster Connected* | terhubung ke MySQL nyata — angka di layar hasil query sungguhan |
| 🔵 *Interactive Simulation Mode* | backend mati, menampilkan data contoh |

> **Perhatikan badge ini saat demo.** Kalau berwarna biru, yang tampil bukan hasil pengukuran. Pastikan `python server.py` berjalan dan container hidup sebelum presentasi.

**Endpoint backend** ([web-demo/server.py](web-demo/server.py)):

| Endpoint | Fungsi | Terhubung ke UI |
|---|---|---|
| `GET /api/health` | cek koneksi cluster | ✅ |
| `POST /api/sqli` | query rentan vs prepared statement | ✅ |
| `POST /api/tls` | uji koneksi dengan/tanpa SSL | ✅ |
| `GET /api/audit` | panggil `sp_harvest_audit()` + tampilkan `audit_log` | ✅ |
| `POST /api/rbac` | uji hak akses per role | ⚠️ belum dipanggil frontend |

**Hasil uji langsung** (25 September 2026, backend hidup):

```
/api/health                    → {"status":"ok","cluster":"online"}
/api/sqli mode=vulnerable      → 3 baris pasien bocor
/api/sqli mode=safe            → {"rows": []}  ← payload sama, serangan gagal
/api/rbac read_only SELECT_MEDIS → ERROR 1142 ... denied for table 'rekam_medis'
```

Panel **RBAC** masih memakai teks statis walaupun endpoint-nya sudah berfungsi di server. Menyambungkannya ke `/api/rbac` akan membuat Skenario 4 ikut membuktikan diri secara langsung.

---

## Lima Skenario Pengujian

Setiap skenario mengikuti pola **Before-Attack → During-Attack → After-Mitigation**.
Panduan lengkap dengan penanda screenshot ada di `pengujian sementara.docx`.

### Skenario 1 — Failover & High Availability `Availability`

```bash
# Before: tulis lewat HAProxy, verifikasi muncul di slave
docker exec db-master mysql -h haproxy -P 3300 -u app_user -pAppPass123! \
  -e "INSERT INTO klinik_db.pasien (nama) VALUES ('Pasien Uji HA');"
docker exec db-slave mysql -uroot -pRootPass123! \
  -e "SELECT nama FROM klinik_db.pasien WHERE nama='Pasien Uji HA';"

# During: matikan master
docker stop db-master
docker exec db-slave mysql -h haproxy -P 3300 -u app_user -pAppPass123! \
  -e "SELECT id, nama FROM klinik_db.pasien LIMIT 3;"   # tetap bisa dibaca

# After: hidupkan kembali
docker start db-master
docker exec db-slave mysql -uroot -pRootPass123! -e "SHOW REPLICA STATUS\G"
```

**Indikator lulus:** slave tetap melayani saat master mati; tidak ada data hilang; `Replica_IO_Running: Yes` dan `Replica_SQL_Running: Yes` setelah master pulih, tanpa intervensi manual.

### Skenario 2 — SQL Injection Attack & Prevention `Confidentiality` `Integrity`

```bash
# During: query rentan (CONCAT) — data bocor
docker exec -i db-master mysql -uroot -pRootPass123! < sql/skenario2-attack.sql
docker exec -i db-master mysql -uroot -pRootPass123! < sql/skenario2-attack-medis.sql

# After: prepared statement — serangan gagal
docker exec -i db-master mysql -uroot -pRootPass123! < sql/skenario2-mitigation.sql
```

Payload: `' OR '1'='1' --` (string) dan `1 OR 1=1` (numerik, tanpa tanda kutip).

**Indikator lulus:** query rentan mengembalikan seluruh data; query dengan parameter `?` mengembalikan **0 rows**; percobaan tercatat sebagai `SQL_INJECTION_ATTEMPT`.

### Skenario 3 — SSL/TLS & Enkripsi Data `Confidentiality`

```bash
# Penolakan koneksi non-TLS
docker exec db-master mysql -h 127.0.0.1 -u app_user -pAppPass123! \
  --ssl-mode=DISABLED -e "SELECT 1;"          # harus ERROR 3159

# Verifikasi cipher aktif
docker exec db-master mysql -uroot -pRootPass123! \
  -e "SHOW STATUS LIKE 'Ssl_cipher';"

# Enkripsi at-rest
docker exec db-master mysql -uroot -pRootPass123! -e "
  SELECT nama, HEX(nik_encrypted) FROM klinik_db.pasien LIMIT 3;
  SELECT nama, CAST(AES_DECRYPT(nik_encrypted,'kunci_rahasia_klinik') AS CHAR) FROM klinik_db.pasien LIMIT 3;
  SELECT nama, CAST(AES_DECRYPT(nik_encrypted,'kunci_salah') AS CHAR) FROM klinik_db.pasien LIMIT 3;"
```

**Indikator lulus:** koneksi tanpa SSL ditolak `ERROR 3159`; koneksi bersertifikat berhasil dengan cipher terkonfirmasi; dekripsi kunci salah menghasilkan `NULL`.

> **⚠️ Kondisi saat ini — baru sebagian terpenuhi.** Hasil uji langsung:
>
> | Uji | Hasil sekarang | Seharusnya |
> |---|---|---|
> | `--ssl-mode=DISABLED` | koneksi **berhasil** (mengembalikan `1`) | **ERROR 3159** |
> | `SHOW STATUS LIKE 'Ssl_cipher'` | `TLS_AES_256_GCM_SHA384` ✅ | cipher aktif |
> | `AES_DECRYPT` kunci salah | `NULL` ✅ | `NULL` |
>
> Artinya: **enkripsi at-rest (AES) sudah bekerja**, dan TLS tersedia — tetapi **belum diwajibkan**, sehingga penyerang masih bisa menyambung tanpa enkripsi. Cipher yang muncul berasal dari sertifikat auto-generate MySQL, bukan dari `ssl/` milik proyek.
>
> Perbaikannya ada di [Yang Masih Perlu Dikerjakan §1](#1-aktifkan-tls-skenario-3).

### Skenario 4 — Least Privilege `Confidentiality` `Integrity`

```bash
docker exec db-master mysql -h127.0.0.1 -u read_only -pReadPass123! \
  -e "INSERT INTO klinik_db.pasien (nama) VALUES ('Hacker');"     # ERROR 1142
docker exec db-master mysql -h127.0.0.1 -u read_only -pReadPass123! \
  -e "SELECT * FROM klinik_db.rekam_medis;"                        # ERROR 1142
docker exec db-master mysql -h127.0.0.1 -u app_user -pAppPass123! \
  -e "DROP TABLE klinik_db.pasien;"                                # ERROR 1142
docker exec db-master mysql -h127.0.0.1 -u app_user -pAppPass123! \
  -e "SELECT * FROM klinik_db.users;"                              # ERROR 1142
docker exec db-master mysql -h127.0.0.1 -u replicator -pReplPass123! \
  -e "SELECT * FROM klinik_db.pasien;"                             # ERROR 1142
```

**Sudah diverifikasi langsung:**

```
ERROR 1142 (42000): SELECT command denied to user 'read_only'@'127.0.0.1' for table 'rekam_medis'
ERROR 1142 (42000): SELECT command denied to user 'app_user'@'127.0.0.1' for table 'users'
```

> **Soal kode error `replicator` — penting untuk sidang.** Hasilnya bergantung cara menyambung:
>
> | Perintah | Kode | Sebab |
> |---|---|---|
> | `mysql ... -e "SELECT * FROM klinik_db.pasien"` | **1142** | lolos level database (`REPLICATION SLAVE` itu privilege global `ON *.*`), ditolak di level **tabel** |
> | `mysql ... klinik_db -e "SELECT * FROM pasien"` | **1044** | database dibuka lebih dulu → ditolak di level **database** |
>
> Keduanya benar. Menjelaskan perbedaan dua lapis pemeriksaan privilege ini adalah jawaban yang lebih kuat daripada sekadar mencocokkan angka dengan proposal.

### Skenario 5 — Audit Logging & Anomaly Detection `Accountability`

```bash
docker exec db-master mysql -uroot -pRootPass123! -e "CALL klinik_db.sp_harvest_audit();"
docker exec db-master mysql -uroot -pRootPass123! -e "
  SELECT id, aksi, tabel_target, ip_address, waktu FROM klinik_db.audit_log ORDER BY waktu;"

# Lapis audit kedua — general log bawaan MySQL
docker exec db-master mysql -uroot -pRootPass123! -e "
  SELECT event_time, user_host, command_type, argument
  FROM mysql.general_log ORDER BY event_time DESC LIMIT 20;"
```

**Sudah diverifikasi berjalan:**

```
id  user_id  aksi                    tabel_target  ip_address
1   NULL     SQL_INJECTION_ATTEMPT   unknown
2   NULL     UNAUTHORIZED_SELECT     rekam_medis   127.0.0.1
3   NULL     UNAUTHORIZED_SELECT     users         127.0.0.1
```

**Indikator lulus:** seluruh percobaan dari skenario lain muncul di `audit_log` lengkap dengan timestamp, jenis aksi, tabel sasaran, dan IP asal.

---

## Status Implementasi

Diverifikasi langsung terhadap container yang berjalan (23 September 2026):

Diuji ulang end-to-end setelah menjalankan ketiga langkah di [Cara Menjalankan](#cara-menjalankan):

| # | Skenario | Status | Bukti terukur |
|---|---|---|---|
| 1 | Failover & HA | ✅ **Lulus** | replikasi `Yes/Yes`; master mati → dilayani `server_id=2`; pulih otomatis |
| 2 | SQL Injection | ✅ **Lulus** | rentan bocor 3 baris → mitigasi `0 rows` |
| 3 | SSL/TLS | ✅ **Lulus** | `ERROR 3159` tanpa SSL; `TLS_AES_256_GCM_SHA384` dengan sertifikat |
| 4 | Least Privilege | ✅ **Lulus** | `ERROR 1142` untuk read_only & app_user |
| 5 | Audit Logging | ✅ **Lulus** | 3 jenis aksi terpanen otomatis dari `mysql.general_log` |

Konfigurasi efektif master setelah setup:

```
general_log               ON
log_output                FILE,TABLE           ← tabel mysql.general_log terisi
require_secure_transport  ON                   ← persisten via conf.d/zz-tls.cnf
ssl_ca                    /etc/mysql/certs/ca.pem   ← sertifikat proyek, bukan auto-generate
```

**Sudah diuji bertahan melewati restart.** Skenario 1 menjalankan `docker stop/start db-master`; setelah itu `require_secure_transport` tetap `ON` dan `ERROR 3159` masih muncul — jadi Skenario 3 tetap bisa diperagakan walau dijalankan setelah Skenario 1.

---

## Yang Masih Perlu Dikerjakan

### ✅ 1. Aktifkan TLS (Skenario 3) — SELESAI

Dikerjakan lewat [aktifkan-tls.sh](aktifkan-tls.sh). Sertifikat di `ssl/` sudah di-mount dan ditunjuk `--ssl-ca/--ssl-cert/--ssl-key` di compose; penegakannya dinyalakan oleh skrip tersebut.

### ✅ 2. Konfigurasi replikasi (Skenario 1) — SELESAI

Dikerjakan lewat [setup-replikasi.sh](setup-replikasi.sh). Skrip mengambil koordinat binlog **otomatis** dari dump (`--source-data=2`), jadi tidak perlu menyalin `SHOW MASTER STATUS` manual.

> Kalau menjalankan `CHANGE REPLICATION SOURCE TO` manual, `SOURCE_LOG_FILE`/`SOURCE_LOG_POS` harus diisi nilai nyata. Menyalin mentah placeholder seperti `'<dari SHOW MASTER STATUS>'` menghasilkan `ERROR 1064` (syntax error). Pakai skrip saja.

### 3. Perbaiki path hardcoded di skrip Python

Ketiga generator menunjuk folder yang **tidak ada di mesin ini**:

```python
r"d:\STIS SEM 6\KSI\ksi-akhir\project-kelompok4\user_screenshots"
```

Projek ini berada di `D:\Perkuliahan\SEMESTER 6\KSI\projek akhir\`, jadi generator akan gagal atau melewati semua gambar. Ganti dengan path relatif supaya jalan di semua mesin anggota tim:

```python
import os
BASE = os.path.dirname(os.path.abspath(__file__))
USER_SCREENSHOTS_DIR = os.path.join(BASE, "user_screenshots")
```

Pertimbangkan juga menghapus `screenshots/` (versi PIL) agar tidak tertukar — `build_full_word_report.py` masih menunjuk ke sana.

### 4. Sambungkan panel RBAC ke backend

Endpoint `POST /api/rbac` sudah berfungsi di [web-demo/server.py](web-demo/server.py) dan mengembalikan `ERROR 1142` sungguhan, tetapi `app.js` belum pernah memanggilnya — panel Least Privilege masih menampilkan teks statis. Menyambungkannya membuat Skenario 4 ikut membuktikan diri saat demo.

### 5. Lengkapi dokumen

- `task.md` — **0 dari 75** item tercentang; perbarui sesuai progres nyata
- `prd.md` & `panduan-pengujian.md` — perbaiki port dashboard 8404 → **8900**
- Proposal BAB I, II, IV, V masih berupa template

---

## Catatan Teknis Penting

### File `.cnf` tidak terbaca oleh MySQL

`config/mysql-master.cnf` dan `mysql-slave.cnf` **diabaikan total**. Bind mount Windows menyajikan file sebagai `0777`, dan MySQL menolak memuat config world-writable:

```
mysqld: [Warning] World-writable config file '/etc/mysql/conf.d/master.cnf' is ignored.
```

Menambahkan `:ro` **tidak** memperbaikinya. Karena itu seluruh konfigurasi ditulis di bagian `command:` pada [docker-compose.yml](docker-compose.yml), dan kedua file `.cnf` kini **hanya berfungsi sebagai dokumentasi** — tidak berpengaruh apa pun terhadap server.

Jika ingin mengubah konfigurasi, ubah di `command:`, bukan di `.cnf`.

### Jangan taruh `--require-secure-transport=ON` di `command:`

Terlihat wajar, tapi **membuat inisialisasi pertama macet permanen**. Saat container baru dibuat, entrypoint MySQL menjalankan temporary server lalu menyambung lewat socket **tanpa TLS** untuk memuat `sql/*.sql`. Kalau TLS sudah diwajibkan sejak boot, koneksi itu ditolak dan proses menggantung — container terlihat `Up` tetapi mysqld tidak pernah ready.

Sudah diuji: macet lebih dari 6 menit tanpa progres, log berhenti di `root@localhost is created with an empty password`.

Karena itu sertifikat (`--ssl-ca/--ssl-cert/--ssl-key`) **tetap** dipasang sejak boot, tetapi **penegakannya** dinyalakan [aktifkan-tls.sh](aktifkan-tls.sh) setelah kedua node siap. Skrip itu menulis `/etc/mysql/conf.d/zz-tls.cnf` (chmod 644) agar setelan bertahan melewati `docker stop/start` pada Skenario 1.

### ERROR 2061 vs ERROR 3159 — jangan tertukar

`app_user` memakai `caching_sha2_password`. Plugin itu menolak koneksi non-SSL lebih dulu dengan **ERROR 2061** ("Authentication requires secure connection") *sebelum* `require_secure_transport` sempat dievaluasi. Errornya benar, tapi datang dari lapisan **autentikasi** — bukan dari kebijakan TLS yang ingin dibuktikan proposal.

Karena itu [aktifkan-tls.sh](aktifkan-tls.sh) membuat user peraga `tls_demo` ber-`mysql_native_password`. Dengan plugin itu, penolakan murni berasal dari kebijakan TLS sehingga yang muncul **ERROR 3159** sesuai BAB III.

### Kenapa `audit_log` tidak boleh diisi manual

Percobaan akses yang ditolak server **tidak bisa mencatat dirinya sendiri**:

1. `read_only` dan `replicator` tidak punya `GRANT INSERT` ke `audit_log`.
2. `TRIGGER` tidak ter-*fire* pada statement yang ditolak (`ERROR 1142`) — statement dihentikan di lapisan privilege sebelum eksekusi.
3. Koneksi yang ditolak karena tanpa SSL (`ERROR 3159`) bahkan belum terautentikasi.

Karena itu [sql/04-audit-harvest.sql](sql/04-audit-harvest.sql) memanen bukti dari `mysql.general_log` — audit trail bawaan MySQL yang mencatat semua statement apa pun hasilnya. Timestamp yang tersimpan adalah **waktu kejadian sungguhan** (`event_time`), bukan waktu panen.

**Sifat kontrol: detektif (forensik), bukan preventif.** Pencegahan dilakukan oleh GRANT dan TLS (Skenario 3 & 4); `audit_log` berperan untuk penelusuran setelah kejadian. Ini justru jawaban yang benar secara akademis, dan sebaiknya dinyatakan eksplisit di laporan.

Prosedur ini **idempoten** — setiap blok `INSERT` memakai `NOT EXISTS` sehingga aman dipanggil berulang tanpa duplikasi.

### `log_output=FILE,TABLE` wajib

Proposal query tabel `mysql.general_log`, tetapi tabel itu hanya terisi jika `log_output` memuat `TABLE`. Default MySQL hanya `FILE`. Tanpa ini, Skenario 5 selalu mengembalikan 0 baris.

### FK pada `audit_log` tidak menghalangi (tapi berisiko)

`audit_log` punya `FOREIGN KEY (user_id) REFERENCES users(id)`, sementara `sp_harvest_audit()` selalu mengisi `user_id` dengan `NULL`. Ini **tetap berjalan** karena MySQL mengizinkan `NULL` pada kolom FK — sudah diverifikasi.

Namun bila suatu saat prosedur diubah untuk mengisi `user_id` sungguhan, penolakan dari `read_only`/`replicator` akan **gagal dicatat**, karena kedua user itu tidak punya baris di tabel `users`. Pertimbangkan melepas FK tersebut.

### Bug web-demo yang sudah diperbaiki (25 Sep 2026)

Tiga tempat melaporkan keberhasilan yang tidak pernah terjadi. Semuanya kini mengikuti hasil nyata:

1. **`/api/tls` selalu mencetak `[STATUS: REJECTED AT TCP HANDSHAKE]`** walau koneksi berhasil. Lewat `subprocess` (tanpa TTY), `--ssl-mode=DISABLED` justru mengembalikan `returncode 0` dan `stdout '1\n1\n'`. Server membuang satu-satunya baris stderr (warning password), menyisakan string kosong, lalu tetap mencetak label penolakan. Sekarang status dipilih dari `returncode` dan isi error: berhasil → "BELUM AMAN" + cara memperbaiki; `3159` → ditolak oleh kebijakan TLS; error lain → ditolak tapi **bukan** oleh TLS.

2. **Fase AFTER pada SQLi hardcode `rows = []`.** Klaim "serangan gagal" tidak pernah diuji ke MySQL. Sekarang memanggil `/api/sqli` dengan `mode: 'safe'`, dan bila mitigasi rusak akan menampilkan `❌ MITIGASI GAGAL` apa adanya.

3. **Fallback panel TLS menampilkan `ERROR 3159`** seolah hasil pengukuran, padahal `require_secure_transport` masih `OFF`. Kini diberi penanda `[MODE SIMULASI - BACKEND TIDAK TERHUBUNG]` dan dilabeli "TARGET YANG INGIN DICAPAI".

Verifikasi kedua cabang `/api/tls` (dengan `SET GLOBAL require_secure_transport` dinyalakan sementara lalu dikembalikan ke `OFF`):

```
OFF → [STATUS: KONEKSI TANPA SSL BERHASIL - BELUM AMAN]
ON  → ERROR 3159 ... [STATUS: DITOLAK - ERROR 3159 (require_secure_transport=ON)]
```

### Catatan Git Bash (Windows)

- Tambahkan `export MSYS_NO_PATHCONV=1`, jika tidak `/etc/mysql/certs/...` berubah menjadi `C:/Program Files/Git/etc/mysql/certs/...`
- Gunakan `docker exec -i` saat mem-pipe SQL; tanpa `-i` stdin dibuang diam-diam
- Client `mysql` di dalam container ikut membaca `.cnf` yang ter-mount → tambahkan `--no-defaults` bila perlu

---

## Troubleshooting

**Container tidak mau start / `Access denied for user 'root'`**
Volume lama mungkin korup atau password tidak sinkron. Bangun ulang bersih:
```bash
docker compose down -v && docker compose up -d
```

**`SHOW REPLICA STATUS` kosong**
Replikasi belum dikonfigurasi — lihat [Yang Masih Perlu Dikerjakan §2](#2-konfigurasi-replikasi-skenario-1).

**`ERROR 1045 Access denied` saat failover ke slave**
User aplikasi belum ada di slave. Jalankan `sql/02-users.sql` di slave.

**`SSL connection error: SSL is required but the server doesn't support it`**
`require_secure_transport=ON` aktif tapi TLS gagal diinisialisasi — biasanya karena path sertifikat menunjuk folder yang tidak ada. Periksa:
```bash
docker logs db-master | grep -i "ssl\|tls"
docker exec db-master mysql -uroot -pRootPass123! -e "SHOW VARIABLES LIKE 'have_ssl';"
```
`have_ssl = DISABLED` berarti sertifikat gagal dimuat.

**Tabel `mysql.general_log` kosong**
Butuh `--log-output=FILE,TABLE` di `command:`.

**Dashboard HAProxy tidak terbuka**
Port yang benar **8900**, bukan 8404: http://localhost:8900

**`audit_log` kosong setelah `CALL sp_harvest_audit()`**
Prosedur hanya memanen pola tertentu. Pastikan percobaan tidak sah benar-benar sudah dijalankan, lalu cek sumbernya:
```bash
docker exec db-master mysql -uroot -pRootPass123! \
  -e "SELECT COUNT(*) FROM mysql.general_log;"
```
