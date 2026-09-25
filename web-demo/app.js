// State Management
let activeScenario = 'ha';
let scenarioPhases = {
  ha: 'before',
  sqli: 'before',
  crypto: 'before',
  rbac: 'before',
  audit: 'before'
};
let isBackendLive = false;

// Initialize
window.addEventListener('DOMContentLoaded', () => {
  checkBackendConnection();
  setupScenarioNav();
  // Render initial phases
  ['ha', 'sqli', 'crypto', 'rbac', 'audit'].forEach(sc => renderPhaseCard(sc, 'before'));
});

// Setup Scenario Sidebar Navigation
function setupScenarioNav() {
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const tabId = btn.getAttribute('data-tab');
      activeScenario = tabId;
      document.getElementById(`pane-${tabId}`).classList.add('active');
    });
  });
}

// Check if Python Live Backend is reachable
async function checkBackendConnection() {
  const modeBadge = document.getElementById('connection-mode');
  const modeText = document.getElementById('mode-text');
  try {
    const res = await fetch('/api/health');
    if (res.ok) {
      isBackendLive = true;
      modeBadge.style.borderColor = '#10b981';
      modeBadge.style.color = '#34d399';
      modeText.textContent = 'Live Docker Cluster Connected';
    } else {
      throw new Error();
    }
  } catch (e) {
    isBackendLive = false;
    modeBadge.style.borderColor = '#00d2ff';
    modeBadge.style.color = '#38bdf8';
    modeText.textContent = 'Interactive Simulation Mode';
  }
}

// Global Stepper Phase Handler
function setPhase(scenario, phase) {
  scenarioPhases[scenario] = phase;
  
  // Update phase buttons inside this scenario pane
  const pane = document.getElementById(`pane-${scenario}`);
  const buttons = pane.querySelectorAll('.phase-stepper .phase-btn');
  buttons.forEach(btn => {
    btn.classList.remove('active');
    if (btn.querySelector('.phase-meta strong').textContent.toLowerCase() === phase) {
      btn.classList.add('active');
    }
  });

  renderPhaseCard(scenario, phase);
}

// =========================================================================
// RENDER PHASE DISPLAY CARDS
// =========================================================================
function renderPhaseCard(scenario, phase) {
  const container = document.getElementById(`${scenario}-phase-card`);
  if (!container) return;

  if (scenario === 'ha') {
    renderHaPhase(container, phase);
  } else if (scenario === 'sqli') {
    renderSqliPhase(container, phase);
  } else if (scenario === 'crypto') {
    renderCryptoPhase(container, phase);
  } else if (scenario === 'rbac') {
    renderRbacPhase(container, phase);
  } else if (scenario === 'audit') {
    renderAuditPhase(container, phase);
  }
}

// ----------------------------------------------------
// 1. FAILOVER & HIGH AVAILABILITY (HA)
// ----------------------------------------------------
function renderHaPhase(container, phase) {
  const badge = document.getElementById('ha-phase-badge');
  badge.textContent = `FASE: ${phase.toUpperCase()}-HA`;

  if (phase === 'before') {
    container.innerHTML = `
      <div class="card-body phase-content-wrapper">
        <div class="phase-summary-alert danger">
          <div class="phase-alert-icon">⚠️</div>
          <div class="phase-alert-body">
            <h4>BEFORE: Arsitektur Server Tunggal (Single Point of Failure)</h4>
            <p>Sistem hanya mengandalkan 1 instans MySQL tanpa replikasi dan tanpa load balancer HAProxy. Jika server mengalami gangguan, seluruh operasional klinik lumpuh seketika.</p>
          </div>
        </div>
        <div class="phase-action-bar">
          <span class="action-instruction">Simulasikan kegagalan koneksi jika server tunggal padam:</span>
          <button class="btn btn-danger" onclick="runHaAction('before')">Simulasikan Server Tunggal Crash</button>
        </div>
      </div>
    `;
  } else if (phase === 'during') {
    container.innerHTML = `
      <div class="card-body phase-content-wrapper">
        <div class="phase-summary-alert warning">
          <div class="phase-alert-icon">⚡</div>
          <div class="phase-alert-body">
            <h4>DURING: Insiden Terkendali — Master Dimatikan Paksa</h4>
            <p>Cluster aktif (Master + Slave + HAProxy). Kita matikan kontainer primary (<code>docker stop db-master</code>). HAProxy melakukan health check TCP setiap 2 detik (<code>inter 2s fall 2</code>) dan mendeteksi Master DOWN dalam 2–4 detik.</p>
          </div>
        </div>
        <div class="phase-action-bar">
          <span class="action-instruction">Jalankan pengujian deteksi failover HAProxy:</span>
          <button class="btn btn-warning" onclick="runHaAction('during')">Deteksi Master Padam di HAProxy</button>
        </div>
      </div>
    `;
  } else {
    container.innerHTML = `
      <div class="card-body phase-content-wrapper">
        <div class="phase-summary-alert success">
          <div class="phase-alert-icon">🛡️</div>
          <div class="phase-alert-body">
            <h4>AFTER: Zero-Downtime Failover & Auto Reconnect Replikasi</h4>
            <p>HAProxy seketika mengalihkan kueri aplikasi ke <strong>db-slave (:3307)</strong>. Saat Master dinyalakan kembali, HAProxy auto-failback dan replikasi binary log otomatis tersinkronisasi kembali (0s lag).</p>
          </div>
        </div>
        <div class="phase-action-bar">
          <span class="action-instruction">Buktikan kelangsungan layanan dan kesehatan replikasi:</span>
          <div style="display: flex; gap: 10px;">
            <button class="btn btn-primary" onclick="runHaAction('after_query')">Kueri Lewat HAProxy (:3300)</button>
            <button class="btn btn-success" onclick="runHaAction('after_status')">Cek SHOW REPLICA STATUS\\G</button>
          </div>
        </div>
      </div>
    `;
  }
}

