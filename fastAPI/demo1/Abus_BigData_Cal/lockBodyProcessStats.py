from fastapi import APIRouter, HTTPException, Query
from pydantic_settings import BaseSettings
from typing import Optional
import os
import pyodbc
import io
from datetime import datetime, date
from collections import defaultdict
from fastapi.responses import StreamingResponse
from fastapi_cache.decorator import cache


def format_datetime_value(val):
    """将 datetime/date 对象转换为字符串，否则直接返回"""
    if isinstance(val, (datetime, date)):
        return val.strftime('%Y-%m-%d')
    return val if val else ""

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

def get_lock_body_data_from_db():
    """从数据库获取锁体C分区域库存原始数据"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = """
        select a.工单编号,a.工单状态,a.生产车间,a.订单批号,a.料品编码,a.料品名称,a.规格型号,a.计划产量,a.实际产量,a.确定交期,a.OpExternalId,b.锁类分区 from 派工单 a
  left join [V_销售订单2] b

  on a.订单批号 = b.sheet_lot
  
  where (a.生产车间 like '锁体C%' and a.确定交期 >getdate() 
  and (a.OpExternalId like '%自动机' or a.OpExternalId like '%加工线' or a.OpExternalId = '拣锁体') and b.锁类分区='铝门锁')

  or a.生产车间='开料车间' and OpExternalId ='流转'  and b.锁类分区='铝门锁' and a.确定交期 >getdate()
        """
        
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        raw_data = []
        for row in rows:
            raw_data.append({
                "工单编号": row[0],
                "工单状态": row[1] if row[1] else "",
                "生产车间": row[2] if row[2] else "",
                "订单批号": row[3],
                "料品编码": row[4] if row[4] else "",
                "料品名称": row[5] if row[5] else "",
                "规格型号": row[6] if row[6] else "",
                "计划产量": float(row[7]) if row[7] else 0,
                "实际产量": float(row[8]) if row[8] else 0,
                "确定交期": format_datetime_value(row[9]),
                "OpExternalId": row[10] if row[10] else "",
                "锁类分区": row[11] if row[11] else ""
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

def process_lock_body_data(raw_data, order_no=None, item_name=None, item_code=None):
    """处理锁体C分区域库存数据"""
    order_data = defaultdict(lambda: {
        "料品编码": "",
        "料品名称": "",
        "规格型号": "",
        "计划产量": 0,
        "确定交期": "",
        "流转_完成量": 0,
        "自动机_完成量": 0,
        "自动机_可用库存": 0,
        "加工线_完成量": 0,
        "加工线_可用库存": 0,
        "拣锁体_完成量": 0,
        "拣锁体_可用库存": 0
    })
    
    for row in raw_data:
        订单批号 = row["订单批号"]
        料品编码 = row["料品编码"]
        料品名称 = row["料品名称"]
        规格型号 = row["规格型号"]
        计划产量 = row["计划产量"]
        实际产量 = row["实际产量"]
        确定交期 = row["确定交期"]
        OpExternalId = row["OpExternalId"]
        
        if not 订单批号:
            continue
        
        data = order_data[订单批号]
        
        if not data["料品编码"] and 料品编码:
            data["料品编码"] = 料品编码
        if not data["料品名称"] and 料品名称:
            data["料品名称"] = 料品名称
        if not data["规格型号"] and 规格型号:
            data["规格型号"] = 规格型号
        if data["计划产量"] == 0 and 计划产量 > 0:
            data["计划产量"] = 计划产量
        # 确定交期：如果当前为空且有值，则赋值
        if (data["确定交期"] in ("", None) or str(data["确定交期"]).strip() == "") and 确定交期:
            data["确定交期"] = 确定交期
        
        if OpExternalId == "流转":
            data["流转_完成量"] += 实际产量
        elif "自动机" in OpExternalId:
            data["自动机_完成量"] += 实际产量
        elif "加工线" in OpExternalId:
            data["加工线_完成量"] += 实际产量
        elif OpExternalId == "拣锁体":
            data["拣锁体_完成量"] += 实际产量
    
    details = []
    for 订单批号, data in order_data.items():
        # 业务逻辑：库存 = 上游完成量 - 当前工序完成量
        data["自动机_可用库存"] = data["流转_完成量"] - data["自动机_完成量"]
        data["加工线_可用库存"] = data["自动机_完成量"] - data["加工线_完成量"]
        data["拣锁体_可用库存"] = data["加工线_完成量"] - data["拣锁体_完成量"]
        data["订单批号"] = 订单批号
        details.append(data)
    
    details.sort(key=lambda x: x["订单批号"])
    
    # 前端筛选
    if order_no:
        details = [d for d in details if order_no.lower() in str(d.get('订单批号', '')).lower()]
    if item_name:
        details = [d for d in details if item_name.lower() in str(d.get('料品名称', '')).lower()]
    if item_code:
        details = [d for d in details if item_code.lower() in str(d.get('料品编码', '')).lower()]
    
    return details

@router.get("/lock_body_process_stats", summary="锁体C分区域库存计算")
@cache(expire=1800)  # 缓存30分钟
async def get_lock_body_process_stats(
    order_no: Optional[str] = Query(None, description="订单批号（模糊查询）"),
    item_name: Optional[str] = Query(None, description="料品名称（模糊查询）"),
    item_code: Optional[str] = Query(None, description="料品编码（模糊查询）")
):
    """
    锁体C分区域库存计算
    工序流转关系：流转 → 自动机 → 加工线 → 拣锁体
    库存传递规则：上游完成量作为下游的可用库存
    数据缓存30分钟
    """
    try:
        raw_data = get_lock_body_data_from_db()
        details = process_lock_body_data(raw_data, order_no, item_name, item_code)
        
        # 调试：打印前3条记录的确定交期
        if details:
            print(f"DEBUG: 前3条记录的确定交期: {[d.get('确定交期') for d in details[:3]]}")
        
        return {
            "status": "success",
            "data": {
                "details": details,
                "total_count": len(details)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as exc:
        print(f"获取锁体C分区域库存数据失败: {exc}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")

@router.get("/lock_body_process_stats/export", summary="锁体C分区域库存计算导出Excel")
async def export_lock_body_process_stats(
    order_no: Optional[str] = Query(None, description="订单批号"),
    item_name: Optional[str] = Query(None, description="料品名称"),
    item_code: Optional[str] = Query(None, description="料品编码")
):
    """导出锁体C分区域库存数据为Excel"""
    try:
        raw_data = get_lock_body_data_from_db()
        details = process_lock_body_data(raw_data, order_no, item_name, item_code)
        
        excel_buffer = io.BytesIO()
        import xlsxwriter
        
        workbook = xlsxwriter.Workbook(excel_buffer)
        worksheet = workbook.add_worksheet('锁体C分区域库存计算')
        
        headers = ['订单批号', '确定交期', '料品编码', '料品名称', '规格型号', '计划产量', 
                   '流转_完成量', '自动机_完成量', '自动机_可用库存',
                   '加工线_完成量', '加工线_可用库存', 
                   '拣锁体_完成量', '拣锁体_可用库存']
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#eef1f6',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        row = 1
        for item in details:
            worksheet.write(row, 0, item.get('订单批号', ''))
            worksheet.write(row, 1, item.get('确定交期', ''))
            worksheet.write(row, 2, item.get('料品编码', ''))
            worksheet.write(row, 3, item.get('料品名称', ''))
            worksheet.write(row, 4, item.get('规格型号', ''))
            worksheet.write(row, 5, item.get('计划产量', 0))
            worksheet.write(row, 6, item.get('流转_完成量', 0))
            worksheet.write(row, 7, item.get('自动机_完成量', 0))
            worksheet.write(row, 8, item.get('自动机_可用库存', 0))
            worksheet.write(row, 9, item.get('加工线_完成量', 0))
            worksheet.write(row, 10, item.get('加工线_可用库存', 0))
            worksheet.write(row, 11, item.get('拣锁体_完成量', 0))
            worksheet.write(row, 12, item.get('拣锁体_可用库存', 0))
            row += 1
        
        workbook.close()
        
        excel_buffer.seek(0)
        filename = f"锁体C分区域库存计算_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        response = StreamingResponse(
            iter([excel_buffer.getvalue()]),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': f'attachment; filename*=UTF-8\'\'{filename}'
            }
        )
        
        return response
        
    except Exception as exc:
        print(f"导出锁体C分区域库存数据失败: {exc}")
        raise HTTPException(status_code=500, detail=f"导出失败: {exc}")

@router.get("/lock_body_process_stats/test", summary="测试锁体C库存计算连接")
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
        raise HTTPException(status_code=500, detail=f"数据库连接失败: {exc}")
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass
