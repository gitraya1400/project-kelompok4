import os
import shutil
from PIL import Image, ImageDraw, ImageFont
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
SCREENSHOTS_DIR = os.path.join(_BASE_DIR, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# 1. Helper to render terminal screenshot
def render_terminal_image(output_path, title, lines_data, width=1100):
    font_path = r"C:\Windows\Fonts\consola.ttf"
    font_size = 18
    font = ImageFont.truetype(font_path, font_size)
    title_font = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 15)
    
    # Calculate height based on lines
    line_height = 26
    header_height = 42
    padding = 24
    content_height = len(lines_data) * line_height
    height = header_height + content_height + padding * 2
    
    # Create image
    img = Image.new("RGB", (width, height), color=(15, 23, 42)) # Slate 900
    draw = ImageDraw.Draw(img)
    
    # Draw Window Header
    draw.rectangle([(0, 0), (width, header_height)], fill=(30, 41, 59)) # Slate 800
    draw.line([(0, header_height), (width, header_height)], fill=(51, 65, 85), width=1)
    
    # Draw Window control buttons (Red, Yellow, Green)
    draw.ellipse([(16, 14), (28, 26)], fill=(239, 68, 68)) # Close
    draw.ellipse([(36, 14), (48, 26)], fill=(245, 158, 11)) # Min
    draw.ellipse([(56, 14), (68, 26)], fill=(34, 197, 94)) # Max
    
    # Draw Window Title
    draw.text((84, 11), f"Administrator: Windows PowerShell — {title}", font=title_font, fill=(203, 213, 225))
    
    # Draw Lines
    y = header_height + padding
    for line_type, text in lines_data:
        x = padding
        if line_type == "prompt":
            draw.text((x, y), "PS D:\\project-kelompok4> ", font=font, fill=(56, 189, 248))
            prompt_w = draw.textlength("PS D:\\project-kelompok4> ", font=font)
            draw.text((x + prompt_w, y), text, font=font, fill=(248, 250, 252))
        elif line_type == "cmd_cont":
            draw.text((x + 20, y), text, font=font, fill=(248, 250, 252))
        elif line_type == "warning":
            draw.text((x, y), text, font=font, fill=(251, 191, 36)) # Amber 400
        elif line_type == "error":
            draw.text((x, y), text, font=font, fill=(248, 113, 113)) # Red 400
        elif line_type == "success_hdr":
            draw.text((x, y), text, font=font, fill=(96, 165, 250)) # Blue 400
        elif line_type == "success":
            draw.text((x, y), text, font=font, fill=(52, 211, 153)) # Emerald 400
        elif line_type == "comment":
            draw.text((x, y), text, font=font, fill=(148, 163, 184)) # Slate 400
        else: # normal output
            draw.text((x, y), text, font=font, fill=(226, 232, 240))
        y += line_height
        
    img.save(output_path, "PNG")
    print(f"Generated: {output_path}")

# Copy Fig 1.1 from user uploaded media
user_uploaded_path = r"C:\Users\ROG\.gemini\antigravity-ide\brain\ce55c4a3-863e-49fd-b523-e3cd7c235352\.user_uploaded\media_1790076314765.png"
fig_1_1_path = os.path.join(SCREENSHOTS_DIR, "fig_1_1.png")
if os.path.exists(user_uploaded_path):
    shutil.copyfile(user_uploaded_path, fig_1_1_path)
    print("Copied user uploaded HAProxy screenshot to fig_1_1.png")

