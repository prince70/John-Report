from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pyodbc
from datetime import datetime
from fastapi_cache.decorator import cache

router = APIRouter()

DB_SERVER = "192.168.10.200"
DB_DATABASE = "APS_SUO"
DB_USERNAME = "sa"
DB_PASSWORD = "5tgb^YHN7ujm*IK<"

TABLE_MAP = {
    "CNC": "Full_process_reporting_CNC",
    "DZS": "Full_process_reporting_DZS",
}

def get_db_connection():
    conn_str = (
        f"DRIVER={{SQL Server}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};"
        f"UID={DB_USERNAME};PWD={DB_PASSWORD};"
    )
    return pyodbc.connect(conn_str)

def get_data_from_db(table_type, 订单批号=None, 料品编码=None, part_name=None, part_spec=None, 生产车间=None):
    if table_type not in TABLE_MAP:
        raise ValueError("无效的table_type")
    table_name = TABLE_MAP[table_type]

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = f"""
        SELECT [id], [订单批号], [料品编码], [part_name], [part_spec],
               [生产车间], [当前工序ID], [下一道工序ID], [报工数量总和], [库存], [备注]
        FROM [APS_SUO].[dbo].[{table_name}]
        WHERE 1=1
        """
        params = []
        if 订单批号:
            sql += " AND [订单批号] LIKE ?"
            params.append(f"%{订单批号}%")
        if 料品编码:
            sql += " AND [料品编码] LIKE ?"
            params.append(f"%{料品编码}%")
        if part_name:
            sql += " AND [part_name] LIKE ?"
            params.append(f"%{part_name}%")
        if part_spec:
            sql += " AND [part_spec] LIKE ?"
            params.append(f"%{part_spec}%")
        if 生产车间:
            sql += " AND [生产车间] = ?"
            params.append(生产车间)

        sql += " ORDER BY [id]"

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        raw_data = []
        for row in rows:
            raw_data.append({
                "id": row[0],
                "订单批号": row[1] if row[1] else "",
                "料品编码": row[2] if row[2] else "",
                "part_name": row[3] if row[3] else "",
                "part_spec": row[4] if row[4] else "",
                "生产车间": row[5] if row[5] else "",
                "当前工序ID": row[6] if row[6] else "",
                "下一道工序ID": row[7] if row[7] else "",
                "报工数量总和": float(row[8]) if row[8] else 0,
                "库存": float(row[9]) if row[9] else 0,
                "备注": row[10] if row[10] else "",
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

def get_options_from_db(table_type, field):
    if table_type not in TABLE_MAP:
        raise ValueError("无效的table_type")
    table_name = TABLE_MAP[table_type]

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if field == "生产车间":
            sql = f"""
            SELECT DISTINCT [生产车间] AS value
            FROM [APS_SUO].[dbo].[{table_name}]
            WHERE [生产车间] IS NOT NULL AND [生产车间] != ''
            ORDER BY [生产车间]
            """
        elif field == "part_name":
            sql = f"""
            SELECT DISTINCT TOP 200 [part_name] AS value
            FROM [APS_SUO].[dbo].[{table_name}]
            WHERE [part_name] IS NOT NULL AND [part_name] != ''
            ORDER BY [part_name]
            """
        elif field == "part_spec":
            sql = f"""
            SELECT DISTINCT TOP 200 [part_spec] AS value
            FROM [APS_SUO].[dbo].[{table_name}]
            WHERE [part_spec] IS NOT NULL
            ORDER BY [part_spec]
            """
        else:
            return []

        cursor.execute(sql)
        rows = cursor.fetchall()
        return [{"value": row[0]} for row in rows]
    except Exception as exc:
        print(f"获取选项失败: table={table_name}, field={field}, error={exc}")
        return []
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

@router.get("/fullProcessInventory/{table_type}", summary="全流程报工库存数据")
@cache(expire=1800)
async def get_full_process_inventory(
    table_type: str,
    订单批号: Optional[str] = Query(None, description="订单批号（模糊查询）"),
    料品编码: Optional[str] = Query(None, description="料品编码（模糊查询）"),
    part_name: Optional[str] = Query(None, description="part_name（模糊查询）"),
    part_spec: Optional[str] = Query(None, description="part_spec（模糊查询）"),
    生产车间: Optional[str] = Query(None, description="生产车间（精确匹配）"),
):
    try:
        raw_data = get_data_from_db(table_type, 订单批号, 料品编码, part_name, part_spec, 生产车间)
        return {
            "status": "success",
            "data": raw_data,
            "total_count": len(raw_data),
            "timestamp": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as exc:
        print(f"获取全流程报工库存数据失败: {exc}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")

@router.get("/fullProcessInventory/{table_type}/options", summary="全流程报工库存下拉选项")
async def get_options(table_type: str, field: str = Query(..., description="字段名")):
    try:
        data = get_options_from_db(table_type, field)
        return {"status": "success", "data": data}
    except Exception as exc:
        print(f"获取选项失败: table_type={table_type}, field={field}, error={exc}")
        return {"status": "success", "data": []}
