# -*- coding: utf-8 -*-
"""BAB V, VI, VII, Daftar Pustaka, dan Lampiran."""
from docx.enum.text import WD_ALIGN_PARAGRAPH


def bab5(doc, H):
    H.judul_bab(doc, "BAB V  RANCANGAN PENGELOLAAN KEAMANAN DATA DAN LAYANAN TI")

    # ================= V.1 =================
    H.sub(doc, "5.1  Pelindungan Data Pribadi dan Kerahasiaan Data Statistik")

    H.sub(doc, "5.1.1  Klasifikasi Data", 3)
    H.par(doc, "Klasifikasi mengacu pada Undang-Undang Nomor 27 Tahun 2022 tentang Pelindungan "
          "Data Pribadi yang membedakan data pribadi umum dan data pribadi spesifik, serta "
          "Undang-Undang Nomor 16 Tahun 1997 tentang Statistik yang mewajibkan kerahasiaan "
          "keterangan individual responden.")
    H.tabel(doc,
        ["Atribut", "Tabel", "Klasifikasi UU PDP", "Tingkat Kerahasiaan", "Kontrol Diterapkan"],
        [
            ["nik_encrypted", "pasien", "Data pribadi spesifik (Pasal 4 ayat 2)", "Sangat Rahasia",
             "Enkripsi AES pada level kolom; akses terbatas app_user"],
            ["nama, tanggal_lahir, alamat, no_telepon", "pasien",
             "Data pribadi umum (Pasal 4 ayat 3)", "Rahasia",
             "TLS in transit; GRANT terbatas; audit log"],
            ["diagnosa, resep", "rekam_medis", "Data pribadi spesifik, yaitu data kesehatan "
             "(Pasal 4 ayat 2 huruf a)", "Sangat Rahasia",
             "Hanya app_user; read_only ditolak galat 1142"],
            ["password", "users", "Kredensial sistem", "Sangat Rahasia",
             "Hash; hanya root; app_user ditolak galat 1142"],
            ["isi audit_log", "audit_log", "Metadata aktivitas", "Internal",
             "Hanya root yang dapat membaca penuh"],
        ],
        caption="Tabel 5.1 Klasifikasi Data pada klinik_db")

    H.sub(doc, "5.1.2  Data Protection Impact Assessment", 3)
    H.par(doc, "DPIA disusun mengacu Pasal 34 UU PDP yang mewajibkan penilaian dampak untuk "
          "pemrosesan berisiko tinggi, termasuk pemrosesan data pribadi spesifik dalam skala besar.")
    H.tabel(doc,
        ["Komponen DPIA", "Uraian"],
        [
            ["Tujuan pemrosesan",
             "Penyelenggaraan layanan klinik: registrasi pasien, pencatatan rekam medis, dan "
             "penyusunan statistik kesehatan agregat."],
            ["Dasar pemrosesan",
             "Pasal 20 ayat 2 UU PDP: pemenuhan kewajiban perjanjian layanan kesehatan dan "
             "pelaksanaan kewenangan penyelenggara statistik."],
            ["Jenis data",
             "Data pribadi spesifik berupa NIK dan data kesehatan, serta data pribadi umum "
             "berupa identitas dan kontak."],
            ["Subjek data", "Pasien klinik; estimasi skala menengah hingga besar."],
            ["Risiko utama 1",
             "Kebocoran NIK dan rekam medis melalui SQL injection. Likelihood: tinggi sebelum "
             "mitigasi. Dampak: berat, karena menyangkut data kesehatan."],
            ["Mitigasi risiko 1",
             "Prepared statement, least privilege, dan enkripsi kolom. Risiko residual: rendah. "
             "Terverifikasi pada Temuan T-01."],
            ["Risiko utama 2",
             "Intersepsi data saat transit. Likelihood: sedang. Dampak: berat."],
            ["Mitigasi risiko 2",
             "Penegakan TLS 1.3 dengan cipher AES-256-GCM. Risiko residual: rendah. "
             "Terverifikasi pada Temuan T-02."],
            ["Risiko utama 3",
             "Akses berlebih oleh pengguna internal. Likelihood: sedang. Dampak: sedang."],
            ["Mitigasi risiko 3",
             "RBAC tiga peran dengan hak minimum dan pembatasan laju kueri. Risiko residual: "
             "rendah. Terverifikasi pada Temuan terkait Skenario 4."],
            ["Risiko utama 4",
             "Ketidaktersediaan layanan saat server utama gagal. Likelihood: sedang. "
             "Dampak: sedang."],
            ["Mitigasi risiko 4",
             "Replikasi master-slave dengan failover otomatis. Risiko residual: rendah untuk "
             "operasi baca, sedang untuk operasi tulis karena slave bersifat read-only."],
            ["Hak subjek data",
             "Hak akses, perbaikan, dan penghapusan difasilitasi melalui prosedur permintaan "
             "tertulis dengan verifikasi identitas; jejak pemenuhan dicatat pada audit_log."],
            ["Kesimpulan DPIA",
             "Pemrosesan dapat dilanjutkan dengan kontrol yang telah diterapkan. Diperlukan "
             "peninjauan ulang apabila terjadi perubahan cakupan data atau arsitektur."],
        ],
        caption="Tabel 5.2 Data Protection Impact Assessment")

    H.sub(doc, "5.1.3  Teknik Pelindungan dan Pengukuran Efektivitas", 3)
    H.par(doc, "Dua teknik pelindungan diterapkan dan diukur efektivitasnya.")
    H.par(doc, "Pertama, enkripsi pada level kolom. NIK disimpan sebagai ciphertext hasil "
          "AES_ENCRYPT. Pengukuran efektivitas dilakukan dengan membandingkan hasil dekripsi "
          "menggunakan kunci benar dan kunci salah. Hasilnya: kunci benar mengembalikan nilai "
          "asli, kunci salah mengembalikan NULL. Dengan demikian, apabila media penyimpanan "
          "berpindah tangan tanpa disertai kunci, NIK tidak dapat dipulihkan.")
    H.par(doc, "Kedua, pengendalian pengungkapan statistik untuk keperluan pelaporan agregat. "
          "Rancangan menerapkan ambang minimum lima pencacahan per sel tabel, penekanan sel "
          "primer untuk sel yang berada di bawah ambang, serta penekanan sekunder untuk mencegah "
          "rekonstruksi melalui selisih marginal.")
    H.tabel(doc,
        ["Teknik", "Penerapan", "Pengukuran Efektivitas", "Hasil"],
        [
            ["Enkripsi kolom AES", "Kolom nik_encrypted bertipe VARBINARY",
             "Uji dekripsi dengan kunci benar dan kunci salah",
             "Kunci benar: nilai asli. Kunci salah: NULL"],
            ["Ambang minimum sel", "Minimum 5 pencacahan per sel pada tabel agregat",
             "Estimasi risiko re-identifikasi melalui keunikan kombinasi atribut",
             "Risiko turun dari tinggi menjadi rendah untuk kombinasi usia, jenis kelamin, "
             "dan wilayah kecamatan"],
            ["Penekanan sel", "Sel di bawah ambang ditandai dan tidak ditampilkan",
             "Pemeriksaan kemungkinan rekonstruksi dari total marginal",
             "Memerlukan penekanan sekunder agar selisih marginal tidak mengungkap sel tertekan"],
            ["Pseudonimisasi", "Pengganti identitas pada salinan data untuk analisis",
             "Uji keterhubungan ulang dengan data sumber",
             "Perlu kontrol tambahan terhadap tabel pemetaan pseudonim"],
        ],
        caption="Tabel 5.3 Teknik Pelindungan dan Pengukuran Efektivitas")
    H.par(doc, "Keterbatasan yang perlu dinyatakan: kunci enkripsi pada implementasi laboratorium "
          "ini masih ditanamkan dalam skrip. Kondisi tersebut tidak memenuhi praktik yang baik "
          "karena kunci tersimpan berdampingan dengan data yang dilindunginya. Penggunaan Key "
          "Management System terpisah dimasukkan sebagai prioritas pada peta jalan subbab 5.4.")

    # ================= V.2 =================
    H.sub(doc, "5.2  Penanganan Insiden")
    H.par(doc, "Rencana tanggap insiden disusun mengikuti empat fase NIST SP 800-61 Revision 2 "
          "dan disesuaikan dengan konteks basis data klinik.")

    H.sub(doc, "5.2.1  Struktur Tim dan Eskalasi", 3)
    H.tabel(doc,
        ["Peran", "Tanggung Jawab", "Kriteria Eskalasi"],
        [
            ["Incident Commander", "Mengoordinasi penanganan, memutuskan isolasi sistem, "
             "menjadi titik komunikasi tunggal",
             "Diaktifkan untuk seluruh insiden tingkat sedang ke atas"],
            ["Database Administrator", "Analisis audit log, isolasi akun, pemulihan data",
             "Dilibatkan sejak fase deteksi"],
            ["Petugas Pelindungan Data", "Menilai keterdampakan data pribadi, menyiapkan "
             "pemberitahuan kepada subjek data dan lembaga pengawas",
             "Dilibatkan apabila data pribadi diduga terdampak"],
            ["Pimpinan Unit", "Keputusan penghentian layanan dan komunikasi publik",
             "Insiden tingkat tinggi atau yang berpotensi diberitakan"],
        ],
        caption="Tabel 5.4 Struktur Tim Tanggap Insiden")

    H.sub(doc, "5.2.2  Playbook Kebocoran Data melalui SQL Injection", 3)
    H.tabel(doc,
        ["Fase", "Tindakan", "Penanggung Jawab", "Target Waktu"],
        [
            ["Preparation", "Audit log aktif dua lapis; backup harian terverifikasi; daftar "
             "kontak tim tanggap insiden mutakhir; latihan tabletop dua kali setahun",
             "DBA dan Incident Commander", "Berkelanjutan"],
            ["Detection and Analysis",
             "Deteksi pola SQL_INJECTION_ATTEMPT pada audit_log; verifikasi melalui "
             "mysql.general_log; penentuan cakupan data terdampak melalui nilai rows_sent",
             "DBA", "Dalam 1 jam sejak indikator muncul"],
            ["Containment", "Pencabutan hak akses akun terdampak; pemblokiran alamat IP sumber; "
             "isolasi node bila diperlukan",
             "DBA dan Incident Commander", "Dalam 2 jam"],
            ["Eradication", "Perbaikan kueri rentan menjadi prepared statement; peninjauan "
             "menyeluruh terhadap kueri sejenis; rotasi kredensial",
             "Tim pengembang dan DBA", "Dalam 24 jam"],
            ["Recovery", "Pemulihan data dari backup bila terjadi perubahan; verifikasi "
             "integritas; pemantauan intensif selama 7 hari",
             "DBA", "Dalam 48 jam"],
            ["Post-Incident", "Rapat pembelajaran; pemutakhiran playbook; pelaporan akhir",
             "Incident Commander", "Dalam 14 hari"],
        ],
        caption="Tabel 5.5 Playbook Penanganan Kebocoran Data")

    H.sub(doc, "5.2.3  Simulasi Tabletop", 3)
    H.par(doc, "Simulasi dilaksanakan dengan skenario berikut: pada hari kerja pukul 09.15, "
          "sistem pemantauan mendeteksi lonjakan entri SQL_INJECTION_ATTEMPT pada audit_log yang "
          "berasal dari satu alamat IP, disertai satu kueri SELECT yang mengembalikan seluruh "
          "baris tabel pasien.")
    H.tabel(doc,
        ["Waktu", "Kejadian dan Keputusan", "Pelaku"],
        [
            ["T+0 (09.15)", "Peringatan otomatis diterima. Verifikasi awal pada audit_log "
             "menemukan 47 entri dalam 3 menit dari IP yang sama.", "DBA"],
            ["T+8 menit", "Konfirmasi pada mysql.general_log: satu kueri mengembalikan 1.284 "
             "baris, jauh di atas pola normal. Insiden dinyatakan valid dan dieskalasi.", "DBA"],
            ["T+15 menit", "Incident Commander diaktifkan. Keputusan: lakukan containment tanpa "
             "menghentikan layanan, karena serangan bersifat baca dan tidak mengubah data.",
             "Incident Commander"],
            ["T+22 menit", "Hak akses akun terdampak dicabut; alamat IP sumber diblokir pada "
             "lapisan jaringan.", "DBA"],
            ["T+40 menit", "Petugas Pelindungan Data menilai keterdampakan: 1.284 baris memuat "
             "NIK terenkripsi dan identitas. Kunci enkripsi tidak ikut terekspos sehingga NIK "
             "tetap terlindungi, namun nama dan alamat terekspos dalam bentuk terbuka.",
             "Petugas Pelindungan Data"],
            ["T+2 jam", "Keputusan: insiden memenuhi kriteria kegagalan pelindungan data pribadi. "
             "Kewajiban pemberitahuan dalam 3 x 24 jam diaktifkan.", "Incident Commander"],
            ["T+6 jam", "Kueri rentan diperbaiki menjadi prepared statement; peninjauan "
             "menemukan dua kueri sejenis yang ikut diperbaiki.", "Tim pengembang"],
            ["T+20 jam", "Uji ulang membuktikan payload yang sama mengembalikan nol baris.", "DBA"],
            ["T+2 hari", "Pemberitahuan tertulis dikirim kepada subjek data terdampak dan "
             "lembaga pengawas, memuat kronologi, jenis data, dampak, dan langkah penanganan.",
             "Petugas Pelindungan Data"],
            ["T+10 hari", "Rapat pembelajaran. Tiga tindak lanjut disepakati.",
             "Incident Commander"],
        ],
        caption="Tabel 5.6 Kronologi Simulasi Tabletop")
    H.par(doc, "Pemberitahuan kegagalan pelindungan data pribadi. Sesuai Pasal 46 UU PDP, "
          "pemberitahuan tertulis wajib disampaikan kepada subjek data dan lembaga pengawas "
          "paling lambat 3 x 24 jam sejak diketahui. Pada simulasi, pemberitahuan dikirim pada "
          "T+2 hari sehingga memenuhi batas waktu. Isi pemberitahuan mencakup data pribadi yang "
          "terungkap, waktu dan cara terungkapnya, serta upaya penanganan dan pemulihan.")
    H.par(doc, "Pelajaran yang dipetik dari simulasi:")
    for t in ["Ambang peringatan perlu diturunkan. Deteksi pada 47 entri terlalu lambat; "
              "ambang 10 entri dalam 5 menit lebih sesuai.",
              "Diperlukan prosedur baku penentuan cakupan terdampak agar penilaian keterdampakan "
              "tidak memakan waktu 40 menit.",
              "Templat pemberitahuan perlu disiapkan sebelum insiden agar penyusunan tidak "
              "menghabiskan waktu pada saat kritis."]:
        H.poin(doc, t)

    # ================= V.3 =================
    H.sub(doc, "5.3  Audit Keamanan")
    H.par(doc, "Audit internal dirancang dengan kriteria ISO/IEC 27001:2022 Annex A. Lingkup "
          "audit mencakup basis data klinik_db beserta infrastruktur pendukungnya. Metode audit "
          "meliputi pemeriksaan konfigurasi, pengujian teknis, dan penelaahan dokumen.")

    H.sub(doc, "5.3.1  Daftar Periksa Audit", 3)
    H.tabel(doc,
        ["No", "Kontrol Annex A", "Kriteria Pemeriksaan", "Hasil"],
        [
            ["1", "A.5.15 Access control", "Kebijakan kontrol akses terdokumentasi dan diterapkan",
             "Sesuai"],
            ["2", "A.5.17 Authentication information", "Kredensial tidak tersimpan dalam bentuk "
             "terbuka", "Sesuai sebagian"],
            ["3", "A.5.18 Access rights", "Hak akses sesuai prinsip least privilege", "Sesuai"],
            ["4", "A.5.23 Cloud services security", "Konfigurasi layanan terkontainer diamankan",
             "Sesuai"],
            ["5", "A.5.24 Incident management planning", "Rencana tanggap insiden tersedia",
             "Sesuai"],
            ["6", "A.5.33 Protection of records", "Rekaman audit dilindungi dari perubahan",
             "Tidak sesuai"],
            ["7", "A.8.2 Privileged access rights", "Akun istimewa dibatasi dan dipantau",
             "Sesuai sebagian"],
            ["8", "A.8.3 Information access restriction", "Pembatasan akses pada level tabel",
             "Sesuai"],
            ["9", "A.8.5 Secure authentication", "Autentikasi melalui kanal terenkripsi", "Sesuai"],
            ["10", "A.8.9 Configuration management", "Konfigurasi terkelola dan terverifikasi",
             "Tidak sesuai"],
            ["11", "A.8.12 Data leakage prevention", "Kontrol pencegahan kebocoran data", "Sesuai"],
            ["12", "A.8.13 Information backup", "Backup berkala dan teruji", "Tidak sesuai"],
            ["13", "A.8.15 Logging", "Pencatatan aktivitas lengkap dan terlindungi", "Sesuai"],
            ["14", "A.8.16 Monitoring activities", "Pemantauan anomali berjalan",
             "Sesuai sebagian"],
            ["15", "A.8.24 Use of cryptography", "Kriptografi diterapkan sesuai kebijakan",
             "Sesuai sebagian"],
            ["16", "A.8.28 Secure coding", "Praktik pengodean aman diterapkan", "Sesuai"],
            ["17", "A.8.32 Change management", "Perubahan terkendali dan terdokumentasi",
             "Sesuai sebagian"],
        ],
        caption="Tabel 5.7 Daftar Periksa Audit Keamanan (17 Kontrol)")

    H.sub(doc, "5.3.2  Temuan Audit", 3)
    H.par(doc, "Lima temuan disajikan dengan format kondisi, kriteria, penyebab, akibat, "
          "dan rekomendasi.")

    temuan = [
        ("A-01", "Kunci enkripsi tertanam dalam skrip (A.8.24)",
         "Kunci AES ditulis langsung pada berkas SQL dan tersimpan pada repositori yang sama "
         "dengan data.",
         "A.8.24 mensyaratkan pengelolaan kunci kriptografi sepanjang siklus hidupnya, termasuk "
         "pemisahan penyimpanan kunci dari data terlindungi.",
         "Keterbatasan lingkungan laboratorium; belum tersedia Key Management System.",
         "Pihak yang memperoleh salinan basis data beserta repositori dapat mendekripsi seluruh "
         "NIK, sehingga kontrol enkripsi menjadi tidak bermakna.",
         "Terapkan KMS terpisah, lakukan rotasi kunci berkala, dan pisahkan kewenangan pengelola "
         "kunci dari pengelola basis data."),
        ("A-02", "Kunci privat sertifikat tersimpan pada repositori (A.5.17)",
         "Berkas ca-key.pem dan server-key.pem tersimpan di dalam repositori proyek.",
         "A.5.17 mensyaratkan informasi autentikasi dilindungi dari pengungkapan tidak sah.",
         "Kebutuhan reproducibility lingkungan laboratorium tanpa pembangkitan ulang sertifikat.",
         "Pihak yang memperoleh akses repositori dapat menerbitkan sertifikat palsu dan "
         "melakukan serangan man-in-the-middle.",
         "Keluarkan kunci privat dari kendali versi, tambahkan ke daftar abaian, dan bangkitkan "
         "sertifikat melalui skrip pada tiap lingkungan."),
        ("A-03", "Konfigurasi tidak terverifikasi setelah penerapan (A.8.9)",
         "Berkas konfigurasi .cnf dipasang namun diabaikan MySQL tanpa disadari selama beberapa "
         "siklus pengembangan.",
         "A.8.9 mensyaratkan konfigurasi ditetapkan, didokumentasikan, diterapkan, dan dipantau.",
         "Ketiadaan langkah verifikasi pascapenerapan; keberhasilan diasumsikan dari keberadaan "
         "berkas.",
         "Kontrol keamanan tampak aktif padahal tidak berfungsi, termasuk pencatatan audit yang "
         "sepenuhnya mati.",
         "Tetapkan verifikasi pascapenerapan sebagai langkah wajib dengan membandingkan nilai "
         "efektif pada server terhadap nilai yang dirancang, bukan terhadap isi berkas."),
        ("A-04", "Rekaman audit dapat diubah pemilik basis data (A.5.33)",
         "Akun root dapat menyunting maupun menghapus isi tabel audit_log tanpa meninggalkan "
         "jejak terpisah.",
         "A.5.33 mensyaratkan rekaman dilindungi dari pemalsuan dan penghapusan tidak sah.",
         "Tabel audit berada pada basis data yang sama dengan data operasional dan dikelola akun "
         "yang sama.",
         "Pelaku dengan akses istimewa dapat menghapus jejak perbuatannya, sehingga nilai "
         "forensik audit log menjadi lemah.",
         "Kirimkan salinan log ke penyimpanan terpisah yang bersifat hanya-tambah, terapkan "
         "pemisahan tugas antara administrator basis data dan administrator log."),
        ("A-05", "Backup belum terjadwal dan belum teruji (A.8.13)",
         "Tidak ditemukan mekanisme pencadangan terjadwal maupun catatan uji pemulihan.",
         "A.8.13 mensyaratkan salinan cadangan dibuat, dipelihara, dan diuji secara berkala.",
         "Lingkup proyek difokuskan pada pengamanan dan ketersediaan, belum mencakup kelangsungan "
         "data.",
         "Replikasi melindungi dari kegagalan perangkat keras namun tidak melindungi dari "
         "penghapusan logis, karena penghapusan ikut tereplikasi ke node slave.",
         "Jadwalkan mysqldump harian dengan retensi 30 hari, simpan di luar klaster, dan uji "
         "pemulihan setiap triwulan."),
    ]
    H.tabel(doc,
        ["ID", "Temuan", "Kondisi", "Kriteria", "Penyebab", "Akibat", "Rekomendasi"],
        [[a, b, c, d, e, f, g] for a, b, c, d, e, f, g in temuan],
        caption="Tabel 5.8 Temuan Audit Keamanan")

    # ================= V.4 =================
    H.sub(doc, "5.4  Rancangan Keamanan Sistem Informasi Statistik")

    H.sub(doc, "5.4.1  Arsitektur Keamanan Terintegrasi", 3)
    H.par(doc, "Rancangan menerapkan pertahanan berlapis dengan lima lapis kendali. Setiap lapis "
          "dirancang agar kegagalan satu lapis tidak langsung mengakibatkan kompromi menyeluruh.")
    H.kode(doc,
        "  Lapis 1  PERIMETER\n"
        "           WAF, pembatasan laju, segmentasi jaringan\n"
        "              |\n"
        "  Lapis 2  TRANSPORT\n"
        "           TLS 1.3 wajib, sertifikat dari CA internal      [TERIMPLEMENTASI]\n"
        "              |\n"
        "  Lapis 3  AUTENTIKASI DAN OTORISASI\n"
        "           RBAC least privilege, pembatasan laju kueri     [TERIMPLEMENTASI]\n"
        "              |\n"
        "  Lapis 4  DATA\n"
        "           Enkripsi kolom AES, prepared statement,         [TERIMPLEMENTASI]\n"
        "           pengendalian pengungkapan statistik\n"
        "              |\n"
        "  Lapis 5  PEMANTAUAN DAN KETERSEDIAAN\n"
        "           Audit dua lapis, replikasi, failover            [TERIMPLEMENTASI]\n"
        "           SIEM terpusat, log hanya-tambah                 [RENCANA]")
    H.par(doc, "Gambar 5.1 Arsitektur keamanan berlapis", just=False)
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    H.sub(doc, "5.4.2  Pemetaan Kontrol ke Annex A ISO/IEC 27001:2022", 3)
    H.tabel(doc,
        ["Kontrol Annex A", "Implementasi pada Proyek", "Status", "Bukti"],
        [
            ["A.8.3 Information access restriction",
             "GRANT per tabel untuk tiga peran", "Terimplementasi",
             "Penolakan galat 1142 pada Skenario 4"],
            ["A.8.24 Use of cryptography",
             "TLS 1.3 dan AES_ENCRYPT pada kolom NIK", "Terimplementasi sebagian",
             "Cipher TLS_AES_256_GCM_SHA384; temuan A-01 tentang pengelolaan kunci"],
            ["A.8.15 Logging",
             "general_log ke tabel dan audit_log hasil pemanenan", "Terimplementasi",
             "Lima jenis aksi terpanen otomatis"],
            ["A.8.16 Monitoring activities",
             "Dashboard HAProxy dan pemantauan status replikasi", "Terimplementasi sebagian",
             "Belum ada peringatan otomatis"],
            ["A.8.13 Information backup", "Belum diterapkan", "Belum",
             "Temuan A-05"],
            ["A.5.33 Protection of records", "audit_log masih dapat diubah root", "Belum",
             "Temuan A-04"],
            ["A.8.9 Configuration management",
             "Konfigurasi terdefinisi pada docker-compose.yml", "Terimplementasi",
             "Verifikasi nilai efektif pada Tabel 4.1"],
            ["A.8.28 Secure coding",
             "Prepared statement pada seluruh kueri dengan masukan pengguna", "Terimplementasi",
             "Nol baris pada uji ulang Temuan T-01"],
            ["A.5.24 Incident management planning",
             "Playbook dan simulasi tabletop", "Terimplementasi",
             "Subbab 5.2"],
            ["A.5.30 ICT readiness for business continuity",
             "Replikasi master-slave dengan failover", "Terimplementasi sebagian",
             "Operasi tulis belum tersedia saat master mati"],
        ],
        caption="Tabel 5.9 Pemetaan Kontrol ke Annex A ISO/IEC 27001:2022")

    H.sub(doc, "5.4.3  Peta Jalan Implementasi Berbasis Prioritas Risiko", 3)
    H.tabel(doc,
        ["Prioritas", "Inisiatif", "Risiko yang Ditangani", "Periode", "Indikator Keberhasilan"],
        [
            ["P1 Kritis", "Pemindahan kunci enkripsi ke KMS",
             "A-01: kunci berdampingan dengan data", "Bulan 1-2",
             "Kunci tidak lagi berada pada repositori; rotasi berkala berjalan"],
            ["P1 Kritis", "Pengeluaran kunci privat dari kendali versi",
             "A-02: risiko penerbitan sertifikat palsu", "Bulan 1",
             "Repositori bersih dari berkas kunci; sertifikat dibangkitkan per lingkungan"],
            ["P2 Tinggi", "Backup terjadwal dan uji pemulihan",
             "A-05: tidak ada perlindungan terhadap penghapusan logis", "Bulan 2-3",
             "Backup harian berjalan; uji pemulihan triwulanan terdokumentasi"],
            ["P2 Tinggi", "Pengiriman log ke penyimpanan hanya-tambah",
             "A-04: rekaman audit dapat diubah", "Bulan 3-4",
             "Log tersalin ke sistem terpisah; integritas terverifikasi"],
            ["P3 Sedang", "Penerapan WAF pada lapisan aplikasi",
             "Percobaan injeksi mencapai server basis data", "Bulan 4-6",
             "Payload umum tertahan sebelum mencapai basis data"],
            ["P3 Sedang", "SIEM dan peringatan otomatis",
             "Deteksi insiden masih manual", "Bulan 5-7",
             "Peringatan terkirim dalam 5 menit sejak anomali"],
            ["P4 Rendah", "HAProxy ganda dengan Virtual IP",
             "Load balancer masih single point of failure", "Bulan 7-9",
             "Kegagalan satu instans HAProxy tidak menghentikan layanan"],
            ["P4 Rendah", "Promosi slave otomatis saat master gagal",
             "Operasi tulis tidak tersedia saat master mati", "Bulan 9-12",
             "Operasi tulis pulih otomatis tanpa intervensi"],
        ],
        caption="Tabel 5.10 Peta Jalan Implementasi Berbasis Prioritas Risiko")


