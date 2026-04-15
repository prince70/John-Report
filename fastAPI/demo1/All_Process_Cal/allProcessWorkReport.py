# 2025-12-04 报工查询（直接查询数据库）
# 功能说明：
# 1. 直接查询APS_FinishedQty_All表
# 2. 支持条件筛选（工序、生产车间、订单批号、结束时间范围）
# 3. 支持分页查询（50/100/200/500条每页）
# 4. 无条件时默认显示前1000条
# 5. 支持导出Excel功能

from fastapi import APIRouter, HTTPException, Query
from pydantic_settings import BaseSettings
import pyodbc
import pandas as pd
from datetime import datetime, timedelta
import os
import time
from typing import Optional
from fastapi.responses import StreamingResponse
import io
import urllib.parse
import re

router = APIRouter()

# 车间列表缓存（30分钟有效期）
workshop_cache = {
    "data": None,
    "last_updated": None
}

# 工序列表缓存（30分钟有效期）
process_cache = {
    "data": None,
    "last_updated": None
}

# 员工姓名列表缓存（30分钟有效期）
emp_name_cache = {
    "data": None,
    "last_updated": None
}

class APSDBSettings(BaseSettings):
    """数据库连接配置"""
    db_server: str = os.getenv("APS_DB_SERVER", "192.168.41.57")
    db_database: str = os.getenv("APS_DB_DATABASE", "department2020")
    db_username: str = os.getenv("APS_DB_USERNAME", "sa")
    db_password: str = os.getenv("APS_DB_PASSWORD", "3518i")

aps_settings = APSDBSettings()

def get_db_connection(settings: BaseSettings):
    """创建数据库连接"""
    connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={settings.db_server};DATABASE={settings.db_database};UID={settings.db_username};PWD={settings.db_password};'
    try:
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库连接失败: {str(e)}")

