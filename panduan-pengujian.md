# Panduan Persiapan & Eksekusi Pengujian — klinik_db

Dokumen ini melengkapi `prd.md` dan `task.md`. Isinya dua bagian:
1. **Kondisi/prasyarat** yang harus siap sebelum mulai testing
2. **Langkah eksekusi detail** per skenario, mengikuti pola Before-Attack → During-Attack → After-Mitigation

> Ganti nilai dalam `<...>` sesuai environment kamu (password, IP, nama file sertifikat, dsb).

---

## BAGIAN 1 — Kondisi Database yang Harus Disiapkan

Sebelum menjalankan skenario apa pun, pastikan checklist ini **semua ✅**, karena satu skenario bisa gagal cuma karena prasyarat skenario lain belum siap.

### 1.1 Infrastruktur jalan & sehat

- [ ] Master (port 3306) dan Slave (port 3307) sama-sama **UP**
- [ ] Replikasi aktif: jalankan di Slave →
  ```sql
  SHOW SLAVE STATUS\G
  ```
  Pastikan `Slave_IO_Running: Yes` dan `Slave_SQL_Running: Yes`
- [ ] HAProxy jalan di port 3300, dashboard bisa dibuka di `http://localhost:8404`
- [ ] Dashboard HAProxy menunjukkan kedua backend (Master & Slave) berstatus **UP** (hijau)

### 1.2 Sertifikat SSL/TLS sudah terpasang

- [ ] CA Certificate, Server Certificate, Client Certificate sudah digenerate via OpenSSL
- [ ] Sertifikat sudah disalin ke: Master, Slave, HAProxy, dan folder tempat kamu menjalankan `mysql` client
- [ ] `require_secure_transport=ON` aktif di my.cnf/config kedua server — cek:
  ```sql
  SHOW VARIABLES LIKE 'require_secure_transport';
  ```

### 1.3 User & hak akses sudah dibuat

Jalankan (di Master, akan terreplikasi ke Slave) dan verifikasi tiga user berikut ada dengan hak yang benar:

```sql
SELECT user, host FROM mysql.user WHERE user IN ('app_user','read_only','replicator');
SHOW GRANTS FOR 'app_user'@'%';
SHOW GRANTS FOR 'read_only'@'%';
SHOW GRANTS FOR 'replicator'@'%';
```

Cek manual bahwa:
- `app_user` → SELECT, INSERT, UPDATE pada `pasien`, `rekam_medis` (bukan DDL, bukan akses `users`)
- `read_only` → SELECT saja, hanya pada `pasien`
- `replicator` → hanya `REPLICATION SLAVE`
- Ketiganya punya klausul `REQUIRE SSL`

### 1.4 Skema & data sampel sudah terisi

- [ ] 4 tabel ada: `users`, `pasien`, `rekam_medis`, `audit_log`
- [ ] `pasien` berisi **minimal 3 baris** data sintetis (dipakai sebagai baseline demo Skenario 2)
- [ ] Kolom `nik_encrypted` sudah diisi dalam bentuk terenkripsi:
  ```sql
  INSERT INTO pasien (nama, nik_encrypted, tanggal_lahir, alamat, no_telepon)
  VALUES ('<nama_sampel>', AES_ENCRYPT('<nik_asli>', '<kunci_demo>'), '<tgl>', '<alamat>', '<no_hp>');
  ```
- [ ] `rekam_medis` berisi minimal 1–2 baris terkait `pasien_id` yang ada
- [ ] `users` (tabel aplikasi, beda dari user MySQL) berisi minimal 1 akun tiap role: admin, dokter, resepsionis

> **Catatan:** `<kunci_demo>` di sini hardcode string biasa (misal `'kunciDemo123'`) — ini sesuai catatan proposal bahwa untuk demo lab kunci ditulis langsung, bukan lewat KMS.

### 1.5 Logging aktif

- [ ] Tabel `audit_log` **kosong** sebelum mulai sesi demo penuh (supaya urutan waktunya rapi saat direkam) — atau minimal dicatat baseline count-nya
- [ ] MySQL General Query Log aktif:
  ```sql
  SET GLOBAL general_log = 'ON';
  SET GLOBAL general_log_file = '<path_log_file>';
  SHOW VARIABLES LIKE 'general_log%';
  ```

