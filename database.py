import sqlite3
from config import DB_NAME

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT,
        saldo INTEGER DEFAULT 0, referral_code TEXT, referred_by INTEGER,
        join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT, nama_apk TEXT, link_referral TEXT,
        bayaran INTEGER, stok INTEGER DEFAULT -1, aktif INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, task_id INTEGER,
        bukti_file_id TEXT, status TEXT DEFAULT 'pending',
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, approved_at TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS withdrawals (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, jumlah INTEGER,
        nomor_dana TEXT, status TEXT DEFAULT 'pending',
        requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, processed_at TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS deposits (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, jumlah INTEGER,
        bukti_file_id TEXT, status TEXT DEFAULT 'pending',
        requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, approved_at TIMESTAMP)''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    r = c.fetchone(); conn.close(); return r

def create_user(user_id, username, full_name, ref_code, referred_by=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id,username,full_name,referral_code,referred_by) VALUES (?,?,?,?,?)",
              (user_id, username, full_name, ref_code, referred_by))
    conn.commit(); conn.close()

def update_saldo(user_id, jumlah):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET saldo=saldo+? WHERE user_id=?", (jumlah, user_id))
    conn.commit(); conn.close()

def get_active_tasks():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE aktif=1")
    r = c.fetchall(); conn.close(); return r

def get_task(task_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
    r = c.fetchone(); conn.close(); return r

def add_task(nama, link, bayaran, stok=-1):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO tasks (nama_apk,link_referral,bayaran,stok) VALUES (?,?,?,?)", (nama,link,bayaran,stok))
    conn.commit(); conn.close()

def deactivate_task(task_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE tasks SET aktif=0 WHERE id=?", (task_id,))
    conn.commit(); conn.close()

def submit_task(user_id, task_id, bukti):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO user_tasks (user_id,task_id,bukti_file_id) VALUES (?,?,?)", (user_id,task_id,bukti))
    r = c.lastrowid; conn.commit(); conn.close(); return r

def user_already_did_task(user_id, task_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id FROM user_tasks WHERE user_id=? AND task_id=? AND status!='rejected'", (user_id,task_id))
    r = c.fetchone(); conn.close(); return r is not None

def get_user_tasks(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT ut.*,t.nama_apk,t.bayaran FROM user_tasks ut JOIN tasks t ON ut.task_id=t.id WHERE ut.user_id=? ORDER BY ut.submitted_at DESC LIMIT 10", (user_id,))
    r = c.fetchall(); conn.close(); return r

def approve_user_task(submit_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE user_tasks SET status='approved',approved_at=CURRENT_TIMESTAMP WHERE id=?", (submit_id,))
    conn.commit(); conn.close()

def reject_user_task(submit_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE user_tasks SET status='rejected' WHERE id=?", (submit_id,))
    conn.commit(); conn.close()

def create_withdrawal(user_id, jumlah, nomor):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO withdrawals (user_id,jumlah,nomor_dana) VALUES (?,?,?)", (user_id,jumlah,nomor))
    r = c.lastrowid; conn.commit(); conn.close(); return r

def approve_withdrawal(wd_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE withdrawals SET status='approved',processed_at=CURRENT_TIMESTAMP WHERE id=?", (wd_id,))
    conn.commit(); conn.close()

def reject_withdrawal(wd_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE withdrawals SET status='rejected',processed_at=CURRENT_TIMESTAMP WHERE id=?", (wd_id,))
    conn.commit(); conn.close()

def create_deposit(user_id, jumlah, bukti):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO deposits (user_id,jumlah,bukti_file_id) VALUES (?,?,?)", (user_id,jumlah,bukti))
    r = c.lastrowid; conn.commit(); conn.close(); return r

def approve_deposit_db(dep_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE deposits SET status='approved',approved_at=CURRENT_TIMESTAMP WHERE id=?", (dep_id,))
    conn.commit(); conn.close()

def get_user_withdrawals(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM withdrawals WHERE user_id=? ORDER BY requested_at DESC LIMIT 10", (user_id,))
    r = c.fetchall(); conn.close(); return r

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    r = c.fetchall(); conn.close(); return r

def get_referral_by_code(code):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE referral_code=?", (code,))
    r = c.fetchone(); conn.close(); return r

def get_total_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    r = c.fetchone()[0]; conn.close(); return r

def get_total_tasks_done():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM user_tasks WHERE status='approved'")
    r = c.fetchone()[0]; conn.close(); return r

def get_user_task_count(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM user_tasks WHERE user_id=? AND status='approved'", (user_id,))
    r = c.fetchone()[0]; conn.close(); return r
