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

try:
    conn = pyodbc.connect(conn_str, timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM FolderCategories__")
    row = cursor.fetchone()
    print(f"✓ 连接成功!")
    print(f"  表记录数: {row[0]}")
    conn.close()
except Exception as e:
    print(f"✗ 连接失败: {e}")
    sys.exit(1)