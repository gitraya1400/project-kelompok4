#!/usr/bin/env bash
# =============================================================================
# Aktifkan penegakan TLS  (Skenario 3: SSL/TLS Connection Enforcement)
#
# Jalankan SETELAH `docker compose up -d` dan kedua node siap:
#     bash aktifkan-tls.sh
#
# KENAPA TIDAK LANGSUNG DI docker-compose.yml:
# Menaruh --require-secure-transport=ON di `command:` membuat inisialisasi
# pertama MACET PERMANEN. Saat container baru dibuat, entrypoint MySQL
# menjalankan temporary server lalu menyambung lewat socket TANPA TLS untuk
# memuat sql/*.sql. Kalau TLS sudah diwajibkan sejak boot, koneksi itu
# ditolak dan proses menggantung -- container terlihat "Up" tetapi mysqld
# tidak pernah ready (sudah diuji: macet >6 menit tanpa progres).
#
# Sertifikat (--ssl-ca/--ssl-cert/--ssl-key) TETAP dipasang sejak boot di
# compose; yang ditunda hanya PENEGAKANNYA.
#
# SET GLOBAL bersifat runtime: setelah `docker compose down`, jalankan lagi.
# =============================================================================
set -uo pipefail
export MSYS_NO_PATHCONV=1

ROOT_PW="RootPass123!"
CERTS="/etc/mysql/certs"

echo "=============================================================="
echo " AKTIFKAN PENEGAKAN TLS"
echo "=============================================================="

for node in db-master db-slave; do
  echo "==> $node"

  if ! docker exec "$node" mysql --no-defaults -uroot -p"$ROOT_PW" \
        -e "SELECT 1" >/dev/null 2>&1; then
    echo "    GAGAL: $node belum siap menerima koneksi."
    echo "    Tunggu inisialisasi selesai, lalu jalankan skrip ini lagi."
    exit 1
  fi

  # Pastikan server benar-benar memuat sertifikat proyek, bukan auto-generate.
  ca=$(docker exec "$node" mysql --no-defaults -uroot -p"$ROOT_PW" -N -B \
         -e "SELECT @@ssl_ca;" 2>/dev/null | tr -d ' \r')
  echo "    ssl_ca = $ca"
  if [ "$ca" != "$CERTS/ca.pem" ]; then
    echo "    PERINGATAN: server tidak memakai sertifikat dari ./ssl."
    echo "    Periksa mount ./ssl dan flag --ssl-ca di docker-compose.yml."
  fi

  # Dua lapis, dan keduanya perlu:
  #
  # (a) SET GLOBAL -> langsung berlaku tanpa restart, tapi HILANG begitu
  #     container di-restart.
  # (b) File config -> PERSISTEN melewati restart.
  #
  # Lapis (b) wajib karena Skenario 1 (failover) menjalankan
  # `docker stop db-master` + `docker start db-master`. Tanpa file config,
  # TLS ikut mati di tengah demo dan Skenario 3 gagal saat diperagakan
  # setelahnya. File ini ditulis SETELAH init selesai, jadi tidak memicu
  # deadlock entrypoint seperti kalau flag ditaruh di `command:`.
  #
  # chmod 644 penting: MySQL mengabaikan file config yang world-writable.
  docker exec "$node" sh -c '
    printf "[mysqld]\nrequire_secure_transport=ON\n" > /etc/mysql/conf.d/zz-tls.cnf
    chmod 644 /etc/mysql/conf.d/zz-tls.cnf' 2>/dev/null

  docker exec "$node" mysql --no-defaults -uroot -p"$ROOT_PW" \
    -e "SET GLOBAL require_secure_transport = ON;" 2>/dev/null

  st=$(docker exec "$node" mysql --no-defaults -uroot -p"$ROOT_PW" \
         --ssl-ca="$CERTS/ca.pem" --ssl-mode=REQUIRED -N -B \
         -e "SELECT @@require_secure_transport;" 2>/dev/null | tr -d ' \r')
  echo "    require_secure_transport = $st (persisten via conf.d/zz-tls.cnf)"
done

# Siapkan user peraga ber-mysql_native_password.
#
# KENAPA PERLU USER KHUSUS: app_user memakai caching_sha2_password. Plugin itu
# menolak koneksi non-SSL lebih dulu dengan ERROR 2061 ("Authentication
# requires secure connection") SEBELUM require_secure_transport sempat
# dievaluasi. Errornya benar, tapi datang dari lapisan autentikasi -- bukan
# dari kebijakan TLS yang ingin dibuktikan proposal. Dengan
# mysql_native_password, penolakan murni berasal dari require_secure_transport
# sehingga yang muncul adalah ERROR 3159 sesuai BAB III.
docker exec db-master mysql --no-defaults -uroot -p"$ROOT_PW" \
  --ssl-ca="$CERTS/ca.pem" --ssl-mode=REQUIRED -e "
    CREATE USER IF NOT EXISTS 'tls_demo'@'%'
      IDENTIFIED WITH mysql_native_password BY 'Demo123!';
    GRANT SELECT ON klinik_db.pasien TO 'tls_demo'@'%';" 2>/dev/null

echo
echo "==> Verifikasi: koneksi TANPA SSL harus ditolak ERROR 3159"
out=$(docker exec db-master mysql --no-defaults -h 127.0.0.1 -P 3306 \
        -u tls_demo -pDemo123! --ssl-mode=DISABLED -e "SELECT 1;" 2>&1 \
      | grep -v "Using a password")
echo "$out" | sed 's/^/    /'
if echo "$out" | grep -q "3159"; then
  echo "    [OK] TLS diwajibkan -- Skenario 3 siap didemokan."
  # Catat ke audit_log SAAT penolakan terjadi. MySQL tidak mencatat ERROR 3159
  # di general_log (ditolak di lapisan transport sebelum autentikasi), jadi
  # sp_harvest_audit() tidak bisa memanennya -- harus dicatat eksplisit.
  docker exec db-master mysql --no-defaults -uroot -p"$ROOT_PW" \
    --ssl-ca="$CERTS/ca.pem" --ssl-mode=REQUIRED \
    -e "CALL klinik_db.sp_log_ssl_rejection('tls_demo','127.0.0.1');" 2>/dev/null \
    && echo "    [OK] Penolakan tercatat di audit_log (Skenario 5)."
else
  echo "    [PERIKSA] Belum muncul ERROR 3159."
fi

echo
echo "==> Verifikasi: koneksi DENGAN sertifikat harus berhasil"
docker exec db-master mysql --no-defaults -h 127.0.0.1 -P 3306 \
  -u app_user -pAppPass123! \
  --ssl-ca="$CERTS/ca.pem" --ssl-mode=VERIFY_CA \
  -e "SELECT 'KONEKSI TLS BERHASIL' AS status; SHOW STATUS LIKE 'Ssl_cipher';" \
  2>&1 | grep -v "Using a password" | sed 's/^/    /'
