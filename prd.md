# PRD — Database Hardening & High Availability Cluster (klinik_db)

**Mata Kuliah:** Keamanan Sistem Informasi
**Program Studi:** D-IV Komputasi Statistik, Politeknik Statistik STIS

---

## 1. Latar Belakang & Masalah

Basis data klinik menyimpan data sensitif (identitas pasien, rekam medis, resep). Dua risiko utama yang harus diatasi:

1. **Keamanan** — konfigurasi default MySQL/MariaDB rentan terhadap SQL Injection, koneksi tanpa enkripsi, dan hak akses berlebihan.
2. **Ketersediaan** — satu server sebagai *single point of failure*; jika down, seluruh layanan klinik (registrasi pasien, akses rekam medis) ikut lumpuh.

## 2. Tujuan Produk

Membangun satu arsitektur basis data yang **mengintegrasikan** hardening keamanan dan high availability, lalu **membuktikan efektivitasnya** lewat pengujian skenario yang terstruktur dan dapat direproduksi.

Tujuan turunan (selaras proposal Bab I.3):
- Menerapkan *database hardening*: SSL/TLS, enkripsi data tersimpan, *least privilege*, *audit log*.
- Membangun *High Availability Cluster* (master-slave + HAProxy) dengan *failover* otomatis.
- Menguji & mendokumentasikan lima skenario keamanan/ketersediaan.

## 3. Ruang Lingkup

**Masuk lingkup:**
- Database `klinik_db` (MySQL/MariaDB) dengan 4 tabel: `users`, `pasien`, `rekam_medis`, `audit_log`.
- Dua jalur implementasi paralel yang harus identik secara konfigurasi:
  - **Jalur A (Docker):** `db-master` + `db-slave` via Docker Compose.
  - **Jalur B (Non-Docker):** XAMPP (Master) + Laragon (Slave) di Windows.
- HAProxy sebagai satu-satunya *load balancer* (port 3300); akses langsung ke 3306/3307 dibatasi.
- Sertifikat SSL/TLS self-signed via OpenSSL (CA lokal).
- 5 skenario pengujian dengan pola Before-Attack → During-Attack → After-Mitigation.

**Di luar lingkup:**
- Deployment produksi nyata.
- Manajemen kunci enkripsi via KMS terpisah (hanya dicatat sebagai catatan/rekomendasi, tidak diimplementasikan).
- Aplikasi frontend/backend klinik yang sesungguhnya (hanya query/script demonstrasi).
- Sertifikat dari CA berbayar/publik.

## 4. Arsitektur Sistem

```
Klien / Script Demo
        │  (port 3300, wajib TLS)
        ▼
    HAProxy (load balancer + health check tiap 2 detik)
    ├── dashboard monitoring: port 8404
        │
   ┌────┴────┐
   ▼         ▼
Master     Slave
(3306)     (3307)
   └──── replikasi Binary Log (ROW format) ────┘
```

- Klien **hanya** boleh konek lewat port 3300 (HAProxy).
- Replikasi: `binlog_format=ROW` untuk konsistensi level baris.
- Health check HAProxy: interval 2 detik; failover otomatis ke Slave saat Master down.

## 5. Skema Data

| Tabel | Kolom Kunci | Catatan Keamanan |
|---|---|---|
| `users` | id, username, password, role (admin/dokter/resepsionis), is_active | password wajib hash bcrypt |
| `pasien` | id, nama, **nik_encrypted** (VARBINARY, AES_ENCRYPT), tanggal_lahir, alamat, no_telepon | NIK terenkripsi (data at rest) |
| `rekam_medis` | id, pasien_id (FK), dokter_id (FK), diagnosa, resep, tanggal | akses dibatasi role |
| `audit_log` | id, user_id (FK), aksi, tabel_target, query_exec, ip_address, waktu | mencatat semua aktivitas mencurigakan |

## 6. Functional Requirements

### FR-1 Database Hardening
- FR-1.1: Semua koneksi wajib TLS (`REQUIRE SSL`, `require_secure_transport=ON`); koneksi non-TLS ditolak (ERROR 3159).
- FR-1.2: Kolom `nik_encrypted` dienkripsi dengan `AES_ENCRYPT`; dekripsi hanya via `AES_DECRYPT` dengan kunci benar (kunci salah → NULL).
- FR-1.3: Role-based access control minimal 3 user:
  - `app_user`: SELECT/INSERT/UPDATE pada tabel operasional.
  - `read_only`: SELECT hanya pada `pasien`.
  - `replicator`: hanya `REPLICATION SLAVE`, tanpa akses data.
