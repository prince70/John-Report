import pyodbc
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn_str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.41.57;DATABASE=department2020;UID=sa;PWD=3518i;"
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

print("=== PGD_WorkOrder_01 ===")
cursor.execute("""
    SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE, ORDINAL_POSITION
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'PGD_WorkOrder_01'
    ORDER BY ORDINAL_POSITION
""")
rows = cursor.fetchall()
for r in rows:
    print(r)

print()
print("=== 派工单 ===")
cursor.execute("""
    SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE, ORDINAL_POSITION
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = N'派工单'
    ORDER BY ORDINAL_POSITION
""")
rows = cursor.fetchall()
for r in rows:
    print(r)

conn.close()
