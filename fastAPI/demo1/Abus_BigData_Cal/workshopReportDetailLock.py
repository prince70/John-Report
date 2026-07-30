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

def fetch_rows(sql, params):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    return cursor.fetchall()

def build_b(rows):
    result = []
    for row in rows:
        理论产能 = float(row[8]) if row[8] else 0
        result.append({
            "是否核对": row[0] or "", "序列号": row[2] or "", "生产车间": row[3] or "",
            "工单编号": row[4] or "", "工单状态": row[5] or "", "订单批号": row[6] or "",
            "订单数量": float(row[7]) if row[7] else 0, "料品编码": row[10] or "",
            "生产线编号": row[11] or "", "规格型号": row[12] or "", "报工人": row[13] or "",
            "工单数量": float(row[14]) if row[14] else 0, "报工数量": float(row[15]) if row[15] else 0,
            "报废数量": float(row[16]) if row[16] else 0, "返修数量": float(row[17]) if row[17] else 0,
            "车间提供": 理论产能,
            "时间": float(row[9]) if row[9] else (round((float(row[15] or 0) + float(row[17] or 0) + float(row[16] or 0)) / 理论产能, 2) if 理论产能 != 0 else None),
            "开工时间": str(row[18]) if row[18] else "", "完工时间": str(row[19]) if row[19] else "",
            "确定交期": row[20] or "", "工序": row[22] or "", "客户": row[21] or "",
            "急货": row[23] or "",
        })
    return result

build_a = build_b

def build_material(rows):
    result = []
    for row in rows:
        理论产能 = float(row[8]) if row[8] else 0
        result.append({
            "是否核对": row[0] or "", "序列号": row[2] or "", "生产车间": row[3] or "",
            "工单编号": row[4] or "", "工单状态": row[5] or "", "订单批号": row[6] or "",
            "订单数量": float(row[7]) if row[7] else 0, "料品编码": row[10] or "",
            "生产线编号": row[11] or "", "规格型号": row[12] or "", "报工人": row[13] or "",
            "工单数量": float(row[14]) if row[14] else 0, "报工数量": float(row[15]) if row[15] else 0,
            "报废数量": float(row[16]) if row[16] else 0, "返修数量": float(row[17]) if row[17] else 0,
            "车间提供": 理论产能,
            "时间": round((float(row[15] or 0) + float(row[17] or 0) + float(row[16] or 0)) / 理论产能, 2) if 理论产能 != 0 else None,
            "开工时间": str(row[18]) if row[18] else "", "完工时间": str(row[19]) if row[19] else "",
            "用料规格": row[20] or "",
        })
    return result

def build_zhuangqian(rows):
    result = []
    for row in rows:
        理论产能 = float(row[8]) if row[8] else 0
        result.append({
            "是否核对": row[0] or "", "序列号": row[2] or "", "生产车间": row[3] or "",
            "工单编号": row[4] or "", "工单状态": row[5] or "", "订单批号": row[6] or "",
            "订单数量": float(row[7]) if row[7] else 0, "料品编码": row[10] or "",
            "生产线编号": row[11] or "", "料品名称": row[12] or "", "规格型号": row[13] or "",
            "报工人": row[14] or "", "工单数量": float(row[15]) if row[15] else 0,
            "报工数量": float(row[16]) if row[16] else 0, "报废数量": float(row[17]) if row[17] else 0,
            "返修数量": float(row[18]) if row[18] else 0,
            "车间提供": 理论产能,
            "时间": float(row[9]) if row[9] else None,
            "开工时间": str(row[19]) if row[19] else "", "完工时间": str(row[20]) if row[20] else "",
            "确定交期": row[21] or "", "客户": row[22] or "", "工序": row[23] or "",
        })
    return result

