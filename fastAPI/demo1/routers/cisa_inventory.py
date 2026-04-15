from datetime import datetime
from typing import Optional

import pyodbc
from fastapi import APIRouter, HTTPException, Query, status

router = APIRouter()
DB_SERVER = "192.168.10.200"
DB_DATABASE = "APS_SUO"
DB_USERNAME = "sa"
DB_PASSWORD = "5tgb^YHN7ujm*IK<"
TABLE_CANDIDATES = ["cisa_inventory", "CISA_Inventory", "pandian_cisa"]


def get_db_connection():
    trusted_conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};"
        f"DATABASE={DB_DATABASE};Trusted_Connection=yes;"
    )
    sql_auth_conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};"
        f"UID={DB_USERNAME};PWD={DB_PASSWORD};"
    )

    sql_auth_error = None
    trusted_error = None

    try:
        return pyodbc.connect(sql_auth_conn_str)
    except Exception as exc:
        sql_auth_error = exc

    try:
        return pyodbc.connect(trusted_conn_str)
    except Exception as exc:
        trusted_error = exc

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=(
            "[cisa-inventory-router] 数据库连接失败。"
            f"SQL认证错误: {sql_auth_error}; 集成认证错误: {trusted_error}"
        ),
    )


def escape_sql_identifier(name: str) -> str:
    return f"[{name.replace(']', ']]')}]"


def resolve_table_name(cursor) -> str:
    for table_name in TABLE_CANDIDATES:
        cursor.execute(
            """
            SELECT COUNT(1)
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = ?
            """,
            table_name,
        )
        exists = int(cursor.fetchone()[0])
        if exists > 0:
            return table_name

    raise HTTPException(status_code=404, detail="未找到CISA库存表数据源")


def get_table_columns(cursor, table_name: str):
    cursor.execute(
        """
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
        """,
        table_name,
    )
    return [row[0] for row in cursor.fetchall()]


def build_where_clause(columns, item_code: Optional[str], product_name: Optional[str], product_spec: Optional[str]):
    conditions = []
    params = []

    if item_code and "料品编码" in columns:
        conditions.append("[料品编码] LIKE ?")
        params.append(f"%{item_code}%")

    if product_name and "产品名称" in columns:
        conditions.append("[产品名称] LIKE ?")
        params.append(f"%{product_name}%")

    if product_spec and "产品规格" in columns:
        conditions.append("[产品规格] LIKE ?")
        params.append(f"%{product_spec}%")

    where_sql = " WHERE " + " AND ".join(conditions) if conditions else ""
    return where_sql, params


@router.get("/list", summary="CISA库存表查询")
async def get_cisa_inventory_list(
    item_code: Optional[str] = None,
    product_name: Optional[str] = None,
    product_spec: Optional[str] = None,
    offset: int = Query(default=0, ge=0, description="分页偏移量，从0开始"),
    limit: int = Query(default=100, ge=1, le=5000, description="分页大小"),
):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        table_name = resolve_table_name(cursor)
        columns = get_table_columns(cursor, table_name)
        if not columns:
            return {
                "status": "success",
                "data": [],
                "columns": [],
                "total": 0,
                "timestamp": datetime.now().isoformat(),
            }

        where_sql, params = build_where_clause(columns, item_code, product_name, product_spec)
        table_sql = f"[APS_SUO].[dbo].{escape_sql_identifier(table_name)}"

        count_sql = "SELECT COUNT(1) FROM " + table_sql + where_sql
        cursor.execute(count_sql, params)
        total = int(cursor.fetchone()[0])

        order_col_sql = escape_sql_identifier(columns[0])
        query_sql = (
            "SELECT * FROM " + table_sql + where_sql +
            f" ORDER BY {order_col_sql} ASC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        )
        cursor.execute(query_sql, [*params, int(offset), int(limit)])

        result_columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        data = []
        for row in rows:
            item = {}
            for idx, value in enumerate(row):
                if hasattr(value, "isoformat"):
                    item[result_columns[idx]] = value.isoformat()
                else:
                    item[result_columns[idx]] = value
            data.append(item)

        return {
            "status": "success",
            "data": data,
            "columns": result_columns,
            "total": total,
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取CISA库存表失败: {exc}",
        )
    finally:
        if conn:
            conn.close()
