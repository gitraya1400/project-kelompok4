USE klinik_db;

-- ========================================
-- SKENARIO 2B: SERANGAN SQL INJECTION PADA REKAM MEDIS
-- ========================================

SET @input_medis = '1 OR 1=1';
SET @query_medis = CONCAT('SELECT id, pasien_id, diagnosa, resep FROM rekam_medis WHERE pasien_id = ', @input_medis);

SELECT '=== QUERY RENTAN REKAM MEDIS ===' AS info;
SELECT @query_medis AS query_yang_dieksekusi;

SELECT '=== HASIL: SELURUH REKAM MEDIS BOCOR ===' AS info;
PREPARE stmt_medis FROM @query_medis;
EXECUTE stmt_medis;
DEALLOCATE PREPARE stmt_medis;
