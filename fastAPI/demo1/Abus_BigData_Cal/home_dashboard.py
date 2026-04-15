#  与前端的home.vue相关
from fastapi import APIRouter, HTTPException, status
from fastapi_cache.decorator import cache
from datetime import datetime
from pydantic_settings import BaseSettings
import os
import pyodbc
import pandas as pd

router = APIRouter(prefix="/home", tags=["home"])

class Settings(BaseSettings):
    db_server: str = os.getenv("DB_SERVER", "192.168.1.1")
    db_database: str = os.getenv("DB_DATABASE", "huayueerp")
    db_username: str = os.getenv("DB_USERNAME", "sa")
    db_password: str = os.getenv("DB_PASSWORD", "3518i")

settings = Settings()

def get_db_connection():
    conn_str = (
        f"DRIVER={{SQL Server}};SERVER={settings.db_server};DATABASE={settings.db_database};"
        f"UID={settings.db_username};PWD={settings.db_password};"
    )
    try:
        return pyodbc.connect(conn_str)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"数据库连接失败: {exc}")

def get_department_db_connection():
    """连接到 department2020 数据库"""
    conn_str = (
        f"DRIVER={{SQL Server}};SERVER=192.168.41.57;DATABASE=department2020;"
        f"UID=sa;PWD=3518i;"
    )
    try:
        return pyodbc.connect(conn_str)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"department2020数据库连接失败: {exc}")


@router.get(
    "/dashboard",
    summary="首页仪表盘数据",
    description="返回本月订单统计、完成情况饼图数据以及本月按锁类分区汇总的柱状图数据"
)
@cache(expire=1800)
async def get_home_dashboard():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 计算当月的起止时间（含起，不含下月起始）
        # 使用与给定 SQL 一致的 SQL Server 计算方式
        # 订单批号数量
        sql_month_count = (
            "SELECT COUNT(*) AS 本月订单数 "
            "FROM osal_ord2 a "
            "LEFT JOIN osal_ord1 b ON a.sheet_no = b.sheet_no "
            "WHERE a.affirm_date >= CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME) "
            "AND a.affirm_date < DATEADD(MONTH, 1, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME))"
        )
        cursor.execute(sql_month_count)
        monthly_order_count = int(cursor.fetchone()[0] or 0)

        # 本月订单只数
        sql_month_qty = (
            "SELECT SUM(ISNULL(sheet_qty,0)) AS 本月订单只数 "
            "FROM osal_ord2 a "
            "LEFT JOIN osal_ord1 b ON a.sheet_no = b.sheet_no "
            "LEFT JOIN obas_part c on a.part_no = c.part_no "
            "WHERE a.affirm_date >= CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME) "
            "AND a.affirm_date < DATEADD(MONTH, 1, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME))"
            "AND c.item_no not like '115%' and c.item_no not like '116%' "
            "AND c.part_name not like '%TSA%' "
        )
        cursor.execute(sql_month_qty)
        monthly_total_qty = int((cursor.fetchone()[0] or 0))

        # 本月已完成只数（截至今天）
        sql_completed_qty = (
            "SELECT SUM(ISNULL(sheet_qty,0)) AS 本月已完成只数 "
            "FROM osal_ord2 a "
            "LEFT JOIN osal_ord1 b ON a.sheet_no = b.sheet_no "
              "LEFT JOIN obas_part c on a.part_no = c.part_no "
            "WHERE a.affirm_date >= CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME) "
            "AND a.affirm_date < CAST(CONVERT(VARCHAR(10), GETDATE(), 120) AS DATETIME)"
              "AND c.item_no not like '115%' and c.item_no not like '116%' "
            "AND c.part_name not like '%TSA%' "
            
        )
        cursor.execute(sql_completed_qty)
        monthly_completed_qty = int((cursor.fetchone()[0] or 0))

        # 本月产品销往国家总数
        sql_country_count = (
            "SELECT COUNT(DISTINCT b.delivery_addr) AS 国家总数 "
            "FROM osal_ord2 a "
            "LEFT JOIN osal_ord1 b ON a.sheet_no = b.sheet_no "
            "WHERE a.affirm_date >= CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME) "
            "AND a.affirm_date < DATEADD(MONTH, 1, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME)) "
            "AND b.delivery_addr IS NOT NULL"
        )
        cursor.execute(sql_country_count)
        country_count = int(cursor.fetchone()[0] or 0)

        # 饼图数据：已完成 vs 未完成（只数）
        unfinished_qty = max(0, monthly_total_qty - monthly_completed_qty)
        pie_data = [
            {"name": "已完成只数", "value": monthly_completed_qty},
            {"name": "未完成只数", "value": unfinished_qty}
        ]

        # 柱状图：本月按锁类分区汇总（来自 OV_TSA，字段 锁类分区1）
        # 仍使用当月 affirm_date 过滤条件
        sql_category = (
            "SELECT ISNULL([锁类分区1], '未分类') AS category, "
            "       SUM(CAST(ISNULL([sheet_qty],0) AS FLOAT)) AS qty "
            "FROM [huayueerp].[dbo].[OV_TSA] "
            "WHERE affirm_date >= CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME) "
            "  AND affirm_date < DATEADD(MONTH, 1, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME)) "
            "GROUP BY [锁类分区1]"
        )
        df_cat = pd.read_sql(sql_category, conn)
        category_bar = (
            df_cat.sort_values(by="qty", ascending=False)
            .assign(qty=lambda d: d["qty"].astype(int))
            .to_dict(orient="records")
        )

        cursor.close()
        conn.close()

        return {
            "status": "success",
            "data": {
                "monthly_order_count": monthly_order_count,
                "monthly_total_qty": monthly_total_qty,
                "monthly_completed_qty": monthly_completed_qty,
                "country_count": country_count,
                "pie": pie_data,
                "category_bar": category_bar
            },
            "timestamp": datetime.now().isoformat()
        }
    except pyodbc.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库错误: {exc}"
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {exc}"
        )

