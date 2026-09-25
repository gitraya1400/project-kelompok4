USE klinik_db;

-- Hapus user lama kalau ada
DROP USER IF EXISTS 'app_user'@'%';
DROP USER IF EXISTS 'read_only'@'%';
DROP USER IF EXISTS 'replicator'@'%';

-- Buat app_user (untuk aplikasi utama)
CREATE USER 'app_user'@'%' IDENTIFIED BY 'AppPass123!' 
  REQUIRE SSL
  WITH MAX_QUERIES_PER_HOUR 1000
  MAX_CONNECTIONS_PER_HOUR 100
  MAX_UPDATES_PER_HOUR 500;
GRANT SELECT, INSERT, UPDATE ON klinik_db.pasien TO 'app_user'@'%';
GRANT SELECT, INSERT, UPDATE ON klinik_db.rekam_medis TO 'app_user'@'%';
GRANT INSERT ON klinik_db.audit_log TO 'app_user'@'%';

-- Buat read_only (hanya baca tabel pasien)
CREATE USER 'read_only'@'%' IDENTIFIED BY 'ReadPass123!' 
  REQUIRE SSL
  WITH MAX_QUERIES_PER_HOUR 500
  MAX_CONNECTIONS_PER_HOUR 50
  MAX_UPDATES_PER_HOUR 250;
GRANT SELECT ON klinik_db.pasien TO 'read_only'@'%';

-- Buat replicator (untuk replikasi master-slave)
CREATE USER 'replicator'@'%' IDENTIFIED BY 'ReplPass123!'
  REQUIRE SSL
  WITH MAX_QUERIES_PER_HOUR 1000
  MAX_CONNECTIONS_PER_HOUR 100
  MAX_UPDATES_PER_HOUR 500;
GRANT REPLICATION SLAVE ON *.* TO 'replicator'@'%';

FLUSH PRIVILEGES;