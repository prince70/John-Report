from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pyodbc
from datetime import datetime, timedelta
from fastapi_cache.decorator import cache

router = APIRouter()

DB_SERVER = "192.168.10.200"
DB_DATABASE = "APS_SUO"
DB_USERNAME = "sa"
DB_PASSWORD = "5tgb^YHN7ujm*IK<"
TABLE_NAME = "锁体C车间_超数记录"

def get_db_connection():
    conn_str = (
        f"DRIVER={{SQL Server}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};"
        f"UID={DB_USERNAME};PWD={DB_PASSWORD};"
    )
    return pyodbc.connect(conn_str)

def get_data_from_db(订单批号=None, 料品规格=None, 开始交期=None, 结束交期=None, 开始报工=None, 结束报工=None):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = f"""
        SELECT * FROM [APS_SUO].[dbo].[{TABLE_NAME}]
        WHERE 1=1
        """
        params = []
        if 订单批号:
            sql += " AND [订单批号] LIKE ?"
            params.append(f"%{订单批号}%")
        if 料品规格:
            sql += " AND [料品规格] = ?"
            params.append(料品规格)
        if 开始交期 and 结束交期:
            sql += " AND [确定交期] >= ? AND [确定交期] < ?"
            params.append(开始交期)
            end_date_obj = datetime.strptime(结束交期, '%Y-%m-%d') + timedelta(days=1)
            params.append(end_date_obj.strftime('%Y-%m-%d'))
        elif 开始交期:
            sql += " AND [确定交期] >= ?"
            params.append(开始交期)
        elif 结束交期:
            sql += " AND [确定交期] <= ?"
            params.append(结束交期)
        if 开始报工 and 结束报工:
            sql += " AND [报工时间] >= ? AND [报工时间] < ?"
            params.append(开始报工)
            end_date_obj = datetime.strptime(结束报工, '%Y-%m-%d') + timedelta(days=1)
            params.append(end_date_obj.strftime('%Y-%m-%d'))
        elif 开始报工:
            sql += " AND [报工时间] >= ?"
            params.append(开始报工)
        elif 结束报工:
            sql += " AND [报工时间] <= ?"
            params.append(结束报工)
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [{col: (str(row[i]) if row[i] is not None else "") for i, col in enumerate(columns)} for row in rows]
    finally:
        if conn:
            try: conn.close()
            except: pass

def get_options_from_db(field):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT DISTINCT TOP 200 [{field}] AS value FROM [APS_SUO].[dbo].[{TABLE_NAME}]
            WHERE [{field}] IS NOT NULL AND [{field}] != '' ORDER BY [{field}]
        """)
        return [{"value": row[0]} for row in cursor.fetchall()]
    finally:
        if conn:
            try: conn.close()
            except: pass

@router.get("/overStockQuantity", summary="超库存数量查询")
# @cache(expire=1800)
async def get_data(
    订单批号: Optional[str] = Query(None), 料品规格: Optional[str] = Query(None),
    开始交期: Optional[str] = Query(None), 结束交期: Optional[str] = Query(None),
    开始报工: Optional[str] = Query(None), 结束报工: Optional[str] = Query(None),
):
    try:
        raw_data = get_data_from_db(订单批号, 料品规格, 开始交期, 结束交期, 开始报工, 结束报工)
        return {"status": "success", "data": raw_data, "total_count": len(raw_data), "timestamp": datetime.now().isoformat()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")

@router.get("/overStockQuantity/options", summary="超库存数量下拉选项")
@cache(expire=72000)
async def get_options(field: str = Query(...)):
    try:
        return {"status": "success", "data": get_options_from_db(field)}
    except Exception as exc:
        return {"status": "success", "data": []}
