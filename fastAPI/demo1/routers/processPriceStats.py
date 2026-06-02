from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pyodbc
from datetime import datetime
from collections import defaultdict
from fastapi_cache.decorator import cache

router = APIRouter()

DB_SERVER = "192.168.41.57"
DB_DATABASE = "department2020"
DB_USERNAME = "sa"
DB_PASSWORD = "3518i"

def get_db_connection():
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USERNAME};PWD={DB_PASSWORD}"
    return pyodbc.connect(conn_str)

def get_data_from_db(部门=None, 工序名称=None):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
        SELECT [_Identify]
              ,[部门]
              ,[工序编号]
              ,[工序名称]
              ,[产品规格]
              ,[单位]
              ,[生效单价]
              ,[每小时产量]
              ,[调整前单价]
              ,[调整单价]
              ,[备注]
              ,[工序规格码]
              ,[规格次序]
              ,[修改时间]
              ,[计件绩效标准]
              ,[产品分区]
              ,[通用规格]
              ,[工序内容]
              ,[作业人数]
              ,[加工尺寸]
              ,[单价状态]
        FROM [department2020].[dbo].[V_工序单价表]
        WHERE 1=1
        """
        params = []
        if 部门:
            sql += " AND [部门] = ?"
            params.append(部门)
        if 工序名称:
            sql += " AND [工序名称] LIKE ?"
            params.append(f"%{工序名称}%")

        sql += " ORDER BY [部门], [工序名称], [规格次序]"

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        raw_data = []
        for row in rows:
            raw_data.append({
                "_Identify": row[0],
                "部门": row[1] if row[1] else "",
                "工序编号": row[2] if row[2] else "",
                "工序名称": row[3] if row[3] else "",
                "产品规格": row[4] if row[4] else "",
                "单位": row[5] if row[5] else "",
                "生效单价": float(row[6]) if row[6] else 0,
                "每小时产量": float(row[7]) if row[7] else 0,
                "调整前单价": float(row[8]) if row[8] else 0,
                "调整单价": float(row[9]) if row[9] else 0,
                "备注": row[10] if row[10] else "",
                "工序规格码": row[11] if row[11] else "",
                "规格次序": row[12] if row[12] else "",
                "修改时间": str(row[13]) if row[13] else "",
                "计件绩效标准": float(row[14]) if row[14] else 0,
                "产品分区": row[15] if row[15] else "",
                "通用规格": row[16] if row[16] else "",
                "工序内容": row[17] if row[17] else "",
                "作业人数": float(row[18]) if row[18] else 0,
                "加工尺寸": row[19] if row[19] else "",
                "单价状态": row[20] if row[20] else ""
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

@router.get("/processPriceStats", summary="工序规格码单价明细与统计")
@cache(expire=1800)
async def get_process_price_stats(
    部门: Optional[str] = Query(None, description="部门（精确匹配）"),
    工序名称: Optional[str] = Query(None, description="工序名称（模糊查询）")
):
    try:
        raw_data = get_data_from_db(部门, 工序名称)

        # 按部门+工序名称聚合统计
        stats = defaultdict(lambda: {"values": [], "部门": "", "工序名称": ""})
        for item in raw_data:
            key = (item["部门"], item["工序名称"])
            stats[key]["部门"] = item["部门"]
            stats[key]["工序名称"] = item["工序名称"]
            stats[key]["values"].append(item["生效单价"])

        stats_data = []
        for key, s in stats.items():
            vals = [v for v in s["values"] if v > 0]
            if not vals:
                continue
            stats_data.append({
                "部门": s["部门"],
                "工序名称": s["工序名称"],
                "记录数": len(vals),
                "最高价": max(vals),
                "最低价": min(vals),
                "平均价": round(sum(vals) / len(vals), 2)
            })

        stats_data.sort(key=lambda x: (x["部门"], x["工序名称"]))

        return {
            "status": "success",
            "data": {
                "stats": stats_data,
                "details": raw_data,
                "total_count": len(raw_data)
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as exc:
        print(f"获取工序单价数据失败: {exc}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")

@router.get("/processPriceStats/departments", summary="获取部门下拉列表")
@cache(expire=72000)
async def get_departments():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT [部门] FROM [department2020].[dbo].[V_工序单价表] WHERE [部门] IS NOT NULL AND [部门] != '' ORDER BY [部门]")
        deps = [row[0] for row in cursor.fetchall()]
        conn.close()
        return {"status": "success", "data": deps}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"获取部门列表失败: {exc}")

@router.get("/processPriceStats/processNames", summary="获取工序名称下拉列表")
@cache(expire=72000)
async def get_process_names():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT [工序名称] FROM [department2020].[dbo].[V_工序单价表] WHERE [工序名称] IS NOT NULL AND [工序名称] != '' ORDER BY [工序名称]")
        names = [row[0] for row in cursor.fetchall()]
        conn.close()
        return {"status": "success", "data": names}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"获取工序名称列表失败: {exc}")