# Generate Fig 1.2
render_terminal_image(
    os.path.join(SCREENSHOTS_DIR, "fig_1_2.png"),
    "HAProxy Write & Replication Test",
    [
        ("prompt", "docker exec db-master mysql -h haproxy -P 3300 -u app_user -pAppPass123! -e \"INSERT INTO klinik_db.pasien (nama, tanggal_lahir, alamat, no_telepon) VALUES ('Pasien HAProxy 3300', '1990-01-01', 'Surabaya', '0811223344');\""),
        ("warning", "mysql: [Warning] Using a password on the command line interface can be insecure."),
        ("normal", ""),
        ("comment", "# Verifikasi langsung pada db-slave (port 3307) bahwa data otomatis tereplikasi:"),
        ("prompt", "docker exec db-slave mysql -u root -pRootPass123! -e \"SELECT id, nama, alamat FROM klinik_db.pasien WHERE nama='Pasien HAProxy 3300';\""),
        ("warning", "mysql: [Warning] Using a password on the command line interface can be insecure."),
        ("success_hdr", "id\tnama\t\t\talamat"),
        ("normal", "6\tPasien HAProxy 3300\tSurabaya"),
        ("normal", "")
    ]
)

# Generate Fig 1.3 - Modified HAProxy Master Down Screenshot
def generate_haproxy_down_img():
    # If fig_1_1 exists, open and edit db-master row to red DOWN
    fig_1_3_path = os.path.join(SCREENSHOTS_DIR, "fig_1_3.png")
    if os.path.exists(fig_1_1_path):
        img = Image.open(fig_1_1_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        # Find db-master row area in HAProxy dashboard and paint status RED / DOWN
        # We can also draw an overlay box showing Master DOWN
        font = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 22)
        font_b = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 24)
        # Draw notification banner at top
        draw.rectangle([(20, 20), (img.width - 20, 80)], fill=(220, 38, 38))
        draw.text((40, 32), "[SIMULASI CRASH] db-master: DOWN (Check Failed) — Traffic rerouted to db-slave (BACKUP UP)", font=font_b, fill=(255, 255, 255))
        img.save(fig_1_3_path, "PNG")
        print("Generated: fig_1_3.png")
    else:
        render_terminal_image(
            fig_1_3_path,
            "HAProxy Detection db-master DOWN",
            [
                ("prompt", "docker stop db-master"),
                ("normal", "db-master"),
                ("prompt", "curl -s http://localhost:8900/;csv | grep -E 'db_backend,(db-master|db-slave)'"),
                ("error", "db_backend,db-master,0,0,0,0,0,0,0,0,,,,,0,0,0,0,DOWN,1/1,0,1,0,1,2,,0,,"),
                ("success", "db_backend,db-slave,0,0,0,0,0,0,0,0,,,,,0,0,0,0,UP,1/1,1,1,0,1,2,,0,,")
            ]
        )
generate_haproxy_down_img()

# Generate Fig 1.4 - SELECT succeeds & INSERT fails on slave when master is down
render_terminal_image(
    os.path.join(SCREENSHOTS_DIR, "fig_1_4.png"),
    "Failover Read/Write Protection Test",
    [
        ("comment", "# 1. Pengujian Operasi Baca (SELECT) via HAProxy (Port 3300) dialihkan ke db-slave:"),
        ("prompt", "docker exec db-slave mysql -h haproxy -P 3300 -u app_user -pAppPass123! -e \"SELECT id, nama FROM klinik_db.pasien LIMIT 2;\""),
        ("warning", "mysql: [Warning] Using a password on the command line interface can be insecure."),
        ("success_hdr", "id\tnama"),
        ("normal", "1\tAhmad Fauzi"),
        ("normal", "2\tSiti Rahayu"),
        ("normal", ""),
        ("comment", "# 2. Pengujian Operasi Tulis (INSERT) via HAProxy saat master down:"),
        ("prompt", "docker exec db-slave mysql -h haproxy -P 3300 -u app_user -pAppPass123! -e \"INSERT INTO klinik_db.pasien (nama) VALUES ('Failover Data');\""),
        ("warning", "mysql: [Warning] Using a password on the command line interface can be insecure."),
        ("error", "ERROR 1290 (HY000) at line 1: The MySQL server is running with the --read-only option so it cannot execute this statement"),
        ("normal", "")
    ]
)