def build_suoliang(rows):
    result = []
    for row in rows:
        理论产能 = float(row[8]) if row[8] else 0
        result.append({
            "是否核对": row[0] or "", "序列号": row[2] or "", "生产车间": row[3] or "",
            "工单编号": row[4] or "", "工单状态": row[5] or "", "订单批号": row[6] or "",
            "订单数量": float(row[7]) if row[7] else 0, "料品编码": row[10] or "",
            "生产线编号": row[11] or "", "规格型号": row[12] or "", "报工人": row[13] or "",
            "工单数量": float(row[14]) if row[14] else 0, "报工数量": float(row[15]) if row[15] else 0,
            "报工重量": float(row[16]) if row[16] else 0,
            "报废数量": float(row[17]) if row[17] else 0, "返修数量": float(row[18]) if row[18] else 0,
            "车间提供": 理论产能,
            "时间": float(row[9]) if row[9] else None,
            "开工时间": str(row[19]) if row[19] else "", "完工时间": str(row[20]) if row[20] else "",
            "确定交期": row[21] or "", "客户": row[22] or "", "工序": row[23] or "",
            "急货": row[24] or "",
        })
    return result

def build_c(rows):
    result = []
    for row in rows:
        理论产能 = float(row[8]) if row[8] else 0
        result.append({
            "是否核对": row[0] or "", "序列号": row[2] or "", "生产车间": row[3] or "",
            "工单编号": row[4] or "", "工单状态": row[5] or "", "订单批号": row[6] or "",
            "订单数量": float(row[7]) if row[7] else 0, "料品编码": row[10] or "",
            "生产线编号": row[11] or "", "规格型号": row[12] or "", "报工人": row[13] or "",
            "工单数量": float(row[14]) if row[14] else 0, "报工数量": float(row[15]) if row[15] else 0,
            "报废数量": float(row[16]) if row[16] else 0, "返修数量": float(row[17]) if row[17] else 0,
            "车间提供": 理论产能,
            "时间": float(row[9]) if row[9] else None,
            "开工时间": str(row[18]) if row[18] else "", "完工时间": str(row[19]) if row[19] else "",
            "确定交期": row[20] or "", "工序": row[21] or "", "客户": row[22] or "",
            "急货": row[23] or "",
        })
    return result

def build_d(rows):
    result = []
    for row in rows:
        理论产能 = float(row[8]) if row[8] else 0
        result.append({
            "是否核对": row[0] or "", "序列号": row[2] or "", "生产车间": row[3] or "",
            "工单编号": row[4] or "", "工单状态": row[5] or "", "订单批号": row[6] or "",
            "订单数量": float(row[7]) if row[7] else 0, "料品编码": row[10] or "",
            "生产线编号": row[11] or "", "规格型号": row[12] or "", "报工人": row[13] or "",
            "工单数量": float(row[14]) if row[14] else 0, "报工数量": float(row[15]) if row[15] else 0,
            "报废数量": float(row[17]) if row[17] else 0, "返修数量": float(row[18]) if row[18] else 0,
            "车间提供": 理论产能,
            "时间": round((float(row[15] or 0) + float(row[18] or 0) + float(row[17] or 0)) / 理论产能, 2) if 理论产能 != 0 else None,
            "开工时间": str(row[19]) if row[19] else "", "完工时间": str(row[20]) if row[20] else "",
            "确定交期": row[21] or "", "工序": row[23] or "", "客户": row[22] or "",
            "急货": row[24] or "",
        })
    return result

