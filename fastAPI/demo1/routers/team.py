from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from numpy import isin
from pydantic import BaseModel, validator
import pyodbc
from pydantic_settings import BaseSettings
from fastapi import APIRouter
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
import pandas as pd
from datetime import datetime
from typing import Optional

router = APIRouter()
security = HTTPBasic()

DB_SERVER = "192.168.41.57"
DB_DATABASE = "department2020"
DB_USERNAME = "sa"
DB_PASSWORD = "3518i"

def get_db_connection():
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USERNAME};PWD={DB_PASSWORD}"
    return pyodbc.connect(conn_str)

class ProjectCreate(BaseModel):
    projectName: str
    projectPeople: str
    Reason: str
    date: str  

    @validator('projectName')
    def validate_project_name(cls, v):
        if not v.strip():
            raise ValueError('项目名称不能为空')
        return v.strip()

    @validator('Reason')
    def validate_reason(cls, v):
        if not v.strip():
            raise ValueError('申请原因不能为空')
        return v.strip()

    @validator('date')
    def validate_date(cls, v):
        try:
            # 尝试解析日期字符串
            if '/' in v:
                datetime.strptime(v, '%Y/%m/%d')
            else:
                datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('日期格式无效，请使用 YYYY/MM/DD 或 YYYY-MM-DD 格式')

    @validator('projectPeople')
    def validate_project_people(cls, v):
        if v is None or not str(v).strip():
            raise ValueError('申请经理不能为空')
        return str(v).strip()

class ProjectUpdate(BaseModel):
    reply: str
    status: str
    projectName: str

class ProjectEdit(BaseModel):
    projectName: str
    name: str
    content: str
    date: str
    currentStatus: str
    reply: str

@router.post("/add", 
         summary="添加新项目",
         description="添加新的项目到数据库")
async def add_project(project: ProjectCreate):
    try:
        # 验证输入数据
        if not project.projectName.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="项目名称不能为空"
            )
        if not project.Reason.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="申请原因不能为空"
            )

        conn = get_db_connection()
        cursor = conn.cursor()
        
        current_date = datetime.now().strftime('%Y/%m/%d')
        
        # 标准化日期格式
        try:
            if '/' in project.date:
                formatted_date = datetime.strptime(project.date, '%Y/%m/%d').strftime('%Y/%m/%d')
            else:
                formatted_date = datetime.strptime(project.date, '%Y-%m-%d').strftime('%Y/%m/%d')
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="日期格式无效，请使用 YYYY/MM/DD 或 YYYY-MM-DD 格式"
            )
        
        query = """
        INSERT INTO 透明化管理 (申请时间, 项目名称, 申请经理, 申请原因, 预计完成时间, 状态)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (current_date, project.projectName, project.projectPeople, project.Reason, formatted_date, '待审核'))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "项目添加成功",
            "timestamp": datetime.now().isoformat()
        }
    except pyodbc.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库错误: {str(e)}"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}"
        )

@router.post("/update", 
         summary="更新项目状态",
         description="更新项目的审核状态")
async def update_project_status(project: ProjectUpdate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        current_date = datetime.now().strftime('%Y/%m/%d')

        query = """
        UPDATE 透明化管理
        SET 批复意见 = ?, 批复时间 = ?, 状态 = ?
        WHERE 项目名称 = ?
        """
        cursor.execute(query, (project.reply, current_date, project.status, project.projectName))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "项目状态更新成功",
            "timestamp": datetime.now().isoformat()
        }
    except pyodbc.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库错误: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}"
        )

@router.post("/edit", 
         summary="编辑项目信息",
         description="编辑项目的基本信息")
async def edit_project(project: ProjectEdit):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        new_status = '待审核' if project.currentStatus in ['通过', '驳回'] else project.currentStatus

        query = """
        UPDATE 透明化管理
        SET 项目名称 = ?, 申请原因 = ?, 预计完成时间 = ?, 状态 = ?, 批复意见 = ?
        WHERE 项目名称 = ?
        """
        cursor.execute(query, (project.name, project.content, project.date, new_status, project.reply, project.projectName))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "项目信息更新成功",
            "timestamp": datetime.now().isoformat()
        }
    except pyodbc.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库错误: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}"
        )

@router.post("/", 
         summary="项目数据",
         description="获取项目信息")
@cache(expire=3600)
async def get_project_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
         SELECT 
            申请时间,
            项目名称,
            申请经理,
            申请原因,
            预计完成时间,
            批复意见,
            批复时间,
            状态
        FROM 透明化管理
        ORDER BY 申请时间 DESC, 项目名称
        """
       
        cursor.execute(query)
        
        columns = [column[0] for column in cursor.description]
        
        rows = cursor.fetchall()
        
        result = []
        for row in rows:
            item = dict(zip(columns, row))
            item['申请时间'] = item['申请时间'] if item['申请时间'] else None
            item['批复时间'] = item['批复时间'] if item['批复时间'] else None
            result.append(item)

        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": result,
            "total": len(result),
            "timestamp": datetime.now().isoformat()
        }
    except pyodbc.Error as e:
        from fastapi import status
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库错误: {str(e)}"
        )
    except Exception as e:
        from fastapi import status
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}"
        )