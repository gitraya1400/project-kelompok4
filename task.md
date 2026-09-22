# Task List — Database Hardening & HA Cluster (klinik_db)

Referensi: `prd.md`. Jadwal mengikuti Bab IV proposal (Minggu 8–14). Checklist per tahap sesuai Metodologi Bab III.

---

## Fase 0 — Studi Literatur & Analisis Kebutuhan (Minggu 8–9)

- [ ] Review konsep CIA Triad, OWASP Top 10, CIS Benchmark for MySQL, NIST SP 800-111
- [ ] Finalisasi 4 vektor ancaman yang diuji: SQL Injection, privilege escalation, intersepsi koneksi tanpa enkripsi, single point of failure
- [ ] Tentukan spesifikasi environment: 2 instance MySQL/MariaDB (master+slave), 1 HAProxy, dua jalur (Docker / XAMPP+Laragon)
- [ ] Tetapkan metrik keberhasilan tiap skenario (acuan §8 PRD)
- [ ] Output: dokumen analisis kebutuhan + daftar referensi

## Fase 1 — Perancangan Arsitektur & Desain Sistem (Minggu 9–10)

- [ ] Gambar topologi jaringan: Master (3306) – Slave (3307) – HAProxy (3300)
- [ ] Desain ERD: `users`, `pasien`, `rekam_medis`, `audit_log` (lihat §5 PRD)
- [ ] Tetapkan tipe kolom `nik_encrypted` (VARBINARY + AES_ENCRYPT)
- [ ] Rancang role-based access control: `app_user`, `read_only`, `replicator` + hak masing-masing
- [ ] Tetapkan kebijakan `REQUIRE SSL` untuk seluruh user
- [ ] Susun dokumen spesifikasi 5 skenario pengujian
- [ ] Output: diagram arsitektur, skema DB lengkap, dokumen spesifikasi skenario

## Fase 2 — Implementasi & Konfigurasi Environment (Minggu 10–12)

### 2.1 Jalur A — Docker
- [ ] Buat `docker-compose.yml`: service `db-master`, `db-slave`, `haproxy`
- [ ] Set `binlog_format=ROW` di kedua node
- [ ] Konfigurasi replikasi master-slave (user `replicator`, `CHANGE MASTER TO`, `START SLAVE`)
- [ ] Verifikasi `SHOW SLAVE STATUS` → `Slave_IO_Running`/`Slave_SQL_Running` = Yes

### 2.2 Jalur B — XAMPP + Laragon
- [ ] Install & konfigurasi XAMPP sebagai Master (port 3306)
- [ ] Install & konfigurasi Laragon sebagai Slave (port 3307)
- [ ] Konfigurasi replikasi Binary Log yang setara dengan Jalur A
- [ ] Pastikan file `.cnf` identik dengan Jalur A

### 2.3 HAProxy
- [ ] Konfigurasi listener port 3300 → backend Master/Slave
- [ ] Aktifkan health check interval 2 detik
- [ ] Aktifkan dashboard monitoring di port 8404
- [ ] Uji manual: matikan Master → cek HAProxy mendeteksi DOWN

### 2.4 SSL/TLS (OpenSSL)
- [ ] Generate CA lokal (self-signed)
- [ ] Generate Server Certificate + Client Certificate
- [ ] Deploy sertifikat ke Master, Slave, HAProxy, dan skrip klien
- [ ] Set `require_secure_transport=ON` di kedua server
- [ ] Uji koneksi TLS berhasil & cipher aktif terverifikasi

### 2.5 User & Hak Akses
- [ ] Buat user `app_user`, `read_only`, `replicator` sesuai rancangan least privilege
- [ ] Terapkan `GRANT`/`REVOKE` sesuai role
- [ ] Wajibkan `REQUIRE SSL` pada setiap user

### 2.6 Data & Skema
- [ ] Jalankan skrip SQL pembuatan skema (4 tabel)
- [ ] Isi data sampel sintetis (pasien, rekam_medis, users)
- [ ] Enkripsi NIK sampel dengan `AES_ENCRYPT` (catat: kunci hardcode hanya untuk demo lab)
- [ ] Aktifkan MySQL General Query Log

- [ ] Output: environment berfungsi penuh, `docker-compose.yml`/config XAMPP, skrip SQL, prosedur setup terdokumentasi

## Fase 3 — Pengujian Skenario & Evaluasi (Minggu 11–12)

Pola tiap skenario: **Before-Attack → During-Attack → After-Mitigation**, dokumentasikan via screenshot + log + video.

### 3.1 Skenario 1 — Failover & High Availability
- [ ] Buktikan kondisi normal: dashboard HAProxy UP, INSERT via 3300 → muncul di Slave (3307)
- [ ] Matikan Master (`docker stop db-master` / XAMPP Control Panel)
- [ ] SELECT via 3300 → harus tetap jalan (dialihkan ke Slave)
- [ ] INSERT via 3300 saat Master down → error informatif, bukan crash
- [ ] Hidupkan Master kembali
- [ ] Verifikasi reconnect otomatis (`SHOW SLAVE STATUS`) + data baru tereplikasi

### 3.2 Skenario 2 — SQL Injection
- [ ] Tampilkan isi tabel `pasien` (baseline)
- [ ] Jalankan query rentan (CONCAT) dengan payload `' OR '1'='1' --`
- [ ] Tampilkan `@query_rentan` sebelum eksekusi, lalu eksekusi via PREPARE/EXECUTE → buktikan data bocor
- [ ] Ulangi pada tabel `rekam_medis`
- [ ] Jalankan query yang sama via prepared statement (`?`) → buktikan 0 rows
- [ ] Verifikasi entri `SQL_INJECTION_ATTEMPT` tercatat di `audit_log`

### 3.3 Skenario 3 — SSL/TLS & Enkripsi Data
- [ ] Verifikasi `require_secure_transport=ON`
- [ ] Coba konek `--ssl-mode=DISABLED` → harus ERROR 3159, tercatat `CONNECTION_REJECTED_NO_SSL`
- [ ] Koneksi dengan sertifikat valid → berhasil, cek `SHOW STATUS LIKE 'Ssl_cipher'`
- [ ] SELECT `nik_encrypted` → tampil ciphertext
- [ ] `AES_DECRYPT` dengan kunci benar → nilai asli; kunci salah → NULL

### 3.4 Skenario 4 — Least Privilege
- [ ] `read_only`: coba INSERT `pasien`, SELECT `rekam_medis`, DROP TABLE → semua ERROR 1142; SELECT `pasien` → berhasil
- [ ] `app_user`: INSERT `pasien` → berhasil; DROP TABLE `pasien` & SELECT `users` → ERROR 1142
- [ ] `replicator`: SELECT `pasien` → ditolak
- [ ] Verifikasi kategori `UNAUTHORIZED_INSERT`/`UNAUTHORIZED_DROP`/`UNAUTHORIZED_SELECT` tercatat

### 3.5 Skenario 5 — Audit Logging & Anomaly Detection
- [ ] Tampilkan seluruh isi `audit_log` (rekap skenario 1–4)
- [ ] Query filter kategori berbahaya + format timestamp (`DATE_FORMAT`)
- [ ] Tampilkan detail `query_exec` untuk rekonstruksi forensik
- [ ] Verifikasi MySQL General Query Log aktif & mencatat independen dari `audit_log`

- [ ] Jika ada skenario gagal → analisis penyebab, perbaiki konfigurasi, uji ulang
- [ ] Output: laporan hasil pengujian + seluruh bukti eksekusi

## Fase 4 — Analisis Hasil & Kesimpulan (Minggu 12–13)

- [ ] Rangkum hasil tiap skenario terhadap kriteria sukses (PRD §8)
- [ ] Kaitkan hasil dengan CIA Triad + Accountability
- [ ] Tulis kesimpulan & rekomendasi (termasuk catatan keterbatasan: KMS untuk kunci enkripsi, dsb.)

## Fase 5 — Dokumentasi & Kompilasi Laporan (Minggu 13–14)

- [ ] Kompilasi laporan akhir (semua Bab)
- [ ] Susun diagram arsitektur & ERD final
- [ ] Susun lampiran (skrip SQL, config, screenshot, log)
- [ ] Tulis README reproduksi environment (Docker & XAMPP)

## Fase 6 — Materi Presentasi & Live Demo (Minggu 14)

- [ ] Susun slide presentasi
- [ ] Siapkan skrip live demo (urutan skenario 1→5)
- [ ] Rehearsal demo end-to-end (pastikan environment reset bersih sebelum demo)
- [ ] Siapkan rencana cadangan jika demo langsung gagal (video rekaman sebagai backup)

---

## Catatan
- Tugas utama Agam (Bab III — Metodologi): draf tahapan pelaksanaan + rencana skenario pengujian (failover & security) — sudah tercermin di Fase 0–3 di atas.
- Konsistensi Jalur A/B wajib dicek ulang di setiap fase sebelum lanjut ke fase berikutnya.
