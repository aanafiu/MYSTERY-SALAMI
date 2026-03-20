from flask import Flask, render_template, request, jsonify
import mysql.connector
import random
import os

app = Flask(__name__)

# ── Box Gifts ─────────────────────────────────────
_amounts = [
    2, 2, 2, 2, 2,
    7, 7, 8, 5,
    15, 20, 25, 26, 13,
    22, 20, 23, 29,
    30, 35, 5,
    10, 10,
    21, 20,
    50
]
random.seed(1447)
random.shuffle(_amounts)
BOX_GIFTS = {i + 1: _amounts[i] for i in range(26)}

# ── MySQL Config (set these as environment variables on Render) ──
DB_CONFIG = {
    'host':     os.environ.get('MYSQL_HOST',     'localhost'),
    'user':     os.environ.get('MYSQL_USER',     'root'),
    'password': os.environ.get('MYSQL_PASSWORD', ''),
    'database': os.environ.get('MYSQL_DATABASE', 'mystery_salami'),
    'port':     int(os.environ.get('MYSQL_PORT', 3306)),
}

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

def get_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn


def init_db():
    conn = get_db()
    cur  = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS claims (
            id           INT          AUTO_INCREMENT PRIMARY KEY,
            name         VARCHAR(255) NOT NULL,
            bkash_number VARCHAR(20)  NOT NULL UNIQUE,
            gift_amount  INT          NOT NULL,
            status       VARCHAR(20)  NOT NULL DEFAULT 'pending',
            claimed_at   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP    NULL
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

# ── Routes ────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/open-box', methods=['POST'])
def open_box():
    data = request.get_json(force=True)
    try:
        box_id = int(data.get('box_id', 0))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid box id'}), 400
    if box_id < 1 or box_id > 26:
        return jsonify({'error': 'Box not found'}), 404
    return jsonify({'gift': BOX_GIFTS[box_id]})


@app.route('/claim', methods=['POST',"GET"])
def claim():
    data   = request.get_json(force=True)
    name   = str(data.get('name', '')).strip()
    bkash  = str(data.get('bkash', '')).strip()
    amount = data.get('amount')

    if not name:
        return jsonify({'error': 'নাম লিখুন'}), 400
    if not bkash or len(bkash) < 11:
        return jsonify({'error': 'সঠিক bKash নম্বর দিন'}), 400
    if not amount:
        return jsonify({'error': 'পরিমাণ নেই'}), 400
    try:
        amount = int(amount)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid amount'}), 400

    conn = get_db()
    cur  = conn.cursor()

    # ── Duplicate bKash check (also enforced by UNIQUE in DB) ──
    cur.execute("SELECT id FROM claims WHERE bkash_number = %s", (bkash,))
    if cur.fetchone():
        cur.close(); conn.close()
        return jsonify({'error': 'এই bKash নম্বর দিয়ে আগেই সালামি নেওয়া হয়েছে! 🚫'}), 400

    cur.execute(
        "INSERT INTO claims (name, bkash_number, gift_amount, status) VALUES (%s, %s, %s, 'pending')",
        (name, bkash, amount)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        'success': True,
        'message': f'ঈদ মোবারক {name}! আপনার ৳{amount:,} সালামি শীঘ্রই পাঠানো হবে! 🌙✨'
    })


@app.route('/history')
def history():
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT id, name, bkash_number, claimed_at FROM claims ORDER BY claimed_at DESC LIMIT 50"
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    # Convert datetime to string for JSON
    for r in rows:
        if r.get('claimed_at'):
            r['claimed_at'] = str(r['claimed_at'])
    return jsonify(rows)


# ── Admin Routes ──────────────────────────────────

@app.route('/admin')
def admin():
    pwd = request.args.get('pwd', '')
    if pwd != ADMIN_PASSWORD:
        return render_template('admin_login.html')
    conn = get_db()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM claims WHERE status='pending'   ORDER BY claimed_at DESC")
    pending = cur.fetchall()
    cur.execute("SELECT * FROM claims WHERE status='completed' ORDER BY completed_at DESC")
    completed = cur.fetchall()
    cur.close()
    conn.close()
    # Convert datetimes
    for r in pending + completed:
        for k in ('claimed_at', 'completed_at'):
            if r.get(k): r[k] = str(r[k])
    total_pending   = sum(r['gift_amount'] for r in pending)
    total_completed = sum(r['gift_amount'] for r in completed)
    return render_template('admin.html',
        pending=pending, completed=completed,
        total_pending=total_pending, total_completed=total_completed,
        pwd=pwd
    )


@app.route('/admin/complete', methods=['POST'])
def admin_complete():
    data = request.get_json(force=True)
    if data.get('pwd') != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 403
    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        "UPDATE claims SET status='completed', completed_at=NOW() WHERE id=%s",
        (data.get('id'),)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'success': True})


@app.route('/admin/delete', methods=['POST'])
def admin_delete():
    data = request.get_json(force=True)
    if data.get('pwd') != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 403
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("DELETE FROM claims WHERE id=%s", (data.get('id'),))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'success': True})





if __name__ == '__main__':
    init_db()
    # print("🌙 Mystery Salami  → http://127.0.0.1:5001")
    # print("🔐 Admin Panel     → http://127.0.0.1:5001/admin?pwd=eid2025")
    app.run(debug=False, port=5001)
