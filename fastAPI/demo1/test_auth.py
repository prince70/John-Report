#!/usr/bin/env python
import pyodbc
import sys

conn_str = (
    "DRIVER={SQL Server};"
    "SERVER=192.168.10.200;"
    "DATABASE=APS_SUO;"
    "UID=sa;"
    "PWD=5tgb^YHN7ujm*IK"
)

print("Testing SQL Authentication...")
try:
    conn = pyodbc.connect(conn_str, timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM [Abus2020].[dbo].[v_pandian_all_workspace]")
    count = cursor.fetchone()[0]
    print(f"SUCCESS: Connected! Records: {count}")
    conn.close()
except Exception as e:
    print(f"FAILED: {e}")
    sys.exit(1)