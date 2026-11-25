from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings
import os
import pyodbc
from datetime import datetime

router = APIRouter()
# 与file.vue相关 是类别相关的
class Settings(BaseSettings):
    db_server: str = os.getenv("DB_SERVER", "192.168.41.57")
    db_database: str = os.getenv("DB_DATABASE", "Abus2020")
    db_username: str = os.getenv("DB_USERNAME", "sa")
    db_password: str = os.getenv("DB_PASSWORD", "3518i")

auth_settings = Settings()

class CategoryCreate(BaseModel):
    name: str

def get_db_connection():
    conn_str = (
        f"DRIVER={{SQL Server}};SERVER={auth_settings.db_server};DATABASE={auth_settings.db_database};"
        f"UID={auth_settings.db_username};PWD={auth_settings.db_password};"
    )
    try:
        return pyodbc.connect(conn_str)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"数据库连接失败: {exc}")

@router.get("/category", summary="获取类别列表")
async def get_categories():
    """获取所有类别"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 先检查表是否存在，如果不存在则创建
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='category' AND xtype='U')
            CREATE TABLE [Abus2020].[dbo].[category] (
                id INT PRIMARY KEY,
                name NVARCHAR(100) NOT NULL UNIQUE
            )
        """)
        conn.commit()
        
        cursor.execute("SELECT id, name FROM [Abus2020].[dbo].[category] ORDER BY name")
        categories = []
        for row in cursor.fetchall():
            categories.append({"id": row[0], "name": row[1]})
        
        return {
            "status": "success",
            "data": categories,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as exc:
        print(f"获取类别失败: {exc}")  # 添加调试日志
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

@router.post("/category", summary="添加新类别")
async def create_category(category: CategoryCreate):
    """添加新类别"""
    conn = None
    try:
        if not category.name.strip():
            raise HTTPException(status_code=400, detail="类别名称不能为空")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 先检查表是否存在，如果不存在则创建
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='category' AND xtype='U')
            CREATE TABLE [Abus2020].[dbo].[category] (
                id INT PRIMARY KEY,
                name NVARCHAR(100) NOT NULL UNIQUE
            )
        """)
        conn.commit()
        
        # 检查是否已存在
        cursor.execute("SELECT COUNT(*) FROM [Abus2020].[dbo].[category] WHERE name = ?", category.name.strip())
        if cursor.fetchone()[0] > 0:
            raise HTTPException(status_code=400, detail="类别名称已存在")
        
        # 插入新类别，id 自增
        cursor.execute("INSERT INTO [Abus2020].[dbo].[category] (name) VALUES (?)", category.name.strip())
        conn.commit()
        
        return {
            "status": "success",
            "message": "类别添加成功",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as exc:
        print(f"创建类别失败: {exc}")  # 添加调试日志
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

@router.delete("/category/{category_id}", summary="删除类别")
async def delete_category(category_id: int):
    """删除类别"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查类别是否存在
        cursor.execute("SELECT COUNT(*) FROM [Abus2020].[dbo].[category] WHERE id = ?", category_id)
        if cursor.fetchone()[0] == 0:
            raise HTTPException(status_code=404, detail="类别不存在")
        
        # 删除类别
        cursor.execute("DELETE FROM [Abus2020].[dbo].[category] WHERE id = ?", category_id)
        conn.commit()
        
        return {
            "status": "success",
            "message": "类别删除成功",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as exc:
        print(f"删除类别失败: {exc}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

@router.get("/category/test", summary="测试数据库连接")
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
