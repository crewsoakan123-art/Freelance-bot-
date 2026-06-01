from pymongo import MongoClient
from config import MONGO_URL

client = MongoClient(MONGO_URL)
db = client["bot_db"]

users = db["users"]
tasks = db["tasks"]
user_tasks = db["user_tasks"]
withdrawals = db["withdrawals"]
deposits = db["deposits"]

def get_user(user_id):
    return users.find_one({"user_id": user_id})

def create_user(user_id, username, full_name, ref_code, referred_by=None):
    if not get_user(user_id):
        users.insert_one({
            "user_id": user_id,
            "username": username,
            "full_name": full_name,
            "saldo": 0,
            "referral_code": ref_code,
            "referred_by": referred_by
        })

def update_saldo(user_id, jumlah):
    users.update_one(
        {"user_id": user_id},
        {"$inc": {"saldo": jumlah}}
    )

def get_saldo(user_id):
    user = get_user(user_id)
    return user["saldo"] if user else 0

def add_task(nama, link, bayaran, stok=-1):
    tasks.insert_one({
        "nama_apk": nama,
        "link_referral": link,
        "bayaran": bayaran,
        "stok": stok,
        "aktif": 1
    })

def get_active_tasks():
    return list(tasks.find({"aktif": 1}))

def deactivate_task(task_id):
    tasks.update_one({"_id": task_id}, {"$set": {"aktif": 0}})

def create_withdrawal(user_id, jumlah, nomor):
    withdrawals.insert_one({
        "user_id": user_id,
        "jumlah": jumlah,
        "nomor_dana": nomor,
        "status": "pending"
    })

def create_deposit(user_id, jumlah, bukti):
    deposits.insert_one({
        "user_id": user_id,
        "jumlah": jumlah,
        "bukti_file_id": bukti,
        "status": "pending"
    })    c = conn.cursor()
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
