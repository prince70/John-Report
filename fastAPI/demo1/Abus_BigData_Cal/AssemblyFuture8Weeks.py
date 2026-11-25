from datetime import datetime
import os

import pandas as pd
import pyodbc
from fastapi import APIRouter, HTTPException

router = APIRouter()


DB_SERVER = os.getenv("DB_SERVER", "192.168.41.57")
DB_DATABASE = os.getenv("DB_DATABASE", "department2020")
DB_USERNAME = os.getenv("DB_USERNAME", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "3518i")


TABLE_NAME = "[department2020].[dbo].[装嵌派工单统计数量工时_理论产能2]"


def get_db_connection():
    conn_str = (
        f"DRIVER={{SQL Server}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};"
        f"UID={DB_USERNAME};PWD={DB_PASSWORD};"
    )
    try:
        return pyodbc.connect(conn_str)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"数据库连接失败: {exc}")


@router.get(
    "/assemblyFuture8Weeks",
    summary="装嵌未来8周需求明细",
    description="装嵌未来8周需求明细列表，数据源：装嵌派工单统计数量工时_理论产能2",
)
async def get_assembly_future_8_weeks(
    page: int = 1,
    pageSize: int = 20,
    工单编号: str | None = None,
    订单批号: str | None = None,
    生产车间: str | None = None,
    料品编码: str | None = None,
    料品名称: str | None = None,
    生产线编号: str | None = None,
    确定交期: str | None = None,
):
    conn = None
    try:
        conn = get_db_connection()

        where_conditions = ["1=1"]
        params: list[str] = []

        if 工单编号:
            where_conditions.append("[工单编号] LIKE ?")
            params.append(f"%{工单编号}%")

        if 订单批号:
            where_conditions.append("[订单批号] LIKE ?")
            params.append(f"%{订单批号}%")

        if 生产车间:
            where_conditions.append("[生产车间] = ?")
            params.append(生产车间)

        if 料品编码:
            where_conditions.append("[料品编码] LIKE ?")
            params.append(f"%{料品编码}%")

        if 料品名称:
            where_conditions.append("[料品名称] LIKE ?")
            params.append(f"%{料品名称}%")

        if 生产线编号:
            where_conditions.append("[生产线编号] = ?")
            params.append(生产线编号)

        if 确定交期:
            try:
                start_date, end_date = 确定交期.split(",")
                where_conditions.append("CAST([确定交期] AS DATE) BETWEEN ? AND ?")
                params.extend([start_date, end_date])
            except ValueError:
                pass

        where_clause = " AND ".join(where_conditions)

        count_sql = f"SELECT COUNT(*) AS total FROM {TABLE_NAME} WHERE {where_clause}"
        count_df = pd.read_sql(count_sql, conn, params=params)
        total = int(count_df.iloc[0]["total"])

        offset = (page - 1) * pageSize
        data_sql = f"""
        SELECT *
        FROM {TABLE_NAME}
        WHERE {where_clause}
        ORDER BY [确定交期] ASC, [工单编号] ASC
        OFFSET {offset} ROWS
        FETCH NEXT {pageSize} ROWS ONLY
        """

        df = pd.read_sql(data_sql, conn, params=params)
        df = df.fillna("")

        for col in df.select_dtypes(include=["datetime", "datetimetz"]):
            df[col] = df[col].astype(str)

        return {
            "status": "success",
            "data": df.to_dict(orient="records"),
            "total": total,
            "page": page,
            "pageSize": pageSize,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
    finally:
        if conn:
            conn.close()


@router.get(
    "/assemblyFuture8Weeks/workshop-options",
    summary="生产车间选项",
    description="从装嵌未来8周需求明细全量数据中提取生产车间去重选项",
)
async def get_assembly_future_8_weeks_workshop_options():
    conn = None
    try:
        conn = get_db_connection()
        sql = f"""
        SELECT DISTINCT [生产车间]
        FROM {TABLE_NAME}
        WHERE [生产车间] IS NOT NULL AND LTRIM(RTRIM([生产车间])) <> ''
        ORDER BY [生产车间]
        """
        df = pd.read_sql(sql, conn)
        options = df["生产车间"].astype(str).str.strip().tolist() if not df.empty else []
        return {
            "status": "success",
            "data": options,
            "total": len(options),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
    finally:
        if conn:
            conn.close()