SQL_A = """
SELECT a.isCheck, a.iNo, b._Identify, b.生产车间,
a.JobExternalId AS 工单编号, b.工单状态, a.OrderNumber AS 订单批号, b.订单数量,
cap.理论产能,
CAST((ISNULL(a.EachFinishedQty, 0) + ISNULL(a.repairQty, 0) + ISNULL(a.scrapQty, 0))
    / NULLIF(cap.理论产能, 0) AS DECIMAL(18, 1)) AS 理论工时,
a.ItemExternalId AS 料品编码, a.ResName AS 生产线编号, a.ProductDescription AS 规格型号,
a.emp_name AS 报工人, b.计划产量 AS 工单数量, a.EachFinishedQty AS 报工数量,
a.scrapQty AS 报废数量, a.repairQty AS 返修数量,
a.StartDate AS 开工时间, a.FinishedDate AS 完工时间, b.确定交期,
b.OpExternalId AS 工序, b.客户, a.urgent
FROM APS_FinishedQty_ST a
JOIN 派工单 b ON a.JobExternalId = b.工单编号
LEFT JOIN APS.APS_SUO.dbo.ProductRules pr
    ON a.ResName = pr.ResourceExternalId AND a.ItemExternalId = pr.ProductItemExternalId
LEFT JOIN APS.APS_SUO.dbo.offline_process d
    ON b.OpExternalId = d.proccess AND a.ItemExternalId = d.item_no
CROSS APPLY (
    SELECT CASE WHEN pr.QtyPerCycle IS NOT NULL THEN pr.QtyPerCycle * 60.0
                WHEN d.capacity IS NOT NULL THEN CAST(d.capacity AS FLOAT) ELSE NULL END AS 理论产能
) AS cap
WHERE (
    (ISNULL(a.EachFinishedQty, 0) >= 0 AND b.生产车间 LIKE '锁体A%')
    OR (ISNULL(a.EachFinishedQty, 0) >= 0 AND b.生产车间 LIKE '锁体B%' AND b.OpExternalId LIKE '锁体A%')
    OR (ISNULL(a.EachFinishedQty, 0) >= 0 AND b.生产车间 LIKE '锁体C%' AND b.OpExternalId LIKE '锁体A%')
)
AND NOT (ISNULL(a.EachFinishedQty, 0) >= 0 AND b.生产车间 LIKE '锁体A%' AND b.OpExternalId LIKE '%锁体B%')
AND a.FinishedDate between ? and ?
"""

SQL_SUOLIANG = """
select a.isCheck, a.iNo, b._Identify, b.生产车间, a.JobExternalId as 工单编号, b.工单状态,
a.OrderNumber as 订单批号, b.订单数量,
(60*pr.QtyPerCycle) as 理论产能,
CAST((isnull(a.EachFinishedQty,0)+isnull(a.repairQty,0)+isnull(a.scrapQty,0))/(60*pr.QtyPerCycle) AS DECIMAL(18,1)) as 理论工时,
a.ItemExternalId as 料品编码, a.ResName as 生产线编号, a.ProductDescription as 规格型号,
a.emp_name as 报工人, b.计划产量 as 工单数量, a.EachFinishedQty as 报工数量,
a.EachFinishedQtykg as 报工重量, a.scrapQty as 报废数量, a.repairQty as 返修数量,
a.StartDate as 开工时间, a.FinishedDate as 完工时间, b.确定交期, b.客户, b.OpExternalId, a.urgent
from APS_FinishedQty_SL a
join 派工单 b on a.JobExternalId = b.工单编号
left join APS.APS_SUO.dbo.ProductRules pr
    on a.ResName = pr.ResourceExternalId and a.ItemExternalId = pr.ProductItemExternalId
where isnull(a.EachFinishedQty,0) > 0 and b.生产车间 = '锁梁车间'
and a.FinishedDate between ? and ?
"""

SQL_B = """
select a.isCheck, a.iNo, b._Identify, b.生产车间, a.JobExternalId as 工单编号, b.工单状态,
a.OrderNumber as 订单批号, b.订单数量,
(60*pr.QtyPerCycle) as 理论产能,
CAST((isnull(a.EachFinishedQty,0)+isnull(a.repairQty,0)+isnull(a.scrapQty,0))/(60*pr.QtyPerCycle) AS DECIMAL(18,1)) as 理论工时,
a.ItemExternalId as 料品编码, a.ResName as 生产线编号, a.ProductDescription as 规格型号,
a.emp_name as 报工人, b.计划产量 as 工单数量, a.EachFinishedQty as 报工数量,
a.scrapQty as 报废数量, a.repairQty as 返修数量, b.确定交期, a.StartDate as 开工时间,
a.FinishedDate as 完工时间, b.客户, b.OpExternalId, a.urgent
from APS_FinishedQty_ST a
join 派工单 b on a.JobExternalId = b.工单编号
left join APS.APS_SUO.dbo.ProductRules pr
    on a.ResName = pr.ResourceExternalId and a.ItemExternalId = pr.ProductItemExternalId
where ((isnull(a.EachFinishedQty,0) >=0 and b.生产车间 like '锁体B%')
  and NOT (isnull(a.EachFinishedQty,0) >=0 and b.生产车间 like '锁体B%' and b.OpExternalId like '锁体A%')
  or (isnull(a.EachFinishedQty,0) >=0 and b.生产车间 like '锁体A%' and b.OpExternalId like '%锁体B%'))
and a.FinishedDate between ? and ?
"""