# 2025-10-21新增的4种原因
@router.get(
    "/order-change-reasons",
    summary="订单交期修改原因统计",
    description="返回客人原因和工厂原因的订单交期修改统计数据（上月改当月、当月改下月）"
)
@cache(expire=1800)
async def get_order_change_reasons():
    """
    查询4个原因的统计数据：
    1. 客人原因-上月改当月
    2. 客人原因-当月改下月
    3. 工厂原因-上月改当月
    4. 工厂原因-当月改下月
    """
    try:
        conn = get_department_db_connection()
        cursor = conn.cursor()
        
        # 使用 UNION ALL 一次性查询4个原因
        sql_reasons = """
        -- 1. 客人原因：修改前-确定交期是上个月，修改至当月
        SELECT 
            '客人原因-上月改当月' AS 统计类型,
            SUM([订单数量]) AS 订单数量总和,
            SUM([装嵌完成数量]) AS 装嵌完成数量总和
        FROM [department2020].[dbo].[erp_osal_ord2_log_report]
        WHERE [订单备注] = '客人原因'
            AND YEAR([修改前-确定交期]) = YEAR(DATEADD(MONTH, -1, GETDATE()))
            AND MONTH([修改前-确定交期]) = MONTH(DATEADD(MONTH, -1, GETDATE()))
            AND YEAR([修改后-确定交期]) = YEAR(GETDATE())
            AND MONTH([修改后-确定交期]) = MONTH(GETDATE())
			AND (
            料品名称 NOT LIKE '%配件%'
        AND 料品名称 NOT LIKE '%包装%'
        AND 料品名称 <> 'TSA006'
        )


        UNION ALL

        -- 2. 客人原因：修改前-确定交期是当月，修改至下个月
        SELECT 
            '客人原因-当月改下月' AS 统计类型,
            SUM([订单数量]) AS 订单数量总和,
            SUM([装嵌完成数量]) AS 装嵌完成数量总和
        FROM [department2020].[dbo].[erp_osal_ord2_log_report]
        WHERE [订单备注] = '客人原因'
            AND YEAR([修改前-确定交期]) = YEAR(GETDATE())
            AND MONTH([修改前-确定交期]) = MONTH(GETDATE())
            AND YEAR([修改后-确定交期]) = YEAR(DATEADD(MONTH, 1, GETDATE()))
            --AND MONTH([修改后-确定交期]) = MONTH(DATEADD(MONTH, 1, GETDATE()))
			AND [修改后-确定交期] >= DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()) + 1, 0)
				AND (
            料品名称 NOT LIKE '%配件%'
        AND 料品名称 NOT LIKE '%包装%'
        AND 料品名称 <> 'TSA006'
        )

        UNION ALL

        -- 3. 工厂原因：修改前-确定交期是上个月，修改至当月
        SELECT 
            '工厂原因-上月改当月' AS 统计类型,
            SUM([订单数量]) AS 订单数量总和,
            SUM([装嵌完成数量]) AS 装嵌完成数量总和
        FROM [department2020].[dbo].[erp_osal_ord2_log_report]
        WHERE [订单备注] = '工厂原因'
            AND YEAR([修改前-确定交期]) = YEAR(DATEADD(MONTH, -1, GETDATE()))
            AND MONTH([修改前-确定交期]) = MONTH(DATEADD(MONTH, -1, GETDATE()))
            AND YEAR([修改后-确定交期]) = YEAR(GETDATE())
            AND MONTH([修改后-确定交期]) = MONTH(GETDATE())
				AND (
            料品名称 NOT LIKE '%配件%'
        AND 料品名称 NOT LIKE '%包装%'
        AND 料品名称 <> 'TSA006'
        )
        UNION ALL

        -- 4. 工厂原因：修改前-确定交期是当月，修改至下个月
        SELECT 
            '工厂原因-当月改下月' AS 统计类型,
            SUM([订单数量]) AS 订单数量总和,
            SUM([装嵌完成数量]) AS 装嵌完成数量总和
        FROM [department2020].[dbo].[erp_osal_ord2_log_report]
        WHERE [订单备注] = '工厂原因'
            AND YEAR([修改前-确定交期]) = YEAR(GETDATE())
            AND MONTH([修改前-确定交期]) = MONTH(GETDATE())
            AND YEAR([修改后-确定交期]) = YEAR(DATEADD(MONTH, 1, GETDATE()))
           -- AND MONTH([修改后-确定交期]) = MONTH(DATEADD(MONTH, 1, GETDATE()))

			AND [修改后-确定交期] >= DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()) + 1, 0)
				AND (
            料品名称 NOT LIKE '%配件%'
        AND 料品名称 NOT LIKE '%包装%'
        AND 料品名称 <> 'TSA006'
        )
        """
        
        cursor.execute(sql_reasons)
        rows = cursor.fetchall()
        
        # 将结果转换为字典列表
        reasons_data = []
        for row in rows:
            reasons_data.append({
                "统计类型": row[0],
                "订单数量总和": int(row[1] or 0),
                "装嵌完成数量总和": int(row[2] or 0)
            })
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": reasons_data,
            "timestamp": datetime.now().isoformat()
        }
    except pyodbc.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库错误: {exc}"
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {exc}"
        ) 