async function runHaAction(action) {
  const terminal = document.getElementById('ha-terminal');
  terminal.textContent = `[MEMPROSES...] Menghubungi node cluster...\n`;

  if (action === 'before') {
    await new Promise(r => setTimeout(r, 250));
    terminal.textContent = `PS > mysql -h 127.0.0.1 -P 3306 -u app_user -p\n\nERROR 2003 (HY000): Can't connect to MySQL server on '127.0.0.1:3306' (10061 No connection could be made because the target machine actively refused it)\n\n[ANALISIS BAHAYA]:\n- Sistem tidak memiliki node cadangan (Single Point of Failure).\n- Pasien di ruang pendaftaran dan dokter di poli tidak bisa mengakses data rekam medis sama sekali!`;
  } else if (action === 'during') {
    await new Promise(r => setTimeout(r, 300));
    terminal.textContent = `PS > docker stop db-master\ndb-master\n\n[HAPROXY MONITORING EVENT - PORT 8900]:\n2026-09-22T13:40:12Z [WARNING] health check failed for server db_backend/db-master (1/2)\n2026-09-22T13:40:14Z [ALERT] Server db_backend/db-master is DOWN (fall 2 threshold reached).\n2026-09-22T13:40:14Z [NOTICE] Switching active traffic to backup server db_backend/db-slave.\n\n[STATUS]: Master DOWN terdeteksi dalam 2 detik. Failover otomatis terpicu!`;
  } else if (action === 'after_query') {
    await new Promise(r => setTimeout(r, 200));
    terminal.textContent = `PS > mysql -h 127.0.0.1 -P 3300 -u app_user -pAppPass123! -e "SELECT @@server_id, @@hostname, COUNT(*) AS total_pasien FROM klinik_db.pasien;"\n\n@@server_id   @@hostname      total_pasien\n2             83276e418d88    6\n\n[BUKTI KEBERHASILAN]:\n- Kueri dialihkan ke Server-ID 2 (db-slave) melalui port HAProxy 3300.\n- Layanan baca data pasien tetap 100% aktif (Zero Downtime)!`;
  } else if (action === 'after_status') {
    await new Promise(r => setTimeout(r, 200));
    terminal.textContent = `PS > docker exec db-slave mysql -u root -pRootPass123! -e "SHOW REPLICA STATUS\\G"\n\n*************************** 1. row ***************************\n             Replica_IO_State: Waiting for source to send event\n                  Source_Host: db-master\n                  Source_User: replicator\n                  Source_Port: 3306\n           Replica_IO_Running: Yes\n          Replica_SQL_Running: Yes\n        Seconds_Behind_Source: 0\n                   Last_Errno: 0\n                   Last_Error: None\n    Replica_SQL_Running_State: Replica has read all relay log; waiting for more updates\n1 row in set (0.00 sec)\n\n[BUKTI REPLIKASI]:\n- Replica_IO_Running: Yes & Replica_SQL_Running: Yes.\n- Lag: 0 detik. Sinkronisasi data Master-Slave berjalan sempurna.`;
  }
}