def query_all_data():
    """
    查询所有数据（直接查询数据库，无缓存）
    """
    start_time = time.time()
    
    # 数据库连接配置
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=192.168.41.57;"
        "DATABASE=department2020;"
        "UID=sa;"
        "PWD=3518i"
    )
    
    conn = None
    try:
        conn = pyodbc.connect(conn_str)
        
        # 查询APS_FinishedQty_All表（查询全部数据）
        """之前的sql
        SELECT   [OpExternalId] 工序
              ,[确定交期]
              ,[生产车间]
              ,[JobExternalId] 工单编号
              ,[OrderNumber] 订单批号
              ,[ItemExternalId] 料品编码
              ,[ResName] 生产线编码
              ,[ProductDescription] 规格型号
              ,[emp_no] 员工编号
              ,[emp_item_no] 工号
              ,[emp_name] 姓名
              ,[EachFinishedQty] 报工数量
              ,[EachFinishedQtykg] 报工重量
              ,[repairQty] 返修数量
              ,[StartDate] 开始时间
              ,[FinishedDate] 结束时间
          FROM [APS_FinishedQty_All]
        """
        query = """
        SELECT         
               [OpExternalId] 工序
              ,[确定交期]
              ,[生产车间]
              ,[JobExternalId] 工单编号
              ,[OrderNumber] 订单批号
              ,[ItemExternalId] 料品编码
              ,[ResName] 生产线编码
              ,[ProductDescription] 规格型号
              ,[emp_no] 员工编号
              ,[emp_item_no] 工号
              ,[emp_name] 姓名
              ,[EachFinishedQty] 报工数量
              ,[EachFinishedQtykg] 报工重量
              ,[repairQty] 返修数量
              ,[每小时产能]
              ,[理论工时]
              ,[StartDate] 开始时间
              ,[FinishedDate] 结束时间
          FROM [APS_FinishedQty_All]
        """
        
        # 读取所有数据到 Pandas DataFrame
        df = pd.read_sql(query, conn)
        
        conn.close()
        
        elapsed = time.time() - start_time
        print(f"✅ 数据加载完成！共 {len(df)} 条记录，耗时 {elapsed:.2f}秒")
        
        return df
        
    except Exception as e:
        print(f"❌ 数据加载失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"数据加载失败: {str(e)}")

def query_data_with_filters(
    process: Optional[str] = None,
    workshop: Optional[str] = None,
    order_number: Optional[str] = None,
    emp_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    has_conditions: bool = True
):
    """
    使用SQL WHERE条件直接查询数据库
    """
    start_time = time.time()
    
    # 数据库连接配置
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=192.168.41.57;"
        "DATABASE=department2020;"
        "UID=sa;"
        "PWD=3518i"
    )
    
    conn = None
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # 构建WHERE条件
        where_conditions = []
        params = []
        
        if process:
            where_conditions.append("[OpExternalId] LIKE ?")
            params.append(f"%{process}%")
        
        if workshop:
            where_conditions.append("[生产车间] = ?")
            params.append(workshop)
        
        if order_number:
            where_conditions.append("[OrderNumber] LIKE ?")
            params.append(f"%{order_number}%")
        
        if emp_name:
            where_conditions.append("[emp_name] LIKE ?")
            params.append(f"%{emp_name}%")
        
        if start_date:
            where_conditions.append("[FinishedDate] >= ?")
            params.append(start_date)
        
        if end_date:
            where_conditions.append("[FinishedDate] <= ?")
            params.append(end_date)
        
        # 添加WHERE子句
        if where_conditions:
            where_clause = " WHERE " + " AND ".join(where_conditions)
        else:
            where_clause = ""
        
        # 查询总数
        count_query = f"SELECT COUNT(*) FROM [APS_FinishedQty_All]{where_clause}"
        cursor.execute(count_query, params)
        filtered_total_actual = cursor.fetchone()[0]
        
        # 无条件时限制为1000条
        if not has_conditions:
            limited_total = min(filtered_total_actual, 1000)
        else:
            limited_total = filtered_total_actual
        
        # 计算总页数并矫正页码
        total_pages = max(1, (limited_total + page_size - 1) // page_size)
        if page > total_pages:
            page = total_pages
        
        # 构建分页查询
        offset = (page - 1) * page_size
        
        # 添加ORDER BY和OFFSET/FETCH
        order_clause = " ORDER BY [FinishedDate] DESC, [JobExternalId] ASC"
        
        if not has_conditions:
            # 无条件时，先取前1000条，再分页
            query = f"""
            SELECT * FROM (
                SELECT TOP 1000
                       [OpExternalId] 工序
                      ,[确定交期]
                      ,[生产车间]
                      ,[JobExternalId] 工单编号
                      ,[OrderNumber] 订单批号
                      ,[ItemExternalId] 料品编码
                      ,[ResName] 生产线编码
                      ,[ProductDescription] 规格型号
                      ,[emp_no] 员工编号
                      ,[emp_item_no] 工号
                      ,[emp_name] 姓名
                      ,[EachFinishedQty] 报工数量
                      ,[EachFinishedQtykg] 报工重量
                      ,[repairQty] 返修数量
                      ,[每小时产能]
                      ,[理论工时]
                      ,[StartDate] 开始时间
                      ,[FinishedDate] 结束时间
                FROM [APS_FinishedQty_All]
                {order_clause}
            ) AS T
            ORDER BY [结束时间] DESC, [工单编号] ASC
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
            """
            cursor.execute(query, [offset, page_size])
        else:
            # 有条件时，直接分页
            query = f"""
            SELECT 
                   [OpExternalId] 工序
                  ,[确定交期]
                  ,[生产车间]
                  ,[JobExternalId] 工单编号
                  ,[OrderNumber] 订单批号
                  ,[ItemExternalId] 料品编码
                  ,[ResName] 生产线编码
                  ,[ProductDescription] 规格型号
                  ,[emp_no] 员工编号
                  ,[emp_item_no] 工号
                  ,[emp_name] 姓名
                  ,[EachFinishedQty] 报工数量
                  ,[EachFinishedQtykg] 报工重量
                  ,[repairQty] 返修数量
                  ,[每小时产能]
                  ,[理论工时]
                  ,[StartDate] 开始时间
                  ,[FinishedDate] 结束时间
            FROM [APS_FinishedQty_All]
            {where_clause}
            {order_clause}
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
            """
            cursor.execute(query, params + [offset, page_size])
        
        # 获取查询结果
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        
        # 转换为字典列表
        result = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                row_dict[col] = row[i]
            result.append(row_dict)
        
        # 查询总数
        table_query = "SELECT COUNT(*) FROM [APS_FinishedQty_All]"
        cursor.execute(table_query)
        table_total = cursor.fetchone()[0]

        # 统计全部筛选结果的汇总（不受分页影响）
        summary_query = f"""
        SELECT
            COALESCE(SUM(CAST([EachFinishedQty] AS FLOAT)), 0) AS total_finished_qty,
            COALESCE(SUM(CAST([理论工时] AS FLOAT)), 0) AS total_theory_hours
        FROM [APS_FinishedQty_All]
        {where_clause}
        """
        cursor.execute(summary_query, params)
        summary_row = cursor.fetchone()
        total_finished_qty = float(summary_row[0] or 0)
        total_theory_hours = float(summary_row[1] or 0)
        
        cursor.close()
        conn.close()
        
        elapsed = time.time() - start_time
        print(f"✅ 查询完成！返回 {len(result)} 条记录，耗时 {elapsed:.3f}秒")
        
        return {
            "data": result,
            "summary": {
                "all": {
                    "finishedQtySum": total_finished_qty,
                    "theoryHoursSum": total_theory_hours
                }
            },
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "filtered_total": limited_total,
                "filtered_total_actual": filtered_total_actual,
                "table_total": table_total,
                "max_records": 1000,
                "limit_applied": not has_conditions,
            },
            "execution_time": f"{elapsed:.3f}秒",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

@router.get(
    "/allProcessWorkReport/workshops",
    summary="获取所有生产车间列表",
    description="返回所有不重复的生产车间，用于下拉菜单"
)
async def get_workshops():
    """获取所有不重复的生产车间列表（直接从 APS_FinishedQty_All 表查询）"""
    try:
        # 检查缓存是否有效
        if workshop_cache["data"] is not None and workshop_cache["last_updated"] is not None:
            cache_age = datetime.now() - workshop_cache["last_updated"]
            if cache_age < timedelta(minutes=30):
                return {
                    "status": "success",
                    "data": workshop_cache["data"],
                    "total": len(workshop_cache["data"]),
                    "last_updated": workshop_cache["last_updated"].isoformat()
                }
        
        # 直接从数据库查询车间列表（使用department2020数据库，服务器192.168.41.57）
        conn_str = (
            "DRIVER={SQL Server};"
            "SERVER=192.168.41.57;"
            "DATABASE=department2020;"
            "UID=sa;"
            "PWD=3518i"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        sql = """
            SELECT DISTINCT [生产车间]
            FROM [APS_FinishedQty_All]
            WHERE 生产车间 IS NOT NULL AND 生产车间 <> ''
            ORDER BY 生产车间
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # 提取车间列表
        workshops = [row[0] for row in rows if row[0]]
        
        # 更新缓存
        workshop_cache["data"] = workshops
        workshop_cache["last_updated"] = datetime.now()
        print(f"📋 从 APS_FinishedQty_All 表获取到 {len(workshops)} 个不重复的生产车间")
        
        return {
            "status": "success",
            "data": workshops,
            "total": len(workshops),
            "last_updated": workshop_cache["last_updated"].isoformat()
        }
    except Exception as e:
        print(f"❌ 获取车间列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取车间列表失败: {str(e)}")

@router.get(
    "/allProcessWorkReport/processes",
    summary="获取所有工序列表",
    description="返回所有不重复的工序，用于下拉菜单。支持按车间筛选"
)
async def get_processes(
    workshop: Optional[str] = Query(None, description="生产车间（可选），提供时只返回该车间的工序")
):
    """获取所有不重复的工序列表（直接从 APS_FinishedQty_All 表查询）"""
    try:
        # 如果提供了车间参数，不使用缓存，直接查询
        if workshop:
            conn_str = (
                "DRIVER={SQL Server};"
                "SERVER=192.168.41.57;"
                "DATABASE=department2020;"
                "UID=sa;"
                "PWD=3518i"
            )
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            
            sql = """
                SELECT DISTINCT [OpExternalId]
                FROM [APS_FinishedQty_All]
                WHERE OpExternalId IS NOT NULL AND OpExternalId <> ''
                AND 生产车间 = ?
                ORDER BY OpExternalId
            """
            cursor.execute(sql, workshop)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            processes = [row[0] for row in rows if row[0]]
            
            return {
                "status": "success",
                "data": processes,
                "total": len(processes),
                "workshop": workshop
            }
        
        # 检查缓存是否有效
        if process_cache["data"] is not None and process_cache["last_updated"] is not None:
            cache_age = datetime.now() - process_cache["last_updated"]
            if cache_age < timedelta(minutes=30):
                return {
                    "status": "success",
                    "data": process_cache["data"],
                    "total": len(process_cache["data"]),
                    "last_updated": process_cache["last_updated"].isoformat()
                }
        
        # 直接从数据库查询工序列表
        conn_str = (
            "DRIVER={SQL Server};"
            "SERVER=192.168.41.57;"
            "DATABASE=department2020;"
            "UID=sa;"
            "PWD=3518i"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        sql = """
            SELECT DISTINCT [OpExternalId]
            FROM [APS_FinishedQty_All]
            WHERE OpExternalId IS NOT NULL AND OpExternalId <> ''
            ORDER BY OpExternalId
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # 提取工序列表
        processes = [row[0] for row in rows if row[0]]
        
        # 更新缓存
        process_cache["data"] = processes
        process_cache["last_updated"] = datetime.now()
        print(f"📋 从 APS_FinishedQty_All 表获取到 {len(processes)} 个不重复的工序")
        
        return {
            "status": "success",
            "data": processes,
            "total": len(processes),
            "last_updated": process_cache["last_updated"].isoformat()
        }
    except Exception as e:
        print(f"❌ 获取工序列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取工序列表失败: {str(e)}")

@router.get(
    "/allProcessWorkReport/empNames",
    summary="获取所有员工姓名列表",
    description="返回所有不重复的员工姓名，用于下拉菜单。支持按车间筛选"
)
async def get_emp_names(
    workshop: Optional[str] = Query(None, description="生产车间（可选），提供时只返回该车间的员工")
):
    """获取所有不重复的员工姓名列表（直接从 APS_FinishedQty_All 表查询）"""
    try:
        # 如果提供了车间参数，不使用缓存，直接查询
        if workshop:
            conn_str = (
                "DRIVER={SQL Server};"
                "SERVER=192.168.41.57;"
                "DATABASE=department2020;"
                "UID=sa;"
                "PWD=3518i"
            )
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            
            sql = """
                SELECT DISTINCT [emp_name]
                FROM [APS_FinishedQty_All]
                WHERE emp_name IS NOT NULL AND emp_name <> ''
                AND 生产车间 = ?
                ORDER BY emp_name
            """
            cursor.execute(sql, workshop)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            emp_names = [row[0] for row in rows if row[0]]
            
            return {
                "status": "success",
                "data": emp_names,
                "total": len(emp_names),
                "workshop": workshop
            }
        
        # 检查缓存是否有效
        if emp_name_cache["data"] is not None and emp_name_cache["last_updated"] is not None:
            cache_age = datetime.now() - emp_name_cache["last_updated"]
            if cache_age < timedelta(minutes=30):
                return {
                    "status": "success",
                    "data": emp_name_cache["data"],
                    "total": len(emp_name_cache["data"]),
                    "last_updated": emp_name_cache["last_updated"].isoformat()
                }
        
        # 直接从数据库查询员工姓名列表
        conn_str = (
            "DRIVER={SQL Server};"
            "SERVER=192.168.41.57;"
            "DATABASE=department2020;"
            "UID=sa;"
            "PWD=3518i"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        sql = """
            SELECT DISTINCT [emp_name]
            FROM [APS_FinishedQty_All]
            WHERE emp_name IS NOT NULL AND emp_name <> ''
            ORDER BY emp_name
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # 提取员工姓名列表
        emp_names = [row[0] for row in rows if row[0]]
        
        # 更新缓存
        emp_name_cache["data"] = emp_names
        emp_name_cache["last_updated"] = datetime.now()
        print(f"📋 从 APS_FinishedQty_All 表获取到 {len(emp_names)} 个不重复的员工姓名")
        
        return {
            "status": "success",
            "data": emp_names,
            "total": len(emp_names),
            "last_updated": emp_name_cache["last_updated"].isoformat()
        }
    except Exception as e:
        print(f"❌ 获取员工姓名列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取员工姓名列表失败: {str(e)}")

@router.get(
    "/allProcessWorkReport", 
    summary="全流程工序报工查询",
    description="直接查询数据库，支持分页和条件筛选"
)
async def get_all_process_work_report(
    process: Optional[str] = Query(None, description="工序（模糊查询）"),
    workshop: Optional[str] = Query(None, description="生产车间（精确匹配）"),
    order_number: Optional[str] = Query(None, description="订单批号（模糊查询）"),
    emp_name: Optional[str] = Query(None, description="姓名（模糊查询）"),
    start_date: Optional[str] = Query(None, description="结束时间范围-开始（>=）"),
    end_date: Optional[str] = Query(None, description="结束时间范围-结束（<=）"),
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(50, ge=1, le=500, description="每页条数，可选50/100/200/500")
):
    """
    全流程工序报工查询接口
    
    查询流程:
    1. 使用SQL WHERE条件直接查询数据库
    2. 使用OFFSET/FETCH进行分页
    
    分页选项: 50/100/200/500 条每页
    无条件时默认显示前1000条
    """
    
    query_start_time = time.time()
    
    # 判断是否有查询条件
    has_conditions = any([workshop, process, order_number, emp_name, start_date, end_date])
    
    print(f"📊 查询参数 - 工序:{process}, 车间:{workshop}, 订单批号:{order_number}, 姓名:{emp_name}, 开始:{start_date}, 结束:{end_date}, 页码:{page}")
    
    # 直接使用SQL查询
    result = query_data_with_filters(
        process=process,
        workshop=workshop,
        order_number=order_number,
        emp_name=emp_name,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
        has_conditions=has_conditions
    )
    
    result["status"] = "success"
    return result

@router.get(
    "/allProcessWorkReport/export",
    summary="导出Excel",
    description="导出筛选后的数据为Excel文件，包含总计行"
)
async def export_to_excel(
    process: Optional[str] = Query(None, description="工序（模糊查询）"),
    workshop: Optional[str] = Query(None, description="生产车间（精确匹配）"),
    order_number: Optional[str] = Query(None, description="订单批号（模糊查询）"),
    emp_name: Optional[str] = Query(None, description="姓名（模糊查询）"),
    start_date: Optional[str] = Query(None, description="结束时间范围-开始（>=）"),
    end_date: Optional[str] = Query(None, description="结束时间范围-结束（<=）")
):
    """
    导出筛选后的数据为Excel文件
    """
    try:
        print("🔄 开始导出Excel...")
        
        # 数据库连接配置
        conn_str = (
            "DRIVER={SQL Server};"
            "SERVER=192.168.41.57;"
            "DATABASE=department2020;"
            "UID=sa;"
            "PWD=3518i"
        )
        
        conn = pyodbc.connect(conn_str)
        
        # 构建WHERE条件
        where_conditions = []
        params = []
        
        if process:
            where_conditions.append("[OpExternalId] LIKE ?")
            params.append(f"%{process}%")
        
        if workshop:
            where_conditions.append("[生产车间] = ?")
            params.append(workshop)
        
        if order_number:
            where_conditions.append("[OrderNumber] LIKE ?")
            params.append(f"%{order_number}%")
        
        if emp_name:
            where_conditions.append("[emp_name] LIKE ?")
            params.append(f"%{emp_name}%")
        
        if start_date:
            where_conditions.append("[FinishedDate] >= ?")
            params.append(start_date)
        
        if end_date:
            where_conditions.append("[FinishedDate] <= ?")
            params.append(end_date)
        
        # 添加WHERE子句
        if where_conditions:
            where_clause = " WHERE " + " AND ".join(where_conditions)
        else:
            where_clause = ""
        
        # 构建查询
        query = f"""
        SELECT 
               [OpExternalId] 工序
              ,[确定交期]
              ,[生产车间]
              ,[JobExternalId] 工单编号
              ,[OrderNumber] 订单批号
              ,[ItemExternalId] 料品编码
              ,[ResName] 生产线编码
              ,[ProductDescription] 规格型号
              ,[emp_no] 员工编号
              ,[emp_item_no] 工号
              ,[emp_name] 姓名
              ,[EachFinishedQty] 报工数量
              ,[EachFinishedQtykg] 报工重量
              ,[repairQty] 返修数量
              ,[每小时产能]
              ,[理论工时]
              ,[StartDate] 开始时间
              ,[FinishedDate] 结束时间
        FROM [APS_FinishedQty_All]
        {where_clause}
        ORDER BY [FinishedDate] DESC, [JobExternalId] ASC
        """
        
        # 直接查询到DataFrame
        df_filtered = pd.read_sql(query, conn, params=params)
        conn.close()
        
        # 按结束时间降序、工单编号升序排序
        df_filtered = df_filtered.sort_values(by=['结束时间', '工单编号'], ascending=[False, True])
        
        # 计算总计
        total_finished_qty = df_filtered['报工数量'].sum()
        total_theory_hours = df_filtered['理论工时'].sum()
        
        # 添加总计行
        total_row = {col: '' for col in df_filtered.columns}
        total_row['工序'] = '总计'
        total_row['报工数量'] = total_finished_qty
        total_row['理论工时'] = total_theory_hours
        
        # 将总计行添加到DataFrame
        df_total = pd.concat([df_filtered, pd.DataFrame([total_row])], ignore_index=True)
        
        # 创建Excel文件
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # 直接导出原始数据，不做任何清理
            df_filtered.to_excel(writer, index=False, sheet_name='报工数据')
            
            # 获取工作表对象进行格式化
            worksheet = writer.sheets['报工数据']
            
            # 调整列宽
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # 添加总计行到工作表末尾
            total_row_idx = len(df_filtered) + 2  # +2 因为有表头和从1开始的索引
            worksheet.cell(row=total_row_idx, column=3, value='总计')  # 在工序列显示"总计"
            worksheet.cell(row=total_row_idx, column=12, value=total_finished_qty)  # 报工数量列
            worksheet.cell(row=total_row_idx, column=16, value=total_theory_hours)  # 理论工时列
        
        output.seek(0)
        
        # 生成文件名
        filename = f"报工数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        # 对文件名进行URL编码
        encoded_filename = urllib.parse.quote(filename)
        
        print(f"✅ Excel导出完成！共 {len(df_filtered)} 条数据")
        
        return StreamingResponse(
            io.BytesIO(output.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )
        
    except Exception as e:
        print(f"❌ 导出Excel失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"导出Excel失败: {str(e)}")

