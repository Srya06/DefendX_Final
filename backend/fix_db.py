import sqlite3

conn = sqlite3.connect('test.db')
conn.execute("UPDATE alembic_version SET version_num='8dcecae8716b'")
conn.commit()
conn.close()
print("Fixed DB version")