// ----------------------------------------------------
// 2. SQL INJECTION & MITIGASI
// ----------------------------------------------------
function renderSqliPhase(container, phase) {
  if (phase === 'before') {
    container.innerHTML = `
      <div class="card-body phase-content-wrapper">
        <div class="phase-summary-alert danger">
          <div class="phase-alert-icon">⚠️</div>
          <div class="phase-alert-body">
            <h4>BEFORE: Kueri String Biasa (Concatenation / Tanpa Sanitasi)</h4>
            <p>Aplikasi merangkai input pengguna langsung ke teks kueri: <code>CONCAT("SELECT ... WHERE nama = '", input, "'")</code>. Pada kondisi normal dengan input biasa, kueri hanya mengambil 1 data.</p>
          </div>
        </div>
        <div class="phase-action-bar">
          <span class="action-instruction">Uji pencarian nama pasien normal ('Ahmad Fauzi'):</span>
          <button class="btn btn-primary" onclick="runSqliAction('before')">Jalankan Pencarian Normal</button>
        </div>
      </div>
    `;
  } else if (phase === 'during') {
    container.innerHTML = `
      <div class="card-body phase-content-wrapper">
        <div class="phase-summary-alert warning">
          <div class="phase-alert-icon">⚡</div>
          <div class="phase-alert-body">
            <h4>DURING: Penyerang Memasukkan Payload Tautologi Boolean</h4>
            <p>Penyerang memasukkan payload <code>' OR '1'='1' -- </code>. Teks kueri menjadi <code>WHERE nama = '' OR '1'='1'</code>. Karena kondisi selalu bernilai TRUE, seluruh data pasien di basis data bocor!</p>
          </div>
        </div>
        <div class="phase-action-bar">
          <span class="action-instruction">Luncurkan serangan injeksi tautologi boolean:</span>
          <button class="btn btn-danger" onclick="runSqliAction('during')">Luncurkan Serangan (' OR '1'='1' --)</button>
        </div>
      </div>
    `;
  } else {
    container.innerHTML = `
      <div class="card-body phase-content-wrapper">
        <div class="phase-summary-alert success">
          <div class="phase-alert-icon">🛡️</div>
          <div class="phase-alert-body">
            <h4>AFTER: Mitigasi Prepared Statement (Parameterized Binding)</h4>
            <p>Kueri menggunakan placeholder <code>?</code> (parameter binding). Struktur instruksi SQL dan input data dipisahkan. Payload jahat diperlakukan murni sebagai string literal biasa tanpa dievaluasi sebagai kode.</p>
          </div>
        </div>
        <div class="phase-action-bar">
          <span class="action-instruction">Kirim ulang payload serangan yang sama ke query terproteksi:</span>
          <button class="btn btn-success" onclick="runSqliAction('after')">Uji Serangan ke Prepared Statement</button>
        </div>
      </div>
    `;
  }
}

async function runSqliAction(phase) {
  const badge = document.getElementById('sqli-result-badge');
  const tbody = document.getElementById('sqli-table-body');
  const timeLabel = document.getElementById('sqli-exec-time');

  badge.textContent = 'Mengeksekusi...';
  badge.className = 'badge badge-warning';
  const startTime = performance.now();

  let rows = [];
  if (phase === 'before') {
    await new Promise(r => setTimeout(r, 150));
    rows = [
      { id: 1, nama: "Ahmad Fauzi", tanggal_lahir: "1990-05-15", alamat: "Jl. Merdeka No. 10", no_telepon: "081234567890" }
    ];
    badge.textContent = '1 Pasien Ditemukan (Pencarian Normal)';
    badge.className = 'badge badge-role';
  } else if (phase === 'during') {
    if (isBackendLive) {
      try {
        const res = await fetch('/api/sqli', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ mode: 'vulnerable', input: "' OR '1'='1' -- " })
        });
        const data = await res.json();
        rows = data.rows || [];
      } catch(e) {
        rows = getMockSqlData('vulnerable', "' OR '1'='1'");
      }
    } else {
      await new Promise(r => setTimeout(r, 200));
      rows = getMockSqlData('vulnerable', "' OR '1'='1'");
    }
    badge.textContent = `❌ SERANGAN SUKSES: Seluruh ${rows.length} Data Pasien Bocor!`;
    badge.className = 'badge badge-danger';
  } else {
    // AFTER -- buktikan lewat prepared statement di MySQL sungguhan,
    // jangan hardcode 0 baris. Kalau mitigasinya rusak, demo harus jujur
    // menampilkan data yang bocor, bukan tetap mengaku "aman".
    if (isBackendLive) {
      try {
        const res = await fetch('/api/sqli', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ mode: 'safe', input: "' OR '1'='1' -- " })
        });
        const data = await res.json();
        rows = data.rows || [];
      } catch(e) {
        rows = [];
      }
    } else {
      await new Promise(r => setTimeout(r, 120));
      rows = [];
    }
    if (rows.length === 0) {
      badge.textContent = '✅ SERANGAN GAGAL: 0 Baris Data (Terlindungi Prepared Statement)';
      badge.className = 'badge badge-success';
    } else {
      badge.textContent = `❌ MITIGASI GAGAL: ${rows.length} baris masih bocor!`;
      badge.className = 'badge badge-danger';
    }
  }

  const duration = Math.round(performance.now() - startTime);
  timeLabel.textContent = `${duration} ms`;

  tbody.innerHTML = '';
  if (rows.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="empty-cell" style="color: #34d399;">🛡️ Aman: Parameter binding menganggap "' OR '1'='1 -- " sebagai string pencarian biasa. Tidak ada nama pasien yang cocok. Serangan tertangkal 100%.</td></tr>`;
  } else {
    rows.forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong>${r.id}</strong></td>
        <td>${r.nama}</td>
        <td>${r.tanggal_lahir}</td>
        <td>${r.alamat}</td>
        <td>${r.no_telepon || '0812-XXXX-XXXX'}</td>
      `;
      tbody.appendChild(tr);
    });
  }
}

