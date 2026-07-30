from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pyodbc

router = APIRouter()

DB_SERVER = "192.168.41.57"
DB_DATABASE = "department2020"
DB_USERNAME = "sa"
DB_PASSWORD = "3518i"

def get_db_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};"
        f"UID={DB_USERNAME};PWD={DB_PASSWORD};"
    )
    return pyodbc.connect(conn_str)

def get_data_from_db(start, end, 序列号=None, 姓名=None, 生产线编号=None, 订单批号=None):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
        SELECT a.isCheck, a.iNo, b._Identify, b.生产车间, a.JobExternalId AS 工单编号,
               b.工单状态, a.OrderNumber AS 订单批号, b.订单数量,
               a.ItemExternalId AS 料品编码, a.ResName AS 生产线编号,
               a.ProductDescription AS 规格型号, a.emp_name AS 报工人,
               b.计划产量 AS 工单数量, a.EachFinishedQty AS 报工数量,
               a.scrapQty AS 报废数量, a.repairQty AS 返修数量,
               CASE WHEN d.capacity IS NOT NULL THEN d.capacity ELSE 0 END AS 每小时产能,
               a.StartDate AS 开工时间, a.FinishedDate AS 完工时间,
               b.确定交期, b.客户, b.OpExternalId
        FROM APS_FinishedQty_Pack a
        JOIN 派工单 b ON a.JobExternalId = b.工单编号
        LEFT JOIN APS.APS_SUO.dbo.offline_process d
            ON b.OpExternalId = d.proccess
            AND b.料品编码 = d.item_no + d.proccess
        WHERE ISNULL(a.EachFinishedQty, 0) > 0
        AND a.FinishedDate BETWEEN ? AND ?
        """
        params = [start, end]
        if 序列号:
            sql += " AND b._Identify LIKE ?"
            params.append(f"%{序列号}%")
        if 姓名:
            sql += " AND a.emp_name LIKE ?"
            params.append(f"%{姓名}%")
        if 生产线编号:
            sql += " AND a.ResName LIKE ?"
            params.append(f"%{生产线编号}%")
        if 订单批号:
            sql += " AND a.OrderNumber LIKE ?"
            params.append(f"%{订单批号}%")
        sql += " ORDER BY b.订单批号"
        cursor.execute(sql, params)
        rows = cursor.fetchall()

        result = []
        for row in rows:
            报工数量 = float(row[13]) if row[13] else 0
            每小时产能 = float(row[16]) if row[16] else 0
            时间 = round(报工数量 / 每小时产能, 2) if 每小时产能 != 0 else None

            result.append({
                "是否核对": row[0] or "",
                "序列号": row[2] or "",
                "生产车间": row[3] or "",
                "工单编号": row[4] or "",
                "工单状态": row[5] or "",
                "订单批号": row[6] or "",
                "订单数量": float(row[7]) if row[7] else 0,
                "料品编码": row[8] or "",
                "生产线编号": row[9] or "",
                "规格型号": row[10] or "",
                "报工人": row[11] or "",
                "工单数量": float(row[12]) if row[12] else 0,
                "报工数量": 报工数量,
                "报废数量": float(row[14]) if row[14] else 0,
                "返修数量": float(row[15]) if row[15] else 0,
                "车间提供": 每小时产能,
                "时间": 时间,
                "开工时间": str(row[17]) if row[17] else "",
                "完工时间": str(row[18]) if row[18] else "",
                "确定交期": row[19] or "",
                "客户": row[20] or "",
                "工序": row[21] or "",
            })
        return result
    finally:
        if conn:
            try: conn.close()
            except: pass

@router.get("/workshopReportDetail/Pack", summary="包装车间报工详情")
async def get_data(
    start: str = Query(..., description="开始时间"),
    end: str = Query(..., description="结束时间"),
    序列号: Optional[str] = Query(None),
    姓名: Optional[str] = Query(None),
    生产线编号: Optional[str] = Query(None),
    订单批号: Optional[str] = Query(None),
):
    try:
        raw_data = get_data_from_db(start, end, 序列号, 姓名, 生产线编号, 订单批号)
        return {"status": "success", "data": raw_data, "total_count": len(raw_data)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