### 1.6 Alat perekaman bukti siap

- [ ] Software screen recorder aktif (untuk video demonstrasi)
- [ ] Terminal font/ukuran cukup besar agar terbaca di rekaman
- [ ] Siapkan folder untuk menyimpan screenshot per langkah, dengan penamaan jelas, misal:
  `skenario1_langkah1_baseline.png`, `skenario2_before.png`, dst.

### 1.7 Snapshot/reset point (sangat disarankan)

Karena beberapa skenario **mengubah data** (INSERT, matikan server), siapkan cara reset environment ke kondisi bersih:
- Jalur Docker: `docker compose down -v && docker compose up -d` lalu jalankan ulang skrip skema+seed
- Jalur XAMPP/Laragon: backup folder data MySQL awal, atau siapkan skrip `DROP DATABASE klinik_db; CREATE DATABASE klinik_db;` + re-seed

Ini penting supaya kalau demo skenario 1 gagal di tengah jalan, kamu tidak perlu install ulang dari nol.

---

## BAGIAN 2 — Langkah Eksekusi Per Skenario

### Skenario 1 — Failover & High Availability

**Prasyarat khusus:** replikasi harus dalam kondisi sehat (§1.1), akses ke Docker CLI atau XAMPP Control Panel.

| Fase | Langkah | Perintah / Aksi |
|---|---|---|
| Before-Attack | 1. Buka dashboard HAProxy, screenshot kedua node UP | Browser → `http://localhost:8404` |
| Before-Attack | 2. INSERT data baru via HAProxy (port 3300) | `mysql -h 127.0.0.1 -P 3300 -u app_user -p --ssl-ca=<ca.pem> klinik_db -e "INSERT INTO pasien (nama, ...) VALUES (...)"` |
| Before-Attack | 3. Verifikasi data sudah masuk ke Slave langsung (port 3307) | `mysql -h 127.0.0.1 -P 3307 -u root -p -e "SELECT * FROM klinik_db.pasien ORDER BY id DESC LIMIT 1"` |
| During-Attack | 4. Matikan Master paksa | Docker: `docker stop db-master` / Windows: matikan MySQL lewat XAMPP Control Panel |
| During-Attack | 5. Screenshot dashboard HAProxy → Master harus DOWN, Slave tetap UP | Browser refresh `:8404` |
| During-Attack | 6. SELECT via port 3300 → harus tetap berhasil (dialihkan ke Slave) | `mysql -h 127.0.0.1 -P 3300 -u app_user -p --ssl-ca=<ca.pem> klinik_db -e "SELECT * FROM pasien"` |
| During-Attack | 7. INSERT via port 3300 saat Master down → harus gagal dengan error informatif, bukan crash | `mysql -h 127.0.0.1 -P 3300 -u app_user -p --ssl-ca=<ca.pem> klinik_db -e "INSERT INTO pasien ..."` → catat pesan error persis |
| After-Mitigation | 8. Nyalakan kembali Master | `docker start db-master` / nyalakan lewat XAMPP |
| After-Mitigation | 9. Cek reconnect otomatis di Slave | `mysql -h 127.0.0.1 -P 3307 -u root -p -e "SHOW SLAVE STATUS\G"` → pastikan `Slave_IO_Running`/`Slave_SQL_Running` = Yes |
| After-Mitigation | 10. INSERT data baru via 3300, verifikasi tereplikasi ke Slave | Ulangi langkah 2–3 dengan data baru |

---

### Skenario 2 — SQL Injection Attack & Prevention

**Prasyarat khusus:** minimal 3 baris data di `pasien`, akun `app_user` aktif dan bisa konek TLS.

| Fase | Langkah | Perintah / Aksi |
|---|---|---|
| Before-Attack | 1. Tampilkan isi tabel `pasien` sebagai baseline | `SELECT id, nama FROM pasien;` |
| During-Attack | 2. Bangun query rentan via konkatenasi (variable session) | ```sql SET @nama_input = '\' OR \'1\'=\'1\' -- '; SET @query_rentan = CONCAT('SELECT * FROM pasien WHERE nama = \'', @nama_input, '\''); SELECT @query_rentan; ``` |
| During-Attack | 3. Eksekusi via PREPARE/EXECUTE, tunjukkan semua data bocor | ```sql PREPARE stmt FROM @query_rentan; EXECUTE stmt; DEALLOCATE PREPARE stmt; ``` |
| During-Attack | 4. Ulangi langkah 2–3 pada `rekam_medis` (ganti nama tabel & kolom filter) | sama seperti di atas, target tabel `rekam_medis` |
| After-Mitigation | 5. Jalankan query setara dengan prepared statement + parameter `?` | ```sql PREPARE stmt2 FROM 'SELECT * FROM pasien WHERE nama = ?'; SET @payload = '\' OR \'1\'=\'1\' -- '; EXECUTE stmt2 USING @payload; DEALLOCATE PREPARE stmt2; ``` |
| After-Mitigation | 6. Bandingkan hasil: langkah 3 = banyak baris, langkah 5 = 0 rows | Screenshot kedua hasil berdampingan |
| After-Mitigation | 7. Cek entri log tercatat | `SELECT * FROM audit_log WHERE aksi = 'SQL_INJECTION_ATTEMPT' ORDER BY waktu DESC;` |

> **Catatan implementasi:** MySQL native tidak otomatis mencatat percobaan injeksi ke `audit_log` — kamu perlu trigger/logic aplikasi (atau trigger SQL) yang mendeteksi pola ini dan INSERT ke `audit_log` secara eksplisit saat query dieksekusi lewat lapisan aplikasi/skrip demo.

---

### Skenario 3 — SSL/TLS Connection Enforcement & Enkripsi Data

**Prasyarat khusus:** sertifikat CA/server/client sudah jadi, `require_secure_transport=ON` aktif, data `nik_encrypted` sudah terisi.

**Bagian A — Data in transit**

| Fase | Langkah | Perintah / Aksi |
|---|---|---|
| Before-Attack | 1. Verifikasi kebijakan aktif | `SHOW VARIABLES LIKE 'require_secure_transport';` → harus `ON` |
| During-Attack | 2. Coba konek tanpa SSL | `mysql -h 127.0.0.1 -P 3300 -u app_user -p --ssl-mode=DISABLED` → harus muncul `ERROR 3159 (HY000): Connections using insecure transport are prohibited...` |
| During-Attack | 3. Cek log penolakan tercatat | `SELECT * FROM audit_log WHERE aksi = 'CONNECTION_REJECTED_NO_SSL' ORDER BY waktu DESC;` |
| After-Mitigation | 4. Konek dengan sertifikat lengkap | `mysql -h 127.0.0.1 -P 3300 -u app_user -p --ssl-ca=<ca.pem> --ssl-cert=<client-cert.pem> --ssl-key=<client-key.pem>` → harus berhasil |
| After-Mitigation | 5. Verifikasi cipher aktif | `SHOW STATUS LIKE 'Ssl_cipher';` → harus tampil `TLS_AES_256_GCM_SHA384` atau setara |

**Bagian B — Data at rest**

| Fase | Langkah | Perintah / Aksi |
|---|---|---|
| Before-Attack (baseline "tanpa enkripsi terlihat") | 6. Tampilkan kolom terenkripsi | `SELECT nama, nik_encrypted FROM pasien;` → tampil data biner tidak terbaca |
| After-Mitigation | 7. Dekripsi dengan kunci benar | `SELECT nama, AES_DECRYPT(nik_encrypted, '<kunci_demo>') AS nik_asli FROM pasien;` → tampil NIK asli |
| After-Mitigation (kontrol negatif) | 8. Dekripsi dengan kunci salah | `SELECT nama, AES_DECRYPT(nik_encrypted, '<kunci_salah>') AS gagal FROM pasien;` → harus `NULL` |

---

### Skenario 4 — Least Privilege & Privilege Escalation Prevention

**Prasyarat khusus:** tiga user (`app_user`, `read_only`, `replicator`) sudah dibuat dengan grant sesuai §1.3.

