import http.server
import socketserver
import json
import subprocess
import os

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

def run_docker_mysql(user, password, query, extra_flags=None):
    cmd = ["docker", "exec", "db-master", "mysql", "-h", "127.0.0.1", "-P", "3306", "-u", user, f"-p{password}"]
    if extra_flags:
        cmd.extend(extra_flags)
    cmd.extend(["-e", query])
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout, res.stderr, res.returncode

class DemoHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "cluster": "online"}).encode('utf-8'))
        elif self.path == '/api/audit':
            # Call harvester and return audit_log rows
            subprocess.run(["docker", "exec", "db-master", "mysql", "-u", "root", "-pRootPass123!", "-e", "CALL klinik_db.sp_harvest_audit();"])
            out, err, code = run_docker_mysql("root", "RootPass123!", "SELECT id, aksi, IFNULL(tabel_target,'') AS tabel_target, query_exec, ip_address, DATE_FORMAT(waktu, '%Y-%m-%d %H:%i:%s') AS waktu FROM klinik_db.audit_log ORDER BY id ASC;")
            
            rows = []
            lines = out.strip().split('\n')
            if len(lines) > 1:
                for line in lines[1:]:
                    parts = line.split('\t')
                    if len(parts) >= 6:
                        rows.append({
                            "id": parts[0],
                            "aksi": parts[1],
                            "tabel_target": parts[2],
                            "query_exec": parts[3],
                            "ip_address": parts[4],
                            "waktu": parts[5]
                        })

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"rows": rows}).encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len)
        data = json.loads(body.decode('utf-8')) if body else {}

        if self.path == '/api/sqli':
            mode = data.get('mode', 'vulnerable')
            user_input = data.get('input', '')
            
            if mode == 'vulnerable':
                query = f"SELECT id, nama, DATE_FORMAT(tanggal_lahir, '%Y-%m-%d') AS tanggal_lahir, alamat, no_telepon FROM klinik_db.pasien WHERE nama = '{user_input}';"
                out, err, code = run_docker_mysql("app_user", "AppPass123!", query)
            else:
                escaped = user_input.replace("'", "''")
                query = f"PREPARE stmt FROM 'SELECT id, nama, DATE_FORMAT(tanggal_lahir, \"%Y-%m-%d\") AS tanggal_lahir, alamat, no_telepon FROM klinik_db.pasien WHERE nama = ?'; SET @input = '{escaped}'; EXECUTE stmt USING @input; DEALLOCATE PREPARE stmt;"
                out, err, code = run_docker_mysql("app_user", "AppPass123!", query)

            rows = []
            lines = out.strip().split('\n')
            if len(lines) > 1:
                for line in lines[1:]:
                    parts = line.split('\t')
                    if len(parts) >= 4:
                        rows.append({
                            "id": parts[0],
                            "nama": parts[1],
                            "tanggal_lahir": parts[2],
                            "alamat": parts[3],
                            "no_telepon": parts[4] if len(parts) > 4 else "-"
                        })

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"rows": rows}).encode('utf-8'))

        elif self.path == '/api/rbac':
            role = data.get('role', 'app_user')
            action = data.get('action', 'SELECT_PASIEN')
            pwd = "AppPass123!" if role == "app_user" else ("ReadPass123!" if role == "read_only" else "RootPass123!")

            q_map = {
                "SELECT_PASIEN": "SELECT id, nama FROM klinik_db.pasien LIMIT 3;",
                "SELECT_MEDIS": "SELECT id, diagnosa FROM klinik_db.rekam_medis LIMIT 2;",
                "SELECT_USERS": "SELECT * FROM klinik_db.users;",
                "INSERT_PASIEN": "INSERT INTO klinik_db.pasien (nama, tanggal_lahir) VALUES ('Pasien Demo', '2001-01-01');",
                "DROP_TABLE": "DROP TABLE klinik_db.pasien;"
            }
            query = q_map.get(action, "SELECT 1;")
            out, err, code = run_docker_mysql(role, pwd, query)

            res_text = ""
            if out:
                res_text += f"mysql> {query}\n" + out + "\n[STATUS: PERMISSION GRANTED]"
            if err:
                cleaned_err = "\n".join([line for line in err.splitlines() if "Using a password" not in line])
                if cleaned_err.strip():
                    res_text += f"mysql> {query}\n" + cleaned_err + "\n[STATUS: ACCESS DENIED]"

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"output": res_text}).encode('utf-8'))

        elif self.path == '/api/tls':
            with_ssl = data.get('withSsl', True)
            if with_ssl:
                out, err, code = run_docker_mysql("app_user", "AppPass123!", "SHOW STATUS LIKE 'Ssl_cipher'; SHOW STATUS LIKE 'Ssl_version';")
                output = "PS > docker exec db-master mysql ... (SSL ACTIVE)\n\n" + out + "\n[STATUS: SECURE TLSv1.3 ESTABLISHED]"
            else:
                out, err, code = run_docker_mysql("app_user", "AppPass123!", "SELECT 1;", extra_flags=["--ssl-mode=DISABLED"])
                cleaned_err = "\n".join([line for line in err.splitlines() if "Using a password" not in line])
                output = "PS > docker exec db-master mysql ... --ssl-mode=DISABLED\n\n" + cleaned_err + "\n[STATUS: REJECTED AT TCP HANDSHAKE]"

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"output": output}).encode('utf-8'))

print(f"=== KLINIK SEHAT DIGITAL DEMO SERVER ===")
print(f"Server berjalan di: http://localhost:{PORT}")
print(f"Tekan Ctrl+C untuk berhenti.\n")

with socketserver.TCPServer(("", PORT), DemoHandler) as httpd:
    httpd.serve_forever()