- FR-1.4: Semua query aplikasi memakai *prepared statement* (parameter `?`), bukan konkatenasi string.
- FR-1.5: Setiap aktivitas mencurigakan (percobaan injeksi, koneksi ditolak, akses tak berwenang) tercatat di `audit_log` dengan kategori standar (lihat §7).
- FR-1.6: MySQL General Query Log aktif sebagai lapisan audit kedua yang independen (tidak bisa dibypass user biasa).

### FR-2 High Availability
- FR-2.1: Replikasi Master → Slave berjalan real-time (binlog ROW).
- FR-2.2: HAProxy mengarahkan seluruh trafik klien lewat port 3300 dan melakukan health check tiap 2 detik.
- FR-2.3: Saat Master down, Slave tetap melayani SELECT; operasi tulis menghasilkan pesan error informatif (bukan crash).
- FR-2.4: Tidak ada data yang sudah ter-commit hilang saat Master down.
- FR-2.5: Saat Master pulih, replikasi reconnect otomatis (`Slave_IO_Running` & `Slave_SQL_Running` = Yes) tanpa konfigurasi ulang manual.

### FR-3 Dual Deployment
- FR-3.1: Konfigurasi Jalur A (Docker Compose) dan Jalur B (XAMPP+Laragon) menghasilkan perilaku dan hasil pengujian yang identik.
- FR-3.2: File `.cnf` dan sertifikat SSL sama persis di kedua jalur.

## 7. Kategori Audit Log (wajib konsisten)

| Kategori | Dipicu oleh |
|---|---|
| `SQL_INJECTION_ATTEMPT` | Skenario 2 |
| `CONNECTION_REJECTED_NO_SSL` | Skenario 3 |
| `UNAUTHORIZED_INSERT` / `UNAUTHORIZED_DROP` / `UNAUTHORIZED_SELECT` | Skenario 4 |

## 8. Kriteria Penerimaan (Acceptance Criteria) per Skenario

| # | Skenario | Aspek CIA | Kriteria Sukses |
|---|---|---|---|
| 1 | Failover & HA | Availability | Slave tetap melayani SELECT saat Master mati; INSERT gagal dengan error informatif; tidak ada data commit yang hilang; reconnect otomatis setelah Master pulih |
| 2 | SQL Injection | Confidentiality, Integrity | Query rentan (tanpa prepared statement) bocor semua data; query dengan prepared statement → 0 rows untuk input serangan sama |
| 3 | SSL/TLS & Enkripsi | Confidentiality | Koneksi non-SSL ditolak (ERROR 3159); cipher aktif (`TLS_AES_256_GCM_SHA384`) terverifikasi; `nik_encrypted` tampil sebagai ciphertext; kunci salah → NULL |
| 4 | Least Privilege | Confidentiality, Integrity | Operasi di luar hak → ERROR 1142; operasi dalam hak → berhasil; semua penolakan tercatat di `audit_log` |
| 5 | Audit & Accountability | Accountability, Non-repudiation | Semua percobaan skenario 1–4 muncul lengkap (timestamp, aksi, tabel, query, IP) di `audit_log` dan General Query Log |

## 9. Non-Functional Requirements

- **Reproducibility:** seluruh environment harus bisa dijalankan ulang dari `docker-compose.yml`/config XAMPP + script SQL oleh anggota lain.
- **Dokumentasi bukti:** setiap skenario didokumentasikan via screenshot terminal, log sistem, dan video demonstrasi.
- **Portabilitas:** environment berjalan lokal, tidak bergantung koneksi eksternal.
- **Keterbatasan yang harus dicatat eksplisit di laporan:** kunci AES pada demo ditulis langsung di script SQL — di produksi nyata harus dikelola lewat environment variable/KMS terpisah.

## 10. Tools & Stack

| Komponen | Tool |
|---|---|
| RDBMS | MySQL / MariaDB |
| Load Balancer | HAProxy |
| Kontainerisasi (Jalur A) | Docker + Docker Compose |
| Local server (Jalur B) | XAMPP (Master), Laragon (Slave) |
| Kriptografi/TLS | OpenSSL (CA self-signed) |

## 11. Risiko & Mitigasi

| Risiko | Mitigasi |
|---|---|
| Konfigurasi Jalur A & B tidak identik → hasil uji tidak sebanding | Gunakan file `.cnf` dan sertifikat yang sama persis, verifikasi ulang sebelum testing |
| Replikasi gagal reconnect otomatis | Uji ulang skenario 1 berkali-kali, cek parameter `binlog_format` dan kredensial `replicator` |
| Skenario tidak menghasilkan output sesuai ekspektasi | Analisis penyebab & sesuaikan konfigurasi sebelum lanjut (sesuai metodologi Tahap 4) |
