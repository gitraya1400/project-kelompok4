#!/usr/bin/env bash
# =============================================================================
# Setup replikasi Master -> Slave  (Skenario 1: Failover & High Availability)
#
# Jalankan dari Git Bash, setelah `docker compose up -d` dan kedua node siap:
#     bash setup-replikasi.sh
#
# Skrip ini mengambil SOURCE_LOG_FILE dan SOURCE_LOG_POS secara OTOMATIS dari
# SHOW MASTER STATUS -- jangan ketik manual, nilainya berubah setiap kali
# master menulis binlog.
# =============================================================================
set -uo pipefail
export MSYS_NO_PATHCONV=1

ROOT_PW="RootPass123!"
CERTS="/etc/mysql/certs"

# Semua koneksi memakai --ssl-mode=REQUIRED karena require_secure_transport=ON.
m() { docker exec -i db-master mysql --no-defaults -uroot -p"$ROOT_PW" \
        --ssl-ca="$CERTS/ca.pem" --ssl-mode=REQUIRED "$@" 2>/dev/null; }
s() { docker exec -i db-slave  mysql --no-defaults -uroot -p"$ROOT_PW" \
        --ssl-ca="$CERTS/ca.pem" --ssl-mode=REQUIRED "$@" 2>/dev/null; }

echo "=============================================================="
echo " SETUP REPLIKASI MASTER -> SLAVE"
echo "=============================================================="

echo "==> Menunggu kedua node siap"
for i in $(seq 1 60); do
  if m -e "SELECT 1" >/dev/null 2>&1 && s -e "SELECT 1" >/dev/null 2>&1; then
    echo "    siap (percobaan ke-$i)"; break
  fi
  [ "$i" = "60" ] && { echo "GAGAL: node tidak siap"; exit 1; }
  sleep 3
done

echo "==> [1/5] Memastikan user replicator ada di master"
m -e "
  CREATE USER IF NOT EXISTS 'replicator'@'%'
    IDENTIFIED WITH mysql_native_password BY 'ReplPass123!' REQUIRE SSL;
  ALTER USER 'replicator'@'%'
    IDENTIFIED WITH mysql_native_password BY 'ReplPass123!' REQUIRE SSL;
  GRANT REPLICATION SLAVE ON *.* TO 'replicator'@'%';
  FLUSH PRIVILEGES;"

echo "==> [2/5] Menyalin skema + data master ke slave"
# --source-data=2 menuliskan koordinat binlog sebagai komentar di dalam dump,
# diambil pada posisi yang konsisten dengan isi dump (lebih aman daripada
# menjalankan SHOW MASTER STATUS terpisah setelah dump selesai).
docker exec db-master mysqldump --no-defaults -uroot -p"$ROOT_PW" \
  --ssl-ca="$CERTS/ca.pem" --ssl-mode=REQUIRED \
  --databases klinik_db --single-transaction --source-data=2 \
  --routines --triggers --events > /tmp/dump-klinik.sql 2>/dev/null

LOG_FILE=$(grep -m1 "CHANGE MASTER TO" /tmp/dump-klinik.sql | sed -n "s/.*MASTER_LOG_FILE='\([^']*\)'.*/\1/p")
LOG_POS=$(grep -m1 "CHANGE MASTER TO" /tmp/dump-klinik.sql | sed -n "s/.*MASTER_LOG_POS=\([0-9]*\).*/\1/p")

if [ -z "$LOG_FILE" ] || [ -z "$LOG_POS" ]; then
  echo "    koordinat tidak ada di dump, ambil dari SHOW MASTER STATUS"
  read -r LOG_FILE LOG_POS < <(m -N -B -e "SHOW MASTER STATUS;" | awk '{print $1, $2}')
fi
echo "    koordinat binlog: $LOG_FILE : $LOG_POS"
[ -z "$LOG_FILE" ] && { echo "GAGAL: koordinat binlog kosong"; exit 1; }

s -e "SET GLOBAL super_read_only=OFF; SET GLOBAL read_only=OFF;"
s < /tmp/dump-klinik.sql
echo "    dump dimuat ke slave"

echo "==> [3/5] Membuat user aplikasi di slave"
# WAJIB: --binlog-do-db=klinik_db membuat CREATE USER/GRANT (yang menyasar
# database `mysql`) TIDAK ter-binlog, jadi user tidak pernah sampai ke slave
# lewat replikasi. Tanpa langkah ini, saat failover semua koneksi ke slave
# gagal dengan ERROR 1045 Access denied.
s < sql/02-users.sql
echo "    user aplikasi dibuat"

echo "==> [4/5] Mengarahkan slave ke master"
s -e "
  STOP REPLICA;
  RESET REPLICA ALL;
  CHANGE REPLICATION SOURCE TO
    SOURCE_HOST='db-master',
    SOURCE_PORT=3306,
    SOURCE_USER='replicator',
    SOURCE_PASSWORD='ReplPass123!',
    SOURCE_LOG_FILE='${LOG_FILE}',
    SOURCE_LOG_POS=${LOG_POS},
    SOURCE_CONNECT_RETRY=5,
    SOURCE_RETRY_COUNT=86400,
    SOURCE_SSL=1,
    SOURCE_SSL_CA='${CERTS}/ca.pem',
    GET_SOURCE_PUBLIC_KEY=1;
  START REPLICA;"

# Kunci slave: read_only menahan user biasa, super_read_only menahan root juga.
# Tanpa super_read_only, root bisa menulis ke slave dan memicu tabrakan
# 'Duplicate entry ... Error_code: 1062' yang menghentikan replikasi PERMANEN.
s -e "SET GLOBAL read_only=ON; SET GLOBAL super_read_only=ON;"

echo "==> [5/5] Menunggu replikasi tersambung"
for i in $(seq 1 30); do
  st=$(s -e "SHOW REPLICA STATUS\G")
  io=$(echo  "$st" | awk -F': ' '/Replica_IO_Running:/{print $2}'  | tr -d ' \r')
  sq=$(echo  "$st" | awk -F': ' '/Replica_SQL_Running:/{print $2}' | tr -d ' \r')
  if [ "$io" = "Yes" ] && [ "$sq" = "Yes" ]; then
    echo
    echo "=============================================================="
    echo " REPLIKASI AKTIF"
    echo "=============================================================="
    echo "$st" | grep -E "Source_Host:|Replica_IO_Running:|Replica_SQL_Running:|Source_SSL_Allowed:|Seconds_Behind_Source:"
    exit 0
  fi
  sleep 2
done

echo "GAGAL: replikasi tidak aktif. Status terakhir:"
s -e "SHOW REPLICA STATUS\G" | grep -E "Replica_IO_Running:|Replica_SQL_Running:|Last_IO_Error:|Last_SQL_Error:"
exit 1
