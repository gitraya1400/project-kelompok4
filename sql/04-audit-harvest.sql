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

    -- 1. Deteksi Insecure Non-TLS Connection (Connect TCP/IP tanpa SSL)
    INSERT INTO klinik_db.audit_log (user_id, aksi, tabel_target, query_exec, ip_address, waktu)
    SELECT 
        NULL,
        'CONNECTION_REJECTED_NO_SSL',
        NULL,
        'Insecure connection attempt (TCP/IP without SSL/TLS) rejected by require_secure_transport=ON',
        REPLACE(REPLACE(SUBSTRING_INDEX(user_host, ' ', -1), '[', ''), ']', ''),
        event_time
    FROM mysql.general_log
    WHERE command_type = 'Connect'
      AND CAST(argument AS CHAR) LIKE '%using TCP/IP%'
      AND CAST(argument AS CHAR) NOT LIKE '%SSL%'
      AND NOT EXISTS (
          SELECT 1 FROM klinik_db.audit_log a 
          WHERE a.aksi = 'CONNECTION_REJECTED_NO_SSL'
            AND a.waktu = mysql.general_log.event_time
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
            AND a.waktu = mysql.general_log.event_time
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
            AND a.waktu = mysql.general_log.event_time
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
            AND a.waktu = mysql.general_log.event_time
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
            AND a.waktu = mysql.general_log.event_time
      );

END //

DELIMITER ;
