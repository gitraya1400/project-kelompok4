# -*- coding: utf-8 -*-
"""Lampiran A-F."""
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH


def lampiran(doc, H):
    H.judul_bab(doc, "LAMPIRAN")

    # ---- A: RoE ----
    H.sub(doc, "Lampiran A  Rules of Engagement")
    H.par(doc, "Dokumen ini mengatur batasan pelaksanaan pengujian keamanan pada proyek akhir "
          "mata kuliah Keamanan Sistem Informasi.")
    for t in [
        "Lingkup target. Hanya container db-master, db-slave, dan haproxy pada jaringan bridge "
        "privat dbnet. Tidak ada sistem pihak ketiga, sistem produksi, maupun layanan publik yang "
        "menjadi sasaran.",
        "Isolasi lingkungan. Jaringan bridge Docker tanpa penerusan porta ke jaringan kampus "
        "maupun internet. Porta yang dipublikasikan terikat pada localhost mesin penguji.",
        "Data. Seluruh data merupakan data sintetis yang dibangkitkan tim. Tidak ada data pasien, "
        "responden, atau data pribadi nyata yang digunakan dalam bentuk apa pun.",
        "Metode yang diizinkan. SQL injection pada basis data milik sendiri, percobaan eskalasi "
        "hak akses menggunakan kredensial yang dibuat tim, penghentian container secara "
        "terkendali, serta koneksi tanpa enkripsi untuk menguji penolakan.",
        "Metode yang dilarang. Denial of service, eksploitasi terhadap sistem operasi host, "
        "pemindaian jaringan di luar dbnet, penggunaan sampel malware biner, serta setiap "
        "tindakan yang menyentuh sistem di luar laboratorium.",
        "Jadwal pelaksanaan. 1 sampai dengan 5 Oktober 2026 pada mesin pengembangan anggota tim.",
        "Penanganan temuan. Seluruh temuan dicatat pada laporan dan tidak dipublikasikan di luar "
        "lingkungan akademik mata kuliah.",
        "Penghentian pengujian. Pengujian dihentikan segera apabila terdapat indikasi dampak di "
        "luar lingkungan laboratorium.",
    ]:
        H.nomor(doc, t)
    H.catatan_isi(doc, "bubuhkan nama penanggung jawab pengujian dan tanggal persetujuan.")

    # ---- B: Pernyataan Etika ----
    H.sub(doc, "Lampiran B  Pernyataan Etika")
    H.par(doc, "Kami yang bertanda tangan di bawah ini menyatakan dengan sesungguhnya bahwa:")
    for t in [
        "Seluruh pengujian dilaksanakan pada lingkungan laboratorium terisolasi milik kelompok "
        "dan tidak menyentuh sistem pihak lain.",
        "Seluruh data yang digunakan merupakan data sintetis, bukan data pribadi nyata.",
        "Seluruh bukti yang disajikan merupakan hasil eksekusi sesungguhnya dan dapat "
        "direproduksi melalui berkas konfigurasi yang disertakan.",
        "Laporan ini merupakan karya kelompok kami dan setiap sumber rujukan telah dikutip "
        "sebagaimana mestinya.",
        "Penggunaan alat bantu kecerdasan buatan generatif telah diungkapkan sepenuhnya pada "
        "Lampiran F.",
    ]:
        H.nomor(doc, t)
    doc.add_paragraph()
    H.tabel(doc,
        ["No", "Nama Lengkap", "NIM", "Tanda Tangan"],
        [[str(i), "[Nama Anggota %d]" % i, "[NIM]", ""] for i in range(1, 6)],
        caption="Tabel B.1 Pernyataan Etika Anggota Kelompok")
    H.catatan_isi(doc, "cetak lampiran ini, bubuhkan tanda tangan basah seluruh anggota, "
                       "lalu pindai dan sisipkan kembali ke berkas PDF akhir.")

    # ---- C: Konfigurasi ----
    H.sub(doc, "Lampiran C  Cuplikan Konfigurasi")
    H.par(doc, "C.1 Konfigurasi node master pada docker-compose.yml")
    H.kode(doc,
        "db-master:\n"
        "  image: mysql:8.0\n"
        "  command: >\n"
        "    --server-id=1\n"
        "    --log-bin=mysql-bin\n"
        "    --binlog-format=ROW\n"
        "    --binlog-do-db=klinik_db\n"
        "    --general-log=1\n"
        "    --general-log-file=/var/log/mysql/general.log\n"
        "    --log-output=FILE,TABLE\n"
        "    --ssl-ca=/etc/mysql/certs/ca.pem\n"
        "    --ssl-cert=/etc/mysql/certs/server-cert.pem\n"
        "    --ssl-key=/etc/mysql/certs/server-key.pem\n"
        "  # CATATAN: --require-secure-transport TIDAK dipasang di sini.\n"
        "  # Lihat Temuan T-03: inisialisasi pertama akan macet permanen.\n"
        "  volumes:\n"
        "    - ./sql:/docker-entrypoint-initdb.d\n"
        "    - ./ssl:/etc/mysql/certs")

    H.par(doc, "C.2 Konfigurasi backend HAProxy")
    H.kode(doc,
        "backend db_backend\n"
        "    mode tcp\n"
        "    option tcp-check\n"
        "    server db-master db-master:3306 check inter 2s rise 1 fall 2\n"
        "    server db-slave  db-slave:3306  check inter 2s rise 1 fall 2 backup\n"
        "\n"
        "# Slave ditandai backup: seluruh trafik ke master selama master sehat.\n"
        "# option tcp-check dipilih karena hanya membuka soket TCP sehingga\n"
        "# tetap lolos meski require_secure_transport aktif.")

    H.par(doc, "C.3 Pembuatan sertifikat dengan OpenSSL")
    H.kode(doc,
        "openssl genrsa -out ca-key.pem 2048\n"
        "openssl req -new -x509 -nodes -days 3650 -key ca-key.pem -out ca.pem \\\n"
        "  -subj \"/C=ID/ST=Jakarta/O=KlinikSehat/CN=KlinikSehat-CA\"\n"
        "openssl req -newkey rsa:2048 -nodes -keyout server-key.pem \\\n"
        "  -out server-req.pem -subj \"/C=ID/.../CN=db-master\"\n"
        "openssl x509 -req -in server-req.pem -days 3650 -CA ca.pem \\\n"
        "  -CAkey ca-key.pem -CAcreateserial -out server-cert.pem \\\n"
        "  -extfile server-ext.cnf\n"
        "\n"
        "# server-ext.cnf memuat:\n"
        "# subjectAltName = DNS:db-master,DNS:db-slave,DNS:localhost,IP:127.0.0.1")

    H.par(doc, "C.4 Konfigurasi replikasi GTID over SSL")
    H.kode(doc,
        "CHANGE REPLICATION SOURCE TO\n"
        "  SOURCE_HOST='db-master', SOURCE_PORT=3306,\n"
        "  SOURCE_USER='replicator', SOURCE_PASSWORD='***',\n"
        "  SOURCE_LOG_FILE='<diambil otomatis dari dump>',\n"
        "  SOURCE_LOG_POS=<diambil otomatis dari dump>,\n"
        "  SOURCE_CONNECT_RETRY=5, SOURCE_RETRY_COUNT=86400,\n"
        "  SOURCE_SSL=1, SOURCE_SSL_CA='/etc/mysql/certs/ca.pem';\n"
        "START REPLICA;")

    # ---- D: Log ----
    H.sub(doc, "Lampiran D  Cuplikan Log Bukti Pengujian")
    H.par(doc, "D.1 Penolakan koneksi tanpa enkripsi (Skenario 3)")
    H.kode(doc,
        "$ mysql -h 127.0.0.1 -u tls_demo -p --ssl-mode=DISABLED -e \"SELECT 1;\"\n"
        "ERROR 3159 (HY000): Connections using insecure transport are\n"
        "prohibited while --require_secure_transport=ON.")

    H.par(doc, "D.2 Penolakan operasi di luar kewenangan (Skenario 4)")
    H.kode(doc,
        "ERROR 1142 (42000): SELECT command denied to user\n"
        "  'read_only'@'127.0.0.1' for table 'rekam_medis'\n"
        "ERROR 1142 (42000): SELECT command denied to user\n"
        "  'app_user'@'127.0.0.1' for table 'users'\n"
        "ERROR 1142 (42000): DROP command denied to user\n"
        "  'app_user'@'127.0.0.1' for table 'pasien'")

    H.par(doc, "D.3 Failover dan pemulihan replikasi (Skenario 1)")
    H.kode(doc,
        "# Master dimatikan\n"
        "$ docker stop db-master\n"
        "\n"
        "# Permintaan melalui HAProxy porta 3300 saat master mati\n"
        "+---------------+-----+\n"
        "| dilayani_oleh | jml |\n"
        "+---------------+-----+\n"
        "|             2 |   5 |\n"
        "+---------------+-----+\n"
        "\n"
        "# Operasi tulis saat master mati\n"
        "ERROR 1290 (HY000): The MySQL server is running with the\n"
        "--read-only option so it cannot execute this statement\n"
        "\n"
        "# Setelah master dihidupkan kembali, tanpa intervensi manual\n"
        "           Replica_IO_Running: Yes\n"
        "          Replica_SQL_Running: Yes\n"
        "        Seconds_Behind_Source: 0")

    H.par(doc, "D.4 Isi tabel audit_log hasil pemanenan otomatis (Skenario 5)")
    H.kode(doc,
        "+----+----------------------------+--------------+-------------+\n"
        "| id | aksi                       | tabel_target | ip_address  |\n"
        "+----+----------------------------+--------------+-------------+\n"
        "|  1 | SQL_INJECTION_ATTEMPT      | pasien       | 127.0.0.1   |\n"
        "|  2 | CONNECTION_REJECTED_NO_SSL | NULL         | 127.0.0.1   |\n"
        "|  3 | UNAUTHORIZED_SELECT        | rekam_medis  | 127.0.0.1   |\n"
        "|  4 | UNAUTHORIZED_SELECT        | users        | 127.0.0.1   |\n"
        "|  5 | UNAUTHORIZED_DROP          | pasien       | 127.0.0.1   |\n"
        "+----+----------------------------+--------------+-------------+")

    H.par(doc, "D.5 Peringatan berkas konfigurasi diabaikan (Temuan T-03)")
    H.kode(doc,
        "mysqld: [Warning] World-writable config file\n"
        "'/etc/mysql/conf.d/master.cnf' is ignored.")

    # ---- E: Hash ----
    H.sub(doc, "Lampiran E  Nilai Hash Sampel Exploit")
    H.par(doc, "Nilai hash berikut dihitung pada berkas sampel yang dianalisis pada subbab 4.3 "
          "dan dapat diverifikasi ulang menggunakan perintah sha256sum dan md5sum.")
    H.tabel(doc,
        ["Berkas", "Algoritma", "Nilai Hash"],
        [
            ["skenario2-attack.sql", "SHA-256",
             "73d4d9cae919de774f2b6c1dd1d06eac2b774f0a4520435b48f83f5e64d4c433"],
            ["skenario2-attack.sql", "MD5", "bf03ce2b67d8f792fdc6d5900096c316"],
            ["skenario2-attack-medis.sql", "SHA-256",
             "d7db7ffa2a1213ff106c1b0a3bb879d17008451837a381f409a5d3f182ef0eb3"],
            ["skenario2-attack-medis.sql", "MD5", "ab243e795b9c060170995c47f2d0eaa3"],
            ["skenario2-mitigation.sql", "SHA-256",
             "df8b83c70a7f408f5f42c89e5da22b4d497ec5b144611547431cba3bf88e9d0f"],
            ["skenario2-mitigation.sql", "MD5", "bb5c256236ce5cc301a6b1b527067063"],
        ],
        caption="Tabel E.1 Nilai Hash Sampel Exploit")
    H.par(doc, "Catatan: sampel yang dianalisis merupakan exploit SQL injection berbentuk berkas "
          "SQL, bukan malware biner. Pemilihan ini sesuai dengan batasan Rules of Engagement pada "
          "Lampiran A butir 5 yang melarang penggunaan sampel malware biner pada laboratorium ini.")

    # ---- F: AI ----
    H.sub(doc, "Lampiran F  Pengungkapan Penggunaan Kecerdasan Buatan Generatif")
    H.par(doc, "Sesuai Petunjuk nomor 3 pada lembar soal, berikut pengungkapan lengkap "
          "penggunaan alat bantu kecerdasan buatan generatif pada proyek ini.")
    H.tabel(doc,
        ["Aspek", "Keterangan"],
        [
            ["Alat yang digunakan", "Claude (Anthropic), diakses melalui antarmuka baris perintah "
             "pada lingkungan pengembangan."],
            ["Tujuan penggunaan", "Membantu analisis kerentanan konfigurasi, penelusuran akar "
             "penyebab kegagalan teknis, penyusunan skrip otomasi, dan penulisan draf laporan."],
            ["Bagian yang dibantu — Bab I sampai III", "Penyusunan draf narasi latar belakang, "
             "tinjauan pustaka, dan metodologi. Substansi teknis berasal dari rancangan tim."],
            ["Bagian yang dibantu — Bab IV", "Penulisan draf uraian temuan. Seluruh nilai "
             "konfigurasi, kode galat, nilai hash, dan hasil pengujian merupakan keluaran nyata "
             "dari sistem, diperoleh melalui eksekusi pada laboratorium, bukan dihasilkan alat "
             "bantu."],
            ["Bagian yang dibantu — Bab V", "Penyusunan draf struktur DPIA, playbook insiden, "
             "daftar periksa audit, dan peta jalan dengan merujuk standar yang disebutkan."],
            ["Bagian yang dibantu — skrip", "Penyusunan skrip setup-replikasi.sh, aktifkan-tls.sh, "
             "prosedur sp_harvest_audit, dan perbaikan aplikasi peraga."],
            ["Temuan yang diidentifikasi dengan bantuan alat", "Temuan T-03 mengenai berkas "
             "konfigurasi world-writable, T-04 mengenai entri audit palsu, dan T-05 mengenai "
             "pelaporan status keliru. Ketiganya diverifikasi ulang secara mandiri oleh tim "
             "melalui eksekusi langsung."],
            ["Bagian yang TIDAK dibantu", "Penentuan topik dan ruang lingkup, perancangan skema "
             "basis data awal, pembagian tugas, serta seluruh keputusan mengenai arah proyek."],
            ["Verifikasi", "Seluruh keluaran alat bantu diperiksa dan diuji ulang oleh tim. "
             "Beberapa saran awal alat bantu terbukti keliru dan dikoreksi, antara lain klaim "
             "mengenai kode galat penolakan akun replicator yang ternyata bergantung pada cara "
             "klien menyambung."],
        ],
        caption="Tabel F.1 Pengungkapan Penggunaan Kecerdasan Buatan Generatif")
    H.catatan_isi(doc, "periksa dan sesuaikan isi tabel ini dengan penggunaan sebenarnya oleh "
                       "tim sebelum pengumpulan. Pengungkapan yang tidak akurat termasuk "
                       "pelanggaran etika.")

    # ---- G: Screenshot ----
    H.sub(doc, "Lampiran G  Tangkapan Layar Bukti Pengujian")
    H.catatan_isi(doc, "sisipkan tangkapan layar asli dari folder user_screenshots. Setiap "
                       "gambar wajib diberi nomor, judul, dan keterangan yang terbaca sesuai "
                       "ketentuan penulisan pada lembar soal.")
    shots = [
        ("image1.png", "Gambar G.1 Dashboard HAProxy menampilkan kedua node berstatus UP"),
        ("image7.png", "Gambar G.2 Hasil eksekusi kueri rentan SQL injection"),
        ("image11.png", "Gambar G.3 Penolakan koneksi tanpa enkripsi dengan galat ERROR 3159"),
        ("image20.png", "Gambar G.4 Isi tabel audit_log hasil pemanenan otomatis"),
        ("image22.png", "Gambar G.5 Cuplikan mysql.general_log sebagai lapis audit kedua"),
    ]
    for nama, cap in shots:
        H.gambar(doc, nama, cap)
