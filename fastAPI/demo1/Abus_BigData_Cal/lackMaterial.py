from fastapi import APIRouter, HTTPException, Query
from pydantic_settings import BaseSettings
from typing import Optional
import os
import pyodbc
from datetime import datetime
from collections import defaultdict
from fastapi_cache.decorator import cache

router = APIRouter()

class Settings(BaseSettings):
    db_server: str = os.getenv("DB_SERVER", "192.168.10.200")
    db_database: str = os.getenv("DB_DATABASE", "APS_Result")
    db_username: str = os.getenv("DB_USERNAME", "sa")
    db_password: str = os.getenv("DB_PASSWORD", "5tgb^YHN7ujm*IK<")

auth_settings = Settings()

def get_db_connection():
    conn_str = (
        f"DRIVER={{SQL Server}};SERVER={auth_settings.db_server};DATABASE={auth_settings.db_database};"
        f"UID={auth_settings.db_username};PWD={auth_settings.db_password};"
    )
    try:
        return pyodbc.connect(conn_str)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"数据库连接失败: {exc}")

def get_lack_material_data_from_db(product_series=None, product_desc=None, start_date=None, end_date=None):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        SELECT [PublishDate]
              ,[资源名称]
              ,[NeedDateTime]
              ,[工单数量]
              ,[产品名称]
              , CASE WHEN CHARINDEX('/', [产品名称]) > 0 THEN LEFT([产品名称], CHARINDEX('/', [产品名称]) - 1) ELSE [产品名称] END AS 产品系列
              ,[ScheduledStartDate]
              ,[JobExternalId]
              ,[MoExternalId]
              ,[OpExternalId]
              ,[WarehouseExternalId]
              ,[OrderNumber]
              ,[Customer]
              ,[确定交期]
              ,[产品描述]
              ,[ItemExternalId]
              ,[Name]
              ,[Description]
              ,[TotalRequiredQty]
              ,[IssuedQty]
              ,[Qty_in_APS]
              ,[Qty_in_ERP]
              ,[LackQty]
              ,[vFactory]
        FROM [APS_Result].[dbo].[V_JobLackMaterial7Days111] a
        WHERE 1=1
        """
        params = []
        if product_series:
            sql += " AND (CASE WHEN CHARINDEX('/', [产品名称]) > 0 THEN LEFT([产品名称], CHARINDEX('/', [产品名称]) - 1) ELSE [产品名称] END) LIKE ?"
            params.append(f"%{product_series}%")
        if product_desc:
            sql += " AND [产品描述] LIKE ?"
            params.append(f"%{product_desc}%")
        if start_date:
            sql += " AND CAST([ScheduledStartDate] AS DATE) >= ?"
            params.append(start_date)
        if end_date:
            sql += " AND CAST([ScheduledStartDate] AS DATE) <= ?"
            params.append(end_date)

        sql += " ORDER BY a.LackQty DESC"

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        raw_data = []
        for row in rows:
            raw_data.append({
                "PublishDate": str(row[0]) if row[0] else "",
                "资源名称": row[1] if row[1] else "",
                "NeedDateTime": str(row[2]) if row[2] else "",
                "工单数量": float(row[3]) if row[3] else 0,
                "产品名称": row[4] if row[4] else "",
                "产品系列": row[5] if row[5] else "",
                "ScheduledStartDate": str(row[6]) if row[6] else "",
                "JobExternalId": row[7] if row[7] else "",
                "MoExternalId": row[8] if row[8] else "",
                "OpExternalId": row[9] if row[9] else "",
                "WarehouseExternalId": row[10] if row[10] else "",
                "OrderNumber": row[11] if row[11] else "",
                "Customer": row[12] if row[12] else "",
                "确定交期": str(row[13]) if row[13] else "",
                "产品描述": row[14] if row[14] else "",
                "ItemExternalId": row[15] if row[15] else "",
                "Name": row[16] if row[16] else "",
                "Description": row[17] if row[17] else "",
                "TotalRequiredQty": float(row[18]) if row[18] else 0,
                "IssuedQty": float(row[19]) if row[19] else 0,
                "Qty_in_APS": float(row[20]) if row[20] else 0,
                "Qty_in_ERP": float(row[21]) if row[21] else 0,
                "LackQty": float(row[22]) if row[22] else 0,
                "vFactory": row[23] if row[23] else ""
            })

        return raw_data

    except Exception as exc:
        raise exc
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

@router.get("/lackMaterial", summary="各车间欠料数据")
@cache(expire=1800)
async def get_lack_material(
    product_series: Optional[str] = Query(None, description="产品系列（模糊查询）"),
    product_desc: Optional[str] = Query(None, description="规格型号（模糊查询）"),
    start_date: Optional[str] = Query(None, description="计划开始日期-开始"),
    end_date: Optional[str] = Query(None, description="计划开始日期-结束")
):
    try:
        raw_data = get_lack_material_data_from_db(product_series, product_desc, start_date, end_date)

        workshop_summary = defaultdict(float)
        for item in raw_data:
            workshop = item["vFactory"] if item["vFactory"] else "未知车间"
            workshop_summary[workshop] += item["LackQty"]

        pie_data = [
            {"name": workshop, "value": round(qty, 2)}
            for workshop, qty in sorted(workshop_summary.items(), key=lambda x: x[1], reverse=True)
        ]

        return {
            "status": "success",
            "data": {
                "pie": pie_data,
                "details": raw_data,
                "total_count": len(raw_data)
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as exc:
        print(f"获取各车间欠料数据失败: {exc}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")

@router.get("/lackMaterial/suggestions", summary="各车间欠料筛选建议")
@cache(expire=1800)
async def get_suggestions(
    field: str = Query(..., description="字段名: product_series 或 product_desc"),
    q: str = Query("", description="搜索关键词")
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if field == "product_series":
            sql = """
            SELECT DISTINCT TOP 50
                CASE WHEN CHARINDEX('/', [产品名称]) > 0 THEN LEFT([产品名称], CHARINDEX('/', [产品名称]) - 1) ELSE [产品名称] END AS value
            FROM [APS_Result].[dbo].[V_JobLackMaterial7Days111]
            WHERE (CASE WHEN CHARINDEX('/', [产品名称]) > 0 THEN LEFT([产品名称], CHARINDEX('/', [产品名称]) - 1) ELSE [产品名称] END) LIKE ?
            AND (CASE WHEN CHARINDEX('/', [产品名称]) > 0 THEN LEFT([产品名称], CHARINDEX('/', [产品名称]) - 1) ELSE [产品名称] END) IS NOT NULL
            AND (CASE WHEN CHARINDEX('/', [产品名称]) > 0 THEN LEFT([产品名称], CHARINDEX('/', [产品名称]) - 1) ELSE [产品名称] END) != ''
            """
            cursor.execute(sql, (f"%{q}%",))
        elif field == "product_desc":
            sql = """
            SELECT DISTINCT TOP 50 [产品描述] AS value
            FROM [APS_Result].[dbo].[V_JobLackMaterial7Days111]
            WHERE [产品描述] LIKE ?
            AND [产品描述] IS NOT NULL
            AND [产品描述] != ''
            """
            cursor.execute(sql, (f"%{q}%",))
        else:
            raise HTTPException(status_code=400, detail="无效的字段名")

        suggestions = [{"value": row[0]} for row in cursor.fetchall()]

        return {
            "status": "success",
            "data": suggestions
        }

    except Exception as exc:
        print(f"获取筛选建议失败: {exc}")
        return {
            "status": "success",
            "data": []
        }
    finally:
        try:
            conn.close()
        except:
            pass
