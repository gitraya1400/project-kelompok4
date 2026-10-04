# -*- coding: utf-8 -*-
"""BAB IV — Hasil Implementasi dan Pengujian."""
from docx.enum.text import WD_ALIGN_PARAGRAPH


def bab4(doc, H):
    H.judul_bab(doc, "BAB IV  HASIL IMPLEMENTASI DAN PENGUJIAN")

    # ---------------- IV.1 ----------------
    H.sub(doc, "4.1  Implementasi Pengamanan")
    H.par(doc, "Subbab ini menguraikan lima kontrol keamanan yang diterapkan beserta bukti "
          "kondisi sebelum dan sesudah penerapan. Seluruh nilai konfigurasi diverifikasi langsung "
          "pada server yang berjalan, bukan dikutip dari berkas konfigurasi, karena sebagian "
          "berkas konfigurasi terbukti tidak termuat sebagaimana diuraikan pada Temuan 3 "
          "subbab 4.2.")

    H.tabel(doc,
        ["Variabel", "Sebelum Hardening", "Sesudah Hardening", "Acuan"],
        [
            ["require_secure_transport", "OFF", "ON", "CIS MySQL 6.2; OWASP A02:2021"],
            ["have_ssl", "DISABLED", "YES", "CIS MySQL 6.2"],
            ["ssl_ca", "ca.pem (bawaan MySQL)", "/etc/mysql/certs/ca.pem (CA proyek)",
             "NIST SP 800-52"],
            ["general_log", "OFF", "ON", "ISO 27001 A.8.15 Logging"],
            ["log_output", "FILE", "FILE,TABLE", "ISO 27001 A.8.15"],
            ["binlog_format", "(tidak diatur)", "ROW", "CIS MySQL 7.x"],
            ["read_only (slave)", "OFF", "ON", "Integritas replikasi"],
            ["super_read_only (slave)", "OFF", "ON", "Integritas replikasi"],
        ],
        caption="Tabel 4.1 Perbandingan Konfigurasi Sebelum dan Sesudah Hardening")

    H.par(doc, "Verifikasi kondisi akhir dilakukan dengan perintah berikut, dan keluarannya "
          "disalin apa adanya:")
    H.kode(doc,
        "mysql> SHOW VARIABLES WHERE Variable_name IN\n"
        "       ('require_secure_transport','have_ssl','general_log',\n"
        "        'log_output','ssl_ca','binlog_format');\n"
        "+--------------------------+----------------------------+\n"
        "| Variable_name            | Value                      |\n"
        "+--------------------------+----------------------------+\n"
        "| binlog_format            | ROW                        |\n"
        "| general_log              | ON                         |\n"
        "| have_ssl                 | YES                        |\n"
        "| log_output               | FILE,TABLE                 |\n"
        "| require_secure_transport | ON                         |\n"
        "| ssl_ca                   | /etc/mysql/certs/ca.pem    |\n"
        "+--------------------------+----------------------------+")

    H.sub(doc, "4.1.1  Enkripsi Transport dan Penyimpanan", 3)
    H.par(doc, "Rantai sertifikat dibangun dengan OpenSSL: Certificate Authority lokal "
          "menandatangani sertifikat server dan sertifikat klien. Sertifikat server memuat "
          "Subject Alternative Name untuk db-master, db-slave, localhost, dan 127.0.0.1 agar "
          "verifikasi identitas dapat dilakukan pada seluruh titik akses.")
    H.par(doc, "Pada sisi penyimpanan, kolom nik_encrypted bertipe VARBINARY dan diisi melalui "
          "fungsi AES_ENCRYPT. Dengan demikian nomor induk kependudukan tidak pernah tersimpan "
          "dalam bentuk teks terbuka pada media penyimpanan.")

    H.sub(doc, "4.1.2  Kontrol Akses Berbasis Peran", 3)
    H.par(doc, "Tiga akun dibuat dengan hak akses minimum sesuai Tabel 3.3. Seluruh akun "
          "diwajibkan memakai koneksi terenkripsi melalui klausa REQUIRE SSL dan dibatasi laju "
          "kuerinya. Cuplikan konfigurasi:")
    H.kode(doc,
        "CREATE USER 'read_only'@'%' IDENTIFIED BY 'ReadPass123!'\n"
        "  REQUIRE SSL\n"
        "  WITH MAX_QUERIES_PER_HOUR 500\n"
        "       MAX_CONNECTIONS_PER_HOUR 50\n"
        "       MAX_UPDATES_PER_HOUR 250;\n"
        "GRANT SELECT ON klinik_db.pasien TO 'read_only'@'%';")

    H.sub(doc, "4.1.3  Pencatatan Audit", 3)
    H.par(doc, "Audit diterapkan dalam dua lapis. Lapis pertama adalah general query log bawaan "
          "MySQL yang diarahkan ke tabel mysql.general_log. Lapis kedua adalah tabel audit_log "
          "yang diisi prosedur tersimpan sp_harvest_audit dengan memanen entri mencurigakan dari "
          "lapis pertama.")
    H.par(doc, "Pendekatan pemanenan dipilih setelah dua alternatif lain terbukti tidak dapat "
          "diterapkan. Trigger tidak dapat digunakan karena pernyataan yang ditolak pada lapisan "
          "privilege dihentikan sebelum dieksekusi sehingga tidak ada trigger yang terpicu. "
          "Pencatatan mandiri oleh akun penyerang juga mustahil karena read_only dan replicator "
          "tidak memiliki hak INSERT pada audit_log. Konsekuensinya, kontrol audit pada proyek "
          "ini bersifat detektif untuk keperluan forensik, bukan preventif. Pencegahan dilakukan "
          "oleh kontrol GRANT dan TLS.")

    H.sub(doc, "4.1.4  Replikasi dan High Availability", 3)
    H.par(doc, "Replikasi menggunakan Global Transaction Identifier agar tidak bergantung pada "
          "penyalinan koordinat berkas binlog secara manual. Kanal replikasi dienkripsi melalui "
          "SOURCE_SSL=1. Hasil verifikasi:")
    H.kode(doc,
        "mysql> SHOW REPLICA STATUS\\G\n"
        "           Replica_IO_Running: Yes\n"
        "          Replica_SQL_Running: Yes\n"
        "           Source_SSL_Allowed: Yes\n"
        "        Seconds_Behind_Source: 0")

    # ---------------- IV.2 ----------------
    H.sub(doc, "4.2  Hasil Pengujian dan Analisis Kerentanan")
    H.par(doc, "Pengujian menghasilkan lima temuan kerentanan. Tiga temuan pertama merupakan "
          "kerentanan pada sistem target yang menjadi sasaran pengujian, sedangkan dua temuan "
          "terakhir ditemukan pada perkakas pendukung selama proses verifikasi. Seluruh temuan "
          "dinilai menggunakan CVSS v3.1 dan telah diperbaiki serta diuji ulang.")

    H.tabel(doc,
        ["ID", "Temuan", "CVSS v3.1", "Tingkat"],
        [
            ["T-01", "Kueri rentan SQL injection pada tabel pasien dan rekam_medis",
             "9.1 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)", "Critical"],
            ["T-02", "Koneksi tanpa enkripsi diterima server",
             "7.4 (AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)", "High"],
            ["T-03", "Berkas konfigurasi .cnf diabaikan MySQL sehingga kontrol tidak aktif",
             "8.6 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L)", "High"],
            ["T-04", "Entri audit palsu: koneksi berhasil dicatat sebagai koneksi ditolak",
             "5.3 (AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)", "Medium"],
            ["T-05", "Aplikasi peraga melaporkan status penolakan walau koneksi berhasil",
             "4.3 (AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)", "Medium"],
        ],
        caption="Tabel 4.2 Ringkasan Temuan Kerentanan dan Tingkat Risiko")

    # --- T-01 ---
    H.sub(doc, "4.2.1  T-01 SQL Injection (Critical, CVSS 9.1)", 3)
    H.par(doc, "Kondisi sebelum mitigasi. Kueri dirakit dengan menyambung masukan pengguna "
          "langsung ke string SQL menggunakan CONCAT. Payload berikut dieksekusi:")
    H.kode(doc,
        "SET @nama_input = '\\' OR \\'1\\'=\\'1\\' -- ';\n"
        "SET @query_rentan = CONCAT(\n"
        "  'SELECT id, nama, tanggal_lahir FROM pasien WHERE nama = \\'',\n"
        "  @nama_input, '\\'');\n"
        "PREPARE stmt_rentan FROM @query_rentan;\n"
        "EXECUTE stmt_rentan;")
    H.par(doc, "Hasil: seluruh baris tabel pasien terekspos meskipun nama yang dicari tidak ada. "
          "Varian numerik dengan payload 1 OR 1=1 pada tabel rekam_medis juga membocorkan seluruh "
          "diagnosa dan resep tanpa memerlukan tanda kutip sama sekali.")
    H.par(doc, "Akar penyebab. Tidak adanya pemisahan antara struktur kueri dan data masukan. "
          "Tanda kutip pada payload menutup kutip pembuka, klausa OR membentuk tautologi yang "
          "selalu bernilai benar, dan tanda komentar ganda menonaktifkan sisa kueri.")
    H.par(doc, "Perbaikan. Seluruh kueri diubah menggunakan prepared statement dengan parameter "
          "penanda tanya:")
    H.kode(doc,
        "PREPARE stmt_aman FROM\n"
        "  'SELECT id, nama, tanggal_lahir FROM pasien WHERE nama = ?';\n"
        "SET @payload = '\\' OR \\'1\\'=\\'1\\' -- ';\n"
        "EXECUTE stmt_aman USING @payload;")
    H.par(doc, "Hasil uji ulang. Payload identik mengembalikan Empty set, yaitu nol baris. "
          "Struktur kueri dikompilasi server sebelum data masuk, sehingga payload diperlakukan "
          "sebagai satu string literal dan dicari sebagai nama pasien. Tidak ada pasien dengan "
          "nama tersebut, maka tidak ada baris yang dikembalikan. Payload tidak pernah dievaluasi "
          "sebagai perintah SQL.")

    # --- T-02 ---
    H.sub(doc, "4.2.2  T-02 Koneksi Tanpa Enkripsi (High, CVSS 7.4)", 3)
    H.par(doc, "Kondisi sebelum mitigasi. Variabel require_secure_transport bernilai OFF "
          "sehingga koneksi tanpa enkripsi diterima server. Lalu lintas termasuk kredensial dan "
          "isi data melintas dalam bentuk terbuka dan rentan terhadap intersepsi.")
    H.par(doc, "Akar penyebab. Nilai bawaan MySQL tidak mewajibkan enkripsi. Sertifikat telah "
          "tersedia pada direktori proyek namun belum dipasang ke dalam container dan belum "
          "ditunjuk oleh parameter server.")
    H.par(doc, "Perbaikan. Direktori sertifikat dipasang ke kedua node, parameter ssl-ca, "
          "ssl-cert, dan ssl-key ditunjuk ke sertifikat proyek, kemudian require_secure_transport "
          "diaktifkan. Penegakan dilakukan setelah inisialisasi selesai karena alasan teknis yang "
          "diuraikan pada Temuan T-03.")
    H.par(doc, "Hasil uji ulang. Koneksi tanpa enkripsi ditolak, sedangkan koneksi bersertifikat "
          "berhasil dengan cipher terkonfirmasi:")
    H.kode(doc,
        "$ mysql -h 127.0.0.1 -u tls_demo -p --ssl-mode=DISABLED -e \"SELECT 1;\"\n"
        "ERROR 3159 (HY000): Connections using insecure transport are prohibited\n"
        "while --require_secure_transport=ON.\n"
        "\n"
        "$ mysql -h 127.0.0.1 -u app_user -p --ssl-ca=ca.pem --ssl-mode=VERIFY_CA \\\n"
        "        -e \"SHOW STATUS LIKE 'Ssl_cipher';\"\n"
        "+---------------+------------------------+\n"
        "| Variable_name | Value                  |\n"
        "+---------------+------------------------+\n"
        "| Ssl_cipher    | TLS_AES_256_GCM_SHA384 |\n"
        "+---------------+------------------------+")
    H.par(doc, "Catatan teknis. Akun app_user menggunakan plugin autentikasi "
          "caching_sha2_password yang menolak koneksi tanpa enkripsi lebih dahulu dengan galat "
          "2061, yaitu sebelum kebijakan require_secure_transport sempat dievaluasi. Galat "
          "tersebut benar namun berasal dari lapisan autentikasi, bukan dari kebijakan transport. "
          "Agar pembuktian tepat sasaran, pengujian menggunakan akun tls_demo dengan plugin "
          "mysql_native_password sehingga penolakan murni berasal dari kebijakan TLS dan "
          "menghasilkan galat 3159.")

    # --- T-03 ---
    H.sub(doc, "4.2.3  T-03 Berkas Konfigurasi Diabaikan MySQL (High, CVSS 8.6)", 3)
    H.par(doc, "Temuan ini merupakan kerentanan paling berbahaya pada proyek karena bersifat "
          "senyap: konfigurasi keamanan tampak sudah diterapkan, padahal tidak aktif sama sekali.")
    H.par(doc, "Kondisi sebelum mitigasi. Berkas config/mysql-master.cnf dan mysql-slave.cnf "
          "dipasang ke dalam container. Bind mount pada Windows menyajikan berkas dengan izin "
          "0777, dan MySQL menolak memuat berkas konfigurasi yang dapat ditulis semua pengguna:")
    H.kode(doc,
        "mysqld: [Warning] World-writable config file\n"
        "'/etc/mysql/conf.d/master.cnf' is ignored.")
    H.par(doc, "Verifikasi dampak dilakukan dengan membandingkan nilai yang tertulis pada berkas "
          "terhadap nilai efektif pada server:")
    H.tabel(doc,
        ["Variabel", "Nilai di berkas .cnf", "Nilai efektif di server", "Dampak"],
        [
            ["general_log", "1", "OFF", "Seluruh lapis audit tidak aktif"],
            ["binlog_do_db", "klinik_db", "(kosong)", "Filter replikasi tidak berlaku"],
            ["log_bin_basename", "/var/log/mysql/mysql-bin", "/var/lib/mysql/binlog",
             "Lokasi binlog berbeda dari rancangan"],
            ["log_output", "FILE,TABLE", "FILE", "Tabel mysql.general_log selalu kosong"],
        ],
        caption="Tabel 4.3 Dampak Berkas Konfigurasi yang Diabaikan")
    H.par(doc, "Akar penyebab. Mekanisme keamanan MySQL yang menolak berkas konfigurasi "
          "world-writable berinteraksi dengan karakteristik bind mount Docker pada Windows yang "
          "selalu menyajikan izin 0777. Penambahan opsi read-only pada mount tidak menyelesaikan "
          "masalah karena izin yang terlihat tetap 0777.")
    H.par(doc, "Perbaikan. Seluruh parameter dipindahkan ke direktif command pada "
          "docker-compose.yml sehingga dibaca langsung sebagai argumen proses, bukan melalui "
          "berkas konfigurasi. Kedua berkas .cnf dipertahankan hanya sebagai dokumentasi.")
    H.par(doc, "Hasil uji ulang. Jumlah peringatan world-writable pada log menjadi nol dan "
          "seluruh variabel bernilai sesuai rancangan sebagaimana ditunjukkan Tabel 4.1.")
    H.par(doc, "Temuan turunan. Upaya menempatkan require_secure_transport pada direktif command "
          "justru menyebabkan inisialisasi macet permanen. Pada pembuatan container pertama, "
          "entrypoint MySQL menjalankan server sementara lalu menyambung melalui soket tanpa "
          "enkripsi untuk memuat berkas SQL awal. Ketika TLS sudah diwajibkan sejak proses boot, "
          "koneksi internal tersebut ditolak dan proses menggantung; container tampak berjalan "
          "namun server tidak pernah siap menerima koneksi. Kondisi ini bertahan lebih dari enam "
          "menit tanpa kemajuan sebelum dihentikan. Solusinya adalah memasang sertifikat sejak "
          "boot namun menunda penegakan kebijakan sampai kedua node siap, melalui berkas "
          "/etc/mysql/conf.d/zz-tls.cnf dengan izin 0644 agar setelan bertahan melewati restart "
          "pada skenario failover.")

    # --- T-04 ---
    H.sub(doc, "4.2.4  T-04 Entri Audit Palsu (Medium, CVSS 5.3)", 3)
    H.par(doc, "Kondisi sebelum mitigasi. Prosedur sp_harvest_audit memanen baris berpola "
          "Connect menggunakan TCP/IP dari general log dan melabelinya sebagai "
          "CONNECTION_REJECTED_NO_SSL. Verifikasi menunjukkan baris tersebut justru merupakan "
          "koneksi yang berhasil tanpa enkripsi, bukan koneksi yang ditolak. Tercatat delapan "
          "entri penolakan palsu, sebagian berasal dari health check internal container.")
    H.par(doc, "Akar penyebab. Kekeliruan asumsi mengenai perilaku pencatatan MySQL. Koneksi yang "
          "ditolak kebijakan transport tidak dicatat sebagai entri Connect biasa. Verifikasi "
          "lanjutan membuktikan penolakan dengan galat 3159 tidak meninggalkan jejak apa pun pada "
          "general log karena dihentikan pada lapisan transport sebelum autentikasi.")
    H.par(doc, "Dampak. Tabel audit berisi klaim penolakan atas koneksi yang sebenarnya berhasil. "
          "Pada konteks forensik, kekeliruan semacam ini berpotensi menyesatkan analisis insiden.")
    H.par(doc, "Perbaikan. Dua langkah diterapkan. Pertama, kriteria pemanenan dipersempit "
          "sehingga hanya entri yang memuat frasa Access denied yang dicatat, disertai penyaringan "
          "entri root@localhost yang berasal dari proses internal. Kedua, karena penolakan TLS "
          "memang tidak terekam, ditambahkan prosedur sp_log_ssl_rejection yang dipanggil tepat "
          "pada saat penolakan terjadi sehingga stempel waktunya merupakan waktu kejadian "
          "sesungguhnya.")
    H.par(doc, "Temuan turunan. Pengujian idempotensi mengungkap bahwa pemanggilan berulang "
          "prosedur menggandakan baris, dari 13 menjadi 22 lalu 31. Penyebabnya adalah kolom "
          "waktu bertipe TIMESTAMP berpresisi detik sedangkan event_time berpresisi mikrodetik, "
          "dan MySQL membulatkan pecahan detik ke atas saat penyimpanan sementara fungsi "
          "pembanding memotongnya. Akibatnya pemeriksaan duplikat tidak pernah menemukan "
          "kecocokan. Perbaikan dilakukan dengan membandingkan isi kueri saja. Hasil uji ulang: "
          "tiga pemanggilan berturut-turut tetap menghasilkan 13 baris.")

    # --- T-05 ---
    H.sub(doc, "4.2.5  T-05 Pelaporan Status Keliru pada Aplikasi Peraga (Medium, CVSS 4.3)", 3)
    H.par(doc, "Kondisi sebelum mitigasi. Endpoint pengujian TLS pada aplikasi peraga selalu "
          "menampilkan status penolakan, termasuk ketika koneksi sebenarnya berhasil. Reproduksi "
          "menunjukkan proses anak mengembalikan kode keluar 0 dengan keluaran standar berisi "
          "hasil kueri, namun penyaring membuang satu-satunya baris galat sehingga menyisakan "
          "teks kosong, lalu label penolakan tetap dicetak karena ditulis secara tetap.")
    H.par(doc, "Dampak. Aplikasi peraga menampilkan klaim keamanan yang tidak sesuai kenyataan. "
          "Pada konteks demonstrasi akademik, hal ini berisiko menyesatkan penilai.")
    H.par(doc, "Perbaikan. Status ditentukan dari kode keluar dan isi pesan galat. Kode keluar 0 "
          "dilaporkan sebagai koneksi berhasil disertai penjelasan penyebab, galat 3159 "
          "dilaporkan sebagai penolakan oleh kebijakan TLS, dan galat lain dilaporkan sebagai "
          "penolakan dari lapisan autentikasi. Fase mitigasi pada panel SQL injection yang semula "
          "menetapkan nol baris secara tetap juga diubah agar benar-benar menguji ke basis data.")
    H.par(doc, "Hasil uji ulang. Dengan require_secure_transport bernilai OFF, endpoint "
          "melaporkan koneksi berhasil beserta saran perbaikan. Setelah kebijakan diaktifkan, "
          "endpoint melaporkan penolakan dengan galat 3159.")

    # ---------------- IV.3 ----------------
    H.sub(doc, "4.3  Analisis Ancaman dan Exploit")
    H.par(doc, "Sesuai ketentuan, subbab ini menganalisis satu sampel ancaman yang relevan dengan "
          "topik keamanan basis data. Sampel yang dipilih adalah exploit SQL injection berbasis "
          "tautologi, bukan sampel malware biner. Pemilihan ini didasarkan pada tiga pertimbangan: "
          "relevansi langsung dengan vektor serangan utama pada basis data, ketersediaan sampel "
          "yang dapat dianalisis secara utuh, dan kesesuaian dengan Rules of Engagement yang "
          "melarang penggunaan sampel malware biner pada laboratorium ini.")

    H.sub(doc, "4.3.1  Analisis Statis", 3)
    H.par(doc, "Analisis statis dilakukan tanpa mengeksekusi sampel. Nilai hash berikut dihitung "
          "pada berkas sampel dan dapat diverifikasi ulang oleh penilai:")
    H.tabel(doc,
        ["Berkas Sampel", "SHA-256", "MD5", "Ukuran"],
        [
            ["skenario2-attack.sql",
             "73d4d9cae919de774f2b6c1dd1d06eac2b774f0a4520435b48f83f5e64d4c433",
             "bf03ce2b67d8f792fdc6d5900096c316", "764 byte"],
            ["skenario2-attack-medis.sql",
             "d7db7ffa2a1213ff106c1b0a3bb879d17008451837a381f409a5d3f182ef0eb3",
             "ab243e795b9c060170995c47f2d0eaa3", "573 byte"],
            ["skenario2-mitigation.sql",
             "df8b83c70a7f408f5f42c89e5da22b4d497ec5b144611547431cba3bf88e9d0f",
             "bb5c256236ce5cc301a6b1b527067063", "583 byte"],
        ],
        caption="Tabel 4.4 Nilai Hash Sampel Exploit")
    H.par(doc, "Pembedahan struktur payload menghasilkan empat komponen fungsional:")
    H.tabel(doc,
        ["Komponen", "Potongan", "Fungsi"],
        [
            ["Pemutus konteks", "' (kutip tunggal)",
             "Menutup kutip pembuka pada kueri yang dirakit, memindahkan posisi parser dari "
             "konteks data ke konteks perintah"],
            ["Operator logika", "OR", "Menambahkan kondisi alternatif pada klausa WHERE"],
            ["Tautologi", "'1'='1'",
             "Pernyataan yang selalu bernilai benar sehingga klausa WHERE tidak lagi menyaring"],
            ["Penetral sisa kueri", "-- (komentar ganda)",
             "Menonaktifkan sisa kueri asli, termasuk kutip penutup yang menjadi yatim"],
        ],
        caption="Tabel 4.5 Analisis Statis Struktur Payload")
    H.par(doc, "Varian numerik pada rekam_medis menggunakan payload 1 OR 1=1 tanpa komponen "
          "pemutup konteks karena kolom sasaran bertipe angka dan tidak memerlukan tanda kutip. "
          "Varian ini membuktikan bahwa penyaringan yang hanya melakukan escaping terhadap tanda "
          "kutip tidak memadai sebagai mitigasi.")

    H.sub(doc, "4.3.2  Analisis Dinamis", 3)
    H.par(doc, "Analisis dinamis dilakukan dengan mengeksekusi sampel pada laboratorium terisolasi "
          "dbnet, kemudian mengamati perubahan perilaku sistem. Tabel 4.6 menyajikan hasil "
          "pengamatan.")
    H.tabel(doc,
        ["Pengamatan", "Kondisi Rentan", "Kondisi Termitigasi"],
        [
            ["Baris dikembalikan", "Seluruh baris tabel", "Nol baris"],
            ["Kolom terekspos", "id, nama, tanggal_lahir, alamat, no_telepon", "Tidak ada"],
            ["Jejak pada general log", "Kueri terakit lengkap dengan payload",
             "Pernyataan PREPARE dan nilai parameter terpisah"],
            ["Entri audit_log", "SQL_INJECTION_ATTEMPT", "SQL_INJECTION_ATTEMPT"],
            ["Perubahan data", "Tidak ada (operasi hanya baca)", "Tidak ada"],
        ],
        caption="Tabel 4.6 Hasil Analisis Dinamis Sampel Exploit")
    H.par(doc, "Perilaku penting yang teramati: pada kondisi termitigasi, general log mencatat "
          "struktur kueri dan nilai parameter sebagai dua entri terpisah. Pemisahan inilah bukti "
          "mekanis bahwa payload tidak pernah masuk ke tahap kompilasi kueri.")

    H.sub(doc, "4.3.3  Indicators of Compromise", 3)
    H.par(doc, "Indikator berikut diturunkan dari jejak nyata pada general log dan audit_log, "
          "dan dapat dipakai sebagai aturan deteksi:")
    H.tabel(doc,
        ["Jenis", "Indikator", "Sumber Deteksi"],
        [
            ["Pola kueri", "OR '1'='1' pada parameter masukan", "mysql.general_log argument"],
            ["Pola kueri", "OR 1=1 pada kolom numerik", "mysql.general_log argument"],
            ["Pola kueri", "UNION SELECT di luar kueri aplikasi yang sah",
             "mysql.general_log argument"],
            ["Pola kueri", "Tanda komentar -- atau # pada akhir nilai masukan",
             "mysql.general_log argument"],
            ["Entri audit", "aksi bernilai SQL_INJECTION_ATTEMPT", "klinik_db.audit_log"],
            ["Anomali volume", "Satu kueri SELECT mengembalikan seluruh baris tabel",
             "Pemantauan rows_sent"],
            ["Hash berkas", "SHA-256 pada Tabel 4.4", "Pemindaian integritas berkas"],
        ],
        caption="Tabel 4.7 Indicators of Compromise")

    H.sub(doc, "4.3.4  Pemetaan MITRE ATT&CK", 3)
    H.tabel(doc,
        ["Taktik", "Teknik", "ID", "Keterkaitan dengan Sampel"],
        [
            ["Initial Access", "Exploit Public-Facing Application", "T1190",
             "Payload disisipkan melalui parameter masukan aplikasi yang terhubung ke basis data"],
            ["Collection", "Data from Information Repositories", "T1213",
             "Seluruh isi tabel pasien dan rekam_medis diekstraksi dalam satu permintaan"],
            ["Credential Access", "Unsecured Credentials", "T1552",
             "Upaya lanjutan membaca tabel users yang memuat hash kata sandi"],
            ["Defense Evasion", "Impair Defenses: Disable or Modify Tools", "T1562",
             "Penggunaan tanda komentar untuk menonaktifkan sisa logika kueri asli"],
        ],
        caption="Tabel 4.8 Pemetaan Sampel ke MITRE ATT&CK")

    H.sub(doc, "4.3.5  Kemampuan Deteksi dan Pencegahan Solusi", 3)
    H.tabel(doc,
        ["Kontrol", "Fungsi terhadap Sampel", "Sifat", "Hasil Pengujian"],
        [
            ["Prepared statement", "Mencegah payload dievaluasi sebagai perintah SQL",
             "Preventif", "Berhasil: nol baris dikembalikan"],
            ["Least privilege (GRANT)",
             "Membatasi cakupan data yang dapat diekstraksi walau injeksi berhasil",
             "Preventif", "Berhasil: akses ke tabel users ditolak galat 1142"],
            ["Audit log harvesting", "Merekam percobaan untuk kebutuhan forensik",
             "Detektif", "Berhasil: tercatat sebagai SQL_INJECTION_ATTEMPT"],
            ["TLS", "Mencegah penyadapan payload dan hasilnya di jaringan",
             "Preventif", "Berhasil: koneksi tanpa enkripsi ditolak galat 3159"],
            ["Enkripsi kolom AES", "Menjaga NIK tetap tidak terbaca walau baris terekstraksi",
             "Preventif", "Berhasil: keluaran berupa ciphertext"],
        ],
        caption="Tabel 4.9 Kemampuan Kontrol terhadap Sampel Exploit")
    H.par(doc, "Keterbatasan yang perlu dicatat: tidak ada satu pun kontrol yang menghentikan "
          "percobaan injeksi sebelum mencapai server. Pencegahan bekerja pada tahap pemrosesan "
          "kueri, bukan pada tahap masukan. Penambahan Web Application Firewall pada lapisan "
          "aplikasi akan melengkapi pertahanan berlapis dan telah dimasukkan ke dalam peta jalan "
          "pada subbab 5.4.")

    # ---------------- IV.4 ----------------
    H.sub(doc, "4.4  Evaluasi")
    H.par(doc, "Evaluasi dilakukan terhadap metrik yang ditetapkan pada subbab 3.3. Seluruh "
          "pengujian diverifikasi ulang dari lingkungan yang dibangun bersih sejak awal untuk "
          "memastikan hasilnya tidak bergantung pada kondisi sisa percobaan sebelumnya.")
    H.tabel(doc,
        ["Skenario", "Metrik", "Target", "Hasil", "Status"],
        [
            ["1. Failover", "server_id yang melayani saat master mati", "2 (slave)", "2", "Tercapai"],
            ["1. Failover", "Status replikasi setelah master pulih", "Yes / Yes",
             "Yes / Yes, Seconds_Behind_Source 0", "Tercapai"],
            ["1. Failover", "Perilaku operasi tulis saat master mati",
             "Galat informatif, bukan crash", "ERROR 1290 read-only", "Tercapai"],
            ["2. SQL Injection", "Baris terekspos pada kondisi rentan", "Seluruh baris",
             "Seluruh baris tabel", "Tercapai"],
            ["2. SQL Injection", "Baris terekspos setelah mitigasi", "0", "0", "Tercapai"],
            ["3. SSL/TLS", "Kode galat koneksi tanpa enkripsi", "3159", "3159", "Tercapai"],
            ["3. SSL/TLS", "Cipher aktif", "Terkonfirmasi", "TLS_AES_256_GCM_SHA384", "Tercapai"],
            ["3. Enkripsi", "Dekripsi dengan kunci salah", "NULL", "NULL", "Tercapai"],
            ["4. Least Privilege", "Penolakan operasi di luar kewenangan", "Ditolak",
             "ERROR 1142 pada seluruh kombinasi", "Tercapai"],
            ["5. Audit", "Jenis aksi tercatat", "Seluruh jenis",
             "5 jenis aksi terpanen otomatis", "Tercapai"],
        ],
        caption="Tabel 4.10 Evaluasi Pencapaian terhadap Metrik")

    H.par(doc, "Seluruh metrik tercapai. Terhadap tujuan proyek pada subbab 1.3, capaiannya "
          "sebagai berikut. Tujuan pertama tercapai dengan lima kontrol aktif dan terverifikasi "
          "sebagaimana Tabel 4.1. Tujuan kedua tercapai melalui lima skenario yang seluruhnya "
          "memenuhi parameter keberhasilan. Tujuan ketiga terlampaui: target minimal tiga temuan "
          "terpenuhi dengan lima temuan, seluruhnya telah diperbaiki dan diuji ulang. Tujuan "
          "keempat dijawab pada Bab V.")
    H.par(doc, "Catatan kejujuran metodologis. Dua dari lima temuan, yaitu T-04 dan T-05, "
          "merupakan kerentanan pada perkakas buatan tim sendiri, bukan pada sistem target. "
          "Keduanya tetap dilaporkan karena memiliki dampak nyata terhadap keandalan bukti: "
          "entri audit palsu dan pelaporan status yang keliru dapat menyesatkan analisis maupun "
          "penilaian. Pengalaman ini menegaskan bahwa perkakas verifikasi pun perlu diverifikasi.")
