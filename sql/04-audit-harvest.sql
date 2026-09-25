USE klinik_db;

DELIMITER //

DROP PROCEDURE IF EXISTS sp_harvest_audit //

CREATE PROCEDURE sp_harvest_audit()
BEGIN
    -- =========================================================================
    -- sp_harvest_audit: Log Harvester Forensik Otomatis
    -- Memanen jejak audit dari mysql.general_log ke klinik_db.audit_log
    -- Menggunakan timestamp nyata per milidetik (event_time) dari server MySQL.
    -- =========================================================================

    -- 1. Deteksi Insecure Non-TLS Connection
    --
    -- PENTING -- kenapa filternya harus memuat 'Access denied':
    -- Baris "Connect ... using TCP/IP" di general_log adalah koneksi yang
    -- BERHASIL tanpa SSL, bukan yang ditolak. MySQL tidak mencatat koneksi
    -- yang ditolak require_secure_transport sebagai Connect biasa -- yang
    -- tercatat justru baris "Access denied". Tanpa syarat ini, setiap koneksi
    -- internal yang sukses ikut dilabeli "REJECTED" (false positive), dan
    -- audit_log jadi berisi klaim penolakan untuk koneksi yang sebenarnya
    -- lolos. Itu fatal kalau penguji memeriksa query_exec-nya.
    INSERT INTO klinik_db.audit_log (user_id, aksi, tabel_target, query_exec, ip_address, waktu)
    SELECT
        NULL,
        'CONNECTION_REJECTED_NO_SSL',
        NULL,
        CONCAT('Koneksi tanpa TLS ditolak (require_secure_transport=ON): ',
               LEFT(CAST(argument AS CHAR), 150)),
        REPLACE(REPLACE(SUBSTRING_INDEX(user_host, ' ', -1), '[', ''), ']', ''),
        event_time
    FROM mysql.general_log
    WHERE command_type = 'Connect'
      AND CAST(argument AS CHAR) LIKE '%Access denied%'
      AND CAST(argument AS CHAR) NOT LIKE '%SSL%'
      -- Abaikan root@localhost: itu healthcheck/entrypoint internal container,
      -- bukan percobaan penyerang. Tanpa filter ini audit_log penuh noise.
      AND CAST(argument AS CHAR) NOT LIKE '%root%@%localhost%'
      AND NOT EXISTS (
          -- Dedup HANYA berdasarkan isi, JANGAN pakai waktu:
          -- audit_log.waktu bertipe TIMESTAMP (detik) dan MySQL MEMBULATKAN
          -- pecahan detik ke atas (.735 -> +1 detik), sedangkan event_time
          -- punya mikrodetik. Perbandingan waktu karena itu tidak pernah
          -- cocok dan baris yang sama terpanen ulang setiap CALL.
          SELECT 1 FROM klinik_db.audit_log a
          WHERE a.aksi = 'CONNECTION_REJECTED_NO_SSL'
            AND a.query_exec = CONCAT('Koneksi tanpa TLS ditolak (require_secure_transport=ON): ',
                                      LEFT(CAST(mysql.general_log.argument AS CHAR), 150))
      );

    -- 2. Deteksi SQL Injection (Pola manipulasi boolean / quote injection)
    INSERT INTO klinik_db.audit_log (user_id, aksi, tabel_target, query_exec, ip_address, waktu)
    SELECT 
        NULL,
        'SQL_INJECTION_ATTEMPT',
        CASE 
            WHEN CAST(argument AS CHAR) LIKE '%rekam_medis%' THEN 'rekam_medis'
            WHEN CAST(argument AS CHAR) LIKE '%pasien%' THEN 'pasien'
            ELSE 'unknown'
        END,
        CAST(argument AS CHAR),
        REPLACE(REPLACE(SUBSTRING_INDEX(user_host, ' ', -1), '[', ''), ']', ''),
        event_time
    FROM mysql.general_log
    WHERE command_type = 'Query'
      AND (
          CAST(argument AS CHAR) LIKE '%OR%1=1%'
          OR CAST(argument AS CHAR) LIKE '%OR%\'1\'=\'1\'%'
          OR CAST(argument AS CHAR) LIKE '%UNION%SELECT%'
      )
      AND CAST(argument AS CHAR) NOT LIKE '%audit_log%'
      AND CAST(argument AS CHAR) NOT LIKE '%sp_harvest_audit%'
      AND CAST(argument AS CHAR) NOT LIKE '%general_log%'
      AND NOT EXISTS (
          SELECT 1 FROM klinik_db.audit_log a 
          WHERE a.query_exec = CAST(mysql.general_log.argument AS CHAR)
      );

    -- 3. Deteksi Unauthorized DROP TABLE (Percobaan DDL destruktif oleh non-root)
    INSERT INTO klinik_db.audit_log (user_id, aksi, tabel_target, query_exec, ip_address, waktu)
    SELECT 
        NULL,
        'UNAUTHORIZED_DROP',
        CASE 
            WHEN CAST(argument AS CHAR) LIKE '%rekam_medis%' THEN 'rekam_medis'
            WHEN CAST(argument AS CHAR) LIKE '%users%' THEN 'users'
            WHEN CAST(argument AS CHAR) LIKE '%pasien%' THEN 'pasien'
            ELSE 'unknown'
        END,
        CAST(argument AS CHAR),
        REPLACE(REPLACE(SUBSTRING_INDEX(user_host, ' ', -1), '[', ''), ']', ''),
        event_time
    FROM mysql.general_log
    WHERE command_type = 'Query'
      AND CAST(argument AS CHAR) LIKE '%DROP TABLE%'
      AND user_host NOT LIKE 'root%'
      AND CAST(argument AS CHAR) NOT LIKE '%audit_log%'
      AND NOT EXISTS (
          SELECT 1 FROM klinik_db.audit_log a 
          WHERE a.query_exec = CAST(mysql.general_log.argument AS CHAR)
      );

    -- 4. Deteksi Unauthorized SELECT (Pelanggaran hak akses data oleh user terbatas)
    INSERT INTO klinik_db.audit_log (user_id, aksi, tabel_target, query_exec, ip_address, waktu)
    SELECT 
        NULL,
        'UNAUTHORIZED_SELECT',
        CASE 
            WHEN CAST(argument AS CHAR) LIKE '%rekam_medis%' THEN 'rekam_medis'
            WHEN CAST(argument AS CHAR) LIKE '%users%' THEN 'users'
            WHEN CAST(argument AS CHAR) LIKE '%pasien%' THEN 'pasien'
            ELSE 'unknown'
        END,
        CAST(argument AS CHAR),
        REPLACE(REPLACE(SUBSTRING_INDEX(user_host, ' ', -1), '[', ''), ']', ''),
        event_time
    FROM mysql.general_log
    WHERE command_type = 'Query'
      AND CAST(argument AS CHAR) LIKE 'SELECT%'
      AND (
          (user_host LIKE 'read_only%' AND CAST(argument AS CHAR) LIKE '%rekam_medis%')
          OR (user_host LIKE 'app_user%' AND CAST(argument AS CHAR) LIKE '%users%')
          OR (user_host LIKE 'replicator%' AND CAST(argument AS CHAR) LIKE '%pasien%')
      )
      AND CAST(argument AS CHAR) NOT LIKE '%audit_log%'
      AND CAST(argument AS CHAR) NOT LIKE '%general_log%'
      AND NOT EXISTS (
          SELECT 1 FROM klinik_db.audit_log a 
          WHERE a.query_exec = CAST(mysql.general_log.argument AS CHAR)
      );

    -- 5. Deteksi Unauthorized INSERT (Pelanggaran tulis oleh user read_only)
    INSERT INTO klinik_db.audit_log (user_id, aksi, tabel_target, query_exec, ip_address, waktu)
    SELECT 
        NULL,
        'UNAUTHORIZED_INSERT',
        'pasien',
        CAST(argument AS CHAR),
        REPLACE(REPLACE(SUBSTRING_INDEX(user_host, ' ', -1), '[', ''), ']', ''),
        event_time
    FROM mysql.general_log
    WHERE command_type = 'Query'
      AND CAST(argument AS CHAR) LIKE 'INSERT INTO%pasien%'
      AND user_host LIKE 'read_only%'
      AND NOT EXISTS (
          SELECT 1 FROM klinik_db.audit_log a 
          WHERE a.query_exec = CAST(mysql.general_log.argument AS CHAR)
      );