SQL_C = """
SELECT a.isCheck, a.iNo, b._Identify, b.生产车间,
a.JobExternalId AS 工单编号, b.工单状态, a.OrderNumber AS 订单批号, b.订单数量,
CASE WHEN pr.QtyPerCycle IS NOT NULL THEN pr.QtyPerCycle * 60.0
     WHEN d.capacity IS NOT NULL THEN CAST(d.capacity AS FLOAT) ELSE NULL END AS 理论产能,
CAST((ISNULL(a.EachFinishedQty, 0) + ISNULL(a.repairQty, 0) + ISNULL(a.scrapQty, 0))
    / NULLIF(CASE WHEN pr.QtyPerCycle IS NOT NULL THEN pr.QtyPerCycle * 60.0
                  WHEN d.capacity IS NOT NULL THEN CAST(d.capacity AS FLOAT) ELSE NULL END, 0)
    AS DECIMAL(18, 1)) AS 理论工时,
a.ItemExternalId AS 料品编码, a.ResName AS 生产线编号, a.ProductDescription AS 规格型号,
a.emp_name AS 报工人, b.计划产量 AS 工单数量, a.EachFinishedQty AS 报工数量,
a.scrapQty AS 报废数量, a.repairQty AS 返修数量,
a.StartDate AS 开工时间, a.FinishedDate AS 完工时间, b.确定交期,
b.OpExternalId AS 工序, b.客户, a.urgent
FROM APS_FinishedQty_ST a
JOIN 派工单 b ON a.JobExternalId = b.工单编号
LEFT JOIN APS.APS_SUO.dbo.ProductRules pr
    ON a.ResName = pr.ResourceExternalId AND a.ItemExternalId = pr.ProductItemExternalId
LEFT JOIN APS.APS_SUO.dbo.offline_process d
    ON b.OpExternalId = d.proccess AND a.ItemExternalId = d.item_no
WHERE ISNULL(a.EachFinishedQty, 0) >= 0 AND b.生产车间 LIKE '锁体C%'
AND a.FinishedDate between ? and ?
"""

SQL_D = """
select a.isCheck, a.iNo, b._Identify, b.生产车间, a.JobExternalId as 工单编号, b.工单状态,
a.OrderNumber as 订单批号, b.订单数量,
(60*pr.QtyPerCycle) as 理论产能,
CAST((isnull(a.EachFinishedQty,0)+isnull(a.repairQty,0)+isnull(a.scrapQty,0))/(60*pr.QtyPerCycle) AS DECIMAL(18,1)) as 理论工时,
a.ItemExternalId as 料品编码, a.ResName as 生产线编号, a.ProductDescription as 规格型号,
a.emp_name as 报工人, b.计划产量 as 工单数量, a.EachFinishedQty as 报工数量,
a.EachFinishedQtykg as 报工重量, a.scrapQty as 报废数量, a.repairQty as 返修数量,
a.StartDate as 开工时间, a.FinishedDate as 完工时间, b.确定交期, b.客户, b.OpExternalId, a.urgent
from APS_FinishedQty_ST a
join 派工单 b on a.JobExternalId = b.工单编号
left join APS.APS_SUO.dbo.ProductRules pr
    on a.ResName = pr.ResourceExternalId and a.ItemExternalId = pr.ProductItemExternalId
where isnull(a.EachFinishedQty,0) >=0 and b.生产车间 like '锁体D%'
and a.FinishedDate between ? and ?
"""