def bab6(doc, H):
    H.judul_bab(doc, "BAB VI  JADWAL PELAKSANAAN DAN PEMBAGIAN TUGAS")

    H.sub(doc, "6.1  Jadwal Pelaksanaan")
    H.par(doc, "Tabel berikut membandingkan rencana dengan realisasi kegiatan.")
    H.tabel(doc,
        ["No", "Kegiatan", "Rencana", "Realisasi", "Keterangan"],
        [
            ["1", "Studi literatur dan analisis kebutuhan", "Hari 1", "Hari 1", "Sesuai rencana"],
            ["2", "Perancangan arsitektur dan skenario uji", "Hari 1-2", "Hari 1-2",
             "Sesuai rencana"],
            ["3", "Implementasi dan konfigurasi lingkungan", "Hari 2-3", "Hari 2-4",
             "Melebihi rencana akibat Temuan T-03 pada pemuatan konfigurasi"],
            ["4", "Pengujian lima skenario", "Hari 3-4", "Hari 3-4", "Sesuai rencana"],
            ["5", "Perbaikan temuan dan uji ulang", "Hari 4", "Hari 4", "Sesuai rencana"],
            ["6", "Penyusunan laporan", "Hari 4-5", "Hari 4-5", "Sesuai rencana"],
        ],
        caption="Tabel 6.1 Perbandingan Rencana dan Realisasi Kegiatan")
    H.catatan_isi(doc, "sesuaikan kolom rencana dan realisasi dengan kondisi tim sebenarnya.")

    H.sub(doc, "6.2  Pembagian Tugas")
    H.tabel(doc,
        ["No", "Nama Anggota", "NIM", "Peran", "Tugas Utama", "Kontribusi"],
        [
            ["1", "[Nama Anggota 1]", "[NIM]", "Ketua dan Koordinator Pengujian",
             "Koordinasi tim; penanggung jawab Rules of Engagement; eksekusi skenario failover",
             "[  ]%"],
            ["2", "[Nama Anggota 2]", "[NIM]", "Database Administrator",
             "Konfigurasi hardening MySQL; penerapan RBAC; pengaturan replikasi", "[  ]%"],
            ["3", "[Nama Anggota 3]", "[NIM]", "Security Engineer",
             "Pembuatan sertifikat TLS; pengujian SQL injection; analisis exploit", "[  ]%"],
            ["4", "[Nama Anggota 4]", "[NIM]", "Audit dan Compliance",
             "Penyusunan DPIA; daftar periksa audit; pemetaan kontrol Annex A", "[  ]%"],
            ["5", "[Nama Anggota 5]", "[NIM]", "Dokumentasi dan Pelaporan",
             "Penyusunan laporan; pendokumentasian bukti; aplikasi peraga", "[  ]%"],
        ],
        caption="Tabel 6.2 Pembagian Tugas dan Persentase Kontribusi")
    H.catatan_isi(doc, "lengkapi nama, NIM, dan persentase kontribusi. Total kontribusi 100 "
                       "persen. Kolom ini memengaruhi perhitungan nilai individu.")


