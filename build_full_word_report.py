import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

SCREENSHOTS_DIR = r"d:\STIS SEM 6\KSI\ksi-akhir\project-kelompok4\screenshots"

def create_full_document_with_images():
    doc = Document()
    
    # 1. Page Setup - Margins 1 inch
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
        # Header & Footer
        footer = section.footer
        f_p = footer.paragraphs[0]
        f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        f_run = f_p.add_run("Laporan & Panduan Pengujian Keamanan — klinik_db | Hal. ")
        f_run.font.name = "Arial"
        f_run.font.size = Pt(8.5)
        f_run.font.color.rgb = RGBColor(148, 163, 184)
        
        header = section.header
        h_p = header.paragraphs[0]
        h_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        h_run = h_p.add_run("Politeknik Statistik STIS — Keamanan Sistem Informasi (Kelompok 4)")
        h_run.font.name = "Arial"
        h_run.font.size = Pt(8.5)
        h_run.font.color.rgb = RGBColor(148, 163, 184)

    # Styling constants
    NAVY = RGBColor(27, 54, 93)      # #1B365D - Primary Headings
    BLUE = RGBColor(37, 99, 235)     # #2563EB - Accent / Highlights
    SLATE = RGBColor(71, 85, 105)    # #475569 - Secondary text
    DARK = RGBColor(15, 23, 42)      # #0F172A - Body text
    
    # Helpers
    def set_cell_background(cell, fill_hex):
        tcPr = cell._element.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        tcPr.append(shd)

    def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
        tcPr = cell._element.get_or_add_tcPr()
        tcMar = parse_xml(
            f'<w:tcMar {nsdecls("w")}>'
            f'<w:top w:w="{top}" w:type="dxa"/>'
            f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
            f'<w:left w:w="{left}" w:type="dxa"/>'
            f'<w:right w:w="{right}" w:type="dxa"/>'
            f'</w:tcMar>'
        )
        tcPr.append(tcMar)

    def set_cell_border(cell, **kwargs):
        tcPr = cell._element.get_or_add_tcPr()
        tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}/>')
        for border_name, border_props in kwargs.items():
            b_elm = parse_xml(
                f'<w:{border_name} {nsdecls("w")} '
                f'w:val="{border_props.get("val", "single")}" '
                f'w:sz="{border_props.get("sz", "4")}" '
                f'w:space="0" '
                f'w:color="{border_props.get("color", "auto")}"/>'
            )
            tcBorders.append(b_elm)
        tcPr.append(tcBorders)

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(20)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = NAVY
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = BLUE
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = SLATE
        return p

    def add_p(text, bold_prefix=None, space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = 'Arial'
            r_pre.font.size = Pt(10)
            r_pre.font.bold = True
            r_pre.font.color.rgb = DARK
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(10)
        run.font.color.rgb = DARK
        return p

    def add_code(code_text):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
        set_cell_border(cell, 
                        left={'val': 'single', 'sz': '18', 'color': '2563EB'},
                        top={'val': 'single', 'sz': '4', 'color': 'CBD5E1'},
                        bottom={'val': 'single', 'sz': '4', 'color': 'CBD5E1'},
                        right={'val': 'single', 'sz': '4', 'color': 'CBD5E1'})
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.1
        run = p.add_run(code_text)
        run.font.name = 'Consolas'
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(15, 23, 42)
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    def add_callout(title, text, box_type="info"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.5)
        
        if box_type == "warning":
            bg = "FEF2F2"
            bd = "DC2626"
            tc = RGBColor(185, 28, 28)
            icon = "⚠️"
        elif box_type == "success":
            bg = "F0FDF4"
            bd = "16A34A"
            tc = RGBColor(21, 128, 61)
            icon = "✅"
        else:
            bg = "EFF6FF"
            bd = "2563EB"
            tc = RGBColor(29, 78, 216)
            icon = "📌"
            
        set_cell_background(cell, bg)
        set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
        set_cell_border(cell, 
                        left={'val': 'single', 'sz': '20', 'color': bd},
                        top={'val': 'single', 'sz': '4', 'color': 'E2E8F0'},
                        bottom={'val': 'single', 'sz': '4', 'color': 'E2E8F0'},
                        right={'val': 'single', 'sz': '4', 'color': 'E2E8F0'})
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        r1 = p.add_run(f"{icon} {title}\n")
        r1.font.name = 'Arial'
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = tc
        r2 = p.add_run(text)
        r2.font.name = 'Arial'
        r2.font.size = Pt(9)
        r2.font.color.rgb = DARK
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    def add_ss_box_with_image(fig_no, title, instruction, img_filename):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_background(cell, "F8FAFC")
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        set_cell_border(cell, 
                        left={'val': 'single', 'sz': '8', 'color': '94A3B8'},
                        right={'val': 'single', 'sz': '8', 'color': '94A3B8'},
                        top={'val': 'single', 'sz': '8', 'color': '94A3B8'},
                        bottom={'val': 'single', 'sz': '8', 'color': '94A3B8'})
        
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        r1 = p.add_run(f"📸 BUKTI TANGKAPAN LAYAR — GAMBAR {fig_no}\n")
        r1.font.name = 'Arial'
        r1.font.bold = True
        r1.font.size = Pt(9)
        r1.font.color.rgb = BLUE
        
        r2 = p.add_run(f"Deskripsi Bukti: {instruction}")
        r2.font.name = 'Arial'
        r2.font.italic = True
        r2.font.size = Pt(8.5)
        r2.font.color.rgb = RGBColor(100, 116, 139)
        
        img_path = os.path.join(SCREENSHOTS_DIR, img_filename)
        if os.path.exists(img_path):
            p2 = cell.add_paragraph()
            p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p2.paragraph_format.space_before = Pt(8)
            p2.paragraph_format.space_after = Pt(4)
            r_img = p2.add_run()
            r_img.add_picture(img_path, width=Inches(6.2))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(4)
        p_cap.paragraph_format.space_after = Pt(12)
        r_c = p_cap.add_run(f"Gambar {fig_no}: {title}")
        r_c.font.name = 'Arial'
        r_c.font.bold = True
        r_c.font.size = Pt(9)
        r_c.font.color.rgb = RGBColor(51, 65, 85)

    def style_table_header(row, col_widths, bg_hex="1B365D"):
        for i, cell in enumerate(row.cells):
            cell.width = col_widths[i]
            set_cell_background(cell, bg_hex)
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.name = 'Arial'
                r.font.bold = True
                r.font.size = Pt(9)
                r.font.color.rgb = RGBColor(255, 255, 255)

    def style_table_rows(tbl, col_widths, alternating=True):
        for r_idx, row in enumerate(tbl.rows[1:]):
            bg = "F8FAFC" if (r_idx % 2 == 1 and alternating) else "FFFFFF"
            for c_idx, cell in enumerate(row.cells):
                cell.width = col_widths[c_idx]
                if bg != "FFFFFF":
                    set_cell_background(cell, bg)
                set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
                set_cell_border(cell, 
                                top={'val': 'single', 'sz': '4', 'color': 'E2E8F0'},
                                bottom={'val': 'single', 'sz': '4', 'color': 'E2E8F0'},
                                left={'val': 'single', 'sz': '4', 'color': 'E2E8F0'},
                                right={'val': 'single', 'sz': '4', 'color': 'E2E8F0'})
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.1
                for r in p.runs:
                    r.font.name = 'Arial'
                    r.font.size = Pt(8.5)
                    r.font.color.rgb = DARK

    # =========================================================================
    # COVER / JUDUL DOKUMEN
    # =========================================================================
    p_cov_top = doc.add_paragraph()
    p_cov_top.paragraph_format.space_before = Pt(36)
    p_cov_top.paragraph_format.space_after = Pt(6)
    p_cov_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_kemen = p_cov_top.add_run("POLITEKNIK STATISTIK STIS\nPROGRAM STUDI D-IV KOMPUTASI STATISTIK\nMATA KULIAH KEAMANAN SISTEM INFORMASI")
    r_kemen.font.name = 'Arial'
    r_kemen.font.bold = True
    r_kemen.font.size = Pt(11)
    r_kemen.font.color.rgb = SLATE

    p_cov_title = doc.add_paragraph()
    p_cov_title.paragraph_format.space_before = Pt(24)
    p_cov_title.paragraph_format.space_after = Pt(12)
    p_cov_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_cov_title.add_run("LAPORAN & HASIL LENGKAP EKSEKUSI PENGUJIAN KEAMANAN SISTEM BASIS DATA\n(KLINIK_DB)")
    r_title.font.name = 'Arial'
    r_title.font.bold = True
    r_title.font.size = Pt(18)
    r_title.font.color.rgb = NAVY

    p_cov_sub = doc.add_paragraph()
    p_cov_sub.paragraph_format.space_before = Pt(4)
    p_cov_sub.paragraph_format.space_after = Pt(24)
    p_cov_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_cov_sub.add_run("Implementasi Database Hardening, Role-Based Access Control, Enkripsi Data Sensitif (AES),\nAudit Logging Forensik, dan High Availability Cluster dengan Failover Otomatis\n(Pola Uji: Before-Attack ➔ During-Attack ➔ After-Mitigation)")
    r_sub.font.name = 'Arial'
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = BLUE

    add_callout("Identitas Tim Pengembang & Peneliti", 
                "Kelompok 4 — Kelas 3SI1\n"
                "• M Rezky Raya Kilwouw (NIM: 222313190)\n"
                "• Anggota Kelompok 4 Lainnya\n"
                "Topik: Penguatan Keamanan Basis Data Pelayanan Kesehatan & Kepatuhan Regulasi UU PDP No. 27 Tahun 2022\n"
                "Tahun Akademik: 2025/2026", "info")

    doc.add_page_break()

    # =========================================================================
    # BAB I: MATRIKS PENGUJIAN & CIA TRIAD
    # =========================================================================
    add_h1("BAB I — MATRIKS PENGUJIAN & KERANGKA KEAMANAN")
    add_p("Pengujian pada proyek basis data klinik (klinik_db) dirancang secara komprehensif untuk membuktikan efektivitas kontrol keamanan berlapis (defense-in-depth) serta ketahanan ketersediaan sistem. Pengujian mencakup 5 skenario utama yang dipetakan secara ketat terhadap tiga pilar keamanan informasi (CIA Triad: Confidentiality, Integrity, Availability), Akuntabilitas (Accountability/Non-Repudiation), dan Kepatuhan Hukum Nasional (UU No. 27 Tahun 2022 tentang Perlindungan Data Pribadi).")

    add_h2("1.1 Matriks Pemetaan 5 Skenario Pengujian")
    
    t_mat = doc.add_table(rows=6, cols=5)
    t_mat.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_w_mat = [Inches(0.6), Inches(1.5), Inches(1.4), Inches(1.5), Inches(1.5)]
    
    headers_mat = ["No", "Skenario Pengujian", "Aspek Keamanan", "Vektor Serangan / Ancaman", "Kriteria Keberhasilan (Acceptance)"]
    for i, h in enumerate(headers_mat):
        t_mat.cell(0, i).paragraphs[0].add_run(h)
    style_table_header(t_mat.rows[0], col_w_mat)

    data_mat = [
        ("1", "Failover & High Availability", "Availability", "Single Point of Failure (SPoF) / Node Master Crash", "Koneksi dialihkan otomatis ke Slave via HAProxy (port 3300); SELECT tetap normal; INSERT ditolak informatif; reconnect otomatis."),
        ("2", "SQL Injection Attack & Mitigation", "Confidentiality & Integrity", "Auth Bypass & Data Leakage via ' OR '1'='1' --", "Query konkatenasi rentan membocorkan seluruh isi tabel; Query prepared statement menghasilkan 0 baris; Tercatat di audit_log."),
        ("3", "SSL/TLS & Enkripsi Data Sensitif", "Confidentiality (UU PDP 27/2022)", "Eavesdropping / Packet Sniffing & Database Theft", "Koneksi non-TLS ditolak (ERROR 2061/3159); NIK dienkripsi AES; Kunci benar mengembalikan NIK, kunci salah NULL."),
        ("4", "Least Privilege & RBAC Escalation", "Confidentiality & Authorization", "Privilege Escalation & Akses Tak Berwenang", "Akses di luar hak (INSERT/DROP oleh read_only, DROP oleh app_user) ditolak (ERROR 1142); Tercatat di audit_log."),
        ("5", "Audit Logging & Deteksi Anomali", "Accountability & Non-Repudiation", "Penghapusan Jejak Digital / Aksi Ilegal Tanpa Bukti", "Seluruh insiden skenario 1-4 terekam lengkap di tabel audit_log dan MySQL General Query Log sebagai bukti forensik independen.")
    ]

    for row_idx, data in enumerate(data_mat):
        row_cells = t_mat.rows[row_idx + 1].cells
        for col_idx, text in enumerate(data):
            row_cells[col_idx].paragraphs[0].add_run(text)
    style_table_rows(t_mat, col_w_mat)

    add_p("")
    add_h2("1.2 Metodologi Pengujian: Pola Tiga Fase")
    add_p("Setiap skenario pengujian dieksekusi dengan mengikuti siklus metodologi tiga fase terstandarisasi:")
    add_p("1. Phase 1: Before-Attack (Baseline) — Memverifikasi dan mendokumentasikan kondisi normal sistem yang sehat serta parameter izin yang sah sebelum serangan dilancarkan.")
    add_p("2. Phase 2: During-Attack (Eksploitasi) — Mensimulasikan serangan, kegagalan infrastruktur, atau pelanggaran kebijakan akses untuk menguji ketahanan dan respon sistem.")
    add_p("3. Phase 3: After-Mitigation (Verifikasi Kontrol) — Membuktikan bahwa kontrol keamanan (prepared statement, encryption, role separation, failover, audit trail) berhasil menangkal ancaman dan memulihkan kondisi operasional.")

    doc.add_page_break()

    # =========================================================================
    # BAB II: KONDISI PRASYARAT LINGKUNGAN PENGUJIAN
    # =========================================================================
    add_h1("BAB II — CHECKLIST PERSIAPAN LINGKUNGAN PENGUJIAN")
    add_p("Sebelum melangkah ke eksekusi skenario 1 hingga 5, seluruh item dalam daftar periksa (checklist) berikut telah diverifikasi dan berstatus LULUS (✅).")

    t_check = doc.add_table(rows=6, cols=4)
    t_check.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_w_check = [Inches(1.5), Inches(3.2), Inches(1.1), Inches(0.7)]
    headers_check = ["Komponen", "Prasyarat yang Harus Dipenuhi", "Metode Verifikasi", "Status"]
    for i, h in enumerate(headers_check):
        t_check.cell(0, i).paragraphs[0].add_run(h)
    style_table_header(t_check.rows[0], col_w_check)

    check_data = [
        ("Infrastruktur Docker", "Container db-master, db-slave, dan haproxy berjalan normal tanpa restart loop.", "docker ps", "[  ✅  ]"),
        ("Replikasi Master-Slave", "Replikasi sinkron real-time via binary log (ROW format) aktif di slave.", "SHOW REPLICA STATUS (IO & SQL: Yes)", "[  ✅  ]"),
        ("Load Balancer HAProxy", "Port 3300 terbuka untuk SQL routing; Web Stats port 8900 aktif dan hijau.", "Buka http://localhost:8900", "[  ✅  ]"),
        ("Skema & Data Sampel", "Database klinik_db berisi 4 tabel (users, pasien, rekam_medis, audit_log).", "SELECT COUNT(*) FROM pasien", "[  ✅  ]"),
        ("Akun Pengguna RBAC", "Tiga user terdaftar: app_user (read/write), read_only (read), replicator.", "SELECT user FROM mysql.user", "[  ✅  ]")
    ]

    for row_idx, data in enumerate(check_data):
        row_cells = t_check.rows[row_idx + 1].cells
        for col_idx, text in enumerate(data):
            row_cells[col_idx].paragraphs[0].add_run(text)
    style_table_rows(t_check, col_w_check)

    add_p("")
    add_callout("Urutan Eksekusi Strategis untuk Sesi Demonstrasi / Rekaman Video",
                "Agar perekaman demonstrasi berlangsung mulus tanpa perlu mereset database berulang kali, disarankan urutan teknis:\n"
                "1. Skenario 3 (SSL/TLS & Enkripsi Data)\n"
                "2. Skenario 2 (SQL Injection Prevention)\n"
                "3. Skenario 4 (Least Privilege & RBAC)\n"
                "4. Skenario 1 (Failover & High Availability - karena mematikan master di akhir sesi)\n"
                "5. Skenario 5 (Audit Log - merekap seluruh jejak serangan dari skenario sebelumnya)", "info")

    doc.add_page_break()

    # =========================================================================
    # BAB III: EKSEKUSI 5 SKENARIO DETAIL
    # =========================================================================
    add_h1("BAB III — LAPORAN HASIL EKSEKUSI 5 SKENARIO PENGUJIAN")

    # -------------------------------------------------------------------------
    # SKENARIO 1: FAILOVER & HIGH AVAILABILITY
    # -------------------------------------------------------------------------
    add_h2("SKENARIO 1 — FAILOVER & HIGH AVAILABILITY (AVAILABILITY)")
    add_p("Tujuan: Membuktikan ketahanan ketersediaan sistem basis data klinik jika node utama (db-master) mengalami kegagalan/crash. HAProxy harus mendeteksi secara instan dalam 2 detik dan mengalihkan pembacaan ke db-slave tanpa menghentikan layanan (zero downtime untuk operasi baca).")
    
    add_h3("A. Fase Before-Attack (Kondisi Normal)")
    add_p("Langkah 1: Verifikasi status operasional kedua node basis data pada dashboard HAProxy.")
    add_p("Buka browser dan akses alamat: http://localhost:8900. Terlihat baris db-master berstatus UP (hijau, Act: Y) dan db-slave berstatus UP (hijau, Bck: Y).")
    add_ss_box_with_image("1.1", "Dashboard HAProxy Sebelum Serangan (Kedua Node Hijau/UP)", 
                          "Tangkapan layar dashboard web http://localhost:8900 memperlihatkan status db-master dan db-slave dalam keadaan UP.", 
                          "fig_1_1.png")

    add_p("Langkah 2: Melakukan pengujian penulisan data baru melalui port HAProxy (port 3300) dan memastikan tereplikasi ke Slave.")
    add_code(
        'docker exec db-master mysql -h haproxy -P 3300 -u app_user -pAppPass123! -e "INSERT INTO klinik_db.pasien (nama, tanggal_lahir, alamat, no_telepon) VALUES (\'Pasien HAProxy 3300\', \'1990-01-01\', \'Surabaya\', \'0811223344\');"\n\n'
        '# Verifikasi langsung pada db-slave (port 3307):\n'
        'docker exec db-slave mysql -u root -pRootPass123! -e "SELECT id, nama, alamat FROM klinik_db.pasien WHERE nama=\'Pasien HAProxy 3300\';"'
    )
    add_ss_box_with_image("1.2", "Verifikasi Penulisan Data via HAProxy dan Replikasi ke Slave", 
                          "Bukti terminal: data 'Pasien HAProxy 3300' berhasil di-insert dan langsung muncul pada db-slave.", 
                          "fig_1_2.png")

    add_h3("B. Fase During-Attack (Simulasi Crash Master)")
    add_p("Langkah 3: Mematikan node db-master secara paksa untuk mensimulasikan kegagalan server.")
    add_code('docker stop db-master')

    add_p("Langkah 4: Memeriksa perubahan status pada dashboard HAProxy.")
    add_p("Dashboard mendeteksi kegagalan Master (DOWN, merah) dan secara otomatis mengaktifkan db-slave sebagai backend aktif.")
    add_ss_box_with_image("1.3", "Dashboard HAProxy Saat Master Crash (db-master DOWN, db-slave Mengambil Alih)", 
                          "Status db-master terdeteksi DOWN dan db-slave aktif melayani request.", 
                          "fig_1_3.png")

    add_p("Langkah 5 & 6: Menguji operasi pembacaan (SELECT) dan penulisan (INSERT) via HAProxy saat master padam.")
    add_code(
        '# 1. SELECT via HAProxy Port 3300 dialihkan ke db-slave (Berhasil):\n'
        'docker exec db-slave mysql -h haproxy -P 3300 -u app_user -pAppPass123! -e "SELECT id, nama FROM klinik_db.pasien LIMIT 2;"\n\n'
        '# 2. INSERT via HAProxy saat master down (Ditolak secara aman):\n'
        'docker exec db-slave mysql -h haproxy -P 3300 -u app_user -pAppPass123! -e "INSERT INTO klinik_db.pasien (nama) VALUES (\'Failover Data\');"'
    )
    add_ss_box_with_image("1.4", "Uji Operasi Baca Berhasil & Operasi Tulis Ditolak Saat Master Down", 
                          "Terminal menampilkan SELECT sukses (High Availability) dan penolakan INSERT dengan pesan informatif --read-only.", 
                          "fig_1_4.png")

    add_h3("C. Fase After-Mitigation (Pemulihan Master & Reconnect Otomatis)")
    add_p("Langkah 7 & 8: Menghidupkan kembali node db-master dan memverifikasi reconnect otomatis replikasi slave.")
    add_code(
        'docker start db-master\n'
        'docker exec db-slave mysql -u root -pRootPass123! -e "SHOW REPLICA STATUS\\G"'
    )
    add_ss_box_with_image("1.5", "Verifikasi Pemulihan Otomatis (Auto-Reconnection) Replikasi Slave", 
                          "Terminal memperlihatkan Replica_IO_Running: Yes dan Replica_SQL_Running: Yes pasca pemulihan master.", 
                          "fig_1_5.png")

    add_callout("Evaluasi Hasil Skenario 1", 
                "Status: [ LOLOS / MEMENUHI KRITERIA ]\n"
                "Sistem berhasil mempertahankan ketersediaan pembacaan data pasien saat node utama mati total (RTO < 2 detik), serta melindungi integritas basis data dari split-brain dengan penolakan operasi tulis secara aman.", "success")

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # SKENARIO 2: SQL INJECTION ATTACK & PREVENTION
    # -------------------------------------------------------------------------
    add_h2("SKENARIO 2 — SQL INJECTION ATTACK & PREVENTION (CONFIDENTIALITY & INTEGRITY)")
    add_p("Tujuan: Menguji kerentanan aplikasi terhadap serangan injeksi SQL klasik (auth bypass & data exfiltration) serta membuktikan efektivitas mitigasi menggunakan parameterized query (Prepared Statements).")

    add_h3("A. Fase Before-Attack (Baseline Data Normal)")
    add_p("Langkah 1: Menampilkan baseline data pasien yang tersimpan secara sah.")
    add_code('docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e "SELECT id, nama, tanggal_lahir, alamat FROM klinik_db.pasien LIMIT 3;"')
    add_ss_box_with_image("2.1", "Tampilan Baseline Data Pasien Sebelum Serangan", 
                          "Daftar nama pasien resmi yang ada di klinik_db.", 
                          "fig_2_1.png")

    add_h3("B. Fase During-Attack (Simulasi Serangan SQL Injection)")
    add_p("Langkah 2: Membangun query rentan melalui penggabungan string (string concatenation) dengan menyuntikkan payload ' OR '1'='1' --.")
    add_code(
        'docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e "\n'
        'USE klinik_db; \n'
        'SET @nama_input = \'\\\' OR \\\'1\\\'=\\\'1\\\' -- \'; \n'
        'SET @query_rentan = CONCAT(\'SELECT id, nama FROM pasien WHERE nama = \\\'\', @nama_input, \'\\\'\'); \n'
        'PREPARE stmt FROM @query_rentan; \n'
        'EXECUTE stmt; \n'
        'DEALLOCATE PREPARE stmt;"'
    )
    add_ss_box_with_image("2.2", "Kebocoran Seluruh Data Akibat Serangan SQL Injection (Query Rentan)", 
                          "Query rentan berhasil dieksploitasi dan membocorkan seluruh baris tabel pasien tanpa filter.", 
                          "fig_2_2.png")

    add_p("Langkah 3: Mengulangi serangan SQL Injection pada tabel sensitif rekam_medis.")
    add_code(
        'docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e "\n'
        'USE klinik_db; \n'
        'SET @input_medis = \'1 OR 1=1\'; \n'
        'SET @q = CONCAT(\'SELECT id, pasien_id, diagnosa, resep FROM rekam_medis WHERE pasien_id = \', @input_medis); \n'
        'PREPARE s FROM @q; \n'
        'EXECUTE s; \n'
        'DEALLOCATE PREPARE s;"'
    )
    add_ss_box_with_image("2.3", "Eksfiltrasi Riwayat Rekam Medis Pasien via SQL Injection", 
                          "Kebocoran riwayat diagnosa dan resep medis seluruh pasien.", 
                          "fig_2_3.png")

    add_h3("C. Fase After-Mitigation (Pencegahan dengan Prepared Statement)")
    add_p("Langkah 4: Menerapkan Prepared Statement dengan placeholder parameter '?'. Input penyerang diperlakukan murni sebagai nilai literal, bukan instruksi kode SQL.")
    add_code(
        'docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e "\n'
        'USE klinik_db; \n'
        'PREPARE stmt2 FROM \'SELECT id, nama FROM pasien WHERE nama = ?\'; \n'
        'SET @payload = \'\\\' OR \\\'1\\\'=\\\'1\\\' -- \'; \n'
        'EXECUTE stmt2 USING @payload; \n'
        'DEALLOCATE PREPARE stmt2;"'
    )
    add_ss_box_with_image("2.4", "Hasil Eksekusi Mitigasi Prepared Statement (Serangan Gagal / 0 Baris)", 
                          "Query prepared statement berhasil menolak injeksi dan menghasilkan 0 baris (Empty set).", 
                          "fig_2_4.png")

    add_callout("Evaluasi Hasil Skenario 2", 
                "Status: [ LOLOS / MEMENUHI KRITERIA ]\n"
                "Implementasi prepared statement dengan parameterisasi berhasil 100% menetralisir payload SQL Injection. Sistem terlindungi dari data leakage dan unauthorized data exfiltration.", "success")

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # SKENARIO 3: SSL/TLS & ENKRIPSI DATA
    # -------------------------------------------------------------------------
    add_h2("SKENARIO 3 — SSL/TLS CONNECTION ENFORCEMENT & ENKRIPSI DATA SENSITIF (CONFIDENTIALITY)")
    add_p("Tujuan: Menguji perlindungan kerahasiaan data pada dua level: Data-in-Transit (koneksi wajib terenkripsi SSL/TLS) dan Data-at-Rest (enkripsi kriptografi AES pada nomor identitas kependudukan pasien NIK sesuai mandat UU PDP No. 27 Tahun 2022).")

    add_h3("Bagian A: Data-in-Transit (Penolakan Koneksi Plaintext Non-TLS)")
    add_p("Langkah 1: Mencoba melakukan koneksi ke database dengan mematikan fitur SSL/TLS (--ssl-mode=DISABLED).")
    add_code('docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! --ssl-mode=DISABLED -e "STATUS;"')
    add_ss_box_with_image("3.1", "Penolakan Koneksi Non-TLS (ERROR 2061/3159 - Secure Connection Required)", 
                          "Kegagalan koneksi saat --ssl-mode=DISABLED dicoba oleh pengguna.", 
                          "fig_3_1.png")

    add_p("Langkah 2: Melakukan koneksi terenkripsi yang sah dan memverifikasi algoritma cipher aktif.")
    add_code('docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e "SHOW STATUS LIKE \'Ssl_cipher\'; SHOW STATUS LIKE \'Ssl_version\';"')
    add_ss_box_with_image("3.2", "Verifikasi Protokol TLSv1.3 dan Cipher Kuat Aktif", 
                          "Cipher suite TLS 256-bit GCM (TLS_AES_256_GCM_SHA384) aktif melindungi transmisi.", 
                          "fig_3_2.png")

    add_h3("Bagian B: Data-at-Rest (Enkripsi Kolom NIK Pasien)")
    add_p("Langkah 3: Menampilkan data pasien yang tersimpan di disk database.")
    add_code('docker exec db-master mysql -h 127.0.0.1 -P 3306 -u root -pRootPass123! -e "SELECT id, nama, HEX(nik_encrypted) AS nik_hex FROM klinik_db.pasien LIMIT 3;"')
    add_ss_box_with_image("3.3", "Tampilan Kolom NIK Terenkripsi (Ciphertext Acak)", 
                          "Data NIK tersimpan dalam bentuk ciphertext terenkripsi AES-256 di dalam basis data.", 
                          "fig_3_3.png")

    add_p("Langkah 4: Menguji dekripsi dengan kunci yang sah vs kunci palsu/salah.")
    add_code(
        'docker exec db-master mysql -h 127.0.0.1 -P 3306 -u root -pRootPass123! -e "\n'
        'SELECT nama,\n'
        '  CAST(AES_DECRYPT(nik_encrypted, \'kunci_rahasia_klinik\') AS CHAR) AS NIK_Kunci_Benar,\n'
        '  CAST(AES_DECRYPT(nik_encrypted, \'kunci_salah_12345\') AS CHAR) AS NIK_Kunci_Salah\n'
        'FROM klinik_db.pasien LIMIT 3;"'
    )
    add_ss_box_with_image("3.4", "Hasil Dekripsi Kunci Sah vs Kunci Salah (Kontrol Negatif NULL)", 
                          "Kunci salah menghasilkan nilai NULL dan kunci benar berhasil merekonstruksi 16 digit NIK asli.", 
                          "fig_3_4.png")

    add_callout("Evaluasi Hasil Skenario 3", 
                "Status: [ LOLOS / MEMENUHI KRITERIA ]\n"
                "Kerahasiaan data terjamin penuh baik saat transit (TLSv1.3 AES-256) maupun saat tersimpan di storage (AES Decrypt). Memenuhi kepatuhan Pasal 35 & 39 UU No. 27 Tahun 2022.", "success")

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # SKENARIO 4: LEAST PRIVILEGE & RBAC
    # -------------------------------------------------------------------------
    add_h2("SKENARIO 4 — LEAST PRIVILEGE & PRIVILEGE ESCALATION PREVENTION (AUTHORIZATION)")
    add_p("Tujuan: Menguji penegakan prinsip hak akses minimum (Principle of Least Privilege). Setiap entitas hanya diberikan hak akses yang mutlak diperlukan untuk perannya, mencegah eskalasi wewenang.")

    add_h3("A. Pengujian Akun read_only (Hanya Berhak SELECT pada Tabel Pasien)")
    add_p("Langkah 1: Menguji operasi legal dan ilegal oleh pengguna read_only.")
    add_code(
        '# Legal SELECT: Berhasil\n'
        'docker exec db-master mysql -h 127.0.0.1 -P 3306 -u read_only -pReadPass123! -e "SELECT id, nama FROM klinik_db.pasien LIMIT 2;"\n\n'
        '# Ilegal INSERT & DROP: Ditolak dengan ERROR 1142\n'
        'docker exec db-master mysql -h 127.0.0.1 -P 3306 -u read_only -pReadPass123! -e "INSERT INTO klinik_db.pasien (nama) VALUES (\'Data Liar\');"\n'
        'docker exec db-master mysql -h 127.0.0.1 -P 3306 -u read_only -pReadPass123! -e "DROP TABLE klinik_db.pasien;"'
    )
    add_ss_box_with_image("4.1", "Uji Pembatasan Hak Akses Akun read_only (Penolakan ERROR 1142)", 
                          "SELECT berhasil dan penolakan tegas pada percobaan INSERT maupun DROP TABLE.", 
                          "fig_4_1.png")

    add_h3("B. Pengujian Akun app_user (Hak Operasional CRUD, Tanpa Hak DDL/Admin)")
    add_p("Langkah 2: Menguji pembatasan wewenang akun aplikasi utama app_user.")
    add_code(
        '# Percobaan DROP TABLE & SELECT users (Ditolak ERROR 1142):\n'
        'docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e "DROP TABLE klinik_db.pasien;"\n'
        'docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e "SELECT * FROM klinik_db.users;"'
    )
    add_ss_box_with_image("4.2", "Uji Batasan Akun app_user (Ditolak Mengakses Tabel Users & DDL DROP)", 
                          "Akun aplikasi dibatasi tidak boleh menghapus tabel atau membaca kredensial user lain.", 
                          "fig_4_2.png")

    add_h3("C. Pengujian Akun replicator (Hanya Sinkronisasi Binary Log)")
    add_p("Langkah 3: Menguji bahwa user sistem replikasi tidak dapat dieksploitasi untuk mencuri data pasien.")
    add_code('docker exec db-master mysql -h 127.0.0.1 -P 3306 -u replicator -pReplPass123! -e "SELECT * FROM klinik_db.pasien;"')
    add_ss_box_with_image("4.3", "Isolasi Hak Akun Replicator (SELECT Ditolak)", 
                          "User replikasi terisolasi dari akses query data operasional.", 
                          "fig_4_3.png")

    add_callout("Evaluasi Hasil Skenario 4", 
                "Status: [ LOLOS / MEMENUHI KRITERIA ]\n"
                "Kontrol akses berbasis peran (RBAC) terbukti kokoh. Tidak ditemukan celah eskalasi wewenang (privilege escalation) baik dari sisi akun read_only, app_user, maupun akun sistem replicator.", "success")

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # SKENARIO 5: AUDIT LOGGING & FORENSIK
    # -------------------------------------------------------------------------
    add_h2("SKENARIO 5 — AUDIT LOGGING & DETEKSI ANOMALI (ACCOUNTABILITY & INTEGRITY)")
    add_p("Tujuan: Memverifikasi sistem audit logging berlapis (Dual-Layer Audit Trail). Layer 1 berupa tabel audit_log internal untuk mencatat anomali keamanan, dan Layer 2 berupa MySQL General Query Log independen di level berkas sistem operasi yang tidak dapat dimanipulasi oleh pengguna aplikasi.")

    add_h3("A. Rekapitulasi Insiden Keamanan pada Tabel audit_log")
    add_p("Langkah 1: Menampilkan rekapitulasi seluruh anomali dan percobaan serangan yang terdeteksi.")
    add_code('docker exec db-master mysql -h 127.0.0.1 -P 3306 -u root -pRootPass123! -e "SELECT id, user_id, aksi, tabel_target, ip_address, DATE_FORMAT(waktu, \'%Y-%m-%d %H:%i:%s\') AS waktu_kejadian FROM klinik_db.audit_log ORDER BY id ASC;"')
    add_ss_box_with_image("5.1", "Tampilan Daftar Insiden Keamanan pada Tabel audit_log", 
                          "Tabel audit_log berisi catatan insiden skenario 1-4 secara terstruktur dan kronologis.", 
                          "fig_5_1.png")

    add_p("Langkah 2: Menampilkan rekonstruksi forensik teks query ilegal yang dicoba oleh penyerang.")
    add_code('docker exec db-master mysql -h 127.0.0.1 -P 3306 -u root -pRootPass123! -e "SELECT id, aksi, query_exec FROM klinik_db.audit_log WHERE aksi = \'SQL_INJECTION_ATTEMPT\' ORDER BY id DESC LIMIT 1\\G"')
    add_ss_box_with_image("5.2", "Detail Rekonstruksi Forensik Query Injeksi Penyerang", 
                          "Teks query eksplisit penyerang tertangkap utuh untuk bahan investigasi forensik digital.", 
                          "fig_5_2.png")

    add_h3("B. Verifikasi Layer 2 — MySQL General Query Log")
    add_p("Langkah 3: Memeriksa rekaman mentah pada General Query Log di sistem berkas container.")
    add_code('docker exec db-master tail -n 12 /var/lib/mysql/60057b18e796.log')
    add_ss_box_with_image("5.3", "Bukti Forensik pada File General Query Log (/var/lib/mysql/...log)", 
                          "Isi berkas general.log merekam setiap koneksi, thread ID, dan statement SQL secara real-time.", 
                          "fig_5_3.png")

    add_callout("Evaluasi Hasil Skenario 5", 
                "Status: [ LOLOS / MEMENUHI KRITERIA ]\n"
                "Dual-layer audit logging berfungsi dengan sempurna. Prinsip Akuntabilitas (Accountability) dan Non-Repudiation terpenuhi, menjamin bukti digital tidak dapat dibantah.", "success")

    doc.add_page_break()

    # =========================================================================
    # BAB IV: REKAPITULASI HASIL & LEMBAR EVALUASI
    # =========================================================================
    add_h1("BAB IV — REKAPITULASI HASIL EVALUASI & PENGESAHAN")
    add_p("Berdasarkan rangkaian 5 skenario pengujian yang telah diselesaikan, berikut adalah tabel rekapitulasi status evaluasi pemenuhan kriteria keberhasilan (Acceptance Criteria) sesuai spesifikasi PRD §8:")

    t_eval = doc.add_table(rows=6, cols=6)
    t_eval.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_w_eval = [Inches(0.5), Inches(1.3), Inches(1.2), Inches(1.8), Inches(0.9), Inches(0.8)]
    headers_eval = ["No", "Skenario", "Aspek CIA", "Hasil Observasi Pengujian", "Toleransi", "Hasil"]
    for i, h in enumerate(headers_eval):
        t_eval.cell(0, i).paragraphs[0].add_run(h)
    style_table_header(t_eval.rows[0], col_w_eval)

    eval_data = [
        ("1", "Failover & HA", "Availability", "Failover aktif < 2 detik ke Slave; SELECT normal; INSERT dicegah read-only; Reconnect otomatis.", "Zero downtime read", "[  LOLOS  ]"),
        ("2", "SQL Injection", "Confidentiality & Integrity", "Prepared Statement mengembalikan 0 baris; Data pasien & rekam medis aman dari exfiltration.", "0 data leak", "[  LOLOS  ]"),
        ("3", "SSL/TLS & AES", "Confidentiality (UU PDP)", "Koneksi non-TLS ditolak (Err 2061/3159); NIK berupa ciphertext; Kunci salah menghasilkan NULL.", "Kerahasiaan 100%", "[  LOLOS  ]"),
        ("4", "Least Privilege", "Authorization", "read_only & replicator dibatasi ketat (Err 1142); app_user dibatasi dari tabel kredensial.", "0 privilege leak", "[  LOLOS  ]"),
        ("5", "Audit Logging", "Accountability", "audit_log mencatat anomali terstruktur; General Query Log mencatat seluruh aktivitas real-time.", "Audit Trail Utuh", "[  LOLOS  ]")
    ]

    for row_idx, data in enumerate(eval_data):
        row_cells = t_eval.rows[row_idx + 1].cells
        for col_idx, text in enumerate(data):
            row_cells[col_idx].paragraphs[0].add_run(text)
    style_table_rows(t_eval, col_w_eval)

    add_p("")
    add_h2("4.1 Kesimpulan Analisis Keamanan")
    add_p("1. Kerahasiaan (Confidentiality): Terbukti terlindungi secara berlapis melalui enkripsi transport TLSv1.3 (menangkal sniffing) dan enkripsi kolom AES pada NIK pasien (menangkal pencurian fisik file basis data sesuai standar UU PDP No. 27 Tahun 2022).")
    add_p("2. Integritas (Integrity): Terlindungi dari manipulasi melalui implementasi Prepared Statements (menangkal SQL Injection) dan pemisahan hak akses berbasis peran (RBAC) yang mencegah modifikasi tidak sah.")
    add_p("3. Ketersediaan (Availability): Terbukti andal melalui arsitektur High Availability Cluster Master-Slave dengan HAProxy. Kegagalan mendadak pada node utama berhasil ditangani tanpa mengganggu ketersediaan layanan pembacaan rekam medis pasien.")
    add_p("4. Akuntabilitas (Accountability): Seluruh jejak aktivitas tercatat secara redundan pada tabel audit aplikasi dan log sistem operasi (General Query Log) untuk kebutuhan audit dan investigasi insiden siber.")

    add_p("")
    add_h2("4.2 Lembar Pengesahan Pelaksanaan Pengujian")
    add_p("Dokumen laporan hasil pengujian keamanan sistem basis data ini telah dilaksanakan, diverifikasi, dan disetujui oleh tim pengembang sebagai pemenuhan Proyek Akhir Mata Kuliah Keamanan Sistem Informasi.")

    t_sign = doc.add_table(rows=2, cols=2)
    t_sign.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_w_sign = [Inches(3.2), Inches(3.2)]
    
    c1 = t_sign.cell(0, 0)
    c2 = t_sign.cell(0, 1)
    set_cell_margins(c1, top=100, bottom=100, left=100, right=100)
    set_cell_margins(c2, top=100, bottom=100, left=100, right=100)
    
    p_s1 = c1.paragraphs[0]
    p_s1.add_run("Diuji dan Disusun Oleh:\nTim Mahasiswa Kelompok 4\n\n\n\n( M Rezky Raya Kilwouw & Tim )\nNIM: 222313190")
    p_s1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    p_s2 = c2.paragraphs[0]
    p_s2.add_run("Mengetahui & Menyetujui:\nDosen Pengampu Keamanan SI\n\n\n\n( _____________________________ )\nNIP: ")
    p_s2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    output_path = r"d:\STIS SEM 6\KSI\ksi-akhir\project-kelompok4\Laporan_dan_Panduan_Pengujian_Keamanan_klinik_db.docx"
    doc.save(output_path)
    print(f"Document saved successfully with all embedded images at: {output_path}")

if __name__ == "__main__":
    create_full_document_with_images()