@router.get(
    "/next-month-dashboard",
    summary="下个月仪表盘数据",
    description="返回下个月订单统计、销往国家数、订单总只数、装嵌和包装完成数等数据"
)
@cache(expire=1800)
async def get_next_month_dashboard():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 下月订单总数
        sql_next_month_total_orders = """
            SELECT count(distinct a.sheet_no) as 下月订单数
            FROM osal_ord2 a
            LEFT JOIN osal_ord1 b ON a.sheet_no = b.sheet_no
            WHERE a.affirm_date >= DATEADD(MONTH, 1, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME))
              AND a.affirm_date <  DATEADD(MONTH, 2, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME))
        """
        cursor.execute(sql_next_month_total_orders)
        next_month_total_orders = int(cursor.fetchone()[0] or 0)

        # 下月订单批次数
        sql_next_month_batch_count = """
            SELECT count(*) as 下月订单批次数
            FROM osal_ord2 a
            LEFT JOIN osal_ord1 b ON a.sheet_no = b.sheet_no
            WHERE a.affirm_date >= DATEADD(MONTH, 1, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME))
              AND a.affirm_date <  DATEADD(MONTH, 2, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME))
        """
        cursor.execute(sql_next_month_batch_count)
        next_month_batch_count = int(cursor.fetchone()[0] or 0)

        # 下月销往国家数
        sql_next_month_country_count = """
            SELECT count(distinct b.delivery_addr) as 下月国家总数
            FROM osal_ord2 a
            LEFT JOIN osal_ord1 b ON a.sheet_no = b.sheet_no
            WHERE a.affirm_date >= DATEADD(MONTH, 1, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME))
              AND a.affirm_date <  DATEADD(MONTH, 2, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME))
              and b.delivery_addr is not null
        """
        cursor.execute(sql_next_month_country_count)
        next_month_country_count = int(cursor.fetchone()[0] or 0)

        # 下月订单总只数
        sql_next_month_total_qty = """
            SELECT sum(isnull(sheet_qty,0)) as 下月订单只数
            FROM osal_ord2 a
            LEFT JOIN osal_ord1 b ON a.sheet_no = b.sheet_no
            left join obas_part c on a.part_no = c.part_no
            WHERE a.affirm_date >= DATEADD(MONTH, 1, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME))
            AND a.affirm_date <  DATEADD(MONTH, 2, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME))
            and c.item_no not like '115%' and c.item_no not like '116%'
            and c.part_name not like '%TSA%'
        """
        cursor.execute(sql_next_month_total_qty)
        next_month_total_qty = int((cursor.fetchone()[0] or 0))

        # 下月装嵌完成数
        # 注意：需要切换到192.168.41.57的数据库连接
        # 为了简化，这里创建一个新的连接
        try:
            next_conn = pyodbc.connect(
                "DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.41.57;DATABASE=department2020;UID=sa;PWD=3518i;"
            )
            next_cursor = next_conn.cursor()

            # 下月装嵌完成数
            sql_next_month_assembly_qty = """
                select isnull(sum(EachFinishedQty),0) as [下月装嵌完成数量/只]
                from (
                    select distinct OrderNumber, EachFinishedQty,确定交期
                    from APS_FinishedQty a
                        left join 派工单 b
                    on a.JobExternalId = b.工单编号
                    WHERE FinishedDate >= DATEADD(MONTH, 1, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME))
                  AND FinishedDate <  DATEADD(MONTH, 2, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME))
                ) t;
            """
            next_cursor.execute(sql_next_month_assembly_qty)
            next_month_assembly_qty = int((next_cursor.fetchone()[0] or 0))

            # 下月包装完成数
            sql_next_month_packaging_qty = """
                select isnull(sum(EachFinishedQty),0) as [下月包装完成数量/只]
                from (
                    select distinct OrderNumber, EachFinishedQty
                    from APS_FinishedQty_Pack a
                    left join 派工单 b
                    on a.JobExternalId = b.工单编号
                    WHERE FinishedDate >= DATEADD(MONTH, 1, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME))
                  AND FinishedDate <  DATEADD(MONTH, 2, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME))
                ) t;
            """
            next_cursor.execute(sql_next_month_packaging_qty)
            next_month_packaging_qty = int((next_cursor.fetchone()[0] or 0))

            next_cursor.close()
            next_conn.close()
        except Exception as exc:
            # 如果获取装嵌和包装数据失败，设置为0
            next_month_assembly_qty = 0
            next_month_packaging_qty = 0

        # 下月已落货数量（默认为0，因为无法从现有信息推断）
        next_month_shipped_qty = 0

        cursor.close()
        conn.close()

        return {
            "status": "success",
            "data": {
                "next_month_total_orders": next_month_total_orders,
                "next_month_batch_count": next_month_batch_count,
                "next_month_country_count": next_month_country_count,
                "next_month_total_qty": next_month_total_qty,
                "next_month_assembly_qty": next_month_assembly_qty,
                "next_month_packaging_qty": next_month_packaging_qty,
                "next_month_shipped_qty": next_month_shipped_qty
            },
            "timestamp": datetime.now().isoformat()
        }
    except pyodbc.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库错误: {exc}"
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {exc}"
        )