SQL_MATERIAL = """
select a.isCheck, a.iNo, b._Identify, b.生产车间, a.JobExternalId as 工单编号, b.工单状态,
a.OrderNumber as 订单批号, b.订单数量,
(60*pr.QtyPerCycle) as 理论产能,
CAST((isnull(a.EachFinishedQty,0)+isnull(a.repairQty,0)+isnull(a.scrapQty,0))/(60*pr.QtyPerCycle) AS DECIMAL(18,1)) as 理论工时,
a.ItemExternalId as 料品编码, a.ResName as 生产线编号, a.ProductDescription as 规格型号,
a.emp_name as 报工人, b.计划产量 as 工单数量, a.EachFinishedQty as 报工数量,
a.scrapQty as 报废数量, a.repairQty as 返修数量,
a.StartDate as 开工时间, a.FinishedDate as 完工时间, b.general_name
from APS_FinishedQty_ST a
join 派工单 b on a.JobExternalId = b.工单编号
left join APS.APS_SUO.dbo.ProductRules pr
    on a.ResName = pr.ResourceExternalId and a.ItemExternalId = pr.ProductItemExternalId
where isnull(a.EachFinishedQty,0) > 0 and b.生产车间 = '开料车间'
and a.FinishedDate between ? and ?
"""

SQL_ZHUANGQIAN = """
select a.isCheck, a.iNo, b._Identify, b.生产车间, a.JobExternalId as 工单编号, b.工单状态,
a.OrderNumber as 订单批号, b.订单数量,
(60*pr.QtyPerCycle) as 理论产能,
CAST((isnull(a.EachFinishedQty,0)+isnull(a.repairQty,0)+isnull(a.scrapQty,0))/(60*pr.QtyPerCycle) AS DECIMAL(18,1)) as 理论工时,
a.ItemExternalId as 料品编码, a.ResName as 生产线编号, b.料品名称, a.ProductDescription as 规格型号,
a.emp_name as 报工人, b.计划产量 as 工单数量, a.EachFinishedQty as 报工数量,
a.scrapQty as 报废数量, a.repairQty as 返修数量,
a.StartDate as 开工时间, a.FinishedDate as 完工时间, b.确定交期, b.客户, b.OpExternalId
from APS_FinishedQty a
join 派工单 b on a.JobExternalId = b.工单编号
left join APS.APS_SUO.dbo.ProductRules pr
    on a.ResName = pr.ResourceExternalId and a.ItemExternalId = pr.ProductItemExternalId
where isnull(a.EachFinishedQty,0) >= 0 and b.锁类分区 in ('铝门锁区','胆仔锁区','功能锁区')
and a.FinishedDate between ? and ?
"""

def build_damo(rows):
    result = []
    for row in rows:
        理论产能 = float(row[9]) if row[9] else 0
        result.append({
            "是否核对": row[0] or "", "序列号": row[2] or "", "生产车间": row[3] or "",
            "工单编号": row[4] or "", "工单状态": row[5] or "", "订单批号": row[6] or "",
            "确定交期": row[7] or "", "订单数量": float(row[8]) if row[8] else 0,
            "料品编码": row[11] or "", "生产线编号": row[12] or "",
            "规格型号": row[13] or "", "报工人": row[14] or "",
            "工单数量": float(row[15]) if row[15] else 0, "报工数量": float(row[16]) if row[16] else 0,
            "报废数量": float(row[17]) if row[17] else 0, "返修数量": float(row[18]) if row[18] else 0,
            "车间提供": 理论产能,
            "时间": round((float(row[16] or 0) + float(row[18] or 0) + float(row[17] or 0)) / 理论产能, 2) if 理论产能 != 0 else None,
            "开工时间": str(row[19]) if row[19] else "", "完工时间": str(row[20]) if row[20] else "",
            "客户": row[21] or "", "工序": row[22] or "",
        })
    return result

