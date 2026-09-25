# Panduan Demo — Keamanan Basis Data `klinik_db`

Panduan lengkap untuk presentasi di depan penguji. Setiap langkah disertai **apa yang terjadi** dan **cara menjawab** kalau ditanya.

**Total waktu demo: ±15 menit** (belum termasuk persiapan).

---

## Daftar Isi

- [Persiapan (H-1 dan hari-H)](#persiapan)
- [Pembagian peran](#pembagian-peran)
- [Skenario 1 — Failover & High Availability](#skenario-1--failover--high-availability)
- [Skenario 2 — SQL Injection](#skenario-2--sql-injection)
- [Skenario 3 — SSL/TLS & Enkripsi Data](#skenario-3--ssltls--enkripsi-data)
- [Skenario 4 — Least Privilege](#skenario-4--least-privilege)
- [Skenario 5 — Audit Logging](#skenario-5--audit-logging)
- [Penutup](#penutup)
- [Antisipasi pertanyaan penguji](#antisipasi-pertanyaan-penguji)
- [Kalau demo gagal](#kalau-demo-gagal)

---

## Persiapan

### H-1: rehearsal penuh

Jangan lewati ini. Inisialisasi pertama MySQL makan **3–5 menit** di Windows — jangan sampai terjadi saat penguji menunggu.

```bash
# Git Bash, dari folder projek
docker compose down -v
docker compose up -d
```

Tunggu sampai kedua node siap (cek berkala, ±3–5 menit):

```bash
docker logs db-master 2>&1 | grep "ready for connections"
docker logs db-slave  2>&1 | grep "ready for connections"
```

Lalu jalankan **tiga langkah wajib** berurutan:

```bash
bash setup-replikasi.sh      # Skenario 1
bash aktifkan-tls.sh         # Skenario 3
docker exec -i db-master mysql -uroot -pRootPass123! \
  --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED < sql/04-audit-harvest.sql
```

**Tanda berhasil:**

| Skrip | Harus muncul |
|---|---|
| `setup-replikasi.sh` | `Replica_IO_Running: Yes` / `Replica_SQL_Running: Yes` / `Source_SSL_Allowed: Yes` |
| `aktifkan-tls.sh` | `ERROR 3159 ...` lalu `[OK] TLS diwajibkan` |

> **Penting:** ketiga langkah ini adalah *state runtime*, bukan bagian dari image. Setiap habis `docker compose down -v`, **harus diulang**.

### Hari-H: 15 menit sebelum mulai

```bash
# 1. Pastikan container hidup
docker ps

# 2. Cek kesehatan sistem (ketiganya harus sesuai)
docker exec db-slave mysql -uroot -pRootPass123! \
  --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED \
  -e "SHOW REPLICA STATUS\G" | grep "Running:"

# 3. Jalankan web demo (biarkan terminal ini terbuka)
cd web-demo && python server.py
```

Buka dua jendela browser:
- **http://localhost:8900** — dashboard HAProxy
- **http://localhost:8080** — web demo

> Di web demo, pastikan badge kanan atas **hijau: "Live Docker Cluster Connected"**. Kalau biru ("Interactive Simulation Mode"), berarti `server.py` belum jalan — angka di layar bukan hasil nyata.

### Bersihkan jejak rehearsal (opsional tapi disarankan)

Supaya `audit_log` di Skenario 5 hanya berisi percobaan dari demo hari itu — bukan tumpukan dari rehearsal:

```bash
docker exec db-master mysql -uroot -pRootPass123! \
  --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED \
  -e "TRUNCATE TABLE klinik_db.audit_log;"
```

> Tabelnya akan terisi ulang otomatis saat Skenario 5 dijalankan, memanen dari `mysql.general_log`.

### Checklist terakhir

- [ ] `docker ps` → `db-master`, `db-slave`, `haproxy` semua Up
- [ ] Dashboard 8900 → kedua node **hijau (UP)**
- [ ] Web demo 8080 → badge **hijau**
- [ ] Replikasi → `IO_Running: Yes`, `SQL_Running: Yes`
- [ ] Terminal Git Bash siap, font diperbesar (Ctrl + Scroll) supaya terbaca penguji
- [ ] Video rekaman demo disiapkan sebagai cadangan

---

## Pembagian peran

| Peran | Tugas |
|---|---|
| **Operator** | Mengetik perintah di terminal / mengklik web demo |
| **Narator** | Menjelaskan apa yang terjadi di layar |
| **Penjawab** | Menangani pertanyaan penguji, pegang bagian [Antisipasi](#antisipasi-pertanyaan-penguji) |

Sepakati siapa memegang apa sebelum masuk ruangan.

---

## Skenario 1 — Failover & High Availability

> **Aspek CIA: Availability** · Durasi ±4 menit

### Kalimat pembuka

> "Skenario pertama membuktikan layanan klinik tetap berjalan meski server utama mati. Arsitekturnya: HAProxy di depan, dua node MySQL di belakang — master menangani semua trafik, slave berperan sebagai cadangan."

### Fase A — Kondisi normal

**Tunjukkan dashboard** http://localhost:8900 → kedua node hijau.

> "Kedua node UP. HAProxy melakukan health check setiap 2 detik."

```bash
docker exec db-slave mysql -uroot -pRootPass123! \
  --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED \
  -e "SHOW REPLICA STATUS\G" | grep -E "Running:|Source_SSL"
```

Keluaran:
```
Replica_IO_Running: Yes
Replica_SQL_Running: Yes
Source_SSL_Allowed: Yes
```

> **Penjelasan:** `IO_Running` artinya slave berhasil menarik binary log dari master. `SQL_Running` artinya log itu dieksekusi. `Source_SSL_Allowed: Yes` — replikasinya sendiri berjalan **terenkripsi**.

### Fase B — Buktikan replikasi bekerja

```bash
docker exec db-master mysql -h haproxy -P 3300 -u app_user -pAppPass123! \
  --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED \
  -e "INSERT INTO klinik_db.pasien (nama) VALUES ('Pasien Demo Sidang');"

docker exec db-slave mysql -uroot -pRootPass123! \
  --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED \
  -e "SELECT id, nama FROM klinik_db.pasien WHERE nama='Pasien Demo Sidang';"
```

> **Penjelasan:** data ditulis lewat **port 3300 (HAProxy)**, bukan langsung ke master. Baris yang sama muncul di slave dalam hitungan detik — inilah replikasi asinkron via binary log.

### Fase C — Matikan master

```bash
docker stop db-master
```

**Refresh dashboard** → `db-master` **merah (DOWN)**, `db-slave` tetap hijau.

> "Master mati. Perhatikan HAProxy langsung mendeteksinya dalam 2 detik."

```bash
docker exec db-slave mysql -h haproxy -P 3300 -u app_user -pAppPass123! \
  --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED \
  -e "SELECT @@server_id AS dilayani_oleh, COUNT(*) AS jml FROM klinik_db.pasien;"
```

Keluaran:
```
dilayani_oleh   jml
2               5
```

> **Penjelasan — ini inti skenarionya.** `server_id = 2` berarti permintaan dilayani **slave**, padahal kita menyambung ke alamat yang sama (port 3300). Klien tidak mengubah apa pun; HAProxy yang mengalihkan otomatis. **Layanan baca tidak pernah mati.**

Lalu tunjukkan batasannya — ini menambah kredibilitas:

```bash
docker exec db-slave mysql -h haproxy -P 3300 -u app_user -pAppPass123! \
  --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED \
  -e "INSERT INTO klinik_db.pasien (nama) VALUES ('Coba Tulis');"
```

Keluaran:
```
ERROR 1290 (HY000): The MySQL server is running with the --read-only option
```

> **Penjelasan:** operasi **tulis** ditolak dengan error yang informatif, bukan crash. Ini disengaja — slave sengaja `read_only` supaya datanya tidak menyimpang dari master. Jadi saat master mati, sistem *degraded* (baca saja), bukan *down*.

### Fase D — Pulihkan master

```bash
docker start db-master
# tunggu ±20 detik
docker exec db-slave mysql -uroot -pRootPass123! \
  --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED \
  -e "SHOW REPLICA STATUS\G" | grep -E "Running:|Seconds_Behind"
```

Keluaran:
```
Replica_IO_Running: Yes
Replica_SQL_Running: Yes
Seconds_Behind_Source: 0
```

**Refresh dashboard** → kedua node hijau lagi.

> **Penjelasan:** replikasi tersambung kembali **tanpa satu pun perintah manual**. `Seconds_Behind_Source: 0` artinya slave sudah sinkron penuh. Inilah yang membedakan HA dari sekadar backup.

---

## Skenario 2 — SQL Injection

> **Aspek CIA: Confidentiality + Integrity** · Durasi ±3 menit

### Kalimat pembuka

> "Skenario kedua membuktikan kerentanan SQL Injection dan mitigasinya. Kami tunjukkan dua kondisi dengan payload yang **persis sama**, hanya beda cara query dibangun."

### Cara termudah: lewat web demo

Buka **http://localhost:8080** → tab **SQL Injection**.

1. Klik fase **DURING** → tombol serangan
   → tabel terisi **seluruh data pasien**, badge merah "SERANGAN SUKSES"
2. Klik fase **AFTER**
   → tabel **kosong**, badge hijau "0 Baris Data"

> **Penjelasan:** payloadnya identik — `' OR '1'='1' --`. Yang berubah hanya cara query dirakit.

### Versi terminal (kalau penguji minta lihat SQL-nya)

```bash
# Query rentan — dirakit dengan CONCAT
docker exec -i db-master mysql -uroot -pRootPass123! \
  --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED < sql/skenario2-attack.sql
```

> **Penjelasan:** input pengguna disambung langsung ke string SQL. Tanda kutip pada payload **menutup** kutip pembuka, lalu `OR '1'='1'` membuat kondisi selalu benar, dan `--` mengomentari sisa query. Hasilnya: seluruh tabel bocor walau nama yang dicari tidak ada.

```bash
# Versi numerik — tanpa tanda kutip sama sekali
docker exec -i db-master mysql -uroot -pRootPass123! \
  --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED < sql/skenario2-attack-medis.sql
```

> **Penjelasan:** pada kolom angka, payload `1 OR 1=1` tidak butuh kutip. Ini membuktikan filter "escape tanda kutip" saja **tidak cukup**.

```bash
# Mitigasi — prepared statement
docker exec -i db-master mysql -uroot -pRootPass123! \
  --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED < sql/skenario2-mitigation.sql
```

Keluaran: `Empty set` / 0 baris.

> **Penjelasan — ini kunci jawabannya.** Dengan `PREPARE ... WHERE nama = ?`, struktur query dikirim ke server **lebih dulu**, terpisah dari datanya. Saat payload masuk lewat parameter `?`, MySQL memperlakukannya sebagai **satu string utuh** — mencari pasien yang namanya benar-benar `' OR '1'='1' --`. Tidak ada. Maka 0 baris. Payload tidak pernah dievaluasi sebagai perintah SQL.

---

## Skenario 3 — SSL/TLS & Enkripsi Data

> **Aspek CIA: Confidentiality** · Durasi ±3 menit

### Kalimat pembuka

> "Skenario ketiga melindungi data di dua tempat: saat **melintas di jaringan** (TLS) dan saat **tersimpan di disk** (AES)."

### Bagian 1 — Data in transit

```bash
docker exec db-master mysql -uroot -pRootPass123! \
  --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED \
  -e "SHOW VARIABLES LIKE 'require_secure_transport';"
```

Harus `ON`.

```bash
# Simulasi penyerang: koneksi tanpa enkripsi
docker exec db-master mysql -h 127.0.0.1 -u tls_demo -pDemo123! \
  --ssl-mode=DISABLED -e "SELECT 1;"
```

Keluaran:
```
ERROR 3159 (HY000): Connections using insecure transport are prohibited
while --require_secure_transport=ON.
```

> **Penjelasan:** koneksi ditolak **sebelum autentikasi** — bahkan sebelum password diperiksa. Penyerang yang menyadap jaringan tidak akan mendapat apa pun, karena tidak ada satu byte pun data yang dikirim polos.

```bash
# Koneksi sah dengan sertifikat
docker exec db-master mysql -h 127.0.0.1 -u app_user -pAppPass123! \
  --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=VERIFY_CA \
  -e "SHOW STATUS LIKE 'Ssl_cipher';"
```

Keluaran:
```
Ssl_cipher      TLS_AES_256_GCM_SHA384
```

> **Penjelasan:** koneksi berhasil dan cipher-nya terkonfirmasi — AES 256-bit mode GCM, standar TLS 1.3. Sertifikatnya kami buat sendiri dengan OpenSSL (CA lokal → server cert → client cert).

### Bagian 2 — Data at rest

```bash
docker exec db-master mysql -uroot -pRootPass123! \
  --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED -e "
  SELECT nama,
         LEFT(HEX(nik_encrypted),24) AS cipher,
         CAST(AES_DECRYPT(nik_encrypted,'kunci_rahasia_klinik') AS CHAR) AS kunci_benar,
         CAST(AES_DECRYPT(nik_encrypted,'salah') AS CHAR) AS kunci_salah
  FROM klinik_db.pasien LIMIT 2;"
```

Keluaran:
```
nama          cipher                    kunci_benar        kunci_salah
Ahmad Fauzi   38E28154D3D083D26EB5EF32  3201234567890001   NULL
Siti Rahayu   A903741B44D4CF8BA0E066D8  3209876543210002   NULL
```

> **Penjelasan:** NIK tidak pernah tersimpan sebagai teks biasa — di disk bentuknya ciphertext. Dengan kunci benar terbaca, dengan kunci salah `NULL`. **Artinya: kalau harddisk server dicuri, NIK pasien tetap tidak terbaca.**
>
> Jujur sebutkan batasannya: kunci masih *hardcoded* untuk keperluan lab. Di produksi harus lewat **KMS** terpisah — ini sudah kami catat sebagai keterbatasan di laporan.

---

## Skenario 4 — Least Privilege

> **Aspek CIA: Confidentiality + Integrity** · Durasi ±3 menit

### Kalimat pembuka

> "Skenario keempat membuktikan setiap akun hanya bisa melakukan persis apa yang menjadi haknya — tidak lebih."

### Cara termudah: web demo

Tab **Least Privilege** → fase **AFTER** → klik kedua tombol uji.
Keduanya menampilkan `ERROR 1142` dari MySQL sungguhan.

### Versi terminal

```bash
# read_only — operasi yang SAH
docker exec db-master mysql -h127.0.0.1 -u read_only -pReadPass123! \
  --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED \
  -e "SELECT COUNT(*) FROM klinik_db.pasien;"        # BERHASIL

# read_only — di luar wewenang
docker exec db-master mysql -h127.0.0.1 -u read_only -pReadPass123! \
  --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED \
  -e "SELECT * FROM klinik_db.rekam_medis;"          # ERROR 1142

# app_user — mencoba merusak skema
docker exec db-master mysql -h127.0.0.1 -u app_user -pAppPass123! \
  --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED \
  -e "DROP TABLE klinik_db.pasien;"                  # ERROR 1142

# app_user — mengintip hash password
docker exec db-master mysql -h127.0.0.1 -u app_user -pAppPass123! \
  --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED \
  -e "SELECT * FROM klinik_db.users;"                # ERROR 1142
```

> **Penjelasan:** tunjukkan kontrasnya — `read_only` **berhasil** membaca pasien (haknya memang itu), tapi **ditolak** membaca rekam medis. `app_user` boleh DML tapi dilarang DDL. Ini bukan penolakan buta; setiap akun punya batas yang dirancang.
>
> Dampaknya: kalau kredensial satu akun bocor, kerusakannya terbatas pada hak akun itu saja — tidak seluruh basis data.

**Kalau penguji menyoroti `replicator`:** lihat [Antisipasi](#antisipasi-pertanyaan-penguji) nomor 3.

---

## Skenario 5 — Audit Logging

> **Aspek: Accountability** · Durasi ±2 menit

### Kalimat pembuka

> "Skenario terakhir membuktikan keempat percobaan tadi **terekam** dan bisa direkonstruksi untuk keperluan forensik."

```bash
docker exec db-master mysql -uroot -pRootPass123! \
  --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED \
  -e "CALL klinik_db.sp_harvest_audit();
      SELECT id, aksi, tabel_target, ip_address,
             DATE_FORMAT(waktu,'%d-%m-%Y %H:%i:%s') AS waktu
      FROM klinik_db.audit_log ORDER BY waktu;"
```

Contoh keluaran:
```
id  aksi                        tabel_target  ip_address  waktu
1   CONNECTION_REJECTED_NO_SSL  NULL          127.0.0.1   25-09-2026 08:15:02
2   SQL_INJECTION_ATTEMPT       pasien                    25-09-2026 08:16:41
3   UNAUTHORIZED_SELECT         rekam_medis   127.0.0.1   25-09-2026 08:18:05
4   UNAUTHORIZED_SELECT         users         127.0.0.1   25-09-2026 08:18:22
```

> **Penjelasan:** setiap percobaan dari skenario sebelumnya tercatat lengkap dengan jenis aksi, tabel sasaran, IP asal, dan waktu kejadian.

**Ini poin terpenting — sampaikan dengan percaya diri:**

> "Isi tabel ini **tidak kami ketik manual**. Semuanya dipanen dari `mysql.general_log`, audit trail bawaan MySQL, lewat prosedur `sp_harvest_audit()`. Jadi buktinya berasal dari server itu sendiri, bukan dari klaim skrip kami — dan timestamp-nya waktu kejadian sungguhan."

> **Aman diklik/dijalankan berulang.** Prosedur ini idempoten — memanggilnya dua atau tiga kali tidak menggandakan baris. Sudah diuji: 13 baris tetap 13 baris setelah tiga kali panggil.
>
> Kalau penguji melihat beberapa baris dengan query sama tapi **waktu berbeda**, itu benar — artinya percobaan yang sama memang terjadi berkali-kali, dan masing-masing tercatat terpisah.

Tunjukkan lapisan keduanya:

```bash
docker exec db-master mysql -uroot -pRootPass123! \
  --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED \
  -e "SELECT event_time, command_type, LEFT(CONVERT(argument USING utf8mb4),60) AS query
      FROM mysql.general_log WHERE command_type='Query'
      ORDER BY event_time DESC LIMIT 8;"
```

> **Penjelasan:** ini sumber mentahnya — audit dua lapis. `audit_log` adalah hasil olahan untuk dibaca manusia; `mysql.general_log` adalah bukti mentah dari MySQL yang tidak bisa kami manipulasi.

---

## Penutup

> "Kelima skenario sudah dibuktikan langsung: Availability lewat failover, Confidentiality lewat TLS dan enkripsi AES, Integrity lewat prepared statement dan least privilege, serta Accountability lewat audit logging. Seluruh environment terdefinisi dalam satu `docker-compose.yml` sehingga dapat direproduksi identik oleh siapa pun."

---

## Antisipasi pertanyaan penguji

### 1. "Kenapa tidak pakai XAMPP/Laragon seperti di proposal?"

> "Kami fokuskan ke satu jalur (Docker) demi reproducibility penuh. Seluruh environment terdefinisi dalam `docker-compose.yml` dan bisa dijalankan ulang identik di mesin mana pun. Pada XAMPP/Laragon, versi MySQL dan lokasi konfigurasi bergantung instalasi tiap mesin, sehingga kesetaraan konfigurasi yang disyaratkan tidak dapat dijamin maupun diverifikasi. Kami catat ini sebagai batasan ruang lingkup."

### 2. "Audit log-nya otomatis atau dimasukkan manual?"

> "Otomatis, dipanen dari `mysql.general_log` oleh `sp_harvest_audit()`."

Kalau ditanya kenapa tidak memakai trigger — ini jawaban yang menunjukkan kedalaman:

> "Trigger tidak bisa dipakai, karena statement yang ditolak `ERROR 1142` sudah dihentikan di lapisan privilege **sebelum** dieksekusi, jadi tidak ada trigger yang ter-*fire*. Selain itu `read_only` dan `replicator` tidak punya hak INSERT ke `audit_log`, jadi mustahil mencatat penolakannya sendiri. Karena itu audit di sini bersifat **detektif** (forensik), bukan preventif — pencegahannya dilakukan GRANT dan TLS."

### 3. "Kenapa `replicator` errornya 1044, bukan 1142?"

Bergantung cara menyambung — **keduanya benar**:

| Perintah | Kode | Sebab |
|---|---|---|
| `mysql ... -e "SELECT * FROM klinik_db.pasien"` | **1142** | lolos cek database (`REPLICATION SLAVE` itu privilege global `ON *.*`), ditolak di level **tabel** |
| `mysql ... klinik_db -e "SELECT * FROM pasien"` | **1044** | database dibuka lebih dulu → ditolak di level **database** |

> "MySQL memeriksa privilege berlapis: database dulu, baru tabel. Kalau klien membuka database lebih dulu, penolakan terjadi lebih awal sehingga kodenya 1044."

### 4. "Kenapa slave tidak bisa menerima tulisan saat failover?"

> "Itu disengaja. Slave di-set `read_only` dan `super_read_only`. Kalau slave menerima tulisan saat master mati, datanya akan menyimpang dan saat master hidup kembali replikasi bisa bentrok — `Duplicate entry`, `Error_code: 1062` — yang menghentikan replikasi permanen. Kami memilih *degraded service* (baca saja) daripada risiko kehilangan konsistensi data."

### 5. "Sertifikatnya self-signed, apa tidak masalah?"

> "Untuk lab ini cukup, karena yang dibuktikan adalah mekanisme enkripsinya. Di produksi harus pakai CA tepercaya agar klien bisa memverifikasi identitas server dan mencegah man-in-the-middle. Ini kami catat sebagai keterbatasan."

### 6. "Kunci AES-nya di-hardcode?"

> "Ya, dan itu kami sadari sebagai kelemahan. Di produksi kunci harus dikelola KMS terpisah supaya tidak ikut tersimpan bersama data. Untuk demo lab, yang ingin dibuktikan adalah efeknya: kunci benar → data terbaca, kunci salah → NULL."

### 7. "Kenapa dashboard-nya port 8900, bukan 8404?"

> "8404 adalah salah tulis di proposal awal. Konfigurasi sebenarnya di `config/haproxy.cfg` memakai 8900, dan dokumen sudah kami perbaiki."

### 8. "Kalau HAProxy sendiri mati bagaimana?"

Jawaban jujur — jangan mengarang:

> "Benar, HAProxy saat ini masih *single point of failure*. Untuk produksi perlu HAProxy ganda dengan Virtual IP (misalnya Keepalived). Di luar ruang lingkup proyek ini, tapi kami sadari sebagai keterbatasan arsitektur."

---

## Kalau demo gagal

**Aturan utama: jangan panik, jangan mengarang.** Penguji lebih menghargai diagnosis yang tepat daripada demo mulus.

### Replikasi mati (`Running: No` atau kosong)

```bash
bash setup-replikasi.sh
```
Butuh ±30 detik. Sambil menunggu, jelaskan arsitekturnya.

### ERROR 3159 tidak muncul (TLS mati)

Biasanya karena `docker compose down` dijalankan tanpa menjalankan ulang skrip:
```bash
bash aktifkan-tls.sh
```

### Web demo badge biru

`server.py` belum jalan atau sudah tertutup:
```bash
cd web-demo && python server.py
```

### Container tidak mau start

```bash
docker compose down -v && docker compose up -d
```
**Perlu 3–5 menit.** Kalau ini terjadi saat sidang, pakai video cadangan dan jelaskan lisan.

### Semua gagal

Putar video rekaman rehearsal, lalu tunjukkan `results/` atau isi laporan sebagai bukti. Sampaikan apa adanya bahwa environment sedang bermasalah — itu jauh lebih baik daripada mengklaim sesuatu yang tidak terlihat di layar.

---

## Ringkasan perintah (contekan)

```bash
# PERSIAPAN
docker compose up -d
bash setup-replikasi.sh
bash aktifkan-tls.sh
cd web-demo && python server.py

# S1 FAILOVER
docker stop db-master
docker exec db-slave mysql -h haproxy -P 3300 -uapp_user -pAppPass123! --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED -e "SELECT @@server_id;"
docker start db-master

# S2 SQL INJECTION
docker exec -i db-master mysql -uroot -pRootPass123! --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED < sql/skenario2-attack.sql
docker exec -i db-master mysql -uroot -pRootPass123! --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED < sql/skenario2-mitigation.sql

# S3 TLS
docker exec db-master mysql -h127.0.0.1 -utls_demo -pDemo123! --ssl-mode=DISABLED -e "SELECT 1;"

# S4 LEAST PRIVILEGE
docker exec db-master mysql -h127.0.0.1 -uread_only -pReadPass123! --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED -e "SELECT * FROM klinik_db.rekam_medis;"

# S5 AUDIT
docker exec db-master mysql -uroot -pRootPass123! --ssl-ca=/etc/mysql/certs/ca.pem --ssl-mode=REQUIRED -e "CALL klinik_db.sp_harvest_audit(); SELECT * FROM klinik_db.audit_log;"
```