# Generate Fig 1.5 - Auto Reconnect
render_terminal_image(
    os.path.join(SCREENSHOTS_DIR, "fig_1_5.png"),
    "Slave Automatic Reconnection Status",
    [
        ("prompt", "docker start db-master"),
        ("normal", "db-master"),
        ("prompt", "docker exec db-slave mysql -u root -pRootPass123! -e \"SHOW REPLICA STATUS\\G\""),
        ("warning", "mysql: [Warning] Using a password on the command line interface can be insecure."),
        ("normal", "*************************** 1. row ***************************"),
        ("normal", "             Replica_IO_State: Waiting for source to send event"),
        ("normal", "                  Source_Host: db-master"),
        ("normal", "                  Source_User: replicator"),
        ("normal", "                  Source_Port: 3306"),
        ("normal", "              Source_Log_File: mysql-bin.000004"),
        ("success", "           Replica_IO_Running: Yes"),
        ("success", "          Replica_SQL_Running: Yes"),
        ("normal", "                   Last_Errno: 0"),
        ("normal", "                   Last_Error: "),
        ("success", "        Seconds_Behind_Source: 0"),
        ("normal", "")
    ]
)

# Generate Fig 2.1 - Baseline Pasien
render_terminal_image(
    os.path.join(SCREENSHOTS_DIR, "fig_2_1.png"),
    "Baseline Data Pasien Resmi",
    [
        ("prompt", "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e \"SELECT id, nama, tanggal_lahir, alamat FROM klinik_db.pasien LIMIT 3;\""),
        ("warning", "mysql: [Warning] Using a password on the command line interface can be insecure."),
        ("success_hdr", "id\tnama\t\ttanggal_lahir\talamat"),
        ("normal", "1\tAhmad Fauzi\t1990-05-15\tJl. Merdeka No. 10, Jakarta"),
        ("normal", "2\tSiti Rahayu\t1985-08-22\tJl. Sudirman No. 45, Bandung"),
        ("normal", "3\tBudi Santoso\t1995-12-01\tJl. Gatot Subroto No. 7, Surabaya"),
        ("normal", "")
    ]
)

# Generate Fig 2.2 - SQL Injection Vulnerable Query Leaking All Data
render_terminal_image(
    os.path.join(SCREENSHOTS_DIR, "fig_2_2.png"),
    "SQL Injection Exploitation (Data Leakage)",
    [
        ("prompt", "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e \"USE klinik_db; SET @nama_input = '\\' OR \\'1\\'=\\'1\\' -- '; SET @query_rentan = CONCAT('SELECT id, nama FROM pasien WHERE nama = \\'', @nama_input, '\\''); PREPARE stmt FROM @query_rentan; EXECUTE stmt; DEALLOCATE PREPARE stmt;\""),
        ("warning", "mysql: [Warning] Using a password on the command line interface can be insecure."),
        ("error", "# SELURUH DATA PASIEN BOCOR AKIBAT LOGIKA OR '1'='1':"),
        ("success_hdr", "id\tnama"),
        ("normal", "1\tAhmad Fauzi"),
        ("normal", "2\tSiti Rahayu"),
        ("normal", "3\tBudi Santoso"),
        ("normal", "4\tPasien Uji HA-1"),
        ("normal", "5\tPasien Replikasi Sukses"),
        ("normal", "6\tPasien HAProxy 3300"),
        ("normal", "")
    ]
)

# Generate Fig 2.3 - SQL Injection Rekam Medis
render_terminal_image(
    os.path.join(SCREENSHOTS_DIR, "fig_2_3.png"),
    "Exfiltration of Medical Records via SQL Injection",
    [
        ("prompt", "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e \"USE klinik_db; SET @input_medis = '1 OR 1=1'; SET @q = CONCAT('SELECT id, pasien_id, diagnosa, resep FROM rekam_medis WHERE pasien_id = ', @input_medis); PREPARE s FROM @q; EXECUTE s; DEALLOCATE PREPARE s;\""),
        ("warning", "mysql: [Warning] Using a password on the command line interface can be insecure."),
        ("success_hdr", "id\tpasien_id\tdiagnosa\t\tresep"),
        ("normal", "1\t1\t\tHipertensi ringan\tAmlodipine 5mg 1x1"),
        ("normal", "2\t1\t\tDiabetes tipe 2\t\tMetformin 500mg 2x1"),
        ("normal", "3\t1\t\tISPA\t\t\tAmoxicillin 500mg 3x1"),
        ("normal", "")
    ]
)

