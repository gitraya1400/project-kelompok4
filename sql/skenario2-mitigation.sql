USE klinik_db;

-- ========================================
-- SKENARIO 2C: MITIGASI DENGAN PREPARED STATEMENT
-- Payload yang SAMA, tapi pakai parameter '?'
-- ========================================

SELECT '=== MITIGASI: PREPARED STATEMENT DENGAN PARAMETER ? ===' AS info;

PREPARE stmt_aman FROM 'SELECT id, nama, tanggal_lahir FROM pasien WHERE nama = ?';
SET @payload = '\' OR \'1\'=\'1\' -- ';

SELECT @payload AS payload_yang_dicoba;

SELECT '=== HASIL EKSEKUSI (SERANGAN GAGAL) ===' AS info;
EXECUTE stmt_aman USING @payload;
DEALLOCATE PREPARE stmt_aman;