@router.get(
    "/order-completion",
    summary="订单完成情况饼图数据",
    description="返回本月订单总数和已完成订单数的饼图数据"
)
# @cache(expire=1800)  # 临时禁用缓存用于测试
async def get_order_completion():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 本月订单总数
        sql_total_orders = """
            SELECT count(distinct a.sheet_no) as 本月订单数
            FROM osal_ord2 a
            LEFT JOIN osal_ord1 b ON a.sheet_no = b.sheet_no
            WHERE a.affirm_date >= CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME)
              AND a.affirm_date < DATEADD(MONTH, 1, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME))
        """
        cursor.execute(sql_total_orders)
        total_orders = int(cursor.fetchone()[0] or 0)

        # 本月已完成订单批号数
        sql_completed_orders = """
            SELECT count( distinct a.sheet_lot) AS 本月已完成订单批号
            FROM osal_ord2 a
            LEFT JOIN osal_ord1 b ON a.sheet_no = b.sheet_no
            WHERE a.affirm_date >=CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME)
              AND a.affirm_date <  CAST(CONVERT(VARCHAR(10), GETDATE(), 120) AS DATETIME)
        """
        cursor.execute(sql_completed_orders)
        completed_orders = int(cursor.fetchone()[0] or 0)

        # 计算未完成订单数
        pending_orders = total_orders - completed_orders

        # 构建饼图数据
        pie_data = [
            {"name": "已完成", "value": completed_orders},
            {"name": "进行中", "value": pending_orders}
        ]

        cursor.close()
        conn.close()

        return {
            "status": "success",
            "data": {
                "total_orders": total_orders, 
                "completed_orders": completed_orders,
                "pending_orders": pending_orders,
                "pie_data": pie_data
            },
            "timestamp": datetime.now().isoformat()
        }
    except pyodbc.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库错误: {exc}"
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {exc}"
        )