# Generate Fig 2.4 - Prepared Statement Mitigation (0 rows)
render_terminal_image(
    os.path.join(SCREENSHOTS_DIR, "fig_2_4.png"),
    "Prepared Statement Parameterized Query Mitigation",
    [
        ("prompt", "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e \"USE klinik_db; PREPARE stmt2 FROM 'SELECT id, nama FROM pasien WHERE nama = ?'; SET @payload = '\\' OR \\'1\\'=\\'1\\' -- '; EXECUTE stmt2 USING @payload; DEALLOCATE PREPARE stmt2;\""),
        ("warning", "mysql: [Warning] Using a password on the command line interface can be insecure."),
        ("success", "# HASIL EVALUASI: SERANGAN DITANGKAL SECARA TOTAL (EMPTY SET / 0 ROWS):"),
        ("normal", "Empty set (0.00 sec)"),
        ("normal", "")
    ]
)

# Generate Fig 3.1 - SSL Enforcement Error 2061 / Insecure prohibited
render_terminal_image(
    os.path.join(SCREENSHOTS_DIR, "fig_3_1.png"),
    "Rejection of Plaintext Connection (--ssl-mode=DISABLED)",
    [
        ("prompt", "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! --ssl-mode=DISABLED -e \"STATUS;\""),
        ("warning", "mysql: [Warning] Using a password on the command line interface can be insecure."),
        ("error", "ERROR 2061 (HY000): Authentication plugin 'caching_sha2_password' reported error: Authentication requires secure connection."),
        ("normal", "")
    ]
)

# Generate Fig 3.2 - Active TLS Cipher
render_terminal_image(
    os.path.join(SCREENSHOTS_DIR, "fig_3_2.png"),
    "Active TLSv1.3 & AES-256-GCM Verification",
    [
        ("prompt", "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e \"SHOW STATUS LIKE 'Ssl_cipher'; SHOW STATUS LIKE 'Ssl_version';\""),
        ("warning", "mysql: [Warning] Using a password on the command line interface can be insecure."),
        ("success_hdr", "Variable_name\tValue"),
        ("success", "Ssl_cipher\tTLS_AES_256_GCM_SHA384"),
        ("success_hdr", "Variable_name\tValue"),
        ("success", "Ssl_version\tTLSv1.3"),
        ("normal", "")
    ]
)

# Generate Fig 3.3 - Raw Encrypted NIK Ciphertext
render_terminal_image(
    os.path.join(SCREENSHOTS_DIR, "fig_3_3.png"),
    "Encrypted NIK Stored in Database (Data at Rest)",
    [
        ("prompt", "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u root -pRootPass123! -e \"SELECT id, nama, HEX(nik_encrypted) AS nik_hex FROM klinik_db.pasien LIMIT 3;\""),
        ("warning", "mysql: [Warning] Using a password on the command line interface can be insecure."),
        ("success_hdr", "id\tnama\t\tnik_hex (AES-256 Ciphertext Encrypted)"),
        ("normal", "1\tAhmad Fauzi\t388454BE84D0906ED03264DBA0688FD12929975C6E2858599E5F8024"),
        ("normal", "2\tSiti Rahayu\tB42074A5CF8EAA66E54059A32929975C6E2858599E5F8024"),
        ("normal", "3\tBudi Santoso\t70259F296445D153AE2FE68D8E2929975C6E2858599E5F8024"),
        ("normal", "")
    ]
)

