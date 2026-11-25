#!/usr/bin/env python
import pyodbc
import sys

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=192.168.10.200;"
    "DATABASE=APS_SUO;"
    "UID=sa;"
    "PWD=5tgb^YHN7ujm*IK"
)

print("=" * 50)
print("Testing SQL Server Connection")
print("=" * 50)
print(f"Connection string: {conn_str}")
print()

try:
    conn = pyodbc.connect(conn_str, timeout=10)
    print("✓ Connection successful!")
    
    cursor = conn.cursor()
    
    # Check databases
    cursor.execute("SELECT NAME FROM SYS.DATABASES WHERE NAME = 'APS_SUO'")
    db = cursor.fetchone()
    print(f"✓ Database APS_SUO exists: {db is not None}")
    
    # Check view
    cursor.execute("SELECT COUNT(*) FROM [Abus2020].[dbo].[v_pandian_all_workspace]")
    count = cursor.fetchone()[0]
    print(f"✓ v_pandian_all_workspace records: {count}")
    
    conn.close()
    print()
    print("=" * 50)
    print("ALL TESTS PASSED!")
    print("=" * 50)
    
except Exception as e:
    print("✗ Connection failed!")
    print(f"Error: {e}")
    sys.exit(1)