USE klinik_db;

-- Hapus user lama kalau ada
DROP USER IF EXISTS 'app_user'@'%';
DROP USER IF EXISTS 'read_only'@'%';
DROP USER IF EXISTS 'replicator'@'%';

-- Buat app_user (untuk aplikasi utama)
CREATE USER 'app_user'@'%' IDENTIFIED BY 'AppPass123!';
GRANT SELECT, INSERT, UPDATE ON klinik_db.pasien TO 'app_user'@'%';
GRANT SELECT, INSERT, UPDATE ON klinik_db.rekam_medis TO 'app_user'@'%';
GRANT INSERT ON klinik_db.audit_log TO 'app_user'@'%';

-- Buat read_only (hanya baca tabel pasien)
CREATE USER 'read_only'@'%' IDENTIFIED BY 'ReadPass123!';
GRANT SELECT ON klinik_db.pasien TO 'read_only'@'%';

-- Buat replicator (untuk replikasi master-slave)
CREATE USER 'replicator'@'%' IDENTIFIED BY 'ReplPass123!';
GRANT REPLICATION SLAVE ON *.* TO 'replicator'@'%';

FLUSH PRIVILEGES;