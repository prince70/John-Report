import pyodbc
from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from fastapi.responses import JSONResponse
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def get_db_connection():
    try:
        logger.info("尝试连接到SQL Server数据库...")
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=192.168.41.57;"
            "DATABASE=department2020;"
            "UID=sa;"
            "PWD=3518i"
        )
        logger.info("数据库连接成功")
        return conn
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        raise

@router.get("/warning/assembly-early")
async def get_assembly_early():
    try:
        logger.info("开始处理装嵌提前一周完成数据请求")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT a.JobExternalId AS 工单编号,
               a.OrderNumber AS 订单批号,
               a.ItemExternalId AS 料品编码, 
               a.ResName AS 生产线编号,
               a.ProductDescription AS 规格型号,
               a.emp_item_no AS 工号,
               a.emp_name AS 姓名,
               a.EachFinishedQty AS 报工数量,
               a.repairQty AS 返修数量,
               a.scrapQty AS 报废数量,
               a.StartDate AS 报工开始时间,
               a.FinishedDate AS 报工结束时间,
               b.确定交期
        FROM APS_FinishedQty a
        LEFT JOIN 派工单 b ON a.JobExternalId = b.工单编号
        WHERE 
            b.确定交期 IS NOT NULL 
            AND a.FinishedDate IS NOT NULL
            AND DATEDIFF(day, a.FinishedDate, b.确定交期) > 7
            AND b.确定交期 >= GETDATE()
        """
        
        logger.info("执行SQL查询")
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        results = []
        
        logger.info("处理查询结果")
        for row in cursor.fetchall():
            result_dict = {}
            for i, value in enumerate(row):
                # Convert datetime objects to string for JSON serialization
                if isinstance(value, (pyodbc.Date, pyodbc.Time, pyodbc.Timestamp)):
                    result_dict[columns[i]] = value.isoformat() if value else None
                else:
                    result_dict[columns[i]] = value
            results.append(result_dict)
        
        logger.info(f"查询完成，返回{len(results)}条记录")
        cursor.close()
        conn.close()
        
        # 返回与patent.py相同格式的响应
        return {
            "status": "success",
            "data": results,
            "message": "数据获取成功"
        }
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        return {
            "status": "error",
            "data": [],
            "message": f"Database error: {str(e)}"
        }