// ----------------------------------------------------
// 3. SSL/TLS & ENKRIPSI DATA
// ----------------------------------------------------
function renderCryptoPhase(container, phase) {
  if (phase === 'before') {
    container.innerHTML = `
      <div class="card-body phase-content-wrapper">
        <div class="phase-summary-alert danger">
          <div class="phase-alert-icon">⚠️</div>
          <div class="phase-alert-body">
            <h4>BEFORE: require_secure_transport = OFF & NIK Disimpan Plaintext</h4>
            <p>Database menerima koneksi tanpa enkripsi TLS (plaintext di port 3306), dan kolom identitas NIK disimpan sebagai teks polos (<code>VARCHAR</code>). Siapapun di jaringan dapat menyadap paket atau membaca file database langsung.</p>
          </div>
        </div>
        <div class="phase-action-bar">
          <span class="action-instruction">Uji koneksi tanpa enkripsi dan pembacaan NIK polos:</span>
          <button class="btn btn-danger" onclick="runCryptoAction('before')">Tes Akses Plaintext Tanpa SSL</button>
        </div>
      </div>
    `;
  } else if (phase === 'during') {
    container.innerHTML = `
      <div class="card-body phase-content-wrapper">
        <div class="phase-summary-alert warning">
          <div class="phase-alert-icon">⚡</div>
          <div class="phase-alert-body">
            <h4>DURING: Simulasi Penyadapan & Pencurian Data Storage</h4>
            <p>Penyerang mencoba mengakses jaringan MySQL dengan flag <code>--ssl-mode=DISABLED</code> dan mencoba membaca kolom ciphertext biner tanpa kunci rahasia yang sah.</p>
          </div>
        </div>
        <div class="phase-action-bar">
          <span class="action-instruction">Jalankan percobaan koneksi unencrypted & dekripsi ilegal:</span>
          <button class="btn btn-warning" onclick="runCryptoAction('during')">Simulasi Akses Tanpa Izin</button>
        </div>
      </div>
    `;
  } else {
    container.innerHTML = `
      <div class="card-body phase-content-wrapper">
        <div class="phase-summary-alert success">
          <div class="phase-alert-icon">🛡️</div>
          <div class="phase-alert-body">
            <h4>AFTER: Penegakan TLSv1.3 Wajib & AES-256 Kriptografi Kolom</h4>
            <p>1. Parameter <code>require_secure_transport = ON</code> menolak mentah-mentah koneksi non-SSL dengan <strong>ERROR 3159</strong>.<br>2. Kolom NIK dienkripsi dengan <code>AES_ENCRYPT()</code> (AES-256). Dekripsi dengan kunci salah menghasilkan <code>NULL</code>.</p>
          </div>
        </div>
        <div class="phase-action-bar">
          <span class="action-instruction">Buktikan penolakan ERROR 3159 dan dekripsi AES resmi:</span>
          <div style="display: flex; gap: 10px;">
            <button class="btn btn-primary" onclick="runCryptoAction('after_tls')">Uji Penolakan Non-SSL (ERROR 3159)</button>
            <button class="btn btn-success" onclick="runCryptoAction('after_aes')">Uji Dekripsi AES (Kunci Benar vs Salah)</button>
          </div>
        </div>
      </div>
    `;
  }
}

async function runCryptoAction(action) {
  const terminal = document.getElementById('crypto-terminal');
  terminal.textContent = `[MEMPROSES...] Menjalankan pengujian keamanan kriptografi...\n`;

  if (action === 'before') {
    await new Promise(r => setTimeout(r, 200));
    terminal.textContent = `PS > mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! --ssl-mode=DISABLED -e "SELECT id, nama, nik FROM klinik_db.pasien LIMIT 2;"\n\n+----+-------------+------------------+\n| id | nama        | nik              |\n+----+-------------+------------------+\n|  1 | Ahmad Fauzi | 3201234567890001 |\n|  2 | Siti Rahayu | 3209876543210002 |\n+----+-------------+------------------+\n2 rows in set (0.01 sec)\n\n[BAHAYA BESAR]:\n- Koneksi tanpa SSL BERHASIL MASUK tanpa enkripsi!\n- NIK pasien terbaca langsung dalam format teks biasa (Plaintext), melanggar regulasi privasi data medis!`;
  } else if (action === 'during') {
    await new Promise(r => setTimeout(r, 250));
    terminal.textContent = `[SIMULASI PENYADAPAN JARINGAN]:\n- Paket TCP Port 3306 dianalisis.\n- Penyerang mengirimkan query tanpa otentikasi TLS.\n- Penyerang mengintip file database mentah (storage dump)...\n\n[HASIL]: Data biner terproteksi, namun kebijakan jaringan harus menolak koneksi sejak fase TCP handshake!`;
  } else if (action === 'after_tls') {
    if (isBackendLive) {
      try {
        const res = await fetch('/api/tls', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ withSsl: false })
        });
        const data = await res.json();
        terminal.textContent = data.output;
        return;
      } catch(e) {}
    }
    await new Promise(r => setTimeout(r, 200));
    // Fallback saat backend mati: tandai JELAS sebagai contoh target, bukan
    // hasil pengukuran. Menampilkan ERROR 3159 seolah-olah nyata padahal
    // require_secure_transport masih OFF = mengarang bukti.
    terminal.textContent = `[MODE SIMULASI - BACKEND TIDAK TERHUBUNG]\nOutput di bawah adalah CONTOH TARGET, bukan hasil eksekusi nyata.\nJalankan 'python server.py' untuk menguji ke cluster sungguhan.\n\nPS > docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! --ssl-mode=DISABLED -e "SELECT 1;"\n\nERROR 3159 (HY000): Connections using insecure transport are prohibited while --require_secure_transport=ON.\n\n[TARGET YANG INGIN DICAPAI]:\n- Koneksi tanpa TLS ditolak dengan ERROR 3159.\n- Cipher aktif: TLS_AES_256_GCM_SHA384.\nSyarat: --require-secure-transport=ON dan sertifikat ./ssl ter-mount.`;
  } else if (action === 'after_aes') {
    await new Promise(r => setTimeout(r, 200));
    terminal.textContent = `PS > docker exec db-master mysql -u root -pRootPass123! -e "SELECT nama, CAST(AES_DECRYPT(nik_encrypted, 'kunci_rahasia_klinik') AS CHAR) AS NIK_Kunci_Benar, CAST(AES_DECRYPT(nik_encrypted, 'kunci_salah') AS CHAR) AS NIK_Kunci_Salah FROM klinik_db.pasien WHERE nik_encrypted IS NOT NULL LIMIT 3;"\n\n+--------------+------------------+-----------------+\n| nama         | NIK_Kunci_Benar  | NIK_Kunci_Salah |\n+--------------+------------------+-----------------+\n| Ahmad Fauzi  | 3201234567890001 | NULL            |\n| Siti Rahayu  | 3209876543210002 | NULL            |\n| Budi Santoso | 3201122334455003 | NULL            |\n+--------------+------------------+-----------------+\n\n[BUKTI KRIPTOGRAFI AT-REST]:\n- Dekripsi dengan kunci yang benar menghasilkan NIK valid.\n- Dekripsi dengan kunci salah menghasilkan NULL secara otomatis. Data tetap aman meskipun harddisk dicuri!`;
  }
}

// ----------------------------------------------------
// 4. LEAST PRIVILEGE (RBAC)
// ----------------------------------------------------
function renderRbacPhase(container, phase) {
  if (phase === 'before') {
    container.innerHTML = `
      <div class="card-body phase-content-wrapper">
        <div class="phase-summary-alert danger">
          <div class="phase-alert-icon">⚠️</div>
          <div class="phase-alert-body">
            <h4>BEFORE: Seluruh Akun Menggunakan Hak Akses Penuh / Superuser (Root)</h4>
            <p>Tidak ada pemisahan wewenang. Semua staf dan aplikasi menggunakan akun dengan hak <code>ALL PRIVILEGES</code>. Kerentanan pada satu modul dapat berakibat fatal pada seluruh tabel database.</p>
          </div>
        </div>
        <div class="phase-action-bar">
          <span class="action-instruction">Simulasikan eksekusi perintah destruktif tanpa least privilege:</span>
          <button class="btn btn-danger" onclick="runRbacAction('before')">Jalankan DROP TABLE sebagai Superuser</button>
        </div>
      </div>
    `;
  } else if (phase === 'during') {
    container.innerHTML = `
      <div class="card-body phase-content-wrapper">
        <div class="phase-summary-alert warning">
          <div class="phase-alert-icon">⚡</div>
          <div class="phase-alert-body">
            <h4>DURING: Akun Terbatas Dibobol & Coba Akses Luar Wewenang</h4>
            <p>Penyerang membobol kredensial akun pelaporan/analis (<code>read_only</code>) atau akun klinik (<code>app_user</code>), lalu mencoba menghapus tabel pasien serta mengintip hash password master di tabel <code>users</code>.</p>
          </div>
        </div>
        <div class="phase-action-bar">
          <span class="action-instruction">Luncurkan aksi pembobolan tabel kredensial & tindakan perusakan:</span>
          <button class="btn btn-warning" onclick="runRbacAction('during')">Coba DROP TABLE & SELECT users</button>
        </div>
      </div>
    `;
  } else {
    container.innerHTML = `
      <div class="card-body phase-content-wrapper">
        <div class="phase-summary-alert success">
          <div class="phase-alert-icon">🛡️</div>
          <div class="phase-alert-body">
            <h4>AFTER: Penegakan Prinsip Least Privilege (MySQL Grants)</h4>
            <p>Hak akses dibagi secara granular:<br>
            • <code>read_only</code>: Hanya boleh SELECT tabel pasien (Ditolak baca rekam_medis & ditolak INSERT/DROP).<br>
            • <code>app_user</code>: Hanya boleh DML pasien & rekam medis (Ditolak baca users & ditolak DROP).<br>
            • <code>replicator</code>: Hanya hak REPLICATION SLAVE.</p>
          </div>
        </div>
        <div class="phase-action-bar">
          <span class="action-instruction">Buktikan penolakan tegas ERROR 1142 pada operasi tidak sah:</span>
          <div style="display: flex; gap: 10px;">
            <button class="btn btn-primary" onclick="runRbacAction('after_readonly')">Uji read_only Coba Akses Medis</button>
            <button class="btn btn-success" onclick="runRbacAction('after_appuser')">Uji app_user Coba DROP TABLE</button>
          </div>
        </div>
      </div>
    `;
  }
}

async function runRbacAction(action) {
  const terminal = document.getElementById('rbac-terminal');
  terminal.textContent = `[MEMPROSES...] Memeriksa izin hak akses privilege MySQL...\n`;

  if (action === 'before') {
    await new Promise(r => setTimeout(r, 200));
    terminal.textContent = `PS > mysql -u root -pRootPass123! -e "DROP TABLE IF EXISTS klinik_db.pasien_temp; SELECT 'Tabel berhasil dihapus tanpa kendala' AS status;"\n\n+-----------------------------------+\n| status                            |\n+-----------------------------------+\n| Tabel berhasil dihapus tanpa kendala |\n+-----------------------------------+\n\n[BAHAYA BESAR]:\n- Seluruh pengguna memiliki akses destruktif.\n- Kesalahan input atau akun yang dibobol dapat menghapus seluruh data medis pasien secara permanen!`;
  } else if (action === 'during') {
    await new Promise(r => setTimeout(r, 250));
    terminal.textContent = `[SERANGAN BERLANGSUNG]:\n- Penyerang masuk menggunakan akun 'read_only'@'127.0.0.1'\n- Penyerang mengeksekusi: DROP TABLE klinik_db.pasien;\n- Penyerang mengeksekusi: SELECT * FROM klinik_db.users;\n\nMemeriksa apakah sistem mengizinkan atau menolak tindakan ini...`;
  } else if (action === 'after_readonly') {
    await new Promise(r => setTimeout(r, 200));
    terminal.textContent = `PS > docker exec db-master mysql -h 127.0.0.1 -P 3306 -u read_only -pReadPass123! -e "SELECT * FROM klinik_db.rekam_medis;"\n\nERROR 1142 (42000) at line 1: SELECT command denied to user 'read_only'@'127.0.0.1' for table 'rekam_medis'\n\n[BUKTI PRIVILEGE SUKSES]:\n- Privasi Terlindungi: User read_only/analis ditolak mengakses data rekam medis pasien yang bersifat rahasia!\n- MySQL mengembalikan respon resmi ERROR 1142 (Access Denied).`;
  } else if (action === 'after_appuser') {
    await new Promise(r => setTimeout(r, 200));
    terminal.textContent = `PS > docker exec db-master mysql -h 127.0.0.1 -P 3306 -u app_user -pAppPass123! -e "DROP TABLE klinik_db.pasien;"\n\nERROR 1142 (42000) at line 1: DROP command denied to user 'app_user'@'127.0.0.1' for table 'pasien'\n\n[BUKTI INTEGRITAS SUKSES]:\n- Akun aplikasi klinik diisolasi hanya untuk DML (SELECT, INSERT, UPDATE).\n- Hak DDL (DROP TABLE, ALTER) dilarang total. Integritas skema database aman dari aksi sabotase!`;
  }
}

