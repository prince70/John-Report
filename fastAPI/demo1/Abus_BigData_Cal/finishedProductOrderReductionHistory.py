from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pyodbc
from datetime import datetime, timedelta

router = APIRouter()

DB_SERVER = "192.168.10.200"
DB_DATABASE = "APS_SUO"
DB_USERNAME = "sa"
DB_PASSWORD = "5tgb^YHN7ujm*IK<"

def get_db_connection():
    conn_str = (
        f"DRIVER={{SQL Server}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};"
        f"UID={DB_USERNAME};PWD={DB_PASSWORD};"
    )
    return pyodbc.connect(conn_str)

def get_data_from_db(规格型号=None, 订单批号=None):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
        SELECT 料品编码, b.Name AS 系列, b.Description as 规格型号,
               订单批号, c.RequiredAvailableDate as 确定交期,
               c.QtyOrdered as 原订单数量,
               新值 as 减单数量, 修改时间 as 减单时间
        FROM [APS_SUO].[dbo].[pandian_change_log] a
        left join item b on a.料品编码 = b.ExternalId
        left join SalesOrder c on a.订单批号 = c.ExternalId
        WHERE 修改时间 > '2026-08-03' AND 料品编码 like '1%'
        """
        params = []
        if 规格型号:
            sql += " AND b.Description LIKE ?"
            params.append(f"%{规格型号}%")
        if 订单批号:
            sql += " AND a.订单批号 LIKE ?"
            params.append(f"%{订单批号}%")
        sql += " ORDER BY 修改时间 DESC"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [{col: (str(row[i]) if row[i] is not None else "") for i, col in enumerate(columns)} for row in rows]
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

@router.get("/finishedProductOrderReductionHistory", summary="成品减单历史记录")
async def get_data(
    规格型号: Optional[str] = Query(None),
    订单批号: Optional[str] = Query(None),
):
    try:
        raw_data = get_data_from_db(规格型号, 订单批号)
        return {"status": "success", "data": raw_data, "total_count": len(raw_data)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