@router.get(
    "/delivery-addresses",
    summary="交货地址列表",
    description="返回本月订单的所有交货地址列表"
)
@cache(expire=1800)
async def get_delivery_addresses():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取本月订单的交货地址
        sql_addresses = """
            SELECT DISTINCT b.delivery_addr 
            FROM osal_ord2 a
            LEFT JOIN osal_ord1 b ON a.sheet_no = b.sheet_no
            WHERE a.affirm_date >= CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME)
              AND a.affirm_date < DATEADD(MONTH, 1, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME))
              AND b.delivery_addr IS NOT NULL
              AND b.delivery_addr != ''
            ORDER BY b.delivery_addr
        """
        cursor.execute(sql_addresses)
        results = cursor.fetchall()

        # 转换为列表格式
        addresses = [{"address": row[0]} for row in results if row[0]]

        cursor.close()
        conn.close()

        return {
            "status": "success",
            "data": {
                "addresses": addresses,
                "total_count": len(addresses)
            },
            "timestamp": datetime.now().isoformat()
        }
    except pyodbc.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库错误: {exc}"
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {exc}"
        )


@router.get(
    "/delivery-address-sales",
    summary="交货地址销量列表",
    description="返回本月各交货地址的订单只数汇总（销量）"
)
@cache(expire=1800)
async def get_delivery_address_sales():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql_address_sales = (
            "SELECT b.delivery_addr, SUM(ISNULL(a.sheet_qty,0)) AS 订单总数 "
            "FROM osal_ord2 a "
            "LEFT JOIN osal_ord1 b ON a.sheet_no = b.sheet_no "
            "LEFT JOIN obas_part c ON a.part_no = c.part_no "
            "WHERE a.affirm_date >= CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME) "
            "  AND a.affirm_date < DATEADD(MONTH, 1, CAST(CONVERT(VARCHAR(7), GETDATE(), 120) + '-01' AS DATETIME)) "
            "  AND b.delivery_addr IS NOT NULL "
            "  AND c.item_no not like '115%' "
            "  AND c.item_no not like '116%' "
            "  AND c.part_name not like '%TSA%' "
            "GROUP BY b.delivery_addr "
            "ORDER BY SUM(ISNULL(a.sheet_qty,0)) DESC"
        )
        cursor.execute(sql_address_sales)
        rows = cursor.fetchall()

        addresses = [
            {"address": row[0], "qty": int(row[1] or 0)}
            for row in rows if row and row[0]
        ]

        cursor.close()
        conn.close()

        return {
            "status": "success",
            "data": {
                "addresses": addresses,
                "total_count": len(addresses)
            },
            "timestamp": datetime.now().isoformat()
        }
    except pyodbc.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库错误: {exc}"
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {exc}"
        )