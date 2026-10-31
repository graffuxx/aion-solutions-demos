"""Synthetic SQLite case: a one-to-many join silently inflates revenue."""
import sqlite3

BROKEN = '''SELECT SUM(o.cents) FROM orders o
            JOIN tags t ON t.order_id=o.id WHERE t.name IN ('api','priority')'''
FIXED = '''SELECT SUM(o.cents) FROM orders o WHERE EXISTS
           (SELECT 1 FROM tags t WHERE t.order_id=o.id AND t.name IN ('api','priority'))'''


def fixture():
    db = sqlite3.connect(':memory:')
    db.executescript('''CREATE TABLE orders(id INTEGER PRIMARY KEY,cents INTEGER);
    CREATE TABLE tags(order_id INTEGER,name TEXT);
    INSERT INTO orders VALUES(1,10000),(2,10000),(3,3000);
    INSERT INTO tags VALUES(1,'api'),(1,'priority'),(2,'api'),(3,'other');''')
    return db


def compare():
    db = fixture()
    try:
        return {'broken_cents': db.execute(BROKEN).fetchone()[0],
                'fixed_cents': db.execute(FIXED).fetchone()[0], 'expected_cents': 20000}
    finally:
        db.close()
