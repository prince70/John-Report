from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pyodbc

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

def fetch_rows(sql, params):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    return cursor.fetchall()

@router.get("/workshopRealTimeInventory", summary="车间实时库存")
async def get_inventory(
    存放位置: Optional[str] = None,
    产品名称: Optional[str] = None,
    系列: Optional[str] = None,
    产品规格: Optional[str] = None,
):
    try:
        sql = """
        SELECT [item_no], [产品名称], [系列], [产品规格], [库存类型], [库存], [存放位置], [备注]
        FROM [APS_SUO].[dbo].[v_库存汇总]
        WHERE [库存] > 0
        """
        params = []
        if 存放位置:
            sql += " AND [存放位置] LIKE ?"
            params.append(f"%{存放位置}%")
        if 产品名称:
            sql += " AND [产品名称] LIKE ?"
            params.append(f"%{产品名称}%")
        if 系列:
            sql += " AND [系列] LIKE ?"
            params.append(f"%{系列}%")
        if 产品规格:
            sql += " AND [产品规格] LIKE ?"
            params.append(f"%{产品规格}%")
        sql += " ORDER BY [存放位置], [item_no]"
        rows = fetch_rows(sql, params)
        result = []
        for row in rows:
            result.append({
                "item_no": row[0] or "",
                "产品名称": row[1] or "",
                "系列": row[2] or "",
                "产品规格": row[3] or "",
                "库存类型": row[4] or "",
                "库存": float(row[5]) if row[5] else 0,
                "存放位置": row[6] or "",
                "备注": row[7] or "",
            })
        total_inventory = sum(r["库存"] for r in result)
        return {"status": "success", "data": result, "total_count": len(result), "total_inventory": total_inventory}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")

def _get_options(field):
    try:
        if field == "产品名称":
            sql = "SELECT DISTINCT [产品名称] FROM [APS_SUO].[dbo].[v_库存汇总] WHERE [产品名称] IS NOT NULL AND [产品名称] != '' ORDER BY [产品名称]"
        elif field == "系列":
            sql = "SELECT DISTINCT [系列] FROM [APS_SUO].[dbo].[v_库存汇总] WHERE [系列] IS NOT NULL AND [系列] != '' ORDER BY [系列]"
        elif field == "产品规格":
            sql = "SELECT DISTINCT [产品规格] FROM [APS_SUO].[dbo].[v_库存汇总] WHERE [产品规格] IS NOT NULL AND [产品规格] != '' ORDER BY [产品规格]"
        elif field == "存放位置":
            sql = "SELECT DISTINCT [存放位置] FROM [APS_SUO].[dbo].[v_库存汇总] WHERE [存放位置] IS NOT NULL AND [存放位置] != '' ORDER BY [存放位置]"
        else:
            return []
        rows = fetch_rows(sql, [])
        return [str(row[0]) for row in rows]
    except:
        return []

@router.get("/workshopRealTimeInventory/options", summary="车间实时库存下拉选项")
async def get_options(field: str = Query(...)):
    return {"status": "success", "data": _get_options(field)}
