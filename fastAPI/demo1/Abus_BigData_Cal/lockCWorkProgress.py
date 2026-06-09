from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pyodbc
from datetime import datetime
from fastapi_cache.decorator import cache

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

def get_summary_from_db(订单批号=None, 料品编码=None, 料品名称=None, 工序=None, 交期开始=None, 交期结束=None):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
        SELECT
            v.客户,
            v.sheet_lot AS 订单批号,
            v.确定交期,
            f_agg.生产车间,
            f_agg.料品名称 AS 半成品料品名称,
            v.item_no AS 料品编码,
            v.part_name AS 料品名称,
            v.part_spec AS 规格型号,
            f_agg.工序,
            CAST(v.sheet_qty AS INT) AS 订单数量,
            f_agg.plan_qty AS 计划产量,
            ISNULL(f_agg.finished_qty, 0) AS 完成数量,
            CAST(f_agg.plan_qty AS INT) - ISNULL(f_agg.finished_qty, 0) AS 未完成数量,
            f_agg.min_finished_date AS 最早完成日期,
            f_agg.max_finished_date AS 最晚完成日期
        FROM
            [department2020].[dbo].[V_销售订单2] v
        INNER JOIN (
            SELECT
                a.OrderNumber,
                [dbo].[OP_RemoveChineseChars](b.OpExternalId) AS 工序,
                b.料品名称,
                b.生产车间,
                SUM(a.EachFinishedQty) AS finished_qty,
                SUM(b.计划产量) AS plan_qty,
                MIN(a.FinishedDate) AS min_finished_date,
                MAX(a.FinishedDate) AS max_finished_date
            FROM APS_FinishedQty_ST a
            LEFT JOIN 派工单 b
                ON a.JobExternalId = b.工单编号
            WHERE
                b.生产车间 = '锁体C车间'
                AND a.FinishedDate IS NOT NULL
            GROUP BY
                a.OrderNumber,
                [dbo].[OP_RemoveChineseChars](b.OpExternalId),
                b.生产车间,
                b.料品名称
        ) f_agg
            ON v.sheet_lot = f_agg.OrderNumber
        WHERE
            v.item_no NOT LIKE '115%'
            AND v.item_no NOT LIKE '116%'
        """
        params = []
        if 订单批号:
            sql += " AND v.sheet_lot LIKE ?"
            params.append(f"%{订单批号}%")
        if 料品编码:
            sql += " AND v.item_no LIKE ?"
            params.append(f"%{料品编码}%")
        if 料品名称:
            sql += " AND v.part_name LIKE ?"
            params.append(f"%{料品名称}%")
        if 工序:
            sql += " AND f_agg.工序 = ?"
            params.append(工序)
        if 交期开始:
            sql += " AND v.确定交期 >= ?"
            params.append(交期开始)
        if 交期结束:
            sql += " AND v.确定交期 <= ?"
            params.append(交期结束)
        sql += " ORDER BY v.确定交期, v.sheet_lot"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [{
            "客户": row[0] or "", "订单批号": row[1] or "", "确定交期": str(row[2])[:10] if row[2] else "",
            "生产车间": row[3] or "", "半成品料品名称": row[4] or "", "料品编码": row[5] or "",
            "料品名称": row[6] or "", "规格型号": row[7] or "", "工序": row[8] or "",
            "订单数量": int(row[9]) if row[9] else 0, "计划产量": float(row[10]) if row[10] else 0,
            "完成数量": float(row[11]) if row[11] else 0, "未完成数量": int(row[12]) if row[12] else 0,
            "最早完成日期": str(row[13])[:10] if row[13] else "",
            "最晚完成日期": str(row[14])[:10] if row[14] else "",
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
        if field == "工序":
            sql = """
            SELECT DISTINCT [dbo].[OP_RemoveChineseChars](b.OpExternalId) AS value
            FROM APS_FinishedQty_ST a
            LEFT JOIN 派工单 b ON a.JobExternalId = b.工单编号
            WHERE b.生产车间 = '锁体C车间'
              AND a.FinishedDate IS NOT NULL
              AND [dbo].[OP_RemoveChineseChars](b.OpExternalId) IS NOT NULL
              AND [dbo].[OP_RemoveChineseChars](b.OpExternalId) != ''
            ORDER BY value
            """
            cursor.execute(sql)
        else:
            return []
        return [{"value": row[0]} for row in cursor.fetchall()]
    finally:
        if conn:
            try: conn.close()
            except: pass

def get_detail_from_db(订单批号, 工序=None):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
        SELECT
            a.isCheck,
            a.iNo,
            b._Identify,
            b.生产车间,
            a.JobExternalId AS 工单编号,
            b.工单状态,
            a.OrderNumber AS 订单批号,
            b.订单数量,
            CASE
                WHEN pr.QtyPerCycle IS NOT NULL THEN pr.QtyPerCycle * 60.0
                WHEN d.capacity IS NOT NULL THEN CAST(d.capacity AS FLOAT)
                ELSE NULL
            END AS 理论产能,
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
            ) AS 理论工时,
            a.ItemExternalId AS 料品编码,
            a.ResName AS 生产线编号,
            a.ProductDescription AS 规格型号,
            a.emp_name AS 报工人,
            b.计划产量 AS 工单数量,
            a.EachFinishedQty AS 报工数量,
            a.scrapQty AS 报废数量,
            a.repairQty AS 返修数量,
            a.StartDate AS 开工时间,
            a.FinishedDate AS 完工时间,
            b.确定交期,
            [dbo].[OP_RemoveChineseChars](b.OpExternalId) AS 工序,
            b.客户
        FROM APS_FinishedQty_ST a
        JOIN 派工单 b
            ON a.JobExternalId = b.工单编号
        LEFT JOIN APS.APS_SUO.dbo.ProductRules pr
            ON a.ResName = pr.ResourceExternalId
            AND a.ItemExternalId = pr.ProductItemExternalId
        LEFT JOIN APS.APS_SUO.dbo.offline_process d
            ON b.OpExternalId = d.proccess
            AND a.ItemExternalId = d.item_no
        WHERE ISNULL(a.EachFinishedQty, 0) >= 0
          AND b.生产车间 LIKE '锁体C%'
          AND a.OrderNumber = ?
        """
        params = [订单批号]
        if 工序:
            sql += " AND [dbo].[OP_RemoveChineseChars](b.OpExternalId) = ?"
            params.append(工序)
        sql += " ORDER BY a.FinishedDate DESC"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        result = []
        for row in rows:
            item = {}
            for i, col in enumerate(cursor.description):
                val = row[i]
                if isinstance(val, datetime):
                    val = val.strftime('%Y-%m-%d %H:%M:%S')
                elif val is None:
                    val = ""
                item[col[0]] = val
            result.append(item)
        return result
    finally:
        if conn:
            try: conn.close()
            except: pass

@router.get("/lockCWorkProgress", summary="锁体C车间生产进度表-汇总")
async def get_summary(
    订单批号: Optional[str] = Query(None),
    料品编码: Optional[str] = Query(None),
    料品名称: Optional[str] = Query(None),
    工序: Optional[str] = Query(None),
    交期开始: Optional[str] = Query(None),
    交期结束: Optional[str] = Query(None),
):
    try:
        data = get_summary_from_db(订单批号, 料品编码, 料品名称, 工序, 交期开始, 交期结束)
        return {"status": "success", "data": data, "total_count": len(data)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")

@router.get("/lockCWorkProgress/options", summary="锁体C车间下拉选项")
async def get_options(field: str = Query(...)):
    try:
        return {"status": "success", "data": get_options_from_db(field)}
    except Exception as exc:
        return {"status": "success", "data": []}

@router.get("/lockCWorkProgress/detail", summary="锁体C车间生产进度表-详情")
async def get_detail(订单批号: str = Query(...), 工序: Optional[str] = Query(None)):
    try:
        data = get_detail_from_db(订单批号, 工序)
        return {"status": "success", "data": data, "total_count": len(data)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