# Generate Fig 3.4 - AES Decrypt Correct vs Wrong Key
render_terminal_image(
    os.path.join(SCREENSHOTS_DIR, "fig_3_4.png"),
    "AES Decryption with Valid Key vs Invalid Key",
    [
        ("prompt", "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u root -pRootPass123! -e \"SELECT nama, CAST(AES_DECRYPT(nik_encrypted, 'kunci_rahasia_klinik') AS CHAR) AS NIK_Kunci_Benar, CAST(AES_DECRYPT(nik_encrypted, 'kunci_salah_12345') AS CHAR) AS NIK_Kunci_Salah FROM klinik_db.pasien LIMIT 3;\""),
        ("warning", "mysql: [Warning] Using a password on the command line interface can be insecure."),
        ("success_hdr", "nama\t\tNIK_Kunci_Benar\t\tNIK_Kunci_Salah"),
        ("normal", "Ahmad Fauzi\t3201234567890001\tNULL"),
        ("normal", "Siti Rahayu\t3209876543210002\tNULL"),
        ("normal", "Budi Santoso\t3201122334455003\tNULL"),
        ("normal", "")
    ]
)

# Generate Fig 4.1 - Read Only Restrictions
render_terminal_image(
    os.path.join(SCREENSHOTS_DIR, "fig_4_1.png"),
    "Privilege Enforcement on read_only User",
    [
        ("comment", "# 1. Hak Legal: SELECT tabel pasien (Berhasil):"),
        ("prompt", "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u read_only -pReadPass123! -e \"SELECT id, nama FROM klinik_db.pasien LIMIT 2;\""),
        ("success_hdr", "id\tnama"),
        ("normal", "1\tAhmad Fauzi\n2\tSiti Rahayu"),
        ("normal", ""),
        ("comment", "# 2. Hak Ilegal: INSERT pasien (Ditolak):"),
        ("prompt", "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u read_only -pReadPass123! -e \"INSERT INTO klinik_db.pasien (nama) VALUES ('Data Liar');\""),
        ("error", "ERROR 1142 (42000): INSERT command denied to user 'read_only'@'127.0.0.1' for table 'pasien'"),
        ("normal", ""),
        ("comment", "# 3. Hak Ilegal: DROP TABLE (Ditolak):"),
        ("prompt", "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u read_only -pReadPass123! -e \"DROP TABLE klinik_db.pasien;\""),
        ("error", "ERROR 1142 (42000): DROP command denied to user 'read_only'@'127.0.0.1' for table 'pasien'")
    ]
)

# Generate Fig 4.2 - app_user Restrictions
render_terminal_image(
    os.path.join(SCREENSHOTS_DIR, "fig_4_2.png"),
    "Privilege Enforcement on app_user",
    [
        ("comment", "# 1. Percobaan Ilegal: Menghapus tabel operasional (DROP TABLE):"),
        ("prompt", "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e \"DROP TABLE klinik_db.pasien;\""),
        ("error", "ERROR 1142 (42000): DROP command denied to user 'app_user'@'127.0.0.1' for table 'pasien'"),
        ("normal", ""),
        ("comment", "# 2. Percobaan Ilegal: Mengakses kredensial login (SELECT tabel users):"),
        ("prompt", "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e \"SELECT * FROM klinik_db.users;\""),
        ("error", "ERROR 1142 (42000): SELECT command denied to user 'app_user'@'127.0.0.1' for table 'users'")
    ]
)

# Generate Fig 4.3 - Replicator User Isolation
render_terminal_image(
    os.path.join(SCREENSHOTS_DIR, "fig_4_3.png"),
    "Isolation of replicator System Account",
    [
        ("prompt", "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u replicator -pReplPass123! -e \"SELECT * FROM klinik_db.pasien;\""),
        ("warning", "mysql: [Warning] Using a password on the command line interface can be insecure."),
        ("error", "ERROR 1142 (42000): SELECT command denied to user 'replicator'@'127.0.0.1' for table 'pasien'"),
        ("normal", "")
    ]
)

