USE klinik_db;

-- Isi tabel users
INSERT INTO users (username, password, role) VALUES
('dr_budi',   '$2b$12$dummy_hash_budi',   'dokter'),
('admin_sari', '$2b$12$dummy_hash_sari',  'admin'),
('resep_andi', '$2b$12$dummy_hash_andi',  'resepsionis');

-- Isi tabel pasien (NIK dienkripsi AES)
INSERT INTO pasien (nama, nik_encrypted, tanggal_lahir, alamat, no_telepon)
VALUES
(
    'Ahmad Fauzi',
    AES_ENCRYPT('3201234567890001', 'kunci_rahasia_klinik'),
    '1990-05-15',
    'Jl. Merdeka No. 10, Jakarta',
    '081234567890'
),
(
    'Siti Rahayu',
    AES_ENCRYPT('3209876543210002', 'kunci_rahasia_klinik'),
    '1985-08-22',
    'Jl. Sudirman No. 45, Bandung',
    '082345678901'
),
(
    'Budi Santoso',
    AES_ENCRYPT('3201122334455003', 'kunci_rahasia_klinik'),
    '1995-12-01',
    'Jl. Gatot Subroto No. 7, Surabaya',
    '083456789012'
);

-- Isi tabel rekam_medis
INSERT INTO rekam_medis (pasien_id, dokter_id, diagnosa, resep)
VALUES
(1, 1, 'Hipertensi ringan', 'Amlodipine 5mg 1x1'),
(2, 1, 'Diabetes tipe 2',   'Metformin 500mg 2x1'),
(3, 1, 'ISPA',              'Amoxicillin 500mg 3x1');