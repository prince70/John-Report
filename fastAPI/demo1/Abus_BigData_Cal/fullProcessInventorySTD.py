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
TABLE_NAME = "Full_process_reporting_STD"

def get_db_connection():
    conn_str = (
        f"DRIVER={{SQL Server}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};"
        f"UID={DB_USERNAME};PWD={DB_PASSWORD};"
    )
    return pyodbc.connect(conn_str)

def get_data_from_db(订单批号=None, 料品编码=None, 料品名称=None, 料品规格=None, 当前工序ID=None, 下一道工序ID=None, 开始日期=None, 结束日期=None):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = f"""
        SELECT [id], [订单批号], [料品编码], [料品名称], [料品规格],
               [生产车间], [当前工序ID], [下一道工序ID], [报工数量总和], [库存], [备注], 
               CONVERT(VARCHAR(10), [FinishedDate], 120) AS [完成日期]
        FROM [APS_SUO].[dbo].[{TABLE_NAME}]
        WHERE 1=1
        """
        params = []
        if 订单批号:
            sql += " AND [订单批号] LIKE ?"
            params.append(f"%{订单批号}%")
        if 料品编码:
            sql += " AND [料品编码] LIKE ?"
            params.append(f"%{料品编码}%")
        if 料品名称:
            sql += " AND [料品名称] LIKE ?"
            params.append(f"%{料品名称}%")
        if 料品规格:
            sql += " AND [料品规格] LIKE ?"
            params.append(f"%{料品规格}%")
        if 当前工序ID:
            sql += " AND [当前工序ID] = ?"
            params.append(当前工序ID)
        if 下一道工序ID:
            sql += " AND [下一道工序ID] = ?"
            params.append(下一道工序ID)
        if 开始日期 and 结束日期:
            sql += " AND [FinishedDate] >= ? AND [FinishedDate] < ?"
            params.append(开始日期)
            end_date_obj = datetime.strptime(结束日期, '%Y-%m-%d') + timedelta(days=1)
            params.append(end_date_obj.strftime('%Y-%m-%d'))
        elif 开始日期:
            sql += " AND [FinishedDate] >= ?"
            params.append(开始日期)
        elif 结束日期:
            sql += " AND [FinishedDate] <= ?"
            params.append(结束日期)
        sql += " ORDER BY [id]"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [{
            "id": row[0], "订单批号": row[1] or "", "料品编码": row[2] or "",
            "料品名称": row[3] or "", "料品规格": row[4] or "",
            "生产车间": row[5] or "", "当前工序ID": row[6] or "",
            "下一道工序ID": row[7] or "", "报工数量总和": float(row[8]) if row[8] else 0,
            "库存": float(row[9]) if row[9] else 0, "备注": row[10] or "",
            "完成日期": row[11] or "",
        } for row in rows]
    finally:
        if conn:
            try: conn.close()
            except: pass

def get_options_from_db(field):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        col_map = {"料品名称": "料品名称", "料品规格": "料品规格", "当前工序ID": "当前工序ID", "下一道工序ID": "下一道工序ID"}
        if field not in col_map:
            return []
        col = col_map[field]
        cursor.execute(f"""
            SELECT DISTINCT TOP 200 [{col}] AS value FROM [APS_SUO].[dbo].[{TABLE_NAME}]
            WHERE [{col}] IS NOT NULL AND [{col}] != '' ORDER BY [{col}]
        """)
        return [{"value": row[0]} for row in cursor.fetchall()]
    finally:
        if conn:
            try: conn.close()
            except: pass

@router.get("/fullProcessInventorySTD", summary="全流程报工库存-锁体D车间")
# @cache(expire=1800)
async def get_data(
    订单批号: Optional[str] = Query(None), 料品编码: Optional[str] = Query(None),
    料品名称: Optional[str] = Query(None), 料品规格: Optional[str] = Query(None),
    当前工序ID: Optional[str] = Query(None),
    下一道工序ID: Optional[str] = Query(None),
    开始日期: Optional[str] = Query(None), 结束日期: Optional[str] = Query(None),
):
    try:
        raw_data = get_data_from_db(订单批号, 料品编码, 料品名称, 料品规格, 当前工序ID, 下一道工序ID, 开始日期, 结束日期)
        return {"status": "success", "data": raw_data, "total_count": len(raw_data), "timestamp": datetime.now().isoformat()}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")

@router.get("/fullProcessInventorySTD/options", summary="锁体D下拉选项")
@cache(expire=72000)
async def get_options(field: str = Query(...)):
    try:
        return {"status": "success", "data": get_options_from_db(field)}
    except Exception as exc:
        return {"status": "success", "data": []}

def get_summary_from_db(订单批号=None, 料品编码=None, 料品名称=None, 料品规格=None, 当前工序ID=None, 下一道工序ID=None, 开始日期=None, 结束日期=None):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = f"""
        SELECT [当前工序ID], SUM(CAST([库存] AS FLOAT)) AS 库存合计, COUNT(*) AS 记录数
        FROM [APS_SUO].[dbo].[{TABLE_NAME}]
        WHERE 1=1
        """
        params = []
        if 订单批号:
            sql += " AND [订单批号] LIKE ?"
            params.append(f"%{订单批号}%")
        if 料品编码:
            sql += " AND [料品编码] LIKE ?"
            params.append(f"%{料品编码}%")
        if 料品名称:
            sql += " AND [料品名称] LIKE ?"
            params.append(f"%{料品名称}%")
        if 料品规格:
            sql += " AND [料品规格] LIKE ?"
            params.append(f"%{料品规格}%")
        if 当前工序ID:
            sql += " AND [当前工序ID] = ?"
            params.append(当前工序ID)
        if 下一道工序ID:
            sql += " AND [下一道工序ID] = ?"
            params.append(下一道工序ID)
        if 开始日期 and 结束日期:
            sql += " AND [FinishedDate] >= ? AND [FinishedDate] < ?"
            params.append(开始日期)
            end_date_obj = datetime.strptime(结束日期, '%Y-%m-%d') + timedelta(days=1)
            params.append(end_date_obj.strftime('%Y-%m-%d'))
        elif 开始日期:
            sql += " AND [FinishedDate] >= ?"
            params.append(开始日期)
        elif 结束日期:
            sql += " AND [FinishedDate] <= ?"
            params.append(结束日期)
        sql += " GROUP BY [当前工序ID] ORDER BY [当前工序ID]"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [{"当前工序ID": row[0] or "", "库存合计": float(row[1]) if row[1] else 0, "记录数": row[2]} for row in rows]
    finally:
        if conn:
            try: conn.close()
            except: pass

@router.get("/fullProcessInventorySTD/summary", summary="锁体D按当前工序ID汇总库存")
async def get_summary(
    订单批号: Optional[str] = Query(None), 料品编码: Optional[str] = Query(None),
    料品名称: Optional[str] = Query(None), 料品规格: Optional[str] = Query(None),
    当前工序ID: Optional[str] = Query(None),
    下一道工序ID: Optional[str] = Query(None),
    开始日期: Optional[str] = Query(None), 结束日期: Optional[str] = Query(None),
):
    try:
        data = get_summary_from_db(订单批号, 料品编码, 料品名称, 料品规格, 当前工序ID, 下一道工序ID, 开始日期, 结束日期)
        return {"status": "success", "data": data}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