def build_damo_dm(rows):
    result = []
    for row in rows:
        理论产能 = float(row[9]) if row[9] else 0
        result.append({
            "是否核对": row[0] or "", "序列号": row[2] or "", "生产车间": row[3] or "",
            "工单编号": row[4] or "", "工单状态": row[5] or "", "订单批号": row[6] or "",
            "确定交期": row[7] or "", "订单数量": float(row[8]) if row[8] else 0,
            "料品编码": row[11] or "", "料品名称": row[12] or "",
            "生产线编号": row[13] or "", "规格型号": row[14] or "",
            "报工人": row[15] or "", "工单数量": float(row[16]) if row[16] else 0,
            "报工数量": float(row[17]) if row[17] else 0, "报废数量": float(row[18]) if row[18] else 0,
            "返修数量": float(row[19]) if row[19] else 0,
            "车间提供": 理论产能,
            "时间": round((float(row[17] or 0) + float(row[19] or 0) + float(row[18] or 0)) / 理论产能, 2) if 理论产能 != 0 else None,
            "开工时间": str(row[20]) if row[20] else "", "完工时间": str(row[21]) if row[21] else "",
            "客户": row[22] or "", "工序": row[23] or "",
            "急货": row[24] or "",
        })
    return result

SQL_DAMO = """
select a.isCheck, a.iNo, b._Identify, b.生产车间, a.JobExternalId as 工单编号, b.工单状态,
a.OrderNumber as 订单批号, b.确定交期, b.订单数量,
(60*pr.QtyPerCycle) as 理论产能,
CAST((isnull(a.EachFinishedQty,0)+isnull(a.repairQty,0)+isnull(a.scrapQty,0))/(60*pr.QtyPerCycle) AS DECIMAL(18,1)) as 理论工时,
a.ItemExternalId as 料品编码, a.ResName as 生产线编号, a.ProductDescription as 规格型号,
a.emp_name as 报工人, b.计划产量 as 工单数量, a.EachFinishedQty as 报工数量,
a.scrapQty as 报废数量, a.repairQty as 返修数量,
a.StartDate as 开工时间, a.FinishedDate as 完工时间, b.客户, b.OpExternalId
from APS_FinishedQty a
join 派工单 b on a.JobExternalId = b.工单编号
left join APS.APS_SUO.dbo.ProductRules pr
    on a.ResName = pr.ResourceExternalId and a.ItemExternalId = pr.ProductItemExternalId
where isnull(a.EachFinishedQty,0) > 0 and b.锁类分区 in ('普通挂锁区')
and a.FinishedDate between ? and ?
"""

SQL_DAMO_DM = """
select a.isCheck, a.iNo, b._Identify, b.生产车间, a.JobExternalId as 工单编号, b.工单状态,
a.OrderNumber as 订单批号, b.确定交期, b.订单数量,
(60*pr.QtyPerCycle) as 理论产能,
CAST((isnull(a.EachFinishedQty,0)+isnull(a.repairQty,0)+isnull(a.scrapQty,0))/(60*pr.QtyPerCycle) AS DECIMAL(18,1)) as 理论工时,
a.ItemExternalId as 料品编码, b.料品名称, a.ResName as 生产线编号, a.ProductDescription as 规格型号,
a.emp_name as 报工人, b.计划产量 as 工单数量, a.EachFinishedQty as 报工数量,
a.scrapQty as 报废数量, a.repairQty as 返修数量,
a.StartDate as 开工时间, a.FinishedDate as 完工时间, b.客户, b.OpExternalId, a.urgent
from APS_FinishedQty_DM a
join 派工单 b on a.JobExternalId = b.工单编号
left join APS.APS_SUO.dbo.ProductRules pr
    on a.ResName = pr.ResourceExternalId and a.ItemExternalId = pr.ProductItemExternalId
where isnull(a.EachFinishedQty,0) > 0 and b.生产车间 = '打磨车间-打磨区'
and a.FinishedDate between ? and ?
"""

