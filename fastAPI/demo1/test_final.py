import pyodbc
import os

# Clear any env vars that might interfere
for key in ['DB_PASSWORD', 'DB_SERVER', 'DB_DATABASE', 'DB_USERNAME']:
    if key in os.environ:
        del os.environ[key]

# Test connection with correct settings
conn_str = (
    "DRIVER={SQL Server};"
    "SERVER=192.168.10.200;"
    "DATABASE=APS_SUO;"
    "UID=sa;"
    "PWD=5tgb^YHN7ujm*IK<"
)

try:
    conn = pyodbc.connect(conn_str, timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM [Abus2020].[dbo].[v_pandian_all_workspace]")
    count = cursor.fetchone()[0]
    print(f"SUCCESS: Connected! Records: {count}")
    conn.close()
except Exception as e:
    print(f"FAILED: {e}")