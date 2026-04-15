from fastapi import APIRouter, HTTPException
from pydantic_settings import BaseSettings
import os
import pyodbc
from datetime import datetime
from fastapi_cache.decorator import cache

router = APIRouter()

class Settings(BaseSettings):
    db_server: str = os.getenv("DB_SERVER", "192.168.41.57")
    db_database: str = os.getenv("DB_DATABASE", "department2020")
    db_username: str = os.getenv("DB_USERNAME", "sa")
    db_password: str = os.getenv("DB_PASSWORD", "3518i")

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

@router.get("/finished_qty", summary="获取装嵌和包装完成数量")
@cache(expire=3600)  # 缓存1小时
async def get_finished_qty():
    """
    获取本月和下月的装嵌、包装完成数量
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 本月装嵌完成数量查询
        sql_monthly_assembly = """
        select sum(EachFinishedQty) as [本月装嵌完成数量/只]
        from (
            select distinct OrderNumber, EachFinishedQty,affirm_date
            from APS_FinishedQty a
                 left join 
				  OPENDATASOURCE ('msdasql', 
                'driver={sql server};server=192.168.1.1;uid=sa;pwd=3518i;' ).huayueERP.dbo.osal_ord2 b
             on a.OrderNumber = b.sheet_lot
             WHERE b.affirm_date >= CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME)
          AND b.affirm_date < DATEADD(MONTH, 1, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME))
               and a.ResName like 'ZQ-%'
  and a.ItemExternalId not like '115%'
  and a.ItemExternalId not like '116%'
  and a.ProductDescription not like '%TSA%'
  and a.JobExternalId not like '%中间件%'

        ) t;
        """
        
        # 本月包装完成数量查询
        sql_monthly_pack = """
        select sum(EachFinishedQty) as [本月包装完成数量/只]
        from (
            select distinct OrderNumber, EachFinishedQty
            from APS_FinishedQty_Pack a
                 left join 
				  OPENDATASOURCE ('msdasql', 
                'driver={sql server};server=192.168.1.1;uid=sa;pwd=3518i;' ).huayueERP.dbo.osal_ord2 b
             on a.OrderNumber = b.sheet_lot
			 left join   OPENDATASOURCE ('msdasql', 
                'driver={sql server};server=192.168.1.1;uid=sa;pwd=3518i;' ).huayueERP.dbo.obas_part c
				on b.part_no = c.part_no
             WHERE b.affirm_date >= CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME)
          AND b.affirm_date < DATEADD(MONTH, 1, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME))
          and c.item_no not like '115%'
  and c.item_no not like '116%'
  and a.ProductDescription not like '%TSA%'
  and a.JobExternalId like '%盒%'
        ) t;
        """
        
        # 下月装嵌完成数量查询
        sql_next_month_assembly = """
        select isnull(sum(EachFinishedQty),0) as [下月装嵌完成数量/只]
        from (
         select distinct OrderNumber, EachFinishedQty,affirm_date
            from APS_FinishedQty a
                 left join 
				  OPENDATASOURCE ('msdasql', 
                'driver={sql server};server=192.168.1.1;uid=sa;pwd=3518i;' ).huayueERP.dbo.osal_ord2 b
             on a.OrderNumber = b.sheet_lot
             WHERE b.affirm_date >= DATEADD(MONTH, 1, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME))
          AND b.affirm_date < DATEADD(MONTH, 2, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME))
               and a.ResName like 'ZQ-%'
  and a.ItemExternalId not like '115%'
  and a.ItemExternalId not like '116%'
  and a.ProductDescription not like '%TSA%'
  and a.JobExternalId not like '%中间件%'
        ) t;
        """
        
        # 下月包装完成数量查询
        sql_next_month_pack = """
        select isnull(sum(EachFinishedQty),0) as [下月包装完成数量/只]
        from (
        select distinct OrderNumber, EachFinishedQty
            from APS_FinishedQty_Pack a
                 left join 
				  OPENDATASOURCE ('msdasql', 
                'driver={sql server};server=192.168.1.1;uid=sa;pwd=3518i;' ).huayueERP.dbo.osal_ord2 b
             on a.OrderNumber = b.sheet_lot
			 left join   OPENDATASOURCE ('msdasql', 
                'driver={sql server};server=192.168.1.1;uid=sa;pwd=3518i;' ).huayueERP.dbo.obas_part c
				on b.part_no = c.part_no
             WHERE b.affirm_date >= DATEADD(MONTH, 1, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME))
          AND b.affirm_date <  DATEADD(MONTH, 2, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME))
          and c.item_no not like '115%'
  and c.item_no not like '116%'
  and a.ProductDescription not like '%TSA%'
  and a.JobExternalId like '%盒%'
        ) t;
        """
        
        # 执行查询并获取结果
        results = {
            "status": "success",
            "data": {}
        }
        
        # 获取本月装嵌完成数量
        cursor.execute(sql_monthly_assembly)
        row = cursor.fetchone()
        results["data"]["本月装嵌完成数量"] = float(row[0]) if row and row[0] is not None else 0.0
        
        # 获取本月包装完成数量
        cursor.execute(sql_monthly_pack)
        row = cursor.fetchone()
        results["data"]["本月包装完成数量"] = float(row[0]) if row and row[0] is not None else 0.0
        
        # 获取下月装嵌完成数量
        cursor.execute(sql_next_month_assembly)
        row = cursor.fetchone()
        results["data"]["下月装嵌完成数量"] = float(row[0]) if row and row[0] is not None else 0.0
        
        # 获取下月包装完成数量
        cursor.execute(sql_next_month_pack)
        row = cursor.fetchone()
        results["data"]["下月包装完成数量"] = float(row[0]) if row and row[0] is not None else 0.0
        
        # 添加时间戳
        results["timestamp"] = datetime.now().isoformat()
        
        return results
        
    except Exception as exc:
        print(f"获取完成数量失败: {exc}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

@router.get("/finished_qty/test", summary="测试数据库连接")
async def test_connection():
    """测试数据库连接"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        return {
            "status": "success",
            "message": "数据库连接正常",
            "test_result": result[0] if result else None,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as exc:
        print(f"数据库连接测试失败: {exc}")
        raise HTTPException(status_code=500, detail=f"数据库连接失败: {exc}")
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass