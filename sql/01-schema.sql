-- Hapus database lama kalau ada
DROP DATABASE IF EXISTS klinik_db;
CREATE DATABASE klinik_db;
USE klinik_db;

-- Tabel users (dokter, admin, resepsionis)
CREATE TABLE users (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    username    VARCHAR(50) UNIQUE NOT NULL,
    password    VARCHAR(255) NOT NULL,
    role        ENUM('admin','dokter','resepsionis') NOT NULL,
    is_active   TINYINT DEFAULT 1,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel pasien
CREATE TABLE pasien (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    nama            VARCHAR(100) NOT NULL,
    nik_encrypted   VARBINARY(255),
    tanggal_lahir   DATE,
    alamat          TEXT,
    no_telepon      VARCHAR(20),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel rekam medis
CREATE TABLE rekam_medis (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    pasien_id   INT NOT NULL,
    dokter_id   INT NOT NULL,
    diagnosa    TEXT,
    resep       TEXT,
    tanggal     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pasien_id) REFERENCES pasien(id),
    FOREIGN KEY (dokter_id) REFERENCES users(id)
);

-- Tabel audit log
CREATE TABLE audit_log (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    user_id         INT,
    aksi            VARCHAR(100),
    tabel_target    VARCHAR(50),
    query_exec      TEXT,
    ip_address      VARCHAR(45),
    waktu           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);