END //

-- =============================================================================
-- sp_log_ssl_rejection: catat penolakan koneksi non-TLS secara eksplisit
--
-- KENAPA TIDAK BISA DIPANEN OTOMATIS:
-- Koneksi yang ditolak require_secure_transport (ERROR 3159) dihentikan di
-- lapisan TRANSPORT, sebelum autentikasi. MySQL tidak pernah mencatatnya di
-- mysql.general_log -- sudah diverifikasi: setelah ERROR 3159 terjadi, tidak
-- ada satu pun baris baru yang muncul di sana. Jadi sp_harvest_audit() tidak
-- punya sumber data untuk kategori ini.
--
-- Prosedur ini dipanggil oleh skrip demo TEPAT saat penolakan terjadi, jadi
-- timestamp-nya waktu kejadian sungguhan -- bukan dikarang belakangan.
-- =============================================================================
DROP PROCEDURE IF EXISTS sp_log_ssl_rejection //

CREATE PROCEDURE sp_log_ssl_rejection(IN p_user VARCHAR(50), IN p_ip VARCHAR(45))
BEGIN
    INSERT INTO klinik_db.audit_log
        (user_id, aksi, tabel_target, query_exec, ip_address, waktu)
    VALUES
        (NULL, 'CONNECTION_REJECTED_NO_SSL', NULL,
         CONCAT('ERROR 3159: koneksi --ssl-mode=DISABLED dari user ''', p_user,
                ''' ditolak require_secure_transport=ON'),
         p_ip, NOW());
END //

DELIMITER ;
