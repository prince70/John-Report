# APS Requirements 项目申请后端接口
from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional
from fastapi_cache.decorator import cache
from datetime import datetime
from pydantic_settings import BaseSettings
from pydantic import BaseModel
import os
import pyodbc
import pandas as pd

router = APIRouter()

#  表-项目管理
class Settings(BaseSettings):
    db_server: str = os.getenv("DB_SERVER_APS_REQ", "192.168.41.57")
    db_database: str = os.getenv("DB_DATABASE_APS_REQ", "department2020")
    db_username: str = os.getenv("DB_USERNAME_APS_REQ", "sa")
    db_password: str = os.getenv("DB_PASSWORD_APS_REQ", "3518i")


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


# 新增请求体模型
class ProjectCreateRequest(BaseModel):
    项目名称: str
    申请经理: str
    申请原因: str
    预计完成时间: str = None
    批复意见: str = None

class StatusUpdateRequest(BaseModel):
    状态: str

class ApprovalUpdateRequest(BaseModel):
    批复时间: Optional[str] = None
    批复意见: Optional[str] = None


@router.get(
    "/apsRequirements",
    summary="APS 项目需求列表",
    description="查询项目管理表，返回申请时间、项目名称、申请经理、申请原因、预计完成时间、批复意见、批复时间、状态等字段"
)
@cache(expire=600)
async def list_aps_requirements(limit: int = Query(1000, ge=1, le=5000), _t: Optional[int] = None):
    try:
        conn = get_db_connection()
        sql = f"""
            SELECT TOP ({limit})
                [RequestID],
                [申请时间],
                [项目名称],
                [申请经理],
                [申请原因],
                [预计完成时间],
                [批复意见],
                [批复时间],
                [状态]
            FROM [department2020].[dbo].[项目管理]
            ORDER BY [申请时间] DESC
        """
        df = pd.read_sql(sql, conn)
        conn.close()

        # 格式化日期字段为 YYYY-MM-DD
        date_cols = ["申请时间", "预计完成时间", "批复时间"]
        for col in date_cols:
            if col in df.columns:
                # 先检查值的类型，避免对字符串调用strftime
                df[col] = df[col].apply(lambda v: v.strftime("%Y-%m-%d") if pd.notna(v) and hasattr(v, 'strftime') else str(v) if pd.notna(v) else "")

        records = df.to_dict(orient="records")
        columns = df.columns.tolist()

        return {
            "status": "success",
            "data": records,
            "columns": columns,
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


# 在现有路由下方添加创建接口
@router.post("/apsRequirements", status_code=status.HTTP_201_CREATED)
async def create_aps_requirement(item: ProjectCreateRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        insert_sql = """
        INSERT INTO [department2020].[dbo].[项目管理] (
            [申请时间], [项目名称], [申请经理], [申请原因],
            [预计完成时间], [批复意见], [状态]
        ) VALUES (GETDATE(), ?, ?, ?, ?, ?, '待审批')
        """
        
        cursor.execute(insert_sql, 
            item.项目名称,
            item.申请经理,
            item.申请原因,
            datetime.strptime(item.预计完成时间, "%Y-%m-%d") if item.预计完成时间 else None,
            item.批复意见
        )
        conn.commit()
        return {"status": "success", "message": "项目需求创建成功"}
    except pyodbc.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"数据库操作失败: {str(e)}")
    finally:
        conn.close()


# 更新项目状态
@router.put("/apsRequirements/{request_id}/status")
async def update_aps_requirement_status(request_id: int, payload: StatusUpdateRequest, username: Optional[str] = Query(default=None)):
    # 简单基于用户名的权限控制
    if not username or username not in {"admin", "John"}:
        raise HTTPException(status_code=403, detail="无权限进行审核操作")
    allowed = {"待审批", "同意", "拒绝"}
    new_status = payload.状态.strip() if payload.状态 else ""
    if new_status not in allowed:
        raise HTTPException(status_code=400, detail=f"非法状态值: {payload.状态}")

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        update_sql = """
            UPDATE [department2020].[dbo].[项目管理]
            SET [状态] = ?
            WHERE [RequestID] = ?
        """
        cursor.execute(update_sql, new_status, request_id)
        if cursor.rowcount == 0:
            conn.rollback()
            raise HTTPException(status_code=404, detail="未找到对应的项目记录")
        conn.commit()
        return {"status": "success", "message": "状态更新成功", "request_id": request_id, "状态": new_status}
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"数据库操作失败: {str(e)}")
    finally:
        if conn:
            conn.close()


# 更新批复时间和批复意见
@router.put("/apsRequirements/{request_id}/approval")
async def update_aps_requirement_approval(request_id: int, payload: ApprovalUpdateRequest, username: Optional[str] = Query(default=None)):
    # 权限控制：仅审核员可编辑
    if not username or username not in {"admin", "John"}:
        raise HTTPException(status_code=403, detail="无权限进行审核操作")
    
    # 至少需要更新一个字段
    if payload.批复时间 is None and payload.批复意见 is None:
        raise HTTPException(status_code=400, detail="至少需要提供批复时间或批复意见")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 动态构建SQL
        update_fields = []
        params = []
        
        if payload.批复时间 is not None:
            update_fields.append("[批复时间] = ?")
            # 解析日期字符串
            if payload.批复时间.strip():
                params.append(datetime.strptime(payload.批复时间, "%Y-%m-%d"))
            else:
                params.append(None)
        
        if payload.批复意见 is not None:
            update_fields.append("[批复意见] = ?")
            params.append(payload.批复意见)
        
        params.append(request_id)
        
        update_sql = f"""
            UPDATE [department2020].[dbo].[项目管理]
            SET {', '.join(update_fields)}
            WHERE [RequestID] = ?
        """
        
        cursor.execute(update_sql, *params)
        if cursor.rowcount == 0:
            conn.rollback()
            raise HTTPException(status_code=404, detail="未找到对应的项目记录")
        conn.commit()
        
        return {
            "status": "success",
            "message": "批复信息更新成功",
            "request_id": request_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"日期格式错误: {str(e)}")
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"数据库操作失败: {str(e)}")
    finally:
        if conn:
            conn.close()
