from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pyodbc
from datetime import datetime, timedelta

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

def get_data_from_db(start, end, 订单批号=None):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
        SELECT b._Identify, b.生产车间, a.JobExternalId AS 工单编号, b.工单状态,
               b.订单批号, b.确定交期, b.订单数量, b.料品编码, a.ResName AS 生产线编号,
               b.规格型号, a.emp_no, a.emp_name AS 报工人, b.计划产量 AS 工单数量,
               a.EachFinishedQty AS 报工数量, a.scrapQty AS 报废数量, a.repairQty AS 返修数量,
               a.StartDate AS 开工时间, a.FinishedDate AS 完工时间,
               CASE
                   WHEN pr.QtyPerCycle IS NOT NULL THEN pr.QtyPerCycle * 60.0
                   WHEN d.capacity IS NOT NULL THEN CAST(d.capacity AS FLOAT)
                   ELSE NULL
               END AS 车间提供,
               CAST(
                   (ISNULL(a.EachFinishedQty, 0) + ISNULL(a.repairQty, 0) + ISNULL(a.scrapQty, 0))
                   / NULLIF(
                       CASE
                           WHEN pr.QtyPerCycle IS NOT NULL THEN pr.QtyPerCycle * 60.0
                           WHEN d.capacity IS NOT NULL THEN CAST(d.capacity AS FLOAT)
                           ELSE NULL
                       END,
                       0
                   )
                   AS DECIMAL(18, 1)
               ) AS 时间
        FROM APS_FinishedQty_CNC a
        JOIN 派工单 b ON a.JobExternalId = b.工单编号
        LEFT JOIN APS.APS_SUO.dbo.ProductRules pr
            ON a.ResName = pr.ResourceExternalId
            AND dbo.RemoveChineseChars(a.ItemExternalId) = pr.ProductItemExternalId
        LEFT JOIN APS.APS_SUO.dbo.offline_process d
            ON b.OpExternalId = d.proccess
            AND dbo.RemoveChineseChars(a.ItemExternalId) = d.item_no
        WHERE a.FinishedDate BETWEEN ? AND ?
        """
        params = [start, end]
        if 订单批号:
            sql += " AND b.订单批号 LIKE ?"
            params.append(f"%{订单批号}%")
        sql += " ORDER BY b.订单批号"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [{
            "序列号": row[0] or "", "生产车间": row[1] or "", "工单编号": row[2] or "", "工单状态": row[3] or "",
            "订单批号": row[4] or "", "确定交期": row[5] or "", "订单数量": float(row[6]) if row[6] else 0,
            "料品编码": row[7] or "", "生产线编号": row[8] or "", "规格型号": row[9] or "",
            "emp_no": row[10] or "", "报工人": row[11] or "", "工单数量": float(row[12]) if row[12] else 0,
            "报工数量": float(row[13]) if row[13] else 0, "报废数量": float(row[14]) if row[14] else 0,
            "返修数量": float(row[15]) if row[15] else 0, "开工时间": str(row[16]) if row[16] else "",
            "完工时间": str(row[17]) if row[17] else "", "车间提供": float(row[18]) if row[18] else None,
            "时间": float(row[19]) if row[19] else None,
        } for row in rows]
    finally:
        if conn:
            try: conn.close()
            except: pass

@router.get("/workshopReportDetail/test", summary="测试数据库连通性")
async def test_db():
    results = {}
    # 1. 测试连接
    try:
        conn = get_db_connection()
        results["连接状态"] = "成功"
        cursor = conn.cursor()
        # 2. 列出所有用户表
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' ORDER BY TABLE_NAME")
        results["所有表"] = [row[0] for row in cursor.fetchall()]
        # 3. 测试 APS_FinishedQty_CNC 表是否存在及行数
        try:
            cursor.execute("SELECT COUNT(*) FROM APS_FinishedQty_CNC")
            results["APS_FinishedQty_CNC_行数"] = cursor.fetchone()[0]
        except Exception as e:
            results["APS_FinishedQty_CNC_错误"] = str(e)
        # 4. 测试 派工单 表是否存在及行数
        try:
            cursor.execute("SELECT COUNT(*) FROM 派工单")
            results["派工单_行数"] = cursor.fetchone()[0]
        except Exception as e:
            results["派工单_错误"] = str(e)
        # 5. 测试 RemoveChineseChars 函数
        try:
            cursor.execute("SELECT dbo.RemoveChineseChars('ABC123测试')")
            results["RemoveChineseChars_测试"] = cursor.fetchone()[0]
        except Exception as e:
            results["RemoveChineseChars_错误"] = str(e)
        # 6. 测试跨库 ProductRules
        try:
            cursor.execute("SELECT COUNT(*) FROM APS.APS_SUO.dbo.ProductRules")
            results["ProductRules_行数"] = cursor.fetchone()[0]
        except Exception as e:
            results["ProductRules_错误"] = str(e)
        conn.close()
    except Exception as e:
        results["连接状态"] = f"失败: {str(e)}"
    return results

@router.get("/workshopReportDetail/CNC", summary="CNC报工详情")
async def get_data(
    start: str = Query(..., description="报工日期始"),
    end: str = Query(..., description="报工日期末"),
    订单批号: Optional[str] = Query(None),
):
    try:
        raw_data = get_data_from_db(start, end, 订单批号)
        return {"status": "success", "data": raw_data, "total_count": len(raw_data)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
