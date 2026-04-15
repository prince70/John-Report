from fastapi import APIRouter, HTTPException
from pydantic_settings import BaseSettings
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
import os
import pandas as pd
import pyodbc
from datetime import datetime

router = APIRouter()

class Settings(BaseSettings):
    db_server: str = os.getenv("DB_SERVER", "192.168.41.57")
    db_database: str = os.getenv("DB_DATABASE", "department2020")
    db_username: str = os.getenv("DB_USERNAME", "sa")
    db_password: str = os.getenv("DB_PASSWORD", "3518i")

auth_settings = Settings()

@router.on_event("startup")
async def startup():
    # 单机运行使用内存缓存即可
    FastAPICache.init(InMemoryBackend(), prefix="assemblyEarlyList-cache")

def get_db_connection():
    conn_str = (
        f"DRIVER={{SQL Server}};SERVER={auth_settings.db_server};DATABASE={auth_settings.db_database};"
        f"UID={auth_settings.db_username};PWD={auth_settings.db_password};"
    )
    try:
        return pyodbc.connect(conn_str)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"数据库连接失败: {exc}")

BASE_SQL = """
SELECT [报表日期],[工单编号],[工单状态],[生产车间],[生产线编号],[订单批号],[料品编码],[料品名称],[规格型号],[订单数量],
       [计划开始时间],[计划完成时间],[计划产量],[实际产量],[确定交期],[LineType],[理论产能],[实际工时],
       [交期_装嵌完成天数],[生产剩余天数],[是否打磨工艺],[是否需要预警]
FROM [department2020].[dbo].[装嵌预警日报]
WHERE 1=1
"""

@router.get("/assemblyEarlyList", summary="装嵌预警列表", description="装嵌预警数据列表，支持分页和多条件筛选")
@cache(expire=1800)
async def get_assembly_early_list(
    page: int = 1,
    pageSize: int = 20,
    报表日期: str | None = None,
    工单编号: str | None = None,
    订单批号: str | None = None,
    生产车间: str | None = None,
    料品编码: str | None = None,
    是否需要预警: str | None = None,
    是否打磨工艺: str | None = None,
    确定交期: str | None = None  # 格式: "2025-01-01,2025-01-31"
):
    try:
        conn = get_db_connection()
        
        # 构建WHERE条件
        where_conditions = ["1=1"]
        params = []
        
        if 报表日期:
            where_conditions.append("报表日期 = ?")
            params.append(报表日期)

        if 工单编号:
            where_conditions.append("工单编号 LIKE ?")
            params.append(f"%{工单编号}%")
            
        if 订单批号:
            where_conditions.append("订单批号 LIKE ?")
            params.append(f"%{订单批号}%")
            
        if 生产车间:
            where_conditions.append("生产车间 = ?")
            params.append(生产车间)
            
        if 料品编码:
            where_conditions.append("料品编码 LIKE ?")
            params.append(f"%{料品编码}%")
            
        if 是否需要预警:
            where_conditions.append("是否需要预警 = ?")
            params.append(是否需要预警)
            
        if 是否打磨工艺:
            where_conditions.append("是否打磨工艺 = ?")
            params.append(是否打磨工艺)
            
        if 确定交期:
            try:
                start_date, end_date = 确定交期.split(',')
                where_conditions.append("CAST(确定交期 AS DATE) BETWEEN ? AND ?")
                params.extend([start_date, end_date])
            except ValueError:
                pass  # 忽略格式错误的日期范围
        
        where_clause = " AND ".join(where_conditions)
        
        # 获取总数
        count_sql = f"""
        SELECT COUNT(*) as total
        FROM [department2020].[dbo].[装嵌预警日报]
        WHERE {where_clause}
        """
        
        count_result = pd.read_sql(count_sql, conn, params=params)
        total = int(count_result.iloc[0]['total'])
        
        # 分页查询数据
        offset = (page - 1) * pageSize
        data_sql = f"""
        SELECT [报表日期],[工单编号],[工单状态],[生产车间],[生产线编号],[订单批号],[料品编码],[料品名称],[规格型号],[订单数量],
               [计划开始时间],[计划完成时间],[计划产量],[实际产量],[确定交期],[LineType],[理论产能],[实际工时],
               [交期_装嵌完成天数],[生产剩余天数],[是否打磨工艺],[是否需要预警]
        FROM [department2020].[dbo].[装嵌预警日报]
        WHERE {where_clause}
        ORDER BY [报表日期] DESC, [工单编号]
        OFFSET {offset} ROWS
        FETCH NEXT {pageSize} ROWS ONLY
        """
        
        df = pd.read_sql(data_sql, conn, params=params)
        # 将 NaT / nan 替换 0 或空
        df = df.fillna(0)
        # datetime 转 ISO
        for col in df.select_dtypes(include=['datetime']):
            df[col] = df[col].astype(str)
        result = df.to_dict(orient='records')
        conn.close()
        
        return {
            "status": "success",
            "data": result,
            "total": total,
            "page": page,
            "pageSize": pageSize,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