Untuk tiap user, konek dengan kredensial user tersebut, lalu jalankan operasi berikut:

**A. User `read_only`**

| Fase | Operasi | Ekspektasi |
|---|---|---|
| During-Attack | `INSERT INTO pasien (...) VALUES (...);` | `ERROR 1142` |
| During-Attack | `SELECT * FROM rekam_medis;` | `ERROR 1142` |
| During-Attack | `DROP TABLE pasien;` | `ERROR 1142` |
| Before-Attack (pembanding hak yang sah) | `SELECT * FROM pasien;` | **Berhasil** |

**B. User `app_user`**

| Fase | Operasi | Ekspektasi |
|---|---|---|
| Before-Attack (hak sah) | `INSERT INTO pasien (...) VALUES (...);` | **Berhasil** |
| During-Attack | `DROP TABLE pasien;` | `ERROR 1142` |
| During-Attack | `SELECT * FROM users;` | `ERROR 1142` |

**C. User `replicator`**

| Fase | Operasi | Ekspektasi |
|---|---|---|
| During-Attack | `SELECT * FROM pasien;` | Ditolak (tidak punya hak SELECT sama sekali) |

Setelah semua percobaan di atas, verifikasi log:
```sql
SELECT * FROM audit_log
WHERE aksi IN ('UNAUTHORIZED_INSERT','UNAUTHORIZED_DROP','UNAUTHORIZED_SELECT')
ORDER BY waktu DESC;
```

> Sama seperti Skenario 2, pencatatan ke `audit_log` untuk error 1142 tidak otomatis dari MySQL — perlu ditangani di lapisan skrip demo (tangkap error via try/catch di script, lalu INSERT manual ke `audit_log`).

---

### Skenario 5 — Audit Logging & Anomaly Detection

**Prasyarat khusus:** Skenario 1–4 sudah selesai dijalankan (skenario ini kumulatif/rekap).

| Fase | Langkah | Perintah / Aksi |
|---|---|---|
| Langkah 1 | Tampilkan seluruh isi `audit_log` | `SELECT * FROM audit_log ORDER BY waktu;` |
| Langkah 2 | Filter kategori berbahaya saja, format waktu mudah dibaca | ```sql SELECT user_id, aksi, tabel_target, DATE_FORMAT(waktu, '%Y-%m-%d %H:%i:%s') AS waktu_format, ip_address FROM audit_log WHERE aksi IN ('SQL_INJECTION_ATTEMPT','CONNECTION_REJECTED_NO_SSL','UNAUTHORIZED_INSERT','UNAUTHORIZED_DROP','UNAUTHORIZED_SELECT') ORDER BY waktu; ``` |
| Langkah 3 | Tampilkan detail lengkap termasuk `query_exec` untuk satu insiden contoh | `SELECT * FROM audit_log WHERE aksi = 'SQL_INJECTION_ATTEMPT' ORDER BY waktu DESC LIMIT 1\G` |
| Langkah 4 | Verifikasi General Query Log independen tercatat | Buka file log: `tail -n 50 <path_log_file>` (Linux/Docker) atau buka file log lewat teks editor (Windows) — cocokkan waktunya dengan entri di `audit_log` |

---

## Ringkasan Urutan Eksekusi Penuh (Sesi Demo)

Supaya video demo mengalir logis dan tidak bolak-balik reset environment:

1. **Skenario 3 dulu** (SSL/TLS) — karena setelah ini semua koneksi lanjutan otomatis memakai jalur aman
2. **Skenario 2** (SQL Injection) — pakai koneksi yang sudah TLS
3. **Skenario 4** (Least Privilege)
4. **Skenario 1** (Failover) — taruh di akhir karena mematikan Master bisa mengganggu skenario lain kalau belum selesai
5. **Skenario 5** (Audit Log) — paling akhir karena sifatnya merekap semua skenario sebelumnya

> Urutan angka di laporan (1–5) tetap ikuti Tabel 3.3 proposal; ini cuma saran **urutan eksekusi teknis** saat rekaman demo, bukan urutan penomoran laporan.
