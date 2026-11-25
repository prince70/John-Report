from fastapi import APIRouter, HTTPException
import pyodbc
from typing import List, Dict, Optional
import pandas as pd

router = APIRouter()

# 数据库连接配置
DB_SERVER = "192.168.41.57"
DB_DATABASE = "Cost_Calculation"
DB_USERNAME = "sa"
DB_PASSWORD = "3518i"

# 允许查询的列白名单，防止SQL注入
ALLOWED_COLUMNS = [
    'product_id', 'product_name', 'product_spec',
    'part_id', 'part_name',
    'processes_id', 'processes_name', 'processes_unit', 'processes_sort',
    'unit_cost'
]

def get_db_connection():
    """获取数据库连接"""
    try:
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USERNAME};PWD={DB_PASSWORD}"
        return pyodbc.connect(conn_str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库连接失败: {str(e)}")

@router.get("/cost/columns", summary="获取所有列的唯一值")
async def get_unique_values(
    column: str,
    product_name: Optional[str] = None,
    product_id: Optional[str] = None,
    product_spec: Optional[str] = None,
    part_id: Optional[str] = None,
    part_name: Optional[str] = None,
    processes_id: Optional[str] = None,
    processes_name: Optional[str] = None,
    processes_unit: Optional[str] = None,
    processes_sort: Optional[str] = None,
    unit_cost: Optional[str] = None,
):
    """获取指定列的唯一值，支持级联筛选"""
    try:
        # 列名白名单校验，防止注入
        if column not in ALLOWED_COLUMNS:
            raise HTTPException(status_code=400, detail=f"不支持的列名: {column}")

        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = f"SELECT DISTINCT [{column}] FROM [Cost_Calculation].[dbo].[VV_Cost]"
        conditions = []
        params = []
        
        # 根据传入的筛选条件构建WHERE子句
        if product_id and product_id != "全部":
            conditions.append("[product_id] = ?")
            params.append(product_id)
        
        if product_name and product_name != "全部":
            conditions.append("[product_name] = ?")
            params.append(product_name)
            
        if product_spec and product_spec != "全部":
            conditions.append("[product_spec] = ?")
            params.append(product_spec)
            
        if part_id and part_id != "全部":
            conditions.append("[part_id] = ?")
            params.append(part_id)
            
        if part_name and part_name != "全部":
            conditions.append("[part_name] = ?")
            params.append(part_name)

        if processes_id and processes_id != "全部":
            conditions.append("[processes_id] = ?")
            params.append(processes_id)

        if processes_name and processes_name != "全部":
            conditions.append("[processes_name] = ?")
            params.append(processes_name)

        if processes_unit and processes_unit != "全部":
            conditions.append("[processes_unit] = ?")
            params.append(processes_unit)

        if processes_sort and processes_sort != "全部":
            conditions.append("[processes_sort] = ?")
            params.append(processes_sort)

        if unit_cost and unit_cost != "全部":
            conditions.append("[unit_cost] = ?")
            params.append(unit_cost)
        
        # 如果有筛选条件，添加WHERE子句
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # 对结果排序，提升可用性
        query += f" ORDER BY [{column}]"
        
        cursor.execute(query, params)
        values = [row[0] for row in cursor.fetchall() if row[0] is not None]
        cursor.close()
        conn.close()
        
        return {"column": column, "values": values}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")

@router.post("/cost/filter", summary="根据条件筛选数据")
async def filter_data(filters: Dict[str, str]):
    """根据筛选条件获取数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 构建查询语句
        query = "SELECT * FROM [Cost_Calculation].[dbo].[VV_Cost]"
        conditions = []
        params = []
        
        # 按优先级顺序处理筛选条件
        priority_filters = [
            'product_id', 'product_name', 'product_spec',
            'part_id', 'part_name',
            'processes_id', 'processes_name', 'processes_unit', 'processes_sort',
            'unit_cost'
        ]
        
        # 处理筛选条件，过滤掉空值和"全部"
        for col in priority_filters:
            if col in filters and filters[col] and filters[col] != "全部":
                conditions.append(f"[{col}] = ?")
                params.append(filters[col])
        
        # 如果有筛选条件，添加WHERE子句
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        cursor.execute(query, params)
        
        # 获取列名
        columns = [column[0] for column in cursor.description]
        
        # 获取数据
        rows = cursor.fetchall()
        results = []
        
        for row in rows:
            row_dict = {}
            for i, value in enumerate(row):
                # 对单位成本字段进行特殊处理，确保四位小数
                if columns[i] == 'unit_cost' and value is not None:
                    row_dict[columns[i]] = round(float(value), 4)
                else:
                    row_dict[columns[i]] = value
            results.append(row_dict)
        
        cursor.close()
        conn.close()
        
        return {
            "total_count": len(results),
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"筛选数据失败: {str(e)}")

@router.post("/cost/calculate", summary="计算筛选结果的总成本")
async def calculate_total_cost(filters: Dict[str, str]):
    """计算筛选结果的总成本"""
    try:
        print(f"计算总成本，接收到的筛选条件: {filters}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 构建查询语句
        query = "SELECT SUM(unit_cost) as total_cost FROM [Cost_Calculation].[dbo].[VV_Cost]"
        conditions = []
        params = []
        
        # 按优先级顺序处理筛选条件
        priority_filters = [
            'product_id', 'product_name', 'product_spec',
            'part_id', 'part_name',
            'processes_id', 'processes_name', 'processes_unit', 'processes_sort',
            'unit_cost'
        ]
        
        # 处理筛选条件，过滤掉空值和"全部"
        for col in priority_filters:
            if col in filters and filters[col] and filters[col] != "全部":
                conditions.append(f"[{col}] = ?")
                params.append(filters[col])
        
        # 如果有筛选条件，添加WHERE子句
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        print(f"执行的SQL查询: {query}")
        print(f"查询参数: {params}")
        
        # 执行查询
        cursor.execute(query, params)
        result = cursor.fetchone()
        
        print(f"查询结果: {result}")
        
        # 获取总成本，如果为None则设为0
        total_cost = result[0] if result[0] is not None else 0
        
        print(f"计算得到的总成本: {total_cost}")
        
        cursor.close()
        conn.close()
        
        # 返回四位小数的总成本
        final_cost = round(float(total_cost), 4)
        print(f"返回的总成本: {final_cost}")
        
        return {"total_cost": final_cost}
    except Exception as e:
        print(f"计算总成本时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"计算成本失败: {str(e)}") 