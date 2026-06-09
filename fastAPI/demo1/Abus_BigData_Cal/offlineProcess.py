from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pyodbc
from datetime import datetime
from fastapi_cache.decorator import cache

router = APIRouter()

DB_SERVER = "192.168.10.200"
DB_USERNAME = "sa"
DB_PASSWORD = "5tgb^YHN7ujm*IK<"

def get_db_connection():
    conn_str = (
        f"DRIVER={{SQL Server}};SERVER={DB_SERVER};DATABASE=APS_SUO;"
        f"UID={DB_USERNAME};PWD={DB_PASSWORD};"
    )
    return pyodbc.connect(conn_str)

def get_data_from_db(data_type=None, part_name=None, part_spec=None, DepartmentName=None, proccess=None, item_no=None):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        SELECT a.[id], a.[data_type], a.[item_no], a.[part_name], a.[part_spec],
               a.[before_proccess], a.[before_proccessNumber], a.[proccess], a.[proccessNumber],
               a.[DepartmentName], a.[capacity], a.[status], a.[days], a.[包装方式], a.[OpExternalId]
        FROM [APS_SUO].[dbo].[offline_process] a
        LEFT JOIN [TSD].[wygz].[dbo].[工序单价表] b
        ON a.proccessNumber = b.工序规格码
        WHERE a.proccessNumber IS NOT NULL
        """
        params = []
        if data_type:
            sql += " AND a.[data_type] LIKE ?"
            params.append(f"%{data_type}%")
        if part_name:
            sql += " AND a.[part_name] LIKE ?"
            params.append(f"%{part_name}%")
        if part_spec:
            sql += " AND a.[part_spec] LIKE ?"
            params.append(f"%{part_spec}%")
        if DepartmentName:
            sql += " AND LTRIM(RTRIM(a.[DepartmentName])) = ?"
            params.append(DepartmentName.strip())
        if proccess:
            sql += " AND a.[proccess] LIKE ?"
            params.append(f"%{proccess}%")
        if item_no:
            sql += " AND a.[item_no] LIKE ?"
            params.append(f"%{item_no}%")

        sql += " ORDER BY a.[id]"

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        raw_data = []
        for row in rows:
            raw_data.append({
                "id": row[0],
                "data_type": row[1] if row[1] else "",
                "item_no": row[2] if row[2] else "",
                "part_name": row[3] if row[3] else "",
                "part_spec": row[4] if row[4] else "",
                "before_proccess": row[5] if row[5] else "",
                "before_proccessNumber": row[6] if row[6] else "",
                "proccess": row[7] if row[7] else "",
                "proccessNumber": row[8] if row[8] else "",
                "DepartmentName": row[9] if row[9] else "",
                "capacity": row[10] if row[10] else "",
                "status": row[11] if row[11] else "",
                "days": str(row[12]) if row[12] else "",
                "包装方式": row[13] if row[13] else "",
                "OpExternalId": row[14] if row[14] else "",
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

def get_options_from_db(field):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if field == "data_type":
            sql = """
            SELECT DISTINCT TOP 200 LTRIM(RTRIM([data_type])) AS value
            FROM [APS_SUO].[dbo].[offline_process]
            WHERE [data_type] IS NOT NULL AND LTRIM(RTRIM([data_type])) != ''
            ORDER BY LTRIM(RTRIM([data_type]))
            """
        elif field == "part_name":
            sql = """
            SELECT DISTINCT TOP 200 LTRIM(RTRIM([part_name])) AS value
            FROM [APS_SUO].[dbo].[offline_process]
            WHERE [part_name] IS NOT NULL AND LTRIM(RTRIM([part_name])) != ''
            ORDER BY LTRIM(RTRIM([part_name]))
            """
        elif field == "DepartmentName":
            sql = """
            SELECT DISTINCT LTRIM(RTRIM([DepartmentName])) AS value
            FROM [APS_SUO].[dbo].[offline_process]
            WHERE [DepartmentName] IS NOT NULL AND LTRIM(RTRIM([DepartmentName])) != ''
            ORDER BY LTRIM(RTRIM([DepartmentName]))
            """
        elif field == "proccess":
            sql = """
            SELECT DISTINCT TOP 200 LTRIM(RTRIM([proccess])) AS value
            FROM [APS_SUO].[dbo].[offline_process]
            WHERE [proccess] IS NOT NULL AND LTRIM(RTRIM([proccess])) != ''
            ORDER BY LTRIM(RTRIM([proccess]))
            """
        else:
            return []

        cursor.execute(sql)
        return [{"value": row[0]} for row in cursor.fetchall()]
    except Exception as exc:
        print(f"获取offline_process选项失败: field={field}, error={exc}")
        return []
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

@router.get("/offlineProcess", summary="工序规格码单价对应产品明细与统计")
@cache(expire=1800)
async def get_offline_process(
    data_type: Optional[str] = Query(None, description="data_type（模糊查询）"),
    part_name: Optional[str] = Query(None, description="part_name（模糊查询）"),
    part_spec: Optional[str] = Query(None, description="part_spec（模糊查询）"),
    DepartmentName: Optional[str] = Query(None, description="部门（精确匹配）"),
    proccess: Optional[str] = Query(None, description="工序（模糊查询）"),
    item_no: Optional[str] = Query(None, description="item_no（模糊查询）"),
):
    try:
        raw_data = get_data_from_db(data_type, part_name, part_spec, DepartmentName, proccess, item_no)
        return {
            "status": "success",
            "data": raw_data,
            "total_count": len(raw_data),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as exc:
        print(f"获取offline_process数据失败: {exc}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")

@router.get("/offlineProcess/options", summary="offline_process下拉选项")
async def get_options(field: str = Query(..., description="字段名")):
    try:
        data = get_options_from_db(field)
        return {"status": "success", "data": data}
    except Exception as exc:
        print(f"获取offline_process选项失败: field={field}, error={exc}")
        return {"status": "success", "data": []}