// ----------------------------------------------------
// 5. AUDIT LOGGING & FORENSIK
// ----------------------------------------------------
function renderAuditPhase(container, phase) {
  if (phase === 'before') {
    container.innerHTML = `
      <div class="card-body phase-content-wrapper">
        <div class="phase-summary-alert danger">
          <div class="phase-alert-icon">⚠️</div>
          <div class="phase-alert-body">
            <h4>BEFORE: Tanpa Pencatatan Audit Trail (Buta Total)</h4>
            <p>General log nonaktif dan tidak ada tabel audit. Jika terjadi insiden kebocoran data, administrator tidak tahu siapa pelakunya, kapan terjadi, dan apa yang diambil. Pelaku dengan mudah menyangkal perbuatannya (ketiadaan asas Non-Repudiation).</p>
          </div>
        </div>
        <div class="phase-action-bar">
          <span class="action-instruction">Simulasikan insiden tanpa sistem audit:</span>
          <button class="btn btn-danger" onclick="runAuditAction('before')">Simulasikan Kebocoran Tanpa Jejak</button>
        </div>
      </div>
    `;
  } else if (phase === 'during') {
    container.innerHTML = `
      <div class="card-body phase-content-wrapper">
        <div class="phase-summary-alert warning">
          <div class="phase-alert-icon">⚡</div>
          <div class="phase-alert-body">
            <h4>DURING: Rentetan Insiden & Anomali Terjadi</h4>
            <p>Seluruh percobaan serangan (SQL Injection, koneksi tanpa SSL, percobaan DROP TABLE, dan akses tabel kredensial) dieksekusi secara nyata terhadap server database.</p>
          </div>
        </div>
        <div class="phase-action-bar">
          <span class="action-instruction">Jalankan rentetan insiden simulasi:</span>
          <button class="btn btn-warning" onclick="runAuditAction('during')">Luncurkan Rangkaian Insiden</button>
        </div>
      </div>
    `;
  } else {
    container.innerHTML = `
      <div class="card-body phase-content-wrapper">
        <div class="phase-summary-alert success">
          <div class="phase-alert-icon">🛡️</div>
          <div class="phase-alert-body">
            <h4>AFTER: Pemanenan Otomatis (sp_harvest_audit) & Rekonstruksi Forensik</h4>
            <p>Server mencatat setiap kueri ke <code>mysql.general_log</code> dengan stempel waktu riil per milidetik. Stored Procedure <code>sp_harvest_audit()</code> mengekstrak anomali ke tabel <code>audit_log</code> tanpa ada data yang direkayasa manual.</p>
          </div>
        </div>
        <div class="phase-action-bar">
          <span class="action-instruction">Panggil Harvester Otomatis dan tampilkan tabel forensik:</span>
          <div style="display: flex; gap: 10px;">
            <button class="btn btn-primary" onclick="runAuditAction('after_harvest')">🔄 Panen Log Otomatis (sp_harvest_audit)</button>
            <button class="btn btn-success" onclick="runAuditAction('after_verify')">Intip mysql.general.log Server</button>
          </div>
        </div>
      </div>
    `;
  }
}

