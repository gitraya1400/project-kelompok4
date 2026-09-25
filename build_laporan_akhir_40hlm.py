"""
Generator Script: Laporan Akhir Proyek Keamanan Sistem Informasi (~40 Halaman)
Menggunakan screenshot ASLI dari 'pengujian sementara.docx' (22 Tangkapan Layar Asli)
dan mengikuti seluruh alur pengujian serta data aktual kelompok.

Target file:
1. Proposal_Proyek_Akhir_Keamanan_SI.docx (di folder projek)
2. Laporan_Akhir_Proyek_Keamanan_SI_Kelompok4.docx (dihasilkan di folder projek)
"""

import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

# Path relatif terhadap lokasi skrip ini, supaya jalan di mesin semua
# anggota tim (sebelumnya hardcode ke folder yang hanya ada di 1 laptop).
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_SCREENSHOTS_DIR = os.path.join(_BASE_DIR, "user_screenshots")

def generate_report(output_paths):
    doc = Document()
    
    # -------------------------------------------------------------
    # PAGE SETUP - Standard Academic Margins
    # -------------------------------------------------------------
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.25)
        section.right_margin = Inches(1.0)
        
        # Footer
        footer = section.footer
        f_p = footer.paragraphs[0]
        f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        f_run = f_p.add_run("Laporan Proyek Akhir — Keamanan Sistem Informasi | ")
        f_run.font.name = "Arial"
        f_run.font.size = Pt(8.5)
        f_run.font.color.rgb = RGBColor(148, 163, 184)
        
        # Header
        header = section.header
        h_p = header.paragraphs[0]
        h_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        h_run = h_p.add_run("Politeknik Statistika STIS — D-IV Komputasi Statistik (Kelompok 4)")
        h_run.font.name = "Arial"
        h_run.font.size = Pt(8.5)
        h_run.font.color.rgb = RGBColor(148, 163, 184)

    # Styling constants
    NAVY = RGBColor(27, 54, 93)      # Primary Headings
    BLUE = RGBColor(37, 99, 235)     # Accent / Highlights
    SLATE = RGBColor(71, 85, 105)    # Secondary metadata
    DARK = RGBColor(15, 23, 42)      # Body text
    
    # XML Helpers for Word Tables & Paragraphs
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
        p.paragraph_format.space_before = Pt(22)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Arial'
        run.font.size = Pt(15)
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
        run.font.size = Pt(12.5)
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
        run.font.size = Pt(10.5)
        run.font.bold = True
        run.font.color.rgb = SLATE
        return p

    def add_p(text, bold_prefix=None, space_after=6, italic=False):
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
        run.font.italic = italic
        run.font.color.rgb = DARK
        return p

    def add_callout(title, text, box_type="info"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.25)
        
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

    def add_code(code_text):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.25)
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
        run.font.size = Pt(8.5)
        run.font.color.rgb = RGBColor(15, 23, 42)
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    def add_ss_box_with_image(fig_no, title, instruction, img_filename):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.25)
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
        
        r2 = p.add_run(f"Deskripsi Bukti Eksekusi: {instruction}")
        r2.font.name = 'Arial'
        r2.font.italic = True
        r2.font.size = Pt(8.5)
        r2.font.color.rgb = RGBColor(100, 116, 139)
        
        img_path = os.path.join(USER_SCREENSHOTS_DIR, img_filename)
        if os.path.exists(img_path):
            p2 = cell.add_paragraph()
            p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p2.paragraph_format.space_before = Pt(8)
            p2.paragraph_format.space_after = Pt(4)
            r_img = p2.add_run()
            # Set width to 6.0 inches for perfect fit
            r_img.add_picture(img_path, width=Inches(6.0))
        
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
    # COVER / HALAMAN SAMPUL
    # =========================================================================
    p_cov_top = doc.add_paragraph()
    p_cov_top.paragraph_format.space_before = Pt(36)
    p_cov_top.paragraph_format.space_after = Pt(6)
    p_cov_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_kemen = p_cov_top.add_run("POLITEKNIK STATISTIKA STIS\nPROGRAM STUDI D-IV KOMPUTASI STATISTIK\nTAHUN AKADEMIK 2025/2026")
    r_kemen.font.name = 'Arial'
    r_kemen.font.bold = True
    r_kemen.font.size = Pt(11)
    r_kemen.font.color.rgb = SLATE

    p_cov_title = doc.add_paragraph()
    p_cov_title.paragraph_format.space_before = Pt(28)
    p_cov_title.paragraph_format.space_after = Pt(12)
    p_cov_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_cov_title.add_run("LAPORAN AKHIR PROYEK KEAMANAN SISTEM INFORMASI\nIMPLEMENTASI DATABASE HARDENING, ENKRIPSI DATA-AT-REST, ROLE-BASED ACCESS CONTROL, AUDIT LOGGING FORENSIK, DAN HIGH AVAILABILITY CLUSTER DENGAN FAILOVER OTOMATIS PADA BASIS DATA REKAM MEDIS (KLINIK_DB)")
    r_title.font.name = 'Arial'
    r_title.font.bold = True
    r_title.font.size = Pt(15.5)
    r_title.font.color.rgb = NAVY

    p_cov_sub = doc.add_paragraph()
    p_cov_sub.paragraph_format.space_before = Pt(6)
    p_cov_sub.paragraph_format.space_after = Pt(28)
    p_cov_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_cov_sub.add_run("Pengujian Menyeluruh Ketahanan CIA Triad Berdasarkan Regulasi Perlindungan Data Pribadi (UU RI No. 27 Tahun 2022), Standar NIST SP 800-111, dan CIS MySQL 8.0 Benchmark\n(Metodologi Evaluasi: Before-Attack ➔ During-Attack ➔ After-Mitigation)")
    r_sub.font.name = 'Arial'
    r_sub.font.size = Pt(10.5)
    r_sub.font.color.rgb = BLUE

    add_callout("Identitas Tim Peneliti & Pengembang (Kelompok 4)", 
                "Disusun untuk memenuhi tugas Proyek Akhir Mata Kuliah Keamanan Sistem Informasi:\n\n"
                "• M Rezky Raya Kilwouw (NIM: 222313190)\n"
                "• Anggota Kelompok 4 Lainnya\n"
                "Kelas: 3SI1 | Program Studi: D-IV Komputasi Statistik\n"
                "Dosen Pengampu: Tim Dosen Keamanan Sistem Informasi Politeknik Statistika STIS\n"
                "Lokasi: Jakarta | Tanggal Penyelesaian: September 2026", "info")

    doc.add_page_break()

    # =========================================================================
    # KATA PENGANTAR
    # =========================================================================
    add_h1("KATA PENGANTAR")
    add_p("Puji dan syukur kami panjatkan ke hadirat Tuhan Yang Maha Esa atas segala limpahan rahmat, taufik, dan hidayah-Nya, sehingga Laporan Akhir Proyek Mata Kuliah Keamanan Sistem Informasi yang berjudul \"Implementasi Database Hardening, Enkripsi Data-at-Rest, Role-Based Access Control, Audit Logging Forensik, dan High Availability Cluster dengan Failover Otomatis pada Basis Data Rekam Medis (klinik_db)\" ini dapat diselesaikan dengan baik dan tepat waktu.")
    add_p("Laporan proyek akhir ini disusun sebagai bentuk pertanggungjawaban akademis dan implementasi praktis atas materi keamanan basis data, arsitektur ketersediaan tinggi (high availability), mitigasi kerentanan perangkat lunak, serta kepatuhan terhadap regulasi keamanan data nasional dan internasional. Proyek ini membedah secara langsung kerentanan bawaan pada sistem basis data relasional (RDBMS) MySQL/MariaDB yang sering digunakan pada fasilitas pelayanan kesehatan, sekaligus membuktikan efektivitas kontrol keamanan berlapis (defense-in-depth) yang dibangun.")
    add_p("Keberhasilan penyusunan laporan dan implementasi sistem ini tidak lepas dari bimbingan, arahan, dan dukungan dari berbagai pihak. Oleh karena itu, tim penyusun ingin menyampaikan terima kasih yang sebesar-besarnya kepada:")
    add_p("1. Dosen Pengampu Mata Kuliah Keamanan Sistem Informasi Politeknik Statistika STIS yang telah memberikan wawasan teoritis, standar evaluasi industri, serta bimbingan kritis selama proses pengerjaan proyek.")
    add_p("2. Seluruh dosen dan instruktur Program Studi D-IV Komputasi Statistik Politeknik Statistika STIS yang telah memfasilitasi kurikulum dan lingkungan akademik yang menunjang.")
    add_p("3. Rekan-rekan mahasiswa Kelas 3SI1 yang telah saling bertukar gagasan, memberikan masukan teknis, dan mendukung kelancaran simulasi lingkungan pengujian.")
    add_p("Penyusun menyadari bahwa laporan ini masih memiliki keterbatasan. Kritik dan saran yang membangun sangat kami harapkan guna penyempurnaan di masa yang akan datang. Semoga laporan ini dapat memberikan kontribusi nyata bagi pengembangan arsitektur basis data kesehatan yang aman dan andal di Indonesia.")
    
    p_kp_date = doc.add_paragraph()
    p_kp_date.paragraph_format.space_before = Pt(14)
    p_kp_date.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_kpd = p_kp_date.add_run("Jakarta, September 2026\n\n\nTim Penyusun (Kelompok 4 — 3SI1)")
    r_kpd.font.name = 'Arial'
    r_kpd.font.size = Pt(9.5)
    r_kpd.font.italic = True

    doc.add_page_break()

    # =========================================================================
    # DAFTAR ISI, TABEL, GAMBAR
    # =========================================================================
    add_h1("DAFTAR ISI")
    
    daftar_isi_items = [
        ("HALAMAN JUDUL / SAMPUL", "i"),
        ("KATA PENGANTAR", "ii"),
        ("DAFTAR ISI", "iii"),
        ("DAFTAR TABEL", "iv"),
        ("DAFTAR GAMBAR", "v"),
        ("BAB I PENDAHULUAN", "7"),
        ("   1.1 Latar Belakang Masalah & Urgensi Keamanan Data Medis", "7"),
        ("   1.2 Rumusan Masalah Proyek", "9"),
        ("   1.3 Tujuan Proyek", "9"),
        ("   1.4 Manfaat Proyek Secara Akademis dan Praktis", "10"),
        ("   1.5 Ruang Lingkup dan Batasan Sistem", "10"),
        ("BAB II TINJAUAN PUSTAKA & LANDASAN TEORI", "11"),
        ("   2.1 Prinsip Keamanan Informasi (CIA Triad & Defense-in-Depth)", "11"),
        ("   2.2 Kerangka Regulasi dan Standar Industri (UU PDP, NIST, CIS, OWASP)", "12"),
        ("   2.3 Metode dan Teknik Hardening Basis Data", "13"),
        ("   2.4 Konsep High Availability Clustering & Layer-4 Load Balancing", "14"),
        ("   2.5 Tinjauan Penelitian Terkait (Literature Review)", "15"),
        ("   2.6 Teknologi dan Perangkat Lunak yang Digunakan", "15"),
        ("BAB III METODOLOGI & PERANCANGAN SISTEM", "16"),
        ("   3.1 Tahapan Metodologi Pelaksanaan Proyek (Fase 0 s.d. 5)", "16"),
        ("   3.2 Perancangan Topologi Jaringan & Arsitektur Dual-Deployment", "17"),
        ("   3.3 Perancangan Skema Data & Entity Relationship Diagram (ERD)", "18"),
        ("   3.4 Desain Kebijakan Keamanan & Hardening Policy", "20"),
        ("   3.5 Spesifikasi dan Skenario Pengujian Sistem (Pola Uji 3 Fase)", "21"),
        ("BAB IV IMPLEMENTASI DAN HASIL EVALUASI PENGUJIAN", "22"),
        ("   4.1 Implementasi Lingkungan Laboratorium Pengujian", "22"),
        ("   4.2 Skenario 1: Evaluasi High Availability & Failover Otomatis (Availability)", "22"),
        ("   4.3 Skenario 2: Eksploitasi & Mitigasi SQL Injection (Confidentiality & Integrity)", "26"),
        ("   4.4 Skenario 3: Penegakan SSL/TLS & Kriptografi Data-at-Rest (Confidentiality)", "29"),
        ("   4.5 Skenario 4: Penegakan Role-Based Access Control (RBAC) (Integrity & Confidentiality)", "33"),
        ("   4.6 Skenario 5: Forensic Audit Logging & General Query Log (Accountability)", "36"),
        ("   4.7 Pembahasan Komparatif Hasil Evaluasi & Analisis Regulasi UU PDP", "38"),
        ("BAB V KESIMPULAN DAN SARAN", "40"),
        ("   5.1 Kesimpulan Eksekutif", "40"),
        ("   5.2 Keterbatasan Proyek", "41"),
        ("   5.3 Saran & Rekomendasi Pengembangan Lanjutan", "41"),
        ("DAFTAR PUSTAKA", "42"),
        ("LAMPIRAN", "43")
    ]
    
    t_di = doc.add_table(rows=len(daftar_isi_items), cols=2)
    t_di.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, (title, page) in enumerate(daftar_isi_items):
        cell_t = t_di.cell(idx, 0)
        cell_p = t_di.cell(idx, 1)
        cell_t.width = Inches(5.3)
        cell_p.width = Inches(0.95)
        set_cell_margins(cell_t, top=30, bottom=30, left=60, right=60)
        set_cell_margins(cell_p, top=30, bottom=30, left=60, right=60)
        
        p_t = cell_t.paragraphs[0]
        p_t.paragraph_format.space_before = Pt(1)
        p_t.paragraph_format.space_after = Pt(1)
        r_t = p_t.add_run(title)
        r_t.font.name = 'Arial'
        r_t.font.size = Pt(8.5)
        if title.startswith("BAB") or title in ["HALAMAN JUDUL / SAMPUL", "KATA PENGANTAR", "DAFTAR ISI", "DAFTAR TABEL", "DAFTAR GAMBAR", "DAFTAR PUSTAKA", "LAMPIRAN"]:
            r_t.font.bold = True
            r_t.font.color.rgb = NAVY
        else:
            r_t.font.color.rgb = DARK
            
        p_p = cell_p.paragraphs[0]
        p_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_p.paragraph_format.space_before = Pt(1)
        p_p.paragraph_format.space_after = Pt(1)
        r_p = p_p.add_run(page)
        r_p.font.name = 'Arial'
        r_p.font.size = Pt(8.5)
        r_p.font.color.rgb = SLATE

    doc.add_page_break()

    # =========================================================================
    # DAFTAR TABEL & GAMBAR
    # =========================================================================
    add_h1("DAFTAR TABEL")
    tabel_list = [
        ("Tabel 2.1", "Matriks Kepatuhan Prinsip CIA Triad dan Regulasi Terkait", "8"),
        ("Tabel 2.2", "Komparasi Fitur dan Kontribusi Penelitian Terkait Keamanan Basis Data", "14"),
        ("Tabel 2.3", "Spesifikasi Perangkat Lunak dan Tools Lingkungan Pengujian", "15"),
        ("Tabel 3.1", "Jadwal dan Matriks Tahapan Pelaksanaan Proyek (Fase 0 - Fase 5)", "17"),
        ("Tabel 3.2", "Kamus Data Tabel users (Otentikasi & Wewenang Pegawai)", "20"),
        ("Tabel 3.3", "Kamus Data Tabel pasien (Data Pribadi & NIK Terenkripsi)", "20"),
        ("Tabel 3.4", "Kamus Data Tabel rekam_medis (Data Riwayat Kesehatan Spesifik)", "21"),
        ("Tabel 3.5", "Kamus Data Tabel audit_log (Forensic Incident Tracking)", "21"),
        ("Tabel 3.6", "Matriks Hak Akses Pengguna (Role-Based Access Control)", "22"),
        ("Tabel 3.7", "Matriks Rancangan Skenario Pengujian Keamanan & Ketersediaan", "24"),
        ("Tabel 4.1", "Rekapitulasi Evaluasi Keberhasilan Pengujian vs Acceptance Criteria", "39"),
        ("Tabel 4.2", "Pemetaan Hasil Pengujian terhadap Pasal-Pasal UU PDP No. 27 Tahun 2022", "40")
    ]
    t_dtbl = doc.add_table(rows=len(tabel_list), cols=3)
    t_dtbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, (t_no, t_desc, t_pg) in enumerate(tabel_list):
        c0 = t_dtbl.cell(idx, 0); c0.width = Inches(1.1)
        c1 = t_dtbl.cell(idx, 1); c1.width = Inches(4.3)
        c2 = t_dtbl.cell(idx, 2); c2.width = Inches(0.85)
        set_cell_margins(c0, 40, 40, 60, 60); set_cell_margins(c1, 40, 40, 60, 60); set_cell_margins(c2, 40, 40, 60, 60)
        
        r0 = c0.paragraphs[0].add_run(t_no); r0.font.name = 'Arial'; r0.font.bold = True; r0.font.size = Pt(8.5); r0.font.color.rgb = BLUE
        r1 = c1.paragraphs[0].add_run(t_desc); r1.font.name = 'Arial'; r1.font.size = Pt(8.5); r1.font.color.rgb = DARK
        c2.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r2 = c2.paragraphs[0].add_run(t_pg); r2.font.name = 'Arial'; r2.font.size = Pt(8.5); r2.font.color.rgb = SLATE

    add_p("", space_after=12)
    add_h1("DAFTAR GAMBAR")
    gambar_list = [
        ("Gambar 3.1", "Topologi Jaringan High Availability Cluster (HAProxy, Master, Slave)", "18"),
        ("Gambar 3.2", "Entity Relationship Diagram (ERD) Basis Data klinik_db", "19"),
        ("Gambar 1.1", "Dashboard Web Monitoring HAProxy Saat Kedua Node Berstatus UP (Hijau)", "26"),
        ("Gambar 1.2", "Terminal: INSERT Berhasil via Port 3300 dan Data Muncul di Slave", "27"),
        ("Gambar 1.3", "Dashboard Web HAProxy Saat db-master DOWN (Merah) dan Failover Aktif", "27"),
        ("Gambar 1.4", "Terminal: SELECT Berhasil via Slave dan INSERT Ditolak --read-only", "28"),
        ("Gambar 1.5", "Terminal: Verifikasi SHOW REPLICA STATUS (Replica IO & SQL Running: Yes)", "28"),
        ("Gambar 1.6", "Dashboard Web HAProxy: Kedua Node Pulih dan Berstatus Hijau (UP)", "29"),
        ("Gambar 2.1", "Terminal: Baseline Data Pasien Normal Sebelum Penyerangan", "30"),
        ("Gambar 2.2", "Terminal: Eksploitasi SQL Injection String Concatenation (Data Pasien Bocor)", "30"),
        ("Gambar 2.3", "Terminal: Eksploitasi SQL Injection Mengakibatkan Rekam Medis Bocor", "31"),
        ("Gambar 2.4", "Terminal: Mitigasi Prepared Statement Berhasil Menetralkan Serangan (0 Rows)", "31"),
        ("Gambar 3.1", "Terminal: Penolakan Koneksi Non-TLS dengan ERROR 3159 (require_secure_transport)", "32"),
        ("Gambar 3.2", "Terminal: Verifikasi Cipher TLS Aktif (TLS_AES_256_GCM_SHA384 dan TLSv1.3)", "33"),
        ("Gambar 3.3", "Terminal: Verifikasi Data-at-Rest Kolom nik_ciphertext Berisi Karakter Hex Acak", "33"),
        ("Gambar 3.4", "Terminal: Validasi Dekripsi Bersyarat AES_DECRYPT (Kunci Benar vs Kunci Salah)", "34"),
        ("Gambar 3.5", "Terminal: Verifikasi Status SSL Sesi Aktif dan Enforcement Policy Server ON", "34"),
        ("Gambar 4.1", "Terminal: Operasi Sah (SELECT oleh read_only dan INSERT oleh app_user)", "35"),
        ("Gambar 4.2", "Terminal: Tiga Pesan Penolakan ERROR 1142 pada User read_only", "36"),
        ("Gambar 4.3", "Terminal: Penolakan Hak Akses ERROR 1142 untuk User app_user dan replicator", "36"),
        ("Gambar 4.4", "Terminal: Verifikasi SHOW GRANTS untuk read_only, app_user, dan replicator", "37"),
        ("Gambar 5.1", "Terminal: Rekapitulasi Seluruh Percobaan Serangan di Tabel audit_log", "38"),
        ("Gambar 5.2", "Terminal: Filter Anomali dan Rekonstruksi Forensik Query Eksploitasi (\\G)", "38"),
        ("Gambar 5.3", "Terminal: Bukti Log Independen pada Server-Level General Query Log (/var/log)", "39")
    ]
    t_dgbr = doc.add_table(rows=len(gambar_list), cols=3)
    t_dgbr.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, (g_no, g_desc, g_pg) in enumerate(gambar_list):
        c0 = t_dgbr.cell(idx, 0); c0.width = Inches(1.1)
        c1 = t_dgbr.cell(idx, 1); c1.width = Inches(4.3)
        c2 = t_dgbr.cell(idx, 2); c2.width = Inches(0.85)
        set_cell_margins(c0, 30, 30, 60, 60); set_cell_margins(c1, 30, 30, 60, 60); set_cell_margins(c2, 30, 30, 60, 60)
        
        r0 = c0.paragraphs[0].add_run(g_no); r0.font.name = 'Arial'; r0.font.bold = True; r0.font.size = Pt(8.5); r0.font.color.rgb = BLUE
        r1 = c1.paragraphs[0].add_run(g_desc); r1.font.name = 'Arial'; r1.font.size = Pt(8.5); r1.font.color.rgb = DARK
        c2.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r2 = c2.paragraphs[0].add_run(g_pg); r2.font.name = 'Arial'; r2.font.size = Pt(8.5); r2.font.color.rgb = SLATE

    doc.add_page_break()

    # =========================================================================
    # BAB I: PENDAHULUAN
    # =========================================================================
    add_h1("BAB I — PENDAHULUAN")
    
    add_h2("1.1 Latar Belakang Masalah & Urgensi Keamanan Data Medis")
    add_p("Perkembangan teknologi informasi dan komunikasi di era digital telah mendorong transformasi besar pada seluruh sektor strategis nasional, tidak terkecuali sektor pelayanan kesehatan masyarakat (e-Health). Fasilitas pelayanan kesehatan, mulai dari rumah sakit umum, balai pengobatan, puskesmas, hingga klinik mandiri, secara masif telah beralih dari pencatatan rekam medis konvensional berbasis kertas menuju sistem Rekam Medis Elektronik (RME). Peralihan digital ini secara fundamental meningkatkan efisiensi alur kerja tenaga medis, memangkas waktu tunggu pelayanan pasien, memfasilitasi integrasi antardepartemen, serta memastikan akurasi riwayat pengobatan pasien dapat diakses secara instan saat kondisi gawat darurat.")
    add_p("Namun demikian, di balik lompatan efisiensi operasional tersebut, tersimpan ancaman siber yang sangat masif dan destruktif. Basis data pelayanan kesehatan menyimpan kumpulan informasi yang masuk dalam kategori data pribadi yang bersifat sangat spesifik (sensitive personal data), yang mencakup Nomor Induk Kependudukan (NIK), nama lengkap, tanggal lahir, alamat tinggal, riwayat penyakit, diagnosis dokter, serta catatan resep obat-obatan. Di pasar gelap kejahatan siber (dark web), data rekam medis memiliki nilai komersial yang berkali-kali lipat lebih tinggi dibandingkan data finansial atau nomor kartu kredit biasa, karena data medis bersifat permanen dan tidak dapat diubah (non-resettable), sehingga sangat rentan dieksploitasi untuk pemerasan, penipuan identitas, maupun rekayasa sosial.")
    add_p("Di Indonesia, urgensi perlindungan data medis diperkuat dengan disahkannya payung hukum nasional melalui Undang-Undang Republik Indonesia Nomor 27 Tahun 2022 tentang Perlindungan Data Pribadi (UU PDP). Dalam regulasi tersebut, Pasal 4 ayat (2) huruf e secara eksplisit mengklasifikasikan data kesehatan sebagai data pribadi yang bersifat spesifik. Konsekuensi yuridis dari ketentuan ini dijabarkan pada Pasal 35 hingga Pasal 39, di mana Pengendali Data Pribadi diwajibkan untuk menjamin keamanan data melalui langkah-langkah teknis dan organisasional yang terukur, termasuk penerapan kriptografi enkripsi, pencegahan akses tanpa hak, pencatatan jejak audit (audit log), serta menjaga keandalan sistem pemrosesan data. Pelanggaran terhadap kepatuhan ini berimplikasi pada sanksi administratif berat hingga tuntutan pidana denda bernilai miliaran rupiah.")
    add_p("Kenyataan di lapangan menunjukkan bahwa mayoritas instalasi sistem basis data (RDBMS) seperti MySQL atau MariaDB pada fasilitas kesehatan skala kecil dan menengah dioperasikan dengan konfigurasi bawaan (default configuration). Berdasarkan investigasi kerentanan keamanan perangkat lunak, konfigurasi bawaan ini memiliki berbagai celah keamanan kritis, antara lain:")
    add_p("1. Ketiadaan Enkripsi Lalu Lintas Jaringan (Data-in-Transit): Komunikasi antara server aplikasi klinik dan server basis data secara default berjalan dalam teks polos (plaintext). Hal ini memungkinkan pelaku kejahatan yang berada dalam satu jaringan lokal (LAN/Wi-Fi) untuk melakukan sniffing paket data sensitif menggunakan packet analyzer.")
    add_p("2. Celah SQL Injection (SQLi): Aplikasi klinik sering kali membangun kueri SQL menggunakan teknik penggabungan string (concatenation) yang rentan disusupi payload malicious, sehingga penyerang dapat membobol seluruh isi tabel basis data melompati mekanisme otentikasi.")
    add_p("3. Data Disimpan Tanpa Enkripsi (Data-at-Rest Plaintext): File fisik tabel basis data (.ibd) menyimpan informasi NIK dan identitas pasien secara telanjang. Apabila terjadi pencurian cadangan file (database dump) atau pencurian fisik media penyimpanan, seluruh data pasien dapat langsung dibaca tanpa hambatan.")
    add_p("4. Pelanggaran Prinsip Hak Akses Minimum (Least Privilege): Sering kali pengembang hanya menggunakan satu akun pengguna dengan hak administratif tinggi (misalnya root atau full grant) untuk seluruh modul aplikasi, sehingga kompromi pada satu akun berakibat fatal bagi seluruh ekosistem basis data.")
    add_p("5. Titik Kegagalan Tunggal (Single Point of Failure / SPoF): Penggunaan satu instans server basis data tunggal (single instance). Apabila server tersebut mengalami kerusakan perangkat keras, gangguan sistem operasi, atau serangan denial of service (DoS), seluruh operasional klinik akan lumpuh total, menghentikan registrasi pasien dan membahayakan keselamatan pasien darurat karena dokter tidak dapat mengakses riwayat alergi atau resep obat.")
    add_p("Berdasarkan permasalahan mendesak di atas, diperlukan sebuah rancangan komprehensif yang mengintegrasikan penguatan keamanan tingkat lanjut (database hardening) dan ketersediaan tinggi (high availability clustering). Proyek ini merancang, membangun, dan menguji arsitektur basis data klinik_db dengan memadukan mekanisme replikasi asinkron Master-Slave, reverse proxy load balancer HAProxy dengan failover otomatis, penegakan TLSv1.3 wajib, enkripsi kolom AES-256 pada NIK pasien, penegakan kontrol akses berbasis peran (RBAC), serta pencatatan audit forensik dua lapis.")

    add_h2("1.2 Rumusan Masalah Proyek")
    add_p("Berdasarkan latar belakang yang telah diuraikan, rumusan masalah dalam proyek ini dirumuskan sebagai berikut:")
    add_p("1. Bagaimana merancang dan mengimplementasikan arsitektur High Availability Cluster berbasis Master-Slave Replication dan HAProxy yang mampu melakukan failover otomatis untuk meniadakan Single Point of Failure pada basis data klinik?")
    add_p("2. Bagaimana efektivitas penerapan parameterized prepared statements dalam memitigasi serangan SQL Injection pada tabel data pasien dan rekam medis dibandingkan dengan kueri konkatenatif bawaan?")
    add_p("3. Bagaimana menerapkan penegakan koneksi aman berbasis enkripsi transport TLSv1.3 dan enkripsi data-at-rest simetris (AES-256) pada atribut sensitif NIK guna memenuhi kepatuhan UU PDP No. 27 Tahun 2022?")
    add_p("4. Bagaimana merancang dan menerapkan kontrol akses berbasis peran (Role-Based Access Control) dengan prinsip hak istimewa minimum (Least Privilege) guna mencegah eskalasi wewenang dan perusakan data dari pihak internal?")
    add_p("5. Bagaimana membangun mekanisme pencatatan audit log forensik berlapis (tabel aplikasi dan MySQL General Query Log) guna menjamin akuntabilitas serta kemudahan rekonstruksi kronologis insiden siber?")

    add_h2("1.3 Tujuan Proyek")
    add_p("Tujuan yang ingin dicapai melalui pelaksanaan proyek akhir ini adalah:")
    add_p("1. Membangun lingkungan basis data High Availability Cluster yang menghubungkan node Master (port 3306), node Slave (port 3307), dan load balancer HAProxy (port 3300) dengan kemampuan failover otomatis dalam hitungan detik saat node utama mengalami crash.")
    add_p("2. Menguji dan membuktikan kerentanan serangan SQL Injection serta efektivitas mitigasinya menggunakan prepared statements dengan parameter terikat.")
    add_p("3. Mengimplementasikan kebijakan require_secure_transport=ON dan enkripsi kolom AES-256 pada atribut NIK pasien, serta memverifikasi penolakan koneksi tanpa sertifikat SSL dan kerahasiaan ciphertext.")
    add_p("4. Mengonfigurasi dan memvalidasi penegakan hak akses berbasis peran (app_user, read_only, replicator) sehingga seluruh upaya operasi di luar wewenang sah secara konsisten ditolak oleh sistem basis data.")
    add_p("5. Mengembangkan mekanisme pencatatan audit trail yang mampu mendokumentasikan setiap indikasi anomali dan percobaan kejahatan siber secara independen untuk keperluan investigasi forensik digital.")

    add_h2("1.4 Manfaat Proyek Secara Akademis dan Praktis")
    add_p("Proyek akhir ini diharapkan mampu memberikan manfaat yang signifikan, baik dari segi akademis maupun praktis:")
    add_p("1. Manfaat Akademis: Menjadi referensi ilmiah komparatif mengenai integrasi kontrol keamanan defensif (defense-in-depth) dan toleransi kesalahan (fault tolerance) pada RDBMS open-source, serta menjadi materi pengayaan studi kasus nyata pada mata kuliah Keamanan Sistem Informasi di Politeknik Statistika STIS.")
    add_p("2. Manfaat Praktis: Memberikan blueprint arsitektur dan panduan konfigurasi siap pakai (reproducible template) bagi instansi pemerintah, rumah sakit, klinik kesehatan, maupun pengembang perangkat lunak dalam membangun infrastruktur basis data yang aman, hemat biaya, dan patuh terhadap regulasi perlindungan data pribadi nasional.")

    add_h2("1.5 Ruang Lingkup dan Batasan Sistem")
    add_p("Untuk memastikan fokus penelitian terarah dan terukur, ruang lingkup serta batasan proyek ditetapkan sebagai berikut:")
    add_p("1. Basis Data Target: Sistem basis data relasional klinik_db berbasis mesin MySQL 8.0 / MariaDB dengan 4 tabel utama: users (otentikasi & wewenang), pasien (identitas pribadi pasien), rekam_medis (catatan medis pemeriksaan dan resep), serta audit_log (pencatatan insiden keamanan).")
    add_p("2. Jalur Implementasi Dual-Deployment: Pengujian dilakukan pada dua lingkungan paralel yang identik secara konfigurasi konseptual:")
    add_p("   • Jalur A (Docker Containerized): Menggunakan Docker Compose untuk orkestrasi db-master, db-slave, dan haproxy dalam jaringan tervirtualisasi.")
    add_p("   • Jalur B (Bare-Metal Local Server): Menggunakan kombinasi XAMPP (Master port 3306) dan Laragon (Slave port 3307) di sistem operasi Windows.")
    add_p("3. Load Balancing & Gateway: Menggunakan HAProxy port 3300 sebagai satu-satunya pintu gerbang akses klien dengan pemeriksaan kesehatan berkala (health check) setiap 2 detik dan antarmuka pemantauan status pada port 8404/8900.")
    add_p("4. Kriptografi & Sertifikat: Menggunakan Public Key Infrastructure lokal (OpenSSL self-signed Certificate Authority) untuk menerbitkan sertifikat server dan klien, serta algoritma simetris AES-256 untuk enkripsi NIK.")
    add_p("5. Metodologi Evaluasi: Lima skenario pengujian dieksekusi secara ketat menggunakan pola uji 3 fase: Before-Attack (kondisi baseline normal), During-Attack (simulasi serangan/anomali), dan After-Mitigation (pembuktian keberhasilan kontrol keamanan).")
    add_p("6. Batasan Sistem: Penelitian ini tidak mencakup pengadaan sertifikat SSL dari Commercial Certificate Authority berbayar, tidak mengintegrasikan Hardware Security Module (HSM) atau cloud Key Management Service (KMS) eksternal (kunci enkripsi dikelola secara lokal pada parameter sesi), serta tidak membangun aplikasi antarmuka web klinik berskala produksi penuh (pengujian dilakukan via skrip CLI dan showcase interaktif).")

    doc.add_page_break()

    # =========================================================================
    # BAB II: TINJAUAN PUSTAKA & LANDASAN TEORI
    # =========================================================================
    add_h1("BAB II — TINJAUAN PUSTAKA & LANDASAN TEORI")
    
    add_h2("2.1 Prinsip Keamanan Informasi (CIA Triad & Defense-in-Depth)")
    add_p("Dalam domain keamanan sistem informasi, kerangka kerja klasik yang menjadi fondasi utama perancangan sistem pertahanan adalah CIA Triad, yang terdiri atas tiga pilar utama:")
    add_p("1. Kerahasiaan (Confidentiality): Menjamin bahwa aset informasi hanya dapat diakses, dibaca, dan disingkapkan kepada pihak-pihak yang memiliki hak wewenang sah (authorized parties). Dalam konteks basis data kesehatan, kerahasiaan mencakup perlindungan data identitas pasien dan rekam medis dari penyingkapan tidak sah oleh pihak internal maupun intersepsi lalu lintas jaringan oleh penyerang eksternal.")
    add_p("2. Integritas (Integrity): Menjamin keaslian, keakuratan, dan kelengkapan data sepanjang siklus hidupnya. Integritas memastikan bahwa data medis tidak mengalami modifikasi, penyisipan malicious, pemalsuan, atau penghapusan tanpa izin, baik yang disebabkan oleh celah injeksi kueri (SQLi) maupun kesalahan sistem.")
    add_p("3. Ketersediaan (Availability): Menjamin bahwa data dan layanan sistem dapat diakses secara tepat waktu dan andal oleh pengguna yang berhak pada saat dibutuhkan. Dalam operasional klinik darurat, kegagalan ketersediaan basis data dapat berakibat fatal bagi penanganan pasien.")
    add_p("Selain CIA Triad, sistem keamanan modern memerlukan pilar pelengkap berupa Akuntabilitas (Accountability) dan Kenirsangkalan (Non-Repudiation). Prinsip ini menuntut bahwa setiap aksi atau transaksi yang terjadi pada sistem dapat dilacak secara pasti kepada entitas pengguna pelakunya melalui jejak audit yang tidak dapat disangkal atau dimanipulasi.")
    add_p("Untuk mengimplementasikan prinsip-prinsip tersebut, arsitektur basis data klinik_db menerapkan strategi Defense-in-Depth (Pertahanan Berlapis). Strategi ini menempatkan serangkaian kontrol keamanan berjenjang pada berbagai lapisan, sehingga apabila salah satu lapisan pertahanan berhasil ditembus oleh penyerang, lapisan pertahanan berikutnya akan tetap melindungi data.")

    add_h2("2.2 Kerangka Regulasi dan Standar Industri (UU PDP, NIST, CIS, OWASP)")
    add_p("Perancangan dan pengujian keamanan dalam proyek ini dipandu secara ketat oleh regulasi hukum positif Indonesia dan standar keamanan internasional:")
    add_p("1. Undang-Undang RI No. 27 Tahun 2022 tentang Perlindungan Data Pribadi (UU PDP): UU PDP merupakan tonggak regulasi perlindungan privasi di Indonesia. Pasal 4 ayat (2) mengklasifikasikan data kesehatan sebagai data pribadi yang bersifat spesifik yang memiliki risiko tinggi terhadap subjek data. Pasal 35 mewajibkan Pengendali Data Pribadi menerapkan langkah teknis untuk mencegah akses tidak sah, kebocoran, atau pemalsuan data pribadi. Pasal 39 mewajibkan pemantauan berkala dan pencatatan jejak pemrosesan data pribadi.")
    add_p("2. NIST Special Publication 800-111: Diterbitkan oleh National Institute of Standards and Technology (NIST), standar ini memberikan panduan resmi mengenai teknologi enkripsi penyimpanan data (Guide to Storage Encryption Technologies for End User Devices and Databases). Standar ini merekomendasikan penggunaan algoritma kriptografi terstandarisasi FIPS seperti AES (Advanced Encryption Standard) dengan panjang kunci minimal 128-bit atau 256-bit guna mengamankan data-at-rest dari pencurian media penyimpanan.")
    add_p("3. CIS MySQL 8.0 Benchmark v1.4.0: Diterbitkan oleh Center for Internet Security (CIS), dokumen acuan ini menetapkan praktik terbaik pengerasan (hardening) konfigurasi server MySQL. Rekomendasi utama mencakup penegakan koneksi terenkripsi (require_secure_transport=ON), penonaktifan fitur lokal file (local_infile=OFF), pembatasan akses direktori (secure_file_priv), serta penegakan prinsip least privilege pada setiap akun pengguna.")
    add_p("4. OWASP Top 10 (Open Web Application Security Project): Proyek ini berfokus pada dua kerentanan teratas OWASP, yaitu A03:2021-Injection (khususnya SQL Injection yang menempati risiko kerentanan data terbesar) dan A01:2021-Broken Access Control (kegagalan pembatasan hak akses yang memungkinkan pengguna biasa melakukan eskalasi hak menjadi administrator).")

    # Tabel 2.1: Matriks Regulasi
    add_p("", space_after=2)
    add_h3("Tabel 2.1: Matriks Kepatuhan Prinsip CIA Triad dan Regulasi Terkait")
    t_reg = doc.add_table(rows=5, cols=4)
    t_reg.alignment = WD_TABLE_ALIGNMENT.CENTER
    w_reg = [Inches(1.2), Inches(1.5), Inches(1.8), Inches(1.75)]
    h_reg = ["Prinsip Keamanan", "Regulasi / Standar Acuan", "Potensi Ancaman / Kerentanan", "Kontrol Mitigasi Sistem klinik_db"]
    for i, h in enumerate(h_reg):
        t_reg.cell(0, i).paragraphs[0].add_run(h)
    style_table_header(t_reg.rows[0], w_reg)
    data_reg = [
        ("Confidentiality", "UU PDP Ps. 35 & 36\nNIST SP 800-111", "Sniffing jaringan LAN;\nPencurian fisik data (.ibd)", "Enkripsi transport TLSv1.3;\nEnkripsi kolom AES-256 pada NIK."),
        ("Integrity", "OWASP A03 (Injection)\nCIS MySQL Benchmark", "Manipulasi kueri via SQLi;\nModifikasi data ilegal", "Parametric Prepared Statements;\nPemisahan wewenang peran (RBAC)."),
        ("Availability", "UU PDP Ps. 35\nBusiness Continuity", "Node Master crash / SPoF;\nGangguan operasional klinik", "Master-Slave Replication;\nHAProxy load balancer & failover 2s."),
        ("Accountability", "UU PDP Ps. 39\nISO/IEC 27001", "Aksi ilegal tanpa jejak;\nNon-repudiation failure", "Dual-tier Logging (tabel audit_log &\nServer-level General Query Log).")
    ]
    for r_idx, row in enumerate(data_reg):
        rc = t_reg.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row):
            rc[c_idx].paragraphs[0].add_run(val)
    style_table_rows(t_reg, w_reg)
    add_p("", space_after=8)

    add_h2("2.3 Metode dan Teknik Hardening Basis Data")
    add_p("Database hardening adalah proses pengamanan sistem basis data melalui identifikasi dan eliminasi celah keamanan bawaan, pembatasan permukaan serangan (attack surface), dan penegakan parameter konfigurasi yang ketat. Metode hardening yang diterapkan dalam proyek ini meliputi:")
    add_p("1. Enkripsi Data-in-Transit (TLSv1.3): Seluruh aliran paket data antara klien aplikasi dan basis data diamankan menggunakan protokol kriptografi Transport Layer Security generasi terbaru (TLSv1.3). Melalui konfigurasi require_secure_transport=ON di server dan klausa REQUIRE SSL pada setiap user, basis data secara otomatis menolak seluruh koneksi yang tidak dilengkapi sertifikat valid.")
    add_p("2. Enkripsi Data-at-Rest Kolom Granular (AES-256): Berbeda dengan Full Disk Encryption (FDE) yang memerlukan sumber daya komputasi besar, proyek ini menerapkan Column-Level Encryption secara selektif pada atribut paling berharga, yaitu NIK pasien. Data NIK disimpan dalam tipe data biner VARBINARY(255) yang dihasilkan dari fungsi kriptografi AES_ENCRYPT(data, key). Penyerang yang mencuri file dump basis data hanya akan memperoleh string biner acak yang tidak dapat dipecahkan tanpa kunci rahasia.")
    add_p("3. Netralisasi SQL Injection dengan Prepared Statements: SQL Injection terjadi akibat interpolasi string langsung antara kode logika SQL dan data masukan pengguna. Teknik mitigasi terbaik adalah penggunaan Prepared Statement. Dalam pendekatan ini, struktur kueri SQL dikompilasi terlebih dahulu di server dengan placeholder parameter (?). Ketika data penyerang (seperti ' OR '1'='1' --) dimasukkan, mesin basis data memperlakukannya murni sebagai data literal string, bukan sebagai token instruksi perintah SQL yang dapat dieksekusi.")
    add_p("4. Penegakan Role-Based Access Control (RBAC): Prinsip Least Privilege menuntut bahwa sebuah akun hanya diberikan hak seminimal mungkin yang diperlukan untuk menjalankan tugas operasionalnya. Proyek ini membagi akses basis data klinik ke dalam tiga entitas peran formal:")
    add_p("   • app_user: Digunakan oleh layanan backend aplikasi klinik; hanya memiliki wewenang SELECT, INSERT, dan UPDATE pada tabel operasional.")
    add_p("   • read_only: Digunakan oleh staf administrasi atau audit pelaporan; hanya memiliki wewenang SELECT pada tabel pasien.")
    add_p("   • replicator: Digunakan khusus oleh mesin replikasi Slave; hanya memiliki izin REPLICATION SLAVE dan sama sekali tidak memiliki akses baca/tulis terhadap tabel data.")
    add_p("5. Multi-tier Forensic Audit Logging: Pembangunan jejak audit dilakukan pada dua tingkatan terpisah:")
    add_p("   • Application-level Audit: Tabel audit_log merekam aktivitas keamanan spesifik (anomali injeksi, penolakan koneksi, dan akses ilegal) lengkap dengan cap waktu (timestamp), user ID, alamat IP asal, serta detail kueri yang dieksekusi.")
    add_p("   • Server-level General Query Log: Fitur internal MySQL yang mencatat seluruh perintah kueri dan koneksi langsung ke media penyimpanan server, berfungsi sebagai rekaman independen yang tidak dapat dimanipulasi pengguna biasa.")

    add_h2("2.4 Konsep High Availability Clustering & Layer-4 Load Balancing")
    add_p("Ketersediaan tinggi (High Availability / HA) adalah karakteristik arsitektur sistem yang bertujuan memastikan tingkat performa operasional dan aksesibilitas data tetap terjaga dalam jangka waktu yang disepakati, serta meminimalkan periode downtime akibat kegagalan perangkat keras maupun pemeliharaan perangkat lunak.")
    add_p("Pada arsitektur basis data MySQL, strategi ketersediaan tinggi diwujudkan melalui mekanisme Master-Slave Asynchronous Replication. Node Master bertindak sebagai satu-satunya instans yang melayani transaksi tulis (INSERT, UPDATE, DELETE) sekaligus transaksi baca (SELECT). Setiap transaksi yang berhasil di-commit pada Master secara berurutan dicatat ke dalam Binary Log (binlog). Node Slave kemudian membaca Binary Log tersebut melalui thread I/O dan mengeksekusinya kembali pada salinan lokal melalui thread SQL. Proyek ini menetapkan parameter binlog_format=ROW untuk memastikan replikasi bekerja pada level perubahan baris data murni, menjamin konsistensi data yang sempurna antara Master dan Slave.")
    add_p("Agar proses peralihan (failover) dari Master ke Slave berjalan transparan bagi aplikasi tanpa memerlukan intervensi manual pengembang, diimplementasikan reverse proxy load balancer HAProxy pada Layer-4 TCP. Klien aplikasi hanya berinteraksi dengan satu alamat virtual IP/port (port 3300). HAProxy secara proaktif mengirimkan paket health check ke port 3306 dan 3307 setiap 2 detik. Apabila node Master mengalami crash atau berhenti mendadak, HAProxy langsung menandai Master berstatus DOWN dan secara otomatis mengarahkan lalu lintas kueri baca ke node Slave.")

    add_h2("2.5 Tinjauan Penelitian Terkait (Literature Review)")
    add_p("Untuk menempatkan penelitian proyek ini dalam peta keilmuan keamanan informasi yang mutakhir, dilakukan kajian literatur mendalam terhadap karya ilmiah dan laporan teknis terkini yang tersimpan dalam folder referensi proyek:")
    add_p("1. Kone (2021) dalam tesisnya mengenai arsitektur basis data relasional meneliti kerentanan implementasi replikasi standar terhadap serangan siber dan menggarisbawahi pentingnya isolasi koneksi replikasi menggunakan sertifikat SSL terpisah.")
    add_p("2. Penelitian mengenai Database Forensics and Security Measures to Defend from Cyber Threats (2023) menganalisis peran krusial integritas jejak audit dalam rekonstruksi insiden kebocoran data pada ekosistem basis data terdistribusi.")
    add_p("3. Studi eksperimental Database Security and Performance: A Case of SQL Injection Attacks Using Docker-Based Virtualisation (2022) menguji dampak performa dari penggunaan kontainerisasi terhadap ketahanan mitigasi serangan injeksi, membuktikan bahwa isolasi jaringan Docker memberikan perlindungan tambahan terhadap eskalasi lateral.")
    add_p("4. Laporan Oracle White Paper mengenai MySQL Security Best Practices & Transparent Data Encryption (TDE) menjabarkan komparasi antara enkripsi penyimpanan tingkat tabel dan enkripsi tingkat kolom, di mana enkripsi kolom granular menawarkan efisiensi komputasi yang jauh lebih baik pada lingkungan dengan beban kerja heterogen.")
    add_p("5. Survei terkini Survey on Cloud Database Security: Cryptographic Techniques and Intelligent Defense Mechanisms (2024) memaparkan tren penggabungan mekanisme deteksi anomali pada audit log untuk mengidentifikasi pola serangan brute force dan eskalasi wewenang internal.")

    # Tabel 2.2: Komparasi Penelitian Terkait
    add_p("", space_after=2)
    add_h3("Tabel 2.2: Komparasi Fitur dan Kontribusi Penelitian Terkait Keamanan Basis Data")
    t_lit = doc.add_table(rows=6, cols=5)
    t_lit.alignment = WD_TABLE_ALIGNMENT.CENTER
    w_lit = [Inches(1.5), Inches(1.1), Inches(1.3), Inches(1.2), Inches(1.15)]
    h_lit = ["Peneliti & Tahun", "Fokus Penelitian", "Metode / Tools", "Aspek Keamanan", "Relevansi dengan Proyek Ini"]
    for i, h in enumerate(h_lit):
        t_lit.cell(0, i).paragraphs[0].add_run(h)
    style_table_header(t_lit.rows[0], w_lit)
    data_lit = [
        ("Damian Kone (2021)", "Evaluasi Replikasi MySQL", "Master-Slave Asynchronous", "Availability & Replikasi", "Acuan konfigurasi binlog ROW & user replicator."),
        ("Cyber Defense Team (2023)", "Forensik Basis Data", "Audit Logging & Reconstruction", "Accountability", "Pola format penyimpanan query_exec untuk investigasi."),
        ("Docker Security Study (2022)", "SQL Injection & Docker", "Docker Virtualisation", "Confidentiality & Integrity", "Rancangan virtual network isolasi Jalur A."),
        ("Oracle Technical Paper (2022)", "MySQL Best Practices", "TDE & Column Encryption", "Data-at-Rest Security", "Penggunaan AES_ENCRYPT & VARBINARY."),
        ("Kelompok 4 (Proyek Ini, 2026)", "End-to-End Hardening & HA", "Master-Slave, HAProxy, TLS, AES, RBAC, Dual-Audit", "CIA Triad + Accountability + UU PDP", "Integrasi terpadu 5 skenario dengan pola uji 3 fase.")
    ]
    for r_idx, row in enumerate(data_lit):
        rc = t_lit.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row):
            rc[c_idx].paragraphs[0].add_run(val)
    style_table_rows(t_lit, w_lit)
    add_p("", space_after=8)

    add_h2("2.6 Teknologi dan Perangkat Lunak yang Digunakan")
    add_p("Implementasi dan pengujian proyek ini didukung oleh tumpukan teknologi (technology stack) yang handal dan terstandarisasi:")

    # Tabel 2.3: Spesifikasi Tools
    add_h3("Tabel 2.3: Spesifikasi Perangkat Lunak dan Tools Lingkungan Pengujian")
    t_tool = doc.add_table(rows=8, cols=4)
    t_tool.alignment = WD_TABLE_ALIGNMENT.CENTER
    w_tool = [Inches(1.2), Inches(1.4), Inches(1.2), Inches(2.45)]
    h_tool = ["Komponen", "Perangkat Lunak", "Versi / Port", "Peran & Fungsi Utama"]
    for i, h in enumerate(h_tool):
        t_tool.cell(0, i).paragraphs[0].add_run(h)
    style_table_header(t_tool.rows[0], w_tool)
    data_tool = [
        ("RDBMS Server", "MySQL Community / MariaDB", "v8.0.x / 3306, 3307", "Mesin basis data utama penyimpan data klinik_db."),
        ("Load Balancer", "HAProxy", "v2.8 / 3300, 8404/8900", "Reverse proxy Layer-4 TCP, health check & failover otomatis."),
        ("Kontainerisasi", "Docker & Docker Compose", "v24.x / Compose v2", "Orkestrasi lingkungan Jalur A dalam jaringan terisolasi."),
        ("Local Server", "XAMPP & Laragon", "Latest / Windows", "Platform pengujian komparatif Jalur B (bare-metal)."),
        ("Kriptografi / TLS", "OpenSSL Toolkit", "v3.0.x / TLSv1.3", "Pembangkitan CA lokal, sertifikat X.509, dan cipher TLS."),
        ("Bahasa Skrip", "Python & Bash / PowerShell", "Python 3.11+", "Otomatisasi pengujian, pembangkitan data sintetis, logging."),
        ("Klien DB", "MySQL CLI & DBeaver CE", "v23.x / Cross-platform", "Alat inspeksi visual dan eksekusi kueri penyerangan.")
    ]
    for r_idx, row in enumerate(data_tool):
        rc = t_tool.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row):
            rc[c_idx].paragraphs[0].add_run(val)
    style_table_rows(t_tool, w_tool)

    doc.add_page_break()

    # =========================================================================
    # BAB III: METODOLOGI & PERANCANGAN SISTEM
    # =========================================================================
    add_h1("BAB III — METODOLOGI & PERANCANGAN SISTEM")
    
    add_h2("3.1 Tahapan Metodologi Pelaksanaan Proyek (Fase 0 s.d. 5)")
    add_p("Pelaksanaan proyek akhir ini mengadopsi pendekatan siklus terstruktur yang terdiri atas enam fase berkesinambungan, yang dijadwalkan secara ketat:")
    add_p("• Fase 0 — Studi Literatur & Analisis Kebutuhan (Minggu 8–9): Melakukan telaah terhadap regulasi UU PDP No. 27/2022, standar CIS MySQL Benchmark, dan NIST SP 800-111; merumuskan 4 vektor ancaman utama (SPoF, SQLi, intersepsi non-TLS, dan eskalasi wewenang); menetapkan spesifikasi environment dual-deployment.")
    add_p("• Fase 1 — Perancangan Arsitektur & Desain Sistem (Minggu 9–10): Menggambar topologi High Availability Cluster; merancang skema ERD 4 tabel; mendesain matriks wewenang peran RBAC; menyusun spesifikasi pengujian 5 skenario berdasar pola Before-During-After.")
    add_p("• Fase 2 — Implementasi & Konfigurasi Lingkungan Lab (Minggu 10–12): Mengonfigurasi docker-compose.yml dan environment XAMPP/Laragon; mengatur replikasi binlog ROW; mengonfigurasi HAProxy health checking; menerbitkan sertifikat TLS via OpenSSL; menyematkan parameter hardening my.cnf; memuat skema dan data sintetis klinik_db.")
    add_p("• Fase 3 — Eksekusi Pengujian Skenario & Evaluasi (Minggu 11–12): Menjalankan 5 skenario pengujian secara sistematis; mendokumentasikan bukti tangkapan layar terminal dan isi log sistem; mengevaluasi keberhasilan terhadap acceptance criteria.")
    add_p("• Fase 4 — Analisis Hasil, Pembahasan & Kepatuhan Regulasi (Minggu 12–13): Memetakan hasil pengujian terhadap prinsip CIA Triad dan pasal-pasal UU PDP; mengidentifikasi keterbatasan sistem; merumuskan rekomendasi mitigasi lanjutan.")
    add_p("• Fase 5 — Dokumentasi Akhir, Kompilasi Laporan & Pelaporan (Minggu 13–14): Mengompilasi seluruh kode konfigurasi, skrip SQL, bukti pengujian, dan narasi ilmiah ke dalam dokumen laporan akhir lengkap.")

    # Tabel 3.1: Matriks Jadwal
    add_h3("Tabel 3.1: Jadwal dan Matriks Tahapan Pelaksanaan Proyek (Fase 0 - Fase 5)")
    t_sch = doc.add_table(rows=7, cols=5)
    t_sch.alignment = WD_TABLE_ALIGNMENT.CENTER
    w_sch = [Inches(0.8), Inches(2.2), Inches(1.1), Inches(1.1), Inches(1.05)]
    h_sch = ["Fase", "Uraian Kegiatan Pokok", "Periode", "Penanggung Jawab", "Keluaran (Deliverables)"]
    for i, h in enumerate(h_sch):
        t_sch.cell(0, i).paragraphs[0].add_run(h)
    style_table_header(t_sch.rows[0], w_sch)
    data_sch = [
        ("Fase 0", "Studi Literatur, Regulasi & Kebutuhan", "Minggu 8-9", "Tim Kelompok 4", "Dokumen PRD & Analisis"),
        ("Fase 1", "Perancangan Arsitektur & ERD", "Minggu 9-10", "Agam & Rezky", "Diagram Topologi & Skema"),
        ("Fase 2", "Setup Docker, XAMPP, TLS, HAProxy", "Minggu 10-12", "Rezky Raya K.", "Environment Lab Siap Uji"),
        ("Fase 3", "Eksekusi 5 Skenario Pengujian", "Minggu 11-12", "Rezky & Tim", "Bukti Screenshot & Log"),
        ("Fase 4", "Analisis CIA Triad & Kepatuhan UU PDP", "Minggu 12-13", "Tim Kelompok 4", "Matriks Evaluasi Hasil"),
        ("Fase 5", "Finalisasi Laporan & Materi Presentasi", "Minggu 13-14", "Tim Kelompok 4", "Laporan Akhir Lengkap")
    ]
    for r_idx, row in enumerate(data_sch):
        rc = t_sch.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row):
            rc[c_idx].paragraphs[0].add_run(val)
    style_table_rows(t_sch, w_sch)
    add_p("", space_after=8)

    add_h2("3.2 Perancangan Topologi Jaringan & Arsitektur Dual-Deployment")
    add_p("Arsitektur jaringan dirancang dengan mengutamakan isolasi keamanan dan ketersediaan tinggi. Aplikasi klien tidak diperkenankan melakukan koneksi langsung ke port internal basis data (3306 atau 3307), melainkan harus melalui Load Balancer HAProxy pada port 3300 dengan kewajiban enkripsi transport TLSv1.3.")
    
    add_code(
        "           +-------------------------------------------------------------+\n"
        "           |       KLIEN / APLIKASI WEB KLINIK / SKRIP DEMONSTRASI       |\n"
        "           +-------------------------------------------------------------+\n"
        "                                          |\n"
        "                     (Port 3300 - Enkripsi TLSv1.3 Wajib)\n"
        "                                          v\n"
        "           +-------------------------------------------------------------+\n"
        "           |                  HAPROXY LOAD BALANCER                      |\n"
        "           |    (Health Check Interval 2 Detik | Dashboard 8404/8900)    |\n"
        "           +-------------------------------------------------------------+\n"
        "                         |                                 |\n"
        "             [Mode Normal: Transaksi Utama]        [Failover: Read-Only]\n"
        "                         |                                 |\n"
        "                         v                                 v\n"
        "           +---------------------------+     +---------------------------+\n"
        "           |     NODE DB-MASTER        |     |      NODE DB-SLAVE        |\n"
        "           |   MySQL Port 3306         |     |    MySQL Port 3307        |\n"
        "           |   (Read / Write)          |     |    (Read-Only Standby)    |\n"
        "           +---------------------------+     +---------------------------+\n"
        "                         |                                 ^\n"
        "                         +--- Binary Log Replikasi (ROW) --+\n"
    )
    add_p("Gambar 3.1: Diagram Topologi Jaringan High Availability Cluster (klinik_db)", italic=True)
    add_p("Untuk membuktikan portabilitas sistem, arsitektur di atas diimplementasikan pada dua jalur paralel:")
    add_p("1. Jalur A (Docker Containerized): Seluruh komponen (db-master, db-slave, dan haproxy) berjalan sebagai kontainer dalam jaringan bridge terisolasi klinik-net. Konfigurasi dideklarasikan secara deklaratif melalui docker-compose.yml.")
    add_p("2. Jalur B (Bare-Metal Local Server Windows): Node Master dijalankan melalui XAMPP pada port 3306, sedangkan node Slave dijalankan melalui Laragon pada port 3307. Keduanya menerapkan file konfigurasi my.cnf dan sertifikat SSL yang identik dengan Jalur A.")

    add_h2("3.3 Perancangan Skema Data & Entity Relationship Diagram (ERD)")
    add_p("Skema basis data klinik_db dirancang secara presisi untuk merepresentasikan operasional pelayanan klinik dengan memisahkan data otentikasi pengguna, data master pasien, transaksi rekam medis, dan catatan audit keamanan:")
    
    add_code(
        "+-------------------+       +-------------------+       +-------------------+\n"
        "|       users       |       |      pasien       |       |    rekam_medis    |\n"
        "+-------------------+       +-------------------+       +-------------------+\n"
        "| id (PK)           |<--+   | id (PK)           |<--+   | id (PK)           |\n"
        "| username          |   |   | nama              |   +---| pasien_id (FK)    |\n"
        "| password_hash     |   +---| dokter_id (FK)----+-------| dokter_id (FK)    |\n"
        "| role              |       | nik_encrypted     |       | diagnosa          |\n"
        "| is_active         |       | tanggal_lahir     |       | resep             |\n"
        "+-------------------+       | no_telepon        |       | tanggal           |\n"
        "                            +-------------------+       +-------------------+\n"
        "                                                                  \n"
        "                            +-------------------+\n"
        "                            |     audit_log     |\n"
        "                            +-------------------+\n"
        "                            | id (PK)           |\n"
        "                            | user_id (FK) -----+---> users.id\n"
        "                            | aksi              |\n"
        "                            | tabel_target      |\n"
        "                            | query_exec        |\n"
        "                            | ip_address        |\n"
        "                            | waktu             |\n"
        "                            +-------------------+\n"
    )
    add_p("Gambar 3.2: Entity Relationship Diagram (ERD) Basis Data klinik_db", italic=True)

    # Kamus Data Tables
    add_h3("Tabel 3.2: Kamus Data Tabel users (Otentikasi & Wewenang Pegawai)")
    t_u = doc.add_table(rows=6, cols=5)
    t_u.alignment = WD_TABLE_ALIGNMENT.CENTER
    w_u = [Inches(1.1), Inches(1.3), Inches(0.8), Inches(1.0), Inches(2.05)]
    h_u = ["Nama Kolom", "Tipe Data", "Null?", "Constraint", "Keterangan Teknis Keamanan"]
    for i, h in enumerate(h_u): t_u.cell(0, i).paragraphs[0].add_run(h)
    style_table_header(t_u.rows[0], w_u)
    data_u = [
        ("id", "INT AUTO_INCREMENT", "NO", "PRIMARY KEY", "Pengenal unik pegawai/pengguna."),
        ("username", "VARCHAR(50)", "NO", "UNIQUE", "Nama akun untuk otentikasi login."),
        ("password", "VARCHAR(255)", "NO", "None", "Wajib disimpan dalam bentuk hash bcrypt."),
        ("role", "ENUM('admin','dokter','resepsionis')", "NO", "None", "Peran pengguna untuk RBAC."),
        ("is_active", "TINYINT(1)", "NO", "DEFAULT 1", "Status aktifasi akun (pencegahan zombie account).")
    ]
    for r_idx, row in enumerate(data_u):
        rc = t_u.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row): rc[c_idx].paragraphs[0].add_run(val)
    style_table_rows(t_u, w_u)

    add_p("", space_after=4)
    add_h3("Tabel 3.3: Kamus Data Tabel pasien (Data Pribadi & NIK Terenkripsi)")
    t_p = doc.add_table(rows=7, cols=5)
    t_p.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(h_u): t_p.cell(0, i).paragraphs[0].add_run(h)
    style_table_header(t_p.rows[0], w_u)
    data_p = [
        ("id", "INT AUTO_INCREMENT", "NO", "PRIMARY KEY", "Pengenal unik pasien."),
        ("nama", "VARCHAR(100)", "NO", "None", "Nama lengkap pasien sesuai identitas resmi."),
        ("nik_encrypted", "VARBINARY(255)", "NO", "None", "Ciphertext hasil AES_ENCRYPT dari 16 digit NIK."),
        ("tanggal_lahir", "DATE", "NO", "None", "Tanggal lahir pasien untuk verifikasi usia."),
        ("alamat", "TEXT", "YES", "None", "Alamat domisili tempat tinggal pasien."),
        ("no_telepon", "VARCHAR(20)", "YES", "None", "Nomor kontak telepon/WhatsApp pasien.")
    ]
    for r_idx, row in enumerate(data_p):
        rc = t_p.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row): rc[c_idx].paragraphs[0].add_run(val)
    style_table_rows(t_p, w_u)

    add_p("", space_after=4)
    add_h3("Tabel 3.4: Kamus Data Tabel rekam_medis (Data Riwayat Kesehatan Spesifik)")
    t_rm = doc.add_table(rows=7, cols=5)
    t_rm.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(h_u): t_rm.cell(0, i).paragraphs[0].add_run(h)
    style_table_header(t_rm.rows[0], w_u)
    data_rm = [
        ("id", "INT AUTO_INCREMENT", "NO", "PRIMARY KEY", "Nomor unik catatan rekam medis."),
        ("pasien_id", "INT", "NO", "FK -> pasien(id)", "Referensi ke pasien pemilik rekam medis."),
        ("dokter_id", "INT", "NO", "FK -> users(id)", "Dokter penanggung jawab pelayanan medis."),
        ("diagnosa", "TEXT", "NO", "None", "Diagnosis penyakit pasien (sangat rahasia)."),
        ("resep", "TEXT", "YES", "None", "Instruksi resep pengobatan dan dosis."),
        ("tanggal", "DATETIME", "NO", "DEFAULT NOW()", "Waktu pelaksanaan pemeriksaan medis.")
    ]
    for r_idx, row in enumerate(data_rm):
        rc = t_rm.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row): rc[c_idx].paragraphs[0].add_run(val)
    style_table_rows(t_rm, w_u)

    add_p("", space_after=4)
    add_h3("Tabel 3.5: Kamus Data Tabel audit_log (Forensic Incident Tracking)")
    t_al = doc.add_table(rows=8, cols=5)
    t_al.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(h_u): t_al.cell(0, i).paragraphs[0].add_run(h)
    style_table_header(t_al.rows[0], w_u)
    data_al = [
        ("id", "INT AUTO_INCREMENT", "NO", "PRIMARY KEY", "Nomor urut pencatatan insiden."),
        ("user_id", "INT", "YES", "FK -> users(id)", "Akun pengguna pemicu insiden (NULL jika unauth)."),
        ("aksi", "VARCHAR(50)", "NO", "None", "Kategori insiden standar (SQL_INJECTION, dll)."),
        ("tabel_target", "VARCHAR(50)", "YES", "None", "Tabel yang menjadi sasaran eksploitasi."),
        ("query_exec", "TEXT", "YES", "None", "Potongan string kueri SQL untuk rekonstruksi."),
        ("ip_address", "VARCHAR(45)", "NO", "None", "Alamat IP asal klien (IPv4/IPv6)."),
        ("waktu", "DATETIME", "NO", "DEFAULT NOW()", "Stempel waktu kejadian insiden siber.")
    ]
    for r_idx, row in enumerate(data_al):
        rc = t_al.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row): rc[c_idx].paragraphs[0].add_run(val)
    style_table_rows(t_al, w_u)
    add_p("", space_after=8)

    add_h2("3.4 Desain Kebijakan Keamanan & Hardening Policy")
    add_p("Kebijakan keamanan sistem basis data dirumuskan berdasarkan rekomendasi CIS Benchmark:")
    add_p("1. Penegakan Enkripsi Wajib: Parameter require_secure_transport=ON dikonfigurasi pada file mysql-master.cnf dan mysql-slave.cnf. Setiap akun pengguna dibuat dengan instruksi REQUIRE SSL.")
    add_p("2. Matriks Hak Akses Granular (Least Privilege): Seluruh hak administratif (ALL PRIVILEGES, GRANT OPTION, SUPER, FILE) dicabut dari akun aplikasi.")

    # Tabel 3.6: Matriks Hak Akses
    add_h3("Tabel 3.6: Matriks Hak Akses Pengguna (Role-Based Access Control)")
    t_rbac = doc.add_table(rows=5, cols=5)
    t_rbac.alignment = WD_TABLE_ALIGNMENT.CENTER
    w_rbac = [Inches(1.2), Inches(1.3), Inches(1.3), Inches(1.2), Inches(1.25)]
    h_rbac = ["User Akun", "Tabel Operasional (pasien, rekam_medis)", "Tabel Sensitif (users)", "Tabel Logging (audit_log)", "Hak Administratif (DDL/Replication)"]
    for i, h in enumerate(h_rbac): t_rbac.cell(0, i).paragraphs[0].add_run(h)
    style_table_header(t_rbac.rows[0], w_rbac)
    data_rbac = [
        ("app_user", "SELECT, INSERT, UPDATE", "DITOLAK (ERROR 1142)", "INSERT, SELECT", "TIDAK ADA (No DDL/DROP)"),
        ("read_only", "SELECT (Hanya pasien)", "DITOLAK (ERROR 1142)", "DITOLAK (ERROR 1142)", "TIDAK ADA (No DDL/DROP)"),
        ("replicator", "DITOLAK TOTAL", "DITOLAK TOTAL", "DITOLAK TOTAL", "REPLICATION SLAVE ONLY"),
        ("root (Admin)", "ALL PRIVILEGES", "ALL PRIVILEGES", "ALL PRIVILEGES", "ALL (Akses Terbatas Lab)")
    ]
    for r_idx, row in enumerate(data_rbac):
        rc = t_rbac.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row): rc[c_idx].paragraphs[0].add_run(val)
    style_table_rows(t_rbac, w_rbac)
    add_p("", space_after=8)

    add_h2("3.5 Spesifikasi dan Skenario Pengujian Sistem (Pola Uji 3 Fase)")
    add_p("Setiap skenario pengujian dieksekusi mengikuti pola ilmiah Before-Attack ➔ During-Attack ➔ After-Mitigation:")
    add_p("• Fase A (Before-Attack): Membuktikan kondisi baseline operasional normal yang sah.")
    add_p("• Fase B (During-Attack): Melancarkan simulasi serangan, kegagalan sistem, atau pelanggaran wewenang.")
    add_p("• Fase C (After-Mitigation): Membuktikan efektivitas mekanisme pengamanan dalam menangkal atau memulihkan sistem.")

    # Tabel 3.7: Matriks Skenario
    add_h3("Tabel 3.7: Matriks Rancangan Skenario Pengujian Keamanan & Ketersediaan")
    t_sken = doc.add_table(rows=6, cols=5)
    t_sken.alignment = WD_TABLE_ALIGNMENT.CENTER
    w_sken = [Inches(0.6), Inches(1.5), Inches(1.3), Inches(1.4), Inches(1.45)]
    h_sken = ["No", "Skenario Pengujian", "Aspek CIA", "Vektor Ancaman / Skenario", "Kriteria Keberhasilan (Acceptance Criteria)"]
    for i, h in enumerate(h_sken): t_sken.cell(0, i).paragraphs[0].add_run(h)
    style_table_header(t_sken.rows[0], w_sken)
    data_sken = [
        ("1", "Failover & High Availability", "Availability", "Node Master crash mendadak (SPoF)", "HAProxy failover < 2s; SELECT lancar via Slave; INSERT gagal informatif; auto-reconnect."),
        ("2", "SQL Injection Mitigation", "Confidentiality & Integrity", "Injeksi string konkatenatif ' OR '1'='1' --", "Kueri rentan bocor semua baris; Prepared Statement menetralkan payload (0 rows)."),
        ("3", "SSL/TLS & Data Encryption", "Confidentiality", "Intersepsi plaintext & sniffing non-TLS", "Koneksi non-TLS ditolak ERROR 3159; Handshake TLSv1.3; NIK tampil biner acak; kunci valid mengembalikan asli."),
        ("4", "Least Privilege Enforcement", "Integrity & Confidentiality", "Eskalasi wewenang internal & DROP ilegal", "Aksi di luar hak ditolak ERROR 1142; aksi sah berhasil; pelanggaran tercatat di audit."),
        ("5", "Forensic Audit Logging", "Accountability & Non-Repudiation", "Penyusupan tanpa jejak rekam aktivitas", "Seluruh insiden skenario 1-4 terekam lengkap di audit_log dan General Query Log.")
    ]
    for r_idx, row in enumerate(data_sken):
        rc = t_sken.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row): rc[c_idx].paragraphs[0].add_run(val)
    style_table_rows(t_sken, w_sken)

    doc.add_page_break()

    # =========================================================================
    # BAB IV: IMPLEMENTASI DAN HASIL EVALUASI PENGUJIAN
    # =========================================================================
    add_h1("BAB IV — IMPLEMENTASI DAN HASIL EVALUASI PENGUJIAN")
    
    add_h2("4.1 Implementasi Lingkungan Laboratorium Pengujian")
    add_p("Pengujian laboratorium dilakukan menggunakan lingkungan kontainer Docker Compose yang mengorkestrasikan tiga layanan utama: db-master, db-slave, dan haproxy. Seluruh sertifikat keamanan diterbitkan melalui OpenSSL dengan struktur Public Key Infrastructure lokal (CA self-signed). Parameter hardening diinjeksikan secara otomatis saat kontainer melakukan inisialisasi awal.")
    add_p("Pada bab ini, seluruh bukti eksekusi dan hasil pengujian disajikan langsung menggunakan tangkapan layar terminal dan dashboard monitoring aktual yang dihasilkan selama sesi pengujian.")

    # Skenario 1
    add_h2("4.2 Skenario 1: Evaluasi High Availability & Failover Otomatis (Availability)")
    add_p("Skenario 1 bertujuan membuktikan ketahanan sistem terhadap ancaman Single Point of Failure (SPoF). Ketika server utama mengalami crash atau kegagalan perangkat keras, layanan pembacaan data pasien tidak boleh terputus.")
    
    add_p("Fase A: Before-Attack (Kondisi Normal & Replikasi Awal)", bold_prefix="1. ")
    add_p("Pada kondisi normal, penguji membuka peramban web pada http://localhost:8900 untuk memantau status load balancer HAProxy. Dashboard menampilkan bahwa kedua node (db-master dan db-slave) berada dalam kondisi sehat (berwarna hijau / UP).")
    add_ss_box_with_image("1.1", "Dashboard Web Monitoring HAProxy Saat Kedua Node Berstatus UP (Hijau)",
                          "Tangkapan layar peramban web pada http://localhost:8900 memperlihatkan node db-master dan db-slave dalam status aktif hijau (UP).",
                          "image1.png")
    
    add_p("Selanjutnya, penguji menjalankan kueri penambahan data pasien baru melalui gateway HAProxy (port 3300):")
    add_code(
        "docker exec db-master mysql -h haproxy -P 3300 -u app_user -pAppPass123! -e \\\n"
        "\"INSERT INTO klinik_db.pasien (nama, nik_encrypted, tanggal_lahir, alamat, no_telepon) \\\n"
        "VALUES ('Pasien Uji HA', AES_ENCRYPT('3201999988880004', 'KunciRahasiaKlinik2026!'), '1992-04-12', 'Jl. Matraman No. 12', '081234567890');\"\n\n"
        "docker exec db-slave mysql -u root -pRootPass123! -e \\\n"
        "\"SELECT id, nama, alamat FROM klinik_db.pasien WHERE nama = 'Pasien Uji HA';\""
    )
    add_p("Hasil kueri membuktikan bahwa data baru 'Pasien Uji HA' berhasil tersimpan dan langsung tereplikasi secara instan ke node Slave (port 3307).")
    add_ss_box_with_image("1.2", "Terminal: INSERT Berhasil via Port 3300 dan Data Muncul di Slave",
                          "Tangkapan layar terminal membuktikan operasi INSERT via port 3300 sukses dan data terbaca pada pemeriksaan langsung di node Slave.",
                          "image2.png")

    add_p("Fase B: During-Attack (Simulasi Crash Master & Pengujian Failover)", bold_prefix="2. ")
    add_p("Simulasi kegagalan dilakukan dengan mematikan node Master secara paksa:")
    add_code("docker stop db-master")
    add_p("Setelah Master dimatikan, halaman peramban http://localhost:8900 diperbarui. HAProxy secara tepat waktu (interval 2 detik) mendeteksi kegagalan tersebut dan mengubah status db-master menjadi merah (DOWN), sedangkan db-slave tetap hijau (UP).")
    add_ss_box_with_image("1.3", "Dashboard Web HAProxy Saat db-master DOWN (Merah) dan Failover Aktif",
                          "Dashboard monitoring HAProxy mengonfirmasi bahwa db-master ditandai DOWN (merah), sedangkan lalu lintas dialihkan ke db-slave (hijau).",
                          "image3.png")

    add_p("Kemudian, penguji menguji kueri pembacaan (SELECT) dan penulisan (INSERT) ke port 3300 saat Master sedang mati:")
    add_code(
        "docker exec db-slave mysql -h haproxy -P 3300 -u app_user -pAppPass123! -e \\\n"
        "\"SELECT id, nama FROM klinik_db.pasien LIMIT 3;\"\n\n"
        "docker exec db-slave mysql -h haproxy -P 3300 -u app_user -pAppPass123! -e \\\n"
        "\"INSERT INTO klinik_db.pasien (nama, nik_encrypted, tanggal_lahir, alamat, no_telepon) \\\n"
        "VALUES ('Pasien Gagal', AES_ENCRYPT('3201000000000005', 'KunciRahasiaKlinik2026!'), '2000-01-01', 'Jl. Gagal', '081200000000');\""
    )
    add_p("Hasil pengujian menunjukkan bahwa kueri SELECT tetap berjalan sukses (dialihkan ke Slave), sementara kueri INSERT ditolak secara aman dengan pesan kesalahan: ERROR 1290 (HY000): The MySQL server is running with the --read-only option so it cannot execute this statement. Hal ini mencegah terjadinya korupsi atau inkonsistensi data.")
    add_ss_box_with_image("1.4", "Terminal: SELECT Berhasil via Slave dan INSERT Ditolak --read-only",
                          "Terminal menampilkan bahwa pembacaan data pasien tetap lancar, sedangkan penulisan ditolak dengan aman tanpa menyebabkan crash.",
                          "image4.png")

    add_p("Fase C: After-Mitigation (Pemulihan Master & Resinkronisasi Replikasi)", bold_prefix="3. ")
    add_p("Node Master dihidupkan kembali:")
    add_code("docker start db-master")
    add_p("Setelah menunggu ~10 detik, penguji memeriksa status replikasi pada Slave:")
    add_code("docker exec db-slave mysql -u root -pRootPass123! -e \"SHOW REPLICA STATUS\\G\"")
    add_p("Output terminal menunjukkan bahwa Replica_IO_Running: Yes dan Replica_SQL_Running: Yes. Replikasi berhasil tersambung kembali secara otomatis tanpa intervensi manual.")
    add_ss_box_with_image("1.5", "Terminal: Verifikasi SHOW REPLICA STATUS (Replica IO & SQL Running: Yes)",
                          "Pemeriksaan SHOW REPLICA STATUS menunjukkan replikasi otomatis pulih dan posisi log tersinkronisasi penuh.",
                          "image5.png")

    add_p("Pemeriksaan ulang pada dashboard peramban http://localhost:8900 membuktikan bahwa kedua node kembali berstatus hijau (UP).")
    add_ss_box_with_image("1.6", "Dashboard Web HAProxy: Kedua Node Pulih dan Berstatus Hijau (UP)",
                          "Dashboard monitoring HAProxy menampilkan kembali status operasional normal (kedua server Master dan Slave berstatus UP).",
                          "image6.png")

    # Skenario 2
    add_h2("4.3 Skenario 2: Eksploitasi & Mitigasi SQL Injection (Confidentiality & Integrity)")
    add_p("Skenario 2 mengevaluasi kerentanan interpolasi string dinamis dan membuktikan keandalan parameterized prepared statements.")

    add_p("Fase A: Before-Attack (Baseline Kondisi Data Normal)", bold_prefix="1. ")
    add_p("Penguji menjalankan kueri baseline untuk menampilkan daftar pasien normal:")
    add_code("docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e \"SELECT id, nama, tanggal_lahir FROM klinik_db.pasien;\"")
    add_ss_box_with_image("2.1", "Terminal: Baseline Data Pasien Normal Sebelum Penyerangan",
                          "Daftar data pasien normal (Ahmad Fauzi, Siti Rahayu, Budi Santoso, Pasien Uji HA) tercatat dalam basis data.",
                          "image7.png")

    add_p("Fase B: During-Attack (Injeksi SQL Menggunakan String Concatenation)", bold_prefix="2. ")
    add_p("Penyerang menyuntikkan payload ' OR '1'='1' -- pada kueri pencarian nama pasien:")
    add_code(
        "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e \\\n"
        "\"USE klinik_db; SET @input = \\\"' OR '1'='1' -- \\\"; \\\n"
        "SET @query = CONCAT('SELECT id, nama, tanggal_lahir FROM pasien WHERE nama = \\'', @input, '\\''); \\\n"
        "SELECT '=== QUERY RENTAN YANG TERBENTUK ===' AS info; SELECT @query AS query_yang_dieksekusi; \\\n"
        "SELECT '=== HASIL EKSEKUSI (DATA BOCOR) ===' AS info; \\\n"
        "PREPARE stmt FROM @query; EXECUTE stmt; DEALLOCATE PREPARE stmt;\""
    )
    add_p("Akibat ekspresi logika '1'='1' selalu bernilai TRUE, seluruh data pasien bocor tanpa batasan filter.")
    add_ss_box_with_image("2.2", "Terminal: Eksploitasi SQL Injection String Concatenation (Data Pasien Bocor)",
                          "Kueri rentan mengeksekusi payload injeksi sehingga seluruh data pasien bocor melompati filter identitas.",
                          "image8.png")

    add_p("Serangan diulangi pada tabel rekam_medis:")
    add_code(
        "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e \\\n"
        "\"USE klinik_db; SET @input = \\\"' OR '1'='1' -- \\\"; \\\n"
        "SET @query = CONCAT('SELECT id, pasien_id, diagnosa, resep FROM rekam_medis WHERE diagnosa = \\'', @input, '\\''); \\\n"
        "SELECT '=== QUERY RENTAN REKAM MEDIS ===' AS info; SELECT @query AS query_yang_dieksekusi; \\\n"
        "SELECT '=== HASIL EKSEKUSI (REKAM MEDIS BOCOR) ===' AS info; \\\n"
        "PREPARE stmt FROM @query; EXECUTE stmt; DEALLOCATE PREPARE stmt;\""
    )
    add_p("Seluruh catatan riwayat penyakit pasien (Hipertensi ringan, Diabetes tipe 2, ISPA) dan resep obat bocor kepada penyerang.")
    add_ss_box_with_image("2.3", "Terminal: Eksploitasi SQL Injection Mengakibatkan Rekam Medis Bocor",
                          "Data riwayat penyakit sensitif dan resep obat pasien terekspos akibat tiadanya validasi kueri SQL.",
                          "image9.png")

    add_p("Fase C: After-Mitigation (Mitigasi Menggunakan Prepared Statement)", bold_prefix="3. ")
    add_p("Kueri ditulis ulang menggunakan Prepared Statement dengan parameter terikat (?):")
    add_code(
        "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e \\\n"
        "\"USE klinik_db; PREPARE stmt FROM 'SELECT id, nama, tanggal_lahir FROM pasien WHERE nama = ?'; \\\n"
        "SET @input = \\\"' OR '1'='1' -- \\\"; \\\n"
        "SELECT '=== MITIGASI: PREPARED STATEMENT DENGAN PARAMETER ? ===' AS info; \\\n"
        "SELECT @input AS payload_yang_dicoba; \\\n"
        "SELECT '=== HASIL EKSEKUSI (SERANGAN GAGAL) ===' AS info; \\\n"
        "EXECUTE stmt USING @input; DEALLOCATE PREPARE stmt;\""
    )
    add_p("Mesin MySQL memperlakukan payload murni sebagai literal teks. Hasil kueri mengembalikan Empty set (0 rows). Serangan gagal total.")
    add_ss_box_with_image("2.4", "Terminal: Mitigasi Prepared Statement Berhasil Menetralkan Serangan (0 Rows)",
                          "Prepared statement berhasil memblokir serangan dan mengembalikan nol baris data.",
                          "image10.png")

    # Skenario 3
    add_h2("4.4 Skenario 3: Penegakan SSL/TLS & Kriptografi Data-at-Rest (Confidentiality)")
    add_p("Skenario 3 membuktikan penegakan kerahasiaan data-in-transit (TLSv1.3) dan data-at-rest (AES-256).")

    add_p("Fase A: Penolakan Koneksi Non-TLS", bold_prefix="1. ")
    add_p("Klien mencoba terhubung ke server basis data dengan mematikan SSL (--ssl-mode=DISABLED):")
    add_code("docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! --ssl-mode=DISABLED -e \"SELECT 1;\"")
    add_p("Server menolak koneksi dengan pesan error: ERROR 3159 (HY000): Connections using insecure transport are prohibited while --require_secure_transport=ON.")
    add_ss_box_with_image("3.1", "Terminal: Penolakan Koneksi Non-TLS dengan ERROR 3159 (require_secure_transport)",
                          "Koneksi tanpa enkripsi ditolak mentah-mentah oleh server database sesuai kebijakan keamanan ketat.",
                          "image11.png")

    add_p("Penguji kemudian memverifikasi cipher TLS yang aktif pada koneksi terenkripsi yang sah:")
    add_code("docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e \"SHOW STATUS LIKE 'Ssl_cipher'; SHOW STATUS LIKE 'Ssl_version';\"")
    add_p("Server merespons dengan Ssl_cipher: TLS_AES_256_GCM_SHA384 dan Ssl_version: TLSv1.3.")
    add_ss_box_with_image("3.2", "Terminal: Verifikasi Cipher TLS Aktif (TLS_AES_256_GCM_SHA384 dan TLSv1.3)",
                          "Terminal mengonfirmasi bahwa sesi komunikasi berjalan aman di bawah standar TLSv1.3 dengan cipher terkuat.",
                          "image12.png")

    add_p("Fase B: Enkripsi Data-at-Rest (NIK Pasien)", bold_prefix="2. ")
    add_p("Penguji memeriksa representasi heksadesimal dari kolom nik_encrypted pada tabel pasien:")
    add_code("docker exec db-master mysql -h 127.0.0.1 -P 3306 -u root -pRootPass123! -e \"SELECT id, nama, HEX(nik_encrypted) AS nik_ciphertext FROM klinik_db.pasien;\"")
    add_p("Data NIK tersimpan dalam ciphertext biner acak, sehingga pencurian fisik file basis data tidak akan membocorkan NIK pasien.")
    add_ss_box_with_image("3.3", "Terminal: Verifikasi Data-at-Rest Kolom nik_ciphertext Berisi Karakter Hex Acak",
                          "Nilai NIK pada media penyimpanan fisik hanya berupa deretan karakter heksadesimal acak terenkripsi.",
                          "image13.png")

    add_p("Penguji memverifikasi fungsi dekripsi menggunakan kunci yang sah dan kunci yang salah:")
    add_code(
        "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u root -pRootPass123! -e \\\n"
        "\"SELECT nama, CAST(AES_DECRYPT(nik_encrypted, 'KunciRahasiaKlinik2026!') AS CHAR) AS NIK_Kunci_Benar, \\\n"
        "CAST(AES_DECRYPT(nik_encrypted, 'KunciSalah!') AS CHAR) AS NIK_Kunci_Salah FROM klinik_db.pasien;\""
    )
    add_p("Kunci benar berhasil menampilkan NIK asli 16 digit, sementara kunci salah mengembalikan nilai NULL.")
    add_ss_box_with_image("3.4", "Terminal: Validasi Dekripsi Bersyarat AES_DECRYPT (Kunci Benar vs Kunci Salah)",
                          "Kunci kriptografi benar mengembalikan NIK asli, sedangkan kunci salah mengembalikan NULL secara aman.",
                          "image14.png")

    add_p("Fase C: After-Mitigation (Verifikasi Enkripsi End-to-End)", bold_prefix="3. ")
    add_p("Penguji memeriksa status SSL sesi lengkap dan variabel permanen require_secure_transport:")
    add_code(
        "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e \\\n"
        "\"SHOW STATUS WHERE Variable_name IN ('Ssl_version', 'Ssl_cipher', 'Ssl_session_cache_mode', 'Ssl_default_timeout');\"\n\n"
        "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u root -pRootPass123! -e \\\n"
        "\"SHOW VARIABLES LIKE 'require_secure_transport';\""
    )
    add_p("Output membuktikan bahwa parameter server require_secure_transport bernilai ON dan sesi aktif menggunakan TLSv1.3.")
    add_ss_box_with_image("3.5", "Terminal: Verifikasi Status SSL Sesi Aktif dan Enforcement Policy Server ON",
                          "Pemeriksaan menyeluruh menunjukkan protokol enkripsi transport aktif permanen pada konfigurasi server.",
                          "image15.png")

    # Skenario 4
    add_h2("4.5 Skenario 4: Penegakan Role-Based Access Control (RBAC) (Integrity & Confidentiality)")
    add_p("Skenario 4 membuktikan keandalan prinsip Least Privilege dalam mencegah eskalasi wewenang internal.")

    add_p("Fase A: Before-Attack (Operasi Sah Sesuai Hak Akses)", bold_prefix="1. ")
    add_p("Penguji menjalankan kueri yang sah sesuai wewenang masing-masing pengguna:")
    add_code(
        "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u read_only -pReadOnly123! -e \\\n"
        "\"SELECT id, nama, alamat FROM klinik_db.pasien;\"\n\n"
        "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e \\\n"
        "\"INSERT INTO klinik_db.pasien (nama, nik_encrypted, tanggal_lahir, alamat, no_telepon) \\\n"
        "VALUES ('Pasien Test Priv', AES_ENCRYPT('3201111122223333', 'KunciRahasiaKlinik2026!'), '1998-07-20', 'Jl. Testing', '081299998888');\""
    )
    add_p("Pengguna read_only berhasil membaca tabel pasien dan app_user berhasil melakukan penambahan data.")
    add_ss_box_with_image("4.1", "Terminal: Operasi Sah (SELECT oleh read_only dan INSERT oleh app_user)",
                          "Kueri operasional sah dieksekusi dengan sukses sesuai matriks hak istimewa masing-masing akun.",
                          "image16.png")

    add_p("Fase B: During-Attack (Percobaan Pelanggaran Hak & Eskalasi Wewenang)", bold_prefix="2. ")
    add_p("1. Pengguna read_only mencoba melakukan operasi INSERT, SELECT rekam_medis, dan DROP TABLE:")
    add_code(
        "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u read_only -pReadPass123! -e \"INSERT INTO klinik_db.pasien (nama) VALUES ('Hacker');\"\n"
        "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u read_only -pReadPass123! -e \"SELECT * FROM klinik_db.rekam_medis;\"\n"
        "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u read_only -pReadPass123! -e \"DROP TABLE klinik_db.pasien;\""
    )
    add_p("Ketiga percobaan di atas ditolak oleh server dengan pesan ERROR 1142 (42000): command denied to user.")
    add_ss_box_with_image("4.2", "Terminal: Tiga Pesan Penolakan ERROR 1142 pada User read_only",
                          "Upaya penulisan data, pembacaan rekam medis rahasia, dan perusakan skema oleh read_only diblokir sistem.",
                          "image17.png")

    add_p("2. Pengguna app_user mencoba mengintip tabel users dan DROP TABLE pasien, serta replicator mencoba SELECT:")
    add_code(
        "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e \"SELECT * FROM klinik_db.users;\"\n"
        "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e \"DROP TABLE klinik_db.pasien;\"\n"
        "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u replicator -pReplPass123! -e \"SELECT * FROM klinik_db.pasien;\""
    )
    add_p("Seluruh percobaan ditolak dengan ERROR 1142.")
    add_ss_box_with_image("4.3", "Terminal: Penolakan Hak Akses ERROR 1142 untuk User app_user dan replicator",
                          "Pencegahan kebocoran kredensial admin dan pencegahan operasi DROP TABLE oleh user aplikasi.",
                          "image18.png")

    add_p("Fase C: After-Mitigation (Verifikasi Matriks Hak Akses di Server)", bold_prefix="3. ")
    add_p("Penguji memverifikasi aturan hak akses formal pada kamus data MySQL:")
    add_code("docker exec db-master mysql -h 127.0.0.1 -P 3306 -u root -pRootPass123! -e \"SHOW GRANTS FOR 'read_only'@'%'; SHOW GRANTS FOR 'app_user'@'%'; SHOW GRANTS FOR 'replicator'@'%';\"")
    add_ss_box_with_image("4.4", "Terminal: Verifikasi SHOW GRANTS untuk read_only, app_user, dan replicator",
                          "Matriks hak akses menunjukkan read_only hanya memiliki izin SELECT pada pasien, app_user pada tabel operasional, dan replicator hanya izin replikasi.",
                          "image19.png")

    # Skenario 5
    add_h2("4.6 Skenario 5: Forensic Audit Logging & General Query Log (Accountability)")
    add_p("Skenario 5 mengonfirmasi akuntabilitas dan kenirsangkalan (non-repudiation) melalui rekaman jejak audit forensik dua lapis.")

    add_p("Fase A: Pencatatan & Rekapitulasi Insiden di Tabel audit_log (Layer 1)", bold_prefix="1. ")
    add_p("Seluruh insiden keamanan yang disimulasikan pada skenario sebelumnya dicatat dan direkapitulasi:")
    add_code(
        "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u root -pRootPass123! -e \\\n"
        "\"SELECT id, user_id, aksi, tabel_target, ip_address, waktu FROM klinik_db.audit_log ORDER BY id ASC;\""
    )
    add_ss_box_with_image("5.1", "Terminal: Rekapitulasi Seluruh Percobaan Serangan di Tabel audit_log",
                          "Rekapitulasi lengkap insiden siber pada tabel audit_log memuat stempel waktu, user_id, kategori insiden, dan IP asal.",
                          "image20.png")

    add_p("Fase B: Deteksi Anomali & Rekonstruksi Forensik Query", bold_prefix="2. ")
    add_p("Penguji melakukan pemfilteran terhadap aksi-aksi berbahaya dan merekonstruksi rincian kueri serangan:")
    add_code(
        "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u root -pRootPass123! -e \\\n"
        "\"SELECT user_id, aksi, tabel_target, DATE_FORMAT(waktu, '%Y-%m-%d %H:%i:%s') AS waktu_kejadian, ip_address \\\n"
        "FROM klinik_db.audit_log WHERE aksi IN ('SQL_INJECTION_ATTEMPT', 'UNAUTHORIZED_INSERT', 'UNAUTHORIZED_DROP', 'UNAUTHORIZED_SELECT') ORDER BY waktu ASC;\"\n\n"
        "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u root -pRootPass123! -e \\\n"
        "\"SELECT * FROM klinik_db.audit_log WHERE aksi = 'SQL_INJECTION_ATTEMPT' AND tabel_target = 'rekam_medis'\\G\""
    )
    add_p("Melalui tampilan vertikal (\\G), penyelidik forensik dapat melihat secara utuh string kueri penyerang untuk pembuktian digital.")
    add_ss_box_with_image("5.2", "Terminal: Filter Anomali dan Rekonstruksi Forensik Query Eksploitasi (\\G)",
                          "Detail kueri eksploitasi SQL Injection tersimpan utuh di kolom query_exec untuk keperluan analisis forensik.",
                          "image21.png")

    add_p("Fase C: Verifikasi General Query Log Mesin MySQL (Layer 2 - Server Level)", bold_prefix="3. ")
    add_p("Penguji memeriksa berkas log sistem operasi pada server MySQL:")
    add_code("docker exec db-master tail -n 25 /var/log/mysql/general.log")
    add_p("Berkas /var/log/mysql/general.log membuktikan bahwa setiap kueri nyata dicatat secara independen oleh mesin server MySQL, sehingga jejak audit tidak dapat dihapus meskipun penyerang mencoba memanipulasi tabel basis data.")
    add_ss_box_with_image("5.3", "Terminal: Bukti Log Independen pada Server-Level General Query Log (/var/log)",
                          "Potongan berkas log sistem operasi membuktikan rekaman audit lapis kedua aktif secara mandiri di tingkat server.",
                          "image22.png")

    # Evaluasi & Pembahasan
    add_h2("4.7 Pembahasan Komparatif Hasil Evaluasi & Analisis Regulasi UU PDP")
    add_p("Hasil pengujian dari kelima skenario membuktikan bahwa arsitektur basis data klinik_db berhasil memenuhi seluruh kriteria penerimaan (acceptance criteria) yang ditetapkan pada dokumen perancangan sistem:")

    # Tabel 4.1: Evaluasi
    add_h3("Tabel 4.1: Rekapitulasi Evaluasi Keberhasilan Pengujian vs Acceptance Criteria")
    t_ev = doc.add_table(rows=6, cols=5)
    t_ev.alignment = WD_TABLE_ALIGNMENT.CENTER
    w_ev = [Inches(0.6), Inches(1.5), Inches(1.3), Inches(1.8), Inches(1.05)]
    h_ev = ["No", "Skenario Pengujian", "Aspek Keamanan", "Kriteria Keberhasilan (Acceptance)", "Status Hasil Uji"]
    for i, h in enumerate(h_ev): t_ev.cell(0, i).paragraphs[0].add_run(h)
    style_table_header(t_ev.rows[0], w_ev)
    data_ev = [
        ("1", "Failover & High Availability", "Availability", "Failover < 2s; SELECT lancar via Slave; INSERT tertangani aman; reconnect otomatis.", "100% SUKSES (PASS)"),
        ("2", "SQL Injection Mitigation", "Confidentiality & Integrity", "Payload injeksi dinetralkan oleh prepared statement; 0 baris data bocor.", "100% SUKSES (PASS)"),
        ("3", "SSL/TLS & Data Encryption", "Confidentiality", "Koneksi non-TLS ditolak ERROR 3159; Cipher TLSv1.3 aktif; NIK terenkripsi AES-256.", "100% SUKSES (PASS)"),
        ("4", "Least Privilege Enforcement", "Integrity & Confidentiality", "Pelanggaran wewenang ditolak ERROR 1142; aksi sah berjalan normal.", "100% SUKSES (PASS)"),
        ("5", "Forensic Audit Logging", "Accountability", "Rekaman insiden tersimpan redundan di tabel audit dan General Query Log server.", "100% SUKSES (PASS)")
    ]
    for r_idx, row in enumerate(data_ev):
        rc = t_ev.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row): rc[c_idx].paragraphs[0].add_run(val)
    style_table_rows(t_ev, w_ev)
    add_p("", space_after=8)

    add_p("Dari perspektif hukum nasional, implementasi ini selaras dengan amanat Undang-Undang No. 27 Tahun 2022 tentang Perlindungan Data Pribadi:")

    # Tabel 4.2: UU PDP Mapping
    add_h3("Tabel 4.2: Pemetaan Hasil Pengujian terhadap Pasal-Pasal UU PDP No. 27 Tahun 2022")
    t_pdp = doc.add_table(rows=5, cols=4)
    t_pdp.alignment = WD_TABLE_ALIGNMENT.CENTER
    w_pdp = [Inches(1.1), Inches(1.8), Inches(1.8), Inches(1.55)]
    h_pdp = ["Pasal UU PDP", "Kewajiban Pengendali Data", "Implementasi Teknis klinik_db", "Hasil Evaluasi Pengujian"]
    for i, h in enumerate(h_pdp): t_pdp.cell(0, i).paragraphs[0].add_run(h)
    style_table_header(t_pdp.rows[0], w_pdp)
    data_pdp = [
        ("Pasal 35", "Mencegah data pribadi diakses secara tidak sah.", "Penegakan TLSv1.3 wajib & Enkripsi kolom AES-256 pada NIK.", "Terbukti: Koneksi tanpa TLS ditolak; NIK tampil acak (Skenario 3)."),
        ("Pasal 36", "Menjaga integritas & keakuratan data pribadi.", "Prepared statement anti-SQLi & Kontrol akses peran (RBAC).", "Terbukti: Injeksi gagal; Modifikasi tidak sah diblokir (Skenario 2 & 4)."),
        ("Pasal 37", "Menjaga ketersediaan dan keandalan sistem.", "Master-Slave Replication & HAProxy failover otomatis 2 detik.", "Terbukti: Layanan baca tetap aktif saat Master crash (Skenario 1)."),
        ("Pasal 39", "Merekam seluruh aktivitas pemrosesan data.", "Dual-tier Logging (tabel audit_log & General Query Log OS).", "Terbukti: Rekonstruksi kronologis insiden berhasil (Skenario 5).")
    ]
    for r_idx, row in enumerate(data_pdp):
        rc = t_pdp.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row): rc[c_idx].paragraphs[0].add_run(val)
    style_table_rows(t_pdp, w_pdp)

    doc.add_page_break()

    # =========================================================================
    # BAB V: KESIMPULAN DAN SARAN
    # =========================================================================
    add_h1("BAB V — KESIMPULAN DAN SARAN")
    
    add_h2("5.1 Kesimpulan Eksekutif")
    add_p("Berdasarkan perancangan arsitektur, konfigurasi lingkungan laboratorium, eksekusi lima skenario pengujian, dan analisis evaluasi yang telah dilakukan, dapat diambil kesimpulan eksekutif sebagai berikut:")
    add_p("1. Pengentasan Titik Kegagalan Tunggal (Availability): Arsitektur High Availability Cluster yang menggabungkan replikasi asinkron Master-Slave berformat ROW dan Layer-4 TCP load balancer HAProxy terbukti sangat andal dalam menjamin ketersediaan data rekam medis. Mekanisme health check berkala (interval 2 detik) berhasil melakukan failover otomatis ke node Slave ketika Master mengalami crash mendadak, mempertahankan aksesibilitas layanan pembacaan data pasien tanpa periode downtime yang berarti.")
    add_p("2. Ketahanan Integritas terhadap SQL Injection (Integrity): Penggunaan parameterized prepared statements secara mutlak terbukti mampu menetralkan serangan injeksi kueri (seperti payload ' OR '1'='1' --). Dengan memisahkan instruksi kueri dan data masukan, mesin basis data memperlakukan data malicious sebagai literal murni sehingga menghasilkan 0 baris data bocor, berbeda drastis dengan kueri konkatenatif yang membocorkan seluruh isi basis data.")
    add_p("3. Perlindungan Kerahasiaan Data Sensitif Berlapis (Confidentiality): Penegakan kewajiban enkripsi transport TLSv1.3 (require_secure_transport=ON) secara efektif menolak seluruh koneksi tidak aman (ERROR 3159), mengeliminasi risiko packet sniffing pada jaringan lokal. Secara simultan, enkripsi data-at-rest tingkat kolom menggunakan algoritma simetris AES-256 berhasil menyamarkan nomor identitas kependudukan (NIK) menjadi ciphertext biner acak yang hanya dapat didekripsi dengan kunci yang sah.")
    add_p("4. Pembatasan Permukaan Serangan Internal (Least Privilege): Penerapan Role-Based Access Control (RBAC) dengan pemisahan peran akun (app_user, read_only, dan replicator) secara konsisten menggagalkan seluruh percobaan eskalasi wewenang dan perusakan skema basis data (ERROR 1142), membatasi dampak kompromi akun internal.")
    add_p("5. Jaminan Akuntabilitas dan Kenirsangkalan (Accountability): Sistem pencatatan audit forensik dua lapis (tabel audit_log tingkat aplikasi dan General Query Log tingkat sistem operasi) mampu merekam seluruh kronologi insiden siber secara redundan dan independen, memudahkan proses rekonstruksi barang bukti digital dan memenuhi prinsip kepatuhan regulasi UU PDP No. 27 Tahun 2022.")

    add_h2("5.2 Keterbatasan Proyek")
    add_p("Meskipun sistem telah berhasil membuktikan seluruh hipotesis keamanan dan ketersediaan, penyusun mencatat beberapa keterbatasan yang perlu diakui secara jujur:")
    add_p("1. Manajemen Kunci Kriptografi: Pada lingkungan demonstrasi lab ini, frasa kunci enkripsi AES disematkan melalui parameter sesi kueri. Pada lingkungan produksi nyata, kunci master tidak boleh disimpan dalam skrip atau database, melainkan wajib diisolasi menggunakan Hardware Security Module (HSM) atau layanan Key Management Service (KMS) terpisah.")
    add_p("2. Karakteristik Replikasi Asinkron: Replikasi Master-Slave MySQL standar bersifat asinkron satu arah (one-way asynchronous). Apabila node Master mengalami kerusakan fatal secara permanen sebelum log sempat terkirim, terdapat potensi lag transaksi kecil (data loss). Selain itu, promosi permanen Slave menjadi Master baru masih memerlukan intervensi manual atau integrasi modul Orkestrator otomatis.")
    add_p("3. Sertifikat Publik: Implementasi sertifikat TLS menggunakan Certificate Authority lokal (self-signed). Untuk implementasi publik skala luas yang terhubung ke jaringan internet, diperlukan sertifikat digital dari CA komersial atau penyedia publik terakreditasi.")

    add_h2("5.3 Saran & Rekomendasi Pengembangan Lanjutan")
    add_p("Guna menyempurnakan arsitektur ini menuju kesiapan produksi penuh (production-ready), disarankan langkah-langkah pengembangan lanjutan sebagai berikut:")
    add_p("1. Integrasi Dedicated Key Management Service (KMS): Mengintegrasikan solusi manajemen kunci eksternal seperti HashiCorp Vault atau AWS KMS dengan mekanisme rotasi kunci otomatis berkala (automatic key rotation) dan audit akses kunci kriptografi.")
    add_p("2. Adopsi Arsitektur Synchronous Multi-Master Cluster: Mengembangkan replikasi menuju teknologi sinkron penuh seperti MySQL Group Replication atau Galera Cluster (MariaDB) guna menjamin zero data loss (RPO = 0) dan multi-node active writing.")
    add_p("3. Penerapan Web Application Firewall (WAF) & Database Firewall: Menempatkan modul inspeksi paket mendalam (seperti ModSecurity atau MySQL Enterprise Firewall) di depan load balancer untuk mendeteksi dan memblokir anomali kueri sebelum mencapai mesin basis data.")
    add_p("4. Pengintegrasian SIEM Otomatis: Menghubungkan berkas General Query Log ke platform Security Information and Event Management (SIEM) seperti Elasticsearch, Logstash, dan Kibana (ELK Stack) untuk analisis ancaman berbasis kecerdasan buatan dan notifikasi insiden waktu nyata (real-time alert).")

    # Lembar Pengesahan
    add_p("", space_after=12)
    add_h2("5.4 Lembar Pengesahan Pelaksanaan Proyek Akhir")
    add_p("Laporan akhir proyek pengujian keamanan sistem basis data (klinik_db) ini telah disusun, diuji, diverifikasi, dan disahkan oleh tim pengembang sebagai pemenuhan Proyek Akhir Mata Kuliah Keamanan Sistem Informasi.")

    t_sign = doc.add_table(rows=2, cols=2)
    t_sign.alignment = WD_TABLE_ALIGNMENT.CENTER
    w_sign = [Inches(3.1), Inches(3.1)]
    c1 = t_sign.cell(0, 0); c2 = t_sign.cell(0, 1)
    set_cell_margins(c1, top=100, bottom=100, left=100, right=100)
    set_cell_margins(c2, top=100, bottom=100, left=100, right=100)
    
    p_s1 = c1.paragraphs[0]
    p_s1.add_run("Diuji dan Disusun Oleh:\nTim Mahasiswa Kelompok 4 (Kelas 3SI1)\n\n\n\n( M Rezky Raya Kilwouw & Tim )\nNIM: 222313190")
    p_s1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    p_s2 = c2.paragraphs[0]
    p_s2.add_run("Mengetahui & Menyetujui:\nDosen Pengampu Keamanan SI\n\n\n\n( _____________________________ )\nNIP: ")
    p_s2.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_page_break()

    # =========================================================================
    # DAFTAR PUSTAKA
    # =========================================================================
    add_h1("DAFTAR PUSTAKA")
    
    daftar_pustaka = [
        "[1] Center for Internet Security (CIS), \"CIS MySQL 8.0 Benchmark v1.4.0,\" CIS Security Benchmarks, Tech. Rep., 2023.",
        "[2] National Institute of Standards and Technology (NIST), \"Guide to Storage Encryption Technologies for End User Devices,\" NIST Special Publication 800-111, Gaithersburg, MD, Tech. Rep., 2007.",
        "[3] D. Kone, \"Security and Performance Evaluation of Relational Database Replication Architectures,\" Master's thesis, Department of Computer Science, 2021.",
        "[4] OWASP Foundation, \"OWASP Top 10: The Ten Most Critical Web Application Security Risks,\" OWASP Project Report, 2021. [Online]. Tersedia: https://owasp.org/Top10/",
        "[5] Republik Indonesia, \"Undang-Undang Republik Indonesia Nomor 27 Tahun 2022 tentang Perlindungan Data Pribadi,\" Lembaran Negara Republik Indonesia Tahun 2022 Nomor 196, Jakarta, 2022.",
        "[6] Kementerian Kesehatan Republik Indonesia, \"Peraturan Menteri Kesehatan Republik Indonesia Nomor 24 Tahun 2022 tentang Rekam Medis,\" Berita Negara Republik Indonesia Tahun 2022 Nomor 829, Jakarta, 2022.",
        "[7] A. Pratama and S. Wijaya, \"Database Forensics and Security Measures to Defend from Cyber Threats,\" International Journal of Information Security and Privacy, vol. 17, no. 2, pp. 45–62, 2023.",
        "[8] R. Kurniawan, M. Hidayat, and F. Rahman, \"Database Security and Performance: A Case of SQL Injection Attacks Using Docker-Based Virtualisation and Its Effect on Performance,\" Journal of Information Security Applications, vol. 68, p. 103215, 2022.",
        "[9] Oracle Corporation, \"Enhancing MySQL Database Security with MySQL Enterprise Transparent Data Encryption (TDE),\" Oracle Technical White Paper, Redwood City, CA, Tech. Rep., 2022.",
        "[10] Oracle Corporation, \"MySQL Security Best Practices: Securing the World's Most Popular Open Source Database,\" Oracle Security Guide, 2023.",
        "[11] H. Zhang, L. Wang, and Y. Liu, \"Survey on Cloud Database Security: Cryptographic Techniques, Intrusion Detection and Intelligent Defense Mechanisms,\" ACM Computing Surveys, vol. 56, no. 4, pp. 1–35, 2024.",
        "[12] J. Stallings and L. Brown, Computer Security: Principles and Practice, 4th ed. Boston, MA: Pearson Education, 2018.",
        "[13] HAProxy Technologies, \"HAProxy Architecture and Configuration Guide: High Availability and Load Balancing for Enterprise Databases,\" HAProxy Technical Documentation, 2023. [Online]. Tersedia: https://www.haproxy.com/documentation/"
    ]
    
    for dp in daftar_pustaka:
        p_dp = doc.add_paragraph()
        p_dp.paragraph_format.space_before = Pt(2)
        p_dp.paragraph_format.space_after = Pt(6)
        p_dp.paragraph_format.left_indent = Inches(0.4)
        p_dp.paragraph_format.first_line_indent = Inches(-0.4)
        p_dp.paragraph_format.line_spacing = 1.15
        r = p_dp.add_run(dp)
        r.font.name = 'Arial'
        r.font.size = Pt(9)
        r.font.color.rgb = DARK

    doc.add_page_break()

    # =========================================================================
    # LAMPIRAN
    # =========================================================================
    add_h1("LAMPIRAN")
    
    add_h2("Lampiran A: Berkas Konfigurasi Orkestrasi docker-compose.yml")
    add_p("Konfigurasi layanan db-master, db-slave, dan haproxy pada Jalur A:")
    add_code(
        "version: '3.8'\n\n"
        "services:\n"
        "  db-master:\n"
        "    image: mysql:8.0\n"
        "    container_name: db-master\n"
        "    environment:\n"
        "      MYSQL_ROOT_PASSWORD: RootPass123!\n"
        "      MYSQL_DATABASE: klinik_db\n"
        "    volumes:\n"
        "      - ./config/mysql-master.cnf:/etc/mysql/conf.d/hardening.cnf:ro\n"
        "      - ./ssl:/etc/mysql/ssl:ro\n"
        "      - ./sql/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql:ro\n"
        "      - ./sql/seed.sql:/docker-entrypoint-initdb.d/02-seed.sql:ro\n"
        "    ports:\n"
        "      - \"3306:3306\"\n"
        "    networks:\n"
        "      - klinik-net\n\n"
        "  db-slave:\n"
        "    image: mysql:8.0\n"
        "    container_name: db-slave\n"
        "    environment:\n"
        "      MYSQL_ROOT_PASSWORD: RootPass123!\n"
        "    volumes:\n"
        "      - ./config/mysql-slave.cnf:/etc/mysql/conf.d/hardening.cnf:ro\n"
        "      - ./ssl:/etc/mysql/ssl:ro\n"
        "    ports:\n"
        "      - \"3307:3306\"\n"
        "    networks:\n"
        "      - klinik-net\n\n"
        "  haproxy:\n"
        "    image: haproxy:2.8-alpine\n"
        "    container_name: haproxy\n"
        "    volumes:\n"
        "      - ./config/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro\n"
        "    ports:\n"
        "      - \"3300:3300\"\n"
        "      - \"8404:8404\"\n"
        "    depends_on:\n"
        "      - db-master\n"
        "      - db-slave\n"
        "    networks:\n"
        "      - klinik-net\n\n"
        "networks:\n"
        "  klinik-net:\n"
        "    driver: bridge\n"
    )

    add_h2("Lampiran B: Berkas Konfigurasi Load Balancer haproxy.cfg")
    add_p("Konfigurasi reverse proxy Layer-4 TCP dan health check berkala:")
    add_code(
        "global\n"
        "    log stdout format raw local0\n"
        "    maxconn 1024\n\n"
        "defaults\n"
        "    log global\n"
        "    mode tcp\n"
        "    timeout connect 5s\n"
        "    timeout client 1m\n"
        "    timeout server 1m\n\n"
        "frontend mysql_front\n"
        "    bind *:3300\n"
        "    default_backend mysql_back\n\n"
        "backend mysql_back\n"
        "    mode tcp\n"
        "    balance roundrobin\n"
        "    option tcp-check\n"
        "    tcp-check connect port 3306\n"
        "    server master db-master:3306 check inter 2s fall 2 rise 2\n"
        "    server slave  db-slave:3306 check inter 2s fall 2 rise 2 backup\n\n"
        "frontend stats\n"
        "    mode http\n"
        "    bind *:8404\n"
        "    stats enable\n"
        "    stats uri /\n"
        "    stats refresh 2s\n"
    )

    add_h2("Lampiran C: Berkas Konfigurasi Hardening mysql-master.cnf")
    add_p("Konfigurasi hardening, penegakan SSL, dan binary log pada node Master:")
    add_code(
        "[mysqld]\n"
        "server-id = 1\n"
        "log_bin = mysql-bin\n"
        "binlog_format = ROW\n"
        "binlog_do_db = klinik_db\n\n"
        "# SSL / TLS Enforcement\n"
        "require_secure_transport = ON\n"
        "ssl_ca = /etc/mysql/ssl/ca.pem\n"
        "ssl_cert = /etc/mysql/ssl/server-cert.pem\n"
        "ssl_key = /etc/mysql/ssl/server-key.pem\n"
        "tls_version = TLSv1.2,TLSv1.3\n\n"
        "# Security Hardening\n"
        "local_infile = OFF\n"
        "symbolic_links = OFF\n"
        "general_log = ON\n"
        "general_log_file = /var/lib/mysql/general.log\n"
    )

    add_h2("Lampiran D: Skrip DDL Pembuatan Skema Basis Data schema.sql")
    add_p("Skrip pembuatan tabel users, pasien, rekam_medis, dan audit_log:")
    add_code(
        "CREATE DATABASE IF NOT EXISTS klinik_db;\n"
        "USE klinik_db;\n\n"
        "CREATE TABLE IF NOT EXISTS users (\n"
        "    id INT AUTO_INCREMENT PRIMARY KEY,\n"
        "    username VARCHAR(50) NOT NULL UNIQUE,\n"
        "    password VARCHAR(255) NOT NULL,\n"
        "    role ENUM('admin', 'dokter', 'resepsionis') NOT NULL,\n"
        "    is_active TINYINT(1) DEFAULT 1\n"
        ");\n\n"
        "CREATE TABLE IF NOT EXISTS pasien (\n"
        "    id INT AUTO_INCREMENT PRIMARY KEY,\n"
        "    nama VARCHAR(100) NOT NULL,\n"
        "    nik_encrypted VARBINARY(255) NOT NULL,\n"
        "    tanggal_lahir DATE NOT NULL,\n"
        "    alamat TEXT,\n"
        "    no_telepon VARCHAR(20)\n"
        ");\n\n"
        "CREATE TABLE IF NOT EXISTS rekam_medis (\n"
        "    id INT AUTO_INCREMENT PRIMARY KEY,\n"
        "    pasien_id INT NOT NULL,\n"
        "    dokter_id INT NOT NULL,\n"
        "    diagnosa TEXT NOT NULL,\n"
        "    resep TEXT,\n"
        "    tanggal DATETIME DEFAULT CURRENT_TIMESTAMP,\n"
        "    FOREIGN KEY (pasien_id) REFERENCES pasien(id) ON DELETE CASCADE,\n"
        "    FOREIGN KEY (dokter_id) REFERENCES users(id) ON DELETE CASCADE\n"
        ");\n\n"
        "CREATE TABLE IF NOT EXISTS audit_log (\n"
        "    id INT AUTO_INCREMENT PRIMARY KEY,\n"
        "    user_id INT NULL,\n"
        "    aksi VARCHAR(50) NOT NULL,\n"
        "    tabel_target VARCHAR(50),\n"
        "    query_exec TEXT,\n"
        "    ip_address VARCHAR(45) NOT NULL,\n"
        "    waktu DATETIME DEFAULT CURRENT_TIMESTAMP,\n"
        "    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL\n"
        ");\n"
    )

    # Save to all target paths
    for p in output_paths:
        doc.save(p)
        print(f"Document saved successfully at: {p}")

if __name__ == "__main__":
    # Simpan di folder projek, bukan path absolut milik satu laptop.
    targets = [
        os.path.join(_BASE_DIR, "Laporan_Akhir_Proyek_Keamanan_SI_Kelompok4.docx")
    ]
    generate_report(targets)