def bab7(doc, H):
    H.judul_bab(doc, "BAB VII  KESIMPULAN DAN SARAN")

    H.sub(doc, "7.1  Kesimpulan")
    H.par(doc, "Kesimpulan disusun sebagai jawaban atas keempat rumusan masalah pada subbab 1.2.")

    H.par(doc, "Jawaban rumusan masalah pertama. Hardening MySQL yang memenuhi CIA Triad dicapai "
          "melalui lima kontrol yang saling melengkapi: penegakan TLS 1.3 untuk data in transit, "
          "enkripsi AES pada level kolom untuk data at rest, kontrol akses berbasis peran dengan "
          "hak minimum, pencatatan audit dua lapis, serta replikasi master-slave dengan failover "
          "otomatis. Seluruh kontrol diverifikasi aktif sebagaimana Tabel 4.1. Pelajaran penting "
          "yang diperoleh adalah bahwa penerapan konfigurasi tidak menjamin keaktifannya, "
          "sebagaimana ditunjukkan Temuan T-03 ketika berkas konfigurasi diabaikan tanpa "
          "disadari. Verifikasi nilai efektif pada server merupakan langkah yang tidak dapat "
          "dilewati.")

    H.par(doc, "Jawaban rumusan masalah kedua. Seluruh kontrol terbukti efektif melalui pengujian "
          "terukur. Prepared statement menurunkan jumlah baris terekspos dari seluruh isi tabel "
          "menjadi nol dengan payload yang identik. Least privilege menolak setiap operasi di "
          "luar kewenangan dengan galat 1142. Penegakan TLS menolak koneksi tanpa enkripsi dengan "
          "galat 3159, sementara koneksi bersertifikat berhasil dengan cipher "
          "TLS_AES_256_GCM_SHA384. Enkripsi kolom mengembalikan NULL ketika dekripsi dilakukan "
          "dengan kunci yang salah. Audit log mencatat seluruh percobaan secara otomatis dari "
          "jejak server, bukan dari pencatatan manual.")

    H.par(doc, "Jawaban rumusan masalah ketiga. Arsitektur replikasi dengan load balancer "
          "menjaga ketersediaan layanan baca secara penuh. Ketika master dihentikan, permintaan "
          "secara otomatis dialihkan ke slave tanpa perubahan apa pun pada sisi klien, dibuktikan "
          "oleh nilai server_id yang berubah dari 1 menjadi 2. Ketika master dihidupkan kembali, "
          "replikasi tersambung ulang tanpa intervensi manual dengan Seconds_Behind_Source "
          "bernilai nol. Keterbatasan yang jujur dinyatakan: operasi tulis tidak tersedia selama "
          "master mati karena slave dikonfigurasi read-only. Pilihan ini diambil secara sadar "
          "untuk mencegah divergensi data yang dapat menghentikan replikasi secara permanen.")

    H.par(doc, "Jawaban rumusan masalah keempat. Rancangan pengelolaan keamanan disusun pada "
          "Bab V mencakup klasifikasi data dan DPIA sesuai UU PDP dan UU Statistik, rencana "
          "tanggap insiden berbasis NIST SP 800-61 beserta simulasi tabletop yang memenuhi "
          "kewajiban pemberitahuan 3 x 24 jam, audit dengan 17 kontrol Annex A yang menghasilkan "
          "lima temuan, serta arsitektur berlapis dan peta jalan dua belas bulan berbasis "
          "prioritas risiko.")

    H.sub(doc, "7.2  Keterbatasan Proyek")
    for t in [
        "Kunci enkripsi masih ditanamkan dalam skrip sehingga tersimpan berdampingan dengan data "
        "yang dilindunginya.",
        "Sertifikat bersifat self-signed sehingga tidak memberikan jaminan identitas dari pihak "
        "ketiga tepercaya.",
        "HAProxy dijalankan sebagai instans tunggal dan masih menjadi single point of failure.",
        "Operasi tulis tidak tersedia selama master mati karena belum tersedia mekanisme promosi "
        "slave otomatis.",
        "Analisis ancaman pada subbab 4.3 menggunakan sampel exploit SQL injection, bukan sampel "
        "malware biner, sesuai batasan Rules of Engagement laboratorium.",
        "Pengujian dilakukan pada data sintetis dengan volume kecil sehingga perilaku pada beban "
        "produksi belum terukur.",
        "Jalur implementasi alternatif berbasis XAMPP dan Laragon tidak dikerjakan.",
    ]:
        H.poin(doc, t)

    H.sub(doc, "7.3  Saran Pengembangan")
    for t in [
        "Menerapkan Key Management System terpisah beserta rotasi kunci berkala sebagai prioritas "
        "pertama, karena tanpa itu kontrol enkripsi kehilangan sebagian besar maknanya.",
        "Menambahkan Web Application Firewall agar percobaan injeksi tertahan sebelum mencapai "
        "basis data, melengkapi pertahanan yang saat ini bekerja pada tahap pemrosesan kueri.",
        "Mengirimkan salinan audit log ke penyimpanan hanya-tambah yang terpisah agar jejak "
        "forensik tidak dapat dihapus pemilik basis data.",
        "Menjadwalkan pencadangan beserta uji pemulihan berkala, karena replikasi tidak "
        "melindungi dari penghapusan logis yang ikut tereplikasi.",
        "Menerapkan HAProxy ganda dengan Virtual IP dan mekanisme promosi slave otomatis untuk "
        "mencapai ketersediaan penuh termasuk operasi tulis.",
        "Melakukan pengujian pada volume data yang menyerupai kondisi produksi untuk mengukur "
        "dampak kontrol keamanan terhadap kinerja.",
    ]:
        H.poin(doc, t)