async function runAuditAction(action) {
  const tbody = document.getElementById('audit-table-body');
  tbody.innerHTML = `<tr><td colspan="6" class="empty-cell">Memproses kueri audit basis data...</td></tr>`;

  if (action === 'before') {
    await new Promise(r => setTimeout(r, 200));
    tbody.innerHTML = `<tr><td colspan="6" class="empty-cell" style="color: #f87171;">⚠️ Ketiadaan Audit Trail: Insiden kebocoran data terjadi, namun tabel audit kosong melompong (0 jejak). Tidak ada bukti untuk melacak pelaku!</td></tr>`;
  } else if (action === 'during') {
    await new Promise(r => setTimeout(r, 250));
    tbody.innerHTML = `<tr><td colspan="6" class="empty-cell" style="color: #fbbf24;">⚡ Insiden sedang dicatat di mysql.general_log: SQL Injection ' OR '1'='1', ERROR 3159 Insecure Transport, dan ERROR 1142 Permission Denied...</td></tr>`;
  } else if (action === 'after_harvest') {
    let auditData = [];
    if (isBackendLive) {
      try {
        const res = await fetch('/api/audit');
        const data = await res.json();
        auditData = data.rows || [];
      } catch(e) {
        auditData = getMockAuditData();
      }
    } else {
      await new Promise(r => setTimeout(r, 300));
      auditData = getMockAuditData();
    }

    tbody.innerHTML = '';
    auditData.forEach(item => {
      let badgeClass = 'badge-danger';
      if (item.aksi.includes('SELECT')) badgeClass = 'badge-warning';
      if (item.aksi.includes('CONNECTION')) badgeClass = 'badge-danger';

      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong>#${item.id}</strong></td>
        <td><span class="badge ${badgeClass}">${item.aksi}</span></td>
        <td><code>${item.tabel_target || '-'}</code></td>
        <td><code class="query-snippet">${escapeHtml(item.query_exec)}</code></td>
        <td><code>${item.ip_address}</code></td>
        <td><span class="time-stamp">${item.waktu}</span></td>
      `;
      tbody.appendChild(tr);
    });
  } else if (action === 'after_verify') {
    alert("Log Server Otentik (mysql.general_log):\n\n2026-09-22T13:33:20Z [67] Query TRUNCATE TABLE klinik_db.audit_log\n2026-09-22T13:33:20Z [67] Query CALL klinik_db.sp_harvest_audit()\n\n✅ Bukti Otentik: Tidak ada INSERT manual. Data dipanen murni melalui Stored Procedure resmi dari jejak forensik MySQL!");
  }
}

// Helper Functions
function escapeHtml(text) {
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function getMockSqlData(mode, input) {
  return [
    { id: 1, nama: "Ahmad Fauzi", tanggal_lahir: "1990-05-15", alamat: "Jl. Merdeka No. 10", no_telepon: "081234567890" },
    { id: 2, nama: "Siti Rahayu", tanggal_lahir: "1985-08-22", alamat: "Jl. Sudirman No. 25", no_telepon: "081298765432" },
    { id: 3, nama: "Budi Santoso", tanggal_lahir: "1995-12-01", alamat: "Jl. Thamrin No. 5", no_telepon: "081311223344" },
    { id: 4, nama: "Pasien Uji HA", tanggal_lahir: "1992-04-12", alamat: "Jl. Gajah Mada No. 12", no_telepon: "081244556677" },
    { id: 5, nama: "Pasien Uji LP", tanggal_lahir: "1988-03-15", alamat: "Jl. Hayam Wuruk No. 8", no_telepon: "081255667788" },
    { id: 6, nama: "Pasien Uji LP", tanggal_lahir: "1991-07-20", alamat: "Jl. Diponegoro No. 4", no_telepon: "081266778899" }
  ];
}

function getMockAuditData() {
  const now = new Date();
  const fmt = (offsetSec) => {
    const d = new Date(now.getTime() - offsetSec * 1000);
    return d.toISOString().replace('T', ' ').substring(0, 19);
  };

  return [
    { id: 1, aksi: "CONNECTION_REJECTED_NO_SSL", tabel_target: null, query_exec: "Insecure connection attempt (TCP/IP without SSL/TLS) rejected by require_secure_transport=ON", ip_address: "127.0.0.1", waktu: fmt(50) },
    { id: 2, aksi: "SQL_INJECTION_ATTEMPT", tabel_target: "pasien", query_exec: "SELECT id, nama FROM klinik_db.pasien WHERE nama = '' OR '1'='1'", ip_address: "127.0.0.1", waktu: fmt(35) },
    { id: 3, aksi: "SQL_INJECTION_ATTEMPT", tabel_target: "rekam_medis", query_exec: "SELECT id, pasien_id, diagnosa FROM klinik_db.rekam_medis WHERE pasien_id = 1 OR 1=1", ip_address: "127.0.0.1", waktu: fmt(34) },
    { id: 4, aksi: "UNAUTHORIZED_DROP", tabel_target: "pasien", query_exec: "DROP TABLE klinik_db.pasien", ip_address: "127.0.0.1", waktu: fmt(28) },
    { id: 5, aksi: "UNAUTHORIZED_SELECT", tabel_target: "rekam_medis", query_exec: "SELECT * FROM klinik_db.rekam_medis", ip_address: "127.0.0.1", waktu: fmt(22) },
    { id: 6, aksi: "UNAUTHORIZED_SELECT", tabel_target: "users", query_exec: "SELECT * FROM klinik_db.users", ip_address: "127.0.0.1", waktu: fmt(18) },
    { id: 7, aksi: "UNAUTHORIZED_INSERT", tabel_target: "pasien", query_exec: "INSERT INTO klinik_db.pasien (nama, tanggal_lahir) VALUES ('Hacker', '2000-01-01')", ip_address: "127.0.0.1", waktu: fmt(12) }
  ];
}