def _query_damo_dm(start, end, 序列号, 姓名, 规格型号, 工序, 生产线编号, 工单批号):
    try:
        extra = ""
        params = [start, end]
        if 序列号:
            extra += " AND b._Identify LIKE ?"
            params.append(f"%{序列号}%")
        if 姓名:
            extra += " AND a.emp_name LIKE ?"
            params.append(f"%{姓名}%")
        if 规格型号:
            extra += " AND a.ProductDescription LIKE ?"
            params.append(f"%{规格型号}%")
        if 工序:
            extra += " AND b.OpExternalId LIKE ?"
            params.append(f"%{工序}%")
        if 生产线编号:
            extra += " AND a.ResName LIKE ?"
            params.append(f"%{生产线编号}%")
        if 工单批号:
            extra += " AND a.OrderNumber LIKE ?"
            params.append(f"%{工单批号}%")
        final_sql = SQL_DAMO_DM + extra + " ORDER BY b.订单批号"
        rows = fetch_rows(final_sql, params)
        data = build_damo_dm(rows)
        return {"status": "success", "data": data, "total_count": len(data)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")

def _query_damo(start, end, 序列号, 姓名, 生产线编号, 工单批号):
    try:
        extra = ""
        params = [start, end]
        if 序列号:
            extra += " AND b._Identify LIKE ?"
            params.append(f"%{序列号}%")
        if 姓名:
            extra += " AND a.emp_name LIKE ?"
            params.append(f"%{姓名}%")
        if 生产线编号:
            extra += " AND a.ResName LIKE ?"
            params.append(f"%{生产线编号}%")
        if 工单批号:
            extra += " AND a.OrderNumber LIKE ?"
            params.append(f"%{工单批号}%")
        final_sql = SQL_DAMO + extra + " ORDER BY b.订单批号"
        rows = fetch_rows(final_sql, params)
        data = build_damo(rows)
        return {"status": "success", "data": data, "total_count": len(data)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")

def _query_zhuangqian(start, end, 序列号, 姓名, 工单批号, 锁类分区, 含TSA):
    try:
        extra = ""
        params = [start, end]
        if 序列号:
            extra += " AND b._Identify LIKE ?"
            params.append(f"%{序列号}%")
        if 姓名:
            extra += " AND a.emp_name LIKE ?"
            params.append(f"%{姓名}%")
        if 工单批号:
            extra += " AND a.OrderNumber LIKE ?"
            params.append(f"%{工单批号}%")
        if 锁类分区:
            extra += " AND b.锁类分区 LIKE ?"
            params.append(f"%{锁类分区}%")
        if not 含TSA:
            extra += " AND b.料品名称 <> 'TSA006'"
        final_sql = SQL_ZHUANGQIAN + extra + " ORDER BY b.订单批号"
        rows = fetch_rows(final_sql, params)
        data = build_zhuangqian(rows)
        return {"status": "success", "data": data, "total_count": len(data)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")

def _query_workshop(sql, build_fn, start, end, 序列号, 姓名, 订单批号):
    try:
        extra = ""
        params = [start, end]
        if 序列号:
            extra += " AND b._Identify LIKE ?"
            params.append(f"%{序列号}%")
        if 姓名:
            extra += " AND a.emp_name LIKE ?"
            params.append(f"%{姓名}%")
        if 订单批号:
            extra += " AND a.OrderNumber LIKE ?"
            params.append(f"%{订单批号}%")
        final_sql = sql + extra + " ORDER BY b.订单批号"
        rows = fetch_rows(final_sql, params)
        data = build_fn(rows)
        return {"status": "success", "data": data, "total_count": len(data)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")

def _query_material(sql, build_fn, start, end, 序列号, 姓名, 工单编号):
    try:
        extra = ""
        params = [start, end]
        if 序列号:
            extra += " AND b._Identify LIKE ?"
            params.append(f"%{序列号}%")
        if 姓名:
            extra += " AND a.emp_name LIKE ?"
            params.append(f"%{姓名}%")
        if 工单编号:
            extra += " AND a.JobExternalId LIKE ?"
            params.append(f"%{工单编号}%")
        final_sql = sql + extra + " ORDER BY b.订单批号"
        rows = fetch_rows(final_sql, params)
        data = build_fn(rows)
        return {"status": "success", "data": data, "total_count": len(data)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")

@router.get("/workshopReportDetail/LockB", summary="锁体B报工详情")
async def lock_b(start: str = Query(...), end: str = Query(...), 序列号: Optional[str] = None, 姓名: Optional[str] = None, 订单批号: Optional[str] = None):
    return _query_workshop(SQL_B, build_b, start, end, 序列号, 姓名, 订单批号)

@router.get("/workshopReportDetail/LockC", summary="锁体C报工详情")
async def lock_c(start: str = Query(...), end: str = Query(...), 序列号: Optional[str] = None, 姓名: Optional[str] = None, 订单批号: Optional[str] = None):
    return _query_workshop(SQL_C, build_c, start, end, 序列号, 姓名, 订单批号)

@router.get("/workshopReportDetail/LockD", summary="锁体D报工详情")
async def lock_d(start: str = Query(...), end: str = Query(...), 序列号: Optional[str] = None, 姓名: Optional[str] = None, 订单批号: Optional[str] = None):
    return _query_workshop(SQL_D, build_d, start, end, 序列号, 姓名, 订单批号)

@router.get("/workshopReportDetail/LockA", summary="锁体A报工详情")
async def lock_a(start: str = Query(...), end: str = Query(...), 序列号: Optional[str] = None, 姓名: Optional[str] = None, 订单批号: Optional[str] = None):
    return _query_workshop(SQL_A, build_a, start, end, 序列号, 姓名, 订单批号)

@router.get("/workshopReportDetail/Suoliang", summary="锁梁报工详情")
async def suoliang(start: str = Query(...), end: str = Query(...), 序列号: Optional[str] = None, 姓名: Optional[str] = None, 订单批号: Optional[str] = None):
    return _query_workshop(SQL_SUOLIANG, build_suoliang, start, end, 序列号, 姓名, 订单批号)

@router.get("/workshopReportDetail/Material", summary="开料车间报工详情")
async def material(start: str = Query(...), end: str = Query(...), 工单编号: Optional[str] = None, 序列号: Optional[str] = None, 姓名: Optional[str] = None):
    return _query_material(SQL_MATERIAL, build_material, start, end, 序列号, 姓名, 工单编号)

@router.get("/workshopReportDetail/Zhuangqian", summary="装嵌报工详情")
async def zhuangqian(start: str = Query(...), end: str = Query(...), 序列号: Optional[str] = None, 姓名: Optional[str] = None, 工单批号: Optional[str] = None, 锁类分区: Optional[str] = None, 含TSA: bool = False):
    return _query_zhuangqian(start, end, 序列号, 姓名, 工单批号, 锁类分区, 含TSA)

@router.get("/workshopReportDetail/Damo", summary="打磨-装配区报工详情")
async def damo(start: str = Query(...), end: str = Query(...), 序列号: Optional[str] = None, 姓名: Optional[str] = None, 生产线编号: Optional[str] = None, 工单批号: Optional[str] = None):
    return _query_damo(start, end, 序列号, 姓名, 生产线编号, 工单批号)

@router.get("/workshopReportDetail/DamoDM", summary="打磨-打磨区报工详情")
async def damo_dm(start: str = Query(...), end: str = Query(...), 序列号: Optional[str] = None, 姓名: Optional[str] = None, 规格型号: Optional[str] = None, 工序: Optional[str] = None, 生产线编号: Optional[str] = None, 工单批号: Optional[str] = None):
    return _query_damo_dm(start, end, 序列号, 姓名, 规格型号, 工序, 生产线编号, 工单批号)