def pustaka(doc, H):
    H.judul_bab(doc, "DAFTAR PUSTAKA")
    refs = [
        "OWASP Foundation, OWASP Top 10:2021 — The Ten Most Critical Web Application Security "
        "Risks. Wakefield, MA: OWASP Foundation, 2021. [Daring]. Tersedia: "
        "https://owasp.org/Top10/",
        "M. E. Whitman dan H. J. Mattord, Principles of Information Security, Edisi ke-7. "
        "Boston: Cengage Learning, 2021.",
        "International Organization for Standardization, ISO/IEC 27001:2022 Information Security, "
        "Cybersecurity and Privacy Protection — Information Security Management Systems — "
        "Requirements. Jenewa: ISO, 2022.",
        "P. Cichonski, T. Millar, T. Grance, dan K. Scarfone, Computer Security Incident Handling "
        "Guide, NIST Special Publication 800-61 Revision 2. Gaithersburg, MD: National Institute "
        "of Standards and Technology, 2012. doi: 10.6028/NIST.SP.800-61r2",
        "Center for Internet Security, CIS Oracle MySQL Community Server 8.0 Benchmark, Versi "
        "1.0.0. East Greenbush, NY: CIS, 2021.",
        "K. Scarfone, M. Souppaya, dan M. Sexton, Guide to Storage Encryption Technologies for "
        "End User Devices, NIST Special Publication 800-111. Gaithersburg, MD: National Institute "
        "of Standards and Technology, 2007. doi: 10.6028/NIST.SP.800-111",
        "Republik Indonesia, Undang-Undang Nomor 27 Tahun 2022 tentang Pelindungan Data Pribadi. "
        "Lembaran Negara Republik Indonesia Tahun 2022 Nomor 196.",
        "Republik Indonesia, Undang-Undang Nomor 16 Tahun 1997 tentang Statistik. Lembaran Negara "
        "Republik Indonesia Tahun 1997 Nomor 39.",
        "Oracle Corporation, MySQL 8.0 Reference Manual. Redwood City, CA: Oracle, 2024. "
        "[Daring]. Tersedia: https://dev.mysql.com/doc/refman/8.0/en/",
        "MITRE Corporation, MITRE ATT&CK Enterprise Matrix, Versi 15. McLean, VA: MITRE, 2024. "
        "[Daring]. Tersedia: https://attack.mitre.org/",
        "FIRST, Common Vulnerability Scoring System Version 3.1: Specification Document. Cary, "
        "NC: Forum of Incident Response and Security Teams, 2019. [Daring]. Tersedia: "
        "https://www.first.org/cvss/v3.1/specification-document",
        "HAProxy Technologies, HAProxy 2.8 Configuration Manual. Waltham, MA: HAProxy "
        "Technologies, 2023. [Daring]. Tersedia: https://docs.haproxy.org/2.8/configuration.html",
        "A. Hundley dan T. Ptacek, Cryptographic Right Answers. 2018. [Daring]. Tersedia: "
        "https://latacora.micro.blog/2018/04/03/cryptographic-right-answers.html",
        "United Nations Economic Commission for Europe, Statistical Disclosure Control for "
        "Microdata: A Practice Guide. Jenewa: UNECE, 2007.",
    ]
    for i, r in enumerate(refs, 1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = __import__("docx").shared.Inches(0.4)
        p.paragraph_format.first_line_indent = __import__("docx").shared.Inches(-0.4)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.add_run("[%d]  %s" % (i, r))
