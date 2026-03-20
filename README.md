# 🌙 Mystery Salami — রহস্যময় সালামি

A festive Eid Salami web game built with Python Flask + Jinja2.

## Setup & Run

```bash
# 1. Install Flask (only dependency)
pip install flask

# 2. Run the app
python app.py

# 3. Open in browser
#    http://127.0.0.1:5000
```

## How It Works

- 26 mystery gift boxes, each hiding a hidden Taka amount
- Player clicks up to **3 boxes** — earns the **last box's value**
- A modal collects Name + bKash number → saved to SQLite3
- **3 attempts** are tracked via browser `localStorage` (persists across sessions)
- Database file `mystery_salami.db` is auto-created on first run

## Gift Amounts (26 boxes)

| Amount | Boxes |
|--------|-------|
| ৳20    | 5×    |
| ৳50    | 4×    |
| ৳100   | 5×    |
| ৳200   | 4×    |
| ৳500   | 3×    |
| ৳1,000 | 2×    |
| ৳2,000 | 2×    |
| ৳5,000 | 1×    |

## Project Structure

```
mystery_salami/
├── app.py              ← Flask routes + SQLite logic
├── requirements.txt    ← pip dependencies
├── mystery_salami.db   ← auto-created SQLite database
└── templates/
    └── index.html      ← Full UI (Jinja2 + CSS + JS)
```

## Database Schema

```sql
CREATE TABLE claims (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL,
    bkash_number TEXT    NOT NULL,
    gift_amount  INTEGER NOT NULL,
    claimed_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

ঈদ মোবারক! 🌙✨
