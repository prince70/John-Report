#!/usr/bin/env python
import os
import sys
import pyodbc
from datetime import datetime

# Force clear any env vars that might interfere
for key in ['DB_PASSWORD', 'DB_SERVER', 'DB_DATABASE', 'DB_USERNAME']:
    if key in os.environ:
        del os.environ[key]

# Now import Settings - this should use defaults
print("=== Testing Settings ===")
from Abus_BigData_Cal.file_api import Settings
s = Settings()
print(f"db_server: {s.db_server}")
print(f"db_database: {s.db_database}")
print(f"db_username: {s.db_username}")
print(f"db_password: {s.db_password}")

print("\n=== Testing DB Connection ===")
conn_str = (
    f"DRIVER={{SQL Server}};"
    f"SERVER={s.db_server};"
    f"DATABASE={s.db_database};"
    f"UID={s.db_username};"
    f"PWD={s.db_password}"
)
try:
    conn = pyodbc.connect(conn_str, timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM [Abus2020].[dbo].[v_pandian_all_workspace]")
    count = cursor.fetchone()[0]
    print(f"✓ SUCCESS: Connected to database!")
    print(f"  Table records: {count}")
    conn.close()
except Exception as e:
    print(f"✗ FAILED: {e}")
    sys.exit(1)

print("\n=== All tests passed! ===")