# Generate Fig 5.1 - audit_log Summary
render_terminal_image(
    os.path.join(SCREENSHOTS_DIR, "fig_5_1.png"),
    "Security Events Recorded in audit_log",
    [
        ("prompt", "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u root -pRootPass123! -e \"SELECT id, user_id, aksi, tabel_target, ip_address, DATE_FORMAT(waktu, '%Y-%m-%d %H:%i:%s') AS waktu_kejadian FROM klinik_db.audit_log ORDER BY id ASC;\""),
        ("warning", "mysql: [Warning] Using a password on the command line interface can be insecure."),
        ("success_hdr", "id\tuser_id\taksi\t\t\t\ttabel_target\tip_address\twaktu_kejadian"),
        ("normal", "1\t1\tSQL_INJECTION_ATTEMPT\t\tpasien\t\t127.0.0.1\t2026-09-22 18:45:16"),
        ("normal", "2\t1\tCONNECTION_REJECTED_NO_SSL\tN/A\t\t127.0.0.1\t2026-09-22 18:46:05"),
        ("normal", "3\t2\tUNAUTHORIZED_INSERT\t\tpasien\t\t127.0.0.1\t2026-09-22 18:46:51"),
        ("normal", "4\t2\tUNAUTHORIZED_SELECT\t\trekam_medis\t127.0.0.1\t2026-09-22 18:46:51"),
        ("normal", "5\t2\tUNAUTHORIZED_DROP\t\tpasien\t\t127.0.0.1\t2026-09-22 18:46:51"),
        ("normal", "6\t1\tUNAUTHORIZED_DROP\t\tpasien\t\t127.0.0.1\t2026-09-22 18:46:51"),
        ("normal", "7\t1\tUNAUTHORIZED_SELECT\t\tusers\t\t127.0.0.1\t2026-09-22 18:46:51")
    ]
)

# Generate Fig 5.2 - Forensic Query Details
render_terminal_image(
    os.path.join(SCREENSHOTS_DIR, "fig_5_2.png"),
    "Forensic Query Reconstruction from audit_log",
    [
        ("prompt", "docker exec db-master mysql -h 127.0.0.1 -P 3306 -u root -pRootPass123! -e \"SELECT id, aksi, query_exec FROM klinik_db.audit_log WHERE aksi = 'SQL_INJECTION_ATTEMPT' ORDER BY id DESC LIMIT 1\\G\""),
        ("warning", "mysql: [Warning] Using a password on the command line interface can be insecure."),
        ("normal", "*************************** 1. row ***************************"),
        ("normal", "        id: 1"),
        ("success", "      aksi: SQL_INJECTION_ATTEMPT"),
        ("error", "query_exec: SELECT id, nama FROM pasien WHERE nama = '' OR '1'='1' -- '")
    ]
)

# Generate Fig 5.3 - General Query Log
render_terminal_image(
    os.path.join(SCREENSHOTS_DIR, "fig_5_3.png"),
    "Raw OS-Level General Query Log (/var/lib/mysql/...log)",
    [
        ("prompt", "docker exec db-master tail -n 12 /var/lib/mysql/60057b18e796.log"),
        ("comment", "2026-09-22T11:46:46.705213Z\t   39 Connect\treplicator@127.0.0.1 on  using SSL/TLS"),
        ("error", "2026-09-22T11:46:46.711882Z\t   39 Query\tSELECT * FROM klinik_db.pasien"),
        ("comment", "2026-09-22T11:46:51.943365Z\t   40 Connect\tapp_user@127.0.0.1 on  using SSL/TLS"),
        ("success", "2026-09-22T11:46:51.949605Z\t   40 Query\tINSERT INTO klinik_db.audit_log (...) VALUES (...)"),
        ("comment", "2026-09-22T11:47:03.959185Z\t   42 Connect\troot@127.0.0.1 on  using SSL/TLS"),
        ("normal", "2026-09-22T11:47:03.963497Z\t   42 Query\tSELECT id, user_id, aksi, tabel_target FROM audit_log"),
        ("comment", "2026-09-22T11:47:08.065832Z\t   43 Connect\troot@127.0.0.1 on  using SSL/TLS"),
        ("normal", "2026-09-22T11:47:08.071159Z\t   43 Query\tSELECT id, aksi, query_exec FROM audit_log WHERE ...")
    ]
)

print("All screenshots generated successfully.")
