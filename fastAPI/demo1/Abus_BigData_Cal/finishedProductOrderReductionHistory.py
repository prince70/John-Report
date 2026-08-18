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

def get_reduction_data(规格型号=None, 订单批号=None):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
        SELECT 料品编码, b.Name AS 系列, b.Description as 规格型号,
               订单批号, c.RequiredAvailableDate as 确定交期,
               c.QtyOrdered as 原订单数量,
               新值 as 减单数量, 修改时间 as 减单时间,
               v.库存 as 即时库存
        FROM [APS_SUO].[dbo].[pandian_change_log] a
        left join item b on a.料品编码 = b.ExternalId
        left join SalesOrder c on a.订单批号 = c.ExternalId
        left join [v_库存汇总] v on a.料品编码 = v.item_no
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
        result = []
        for row in rows:
            d = {col: (str(row[i]) if row[i] is not None else "") for i, col in enumerate(columns)}
            try:
                d["原订单数量"] = int(row[columns.index("原订单数量")]) if row[columns.index("原订单数量")] is not None else 0
            except (ValueError, TypeError):
                d["原订单数量"] = 0
            try:
                d["减单数量"] = int(row[columns.index("减单数量")]) if row[columns.index("减单数量")] is not None else 0
            except (ValueError, TypeError):
                d["减单数量"] = 0
            result.append(d)
        return result
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

def get_stock_data(item_no=None, 产品名称=None, 系列=None, 产品规格=None):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
        SELECT [item_no], [产品名称], [系列], [产品规格], [库存], [存放位置]
        FROM [APS_SUO].[dbo].[v_库存汇总]
        WHERE 库存类型 LIKE '%成品%' AND 库存类型 NOT LIKE '%半成品%' AND 库存类型 NOT LIKE 'CISA成品库存'
        """
        params = []
        if item_no:
            sql += " AND [item_no] LIKE ?"
            params.append(f"%{item_no}%")
        if 产品名称:
            sql += " AND [产品名称] LIKE ?"
            params.append(f"%{产品名称}%")
        if 系列:
            sql += " AND [系列] LIKE ?"
            params.append(f"%{系列}%")
        if 产品规格:
            sql += " AND [产品规格] LIKE ?"
            params.append(f"%{产品规格}%")
        sql += " ORDER BY [item_no]"
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

@router.get("/finishedProductOrderReductionHistory", summary="成品库存及成品减单历史记录")
async def get_data(
    规格型号: Optional[str] = Query(None),
    订单批号: Optional[str] = Query(None),
):
    try:
        raw_data = get_reduction_data(规格型号, 订单批号)
        return {"status": "success", "data": raw_data, "total_count": len(raw_data)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")

def _get_stock_options(field, 产品名称=None, 系列=None, 产品规格=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        base = "SELECT DISTINCT [{}] FROM [APS_SUO].[dbo].[v_库存汇总] WHERE [{}] IS NOT NULL AND [{}] != '' AND 库存类型 LIKE '%成品%' AND 库存类型 NOT LIKE '%半成品%' AND 库存类型 NOT LIKE 'CISA成品库存'".format(field, field, field)
        params = []
        if field != '产品名称' and 产品名称:
            base += " AND [产品名称] = ?"
            params.append(产品名称)
        if field != '系列' and 系列:
            base += " AND [系列] = ?"
            params.append(系列)
        if field != '产品规格' and 产品规格:
            base += " AND [产品规格] = ?"
            params.append(产品规格)
        base += " ORDER BY [{}]".format(field)
        cursor.execute(base, params)
        result = [str(row[0]) for row in cursor.fetchall()]
        conn.close()
        return result
    except:
        return []

@router.get("/finishedProductStock/options", summary="成品库存下拉选项（联动）")
async def get_stock_options(
    field: str = Query(...),
    产品名称: Optional[str] = Query(None),
    系列: Optional[str] = Query(None),
    产品规格: Optional[str] = Query(None),
):
    return {"status": "success", "data": _get_stock_options(field, 产品名称, 系列, 产品规格)}

@router.get("/finishedProductStock", summary="成品库存查询")
async def get_stock(
    item_no: Optional[str] = Query(None),
    产品名称: Optional[str] = Query(None),
    系列: Optional[str] = Query(None),
    产品规格: Optional[str] = Query(None),
):
    try:
        raw_data = get_stock_data(item_no, 产品名称, 系列, 产品规格)
        total_inventory = sum(float(r.get("库存", 0) or 0) for r in raw_data)
        return {"status": "success", "data": raw_data, "total_count": len(raw_data), "total_inventory": total_inventory}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")

@router.get("/finishedProductStock/stats", summary="成品库存按系列统计")
async def get_stock_stats(
    item_no: Optional[str] = Query(None),
    产品名称: Optional[str] = Query(None),
    系列: Optional[str] = Query(None),
    产品规格: Optional[str] = Query(None),
):
    try:
        raw_data = get_stock_data(item_no, 产品名称, 系列, 产品规格)
        series_map = {}
        for r in raw_data:
            s = r.get("系列", "") or "未知"
            qty = float(r.get("库存", 0) or 0)
            if s not in series_map:
                series_map[s] = 0
            series_map[s] += qty
        stats_data = [{"系列": k, "库存": v} for k, v in series_map.items() if v > 0]
        def sort_key(item):
            return (1, 0) if item["系列"] == "未知" else (0, -item["库存"])
        stats_data.sort(key=sort_key)
        total_inventory = sum(v for v in series_map.values())
        return {"status": "success", "data": stats_data, "total_inventory": total_inventory}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")


def get_reduction_monthly_stats(规格型号=None, 订单批号=None):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
        SELECT FORMAT(修改时间, 'yyyy-MM') AS 月份, SUM(新值) AS 减单数量
        FROM [APS_SUO].[dbo].[pandian_change_log] a
        LEFT JOIN item b ON a.料品编码 = b.ExternalId
        WHERE 修改时间 > '2026-08-03' AND 料品编码 LIKE '1%'
        """
        params = []
        if 规格型号:
            sql += " AND b.Description LIKE ?"
            params.append(f"%{规格型号}%")
        if 订单批号:
            sql += " AND a.订单批号 LIKE ?"
            params.append(f"%{订单批号}%")
        sql += " GROUP BY FORMAT(修改时间, 'yyyy-MM') ORDER BY 月份 DESC"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        result = [{"月份": str(row[0]), "减单数量": int(row[1]) if row[1] is not None else 0} for row in rows]
        return result
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


@router.get("/finishedProductOrderReduction/stats", summary="成品减单按月统计")
async def get_reduction_stats(
    规格型号: Optional[str] = Query(None),
    订单批号: Optional[str] = Query(None),
):
    try:
        raw_data = get_reduction_monthly_stats(规格型号, 订单批号)
        total_reduction = sum(r["减单数量"] for r in raw_data)
        return {"status": "success", "data": raw_data, "total_reduction": total_reduction}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
