from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings
import os
import pyodbc
from datetime import datetime

router = APIRouter()
# 与file.vue相关 是体系类别的 2025-10-21新增
class Settings(BaseSettings):
    db_server: str = os.getenv("DB_SERVER", "192.168.41.57")
    db_database: str = os.getenv("DB_DATABASE", "Abus2020")
    db_username: str = os.getenv("DB_USERNAME", "sa")
    db_password: str = os.getenv("DB_PASSWORD", "3518i")

auth_settings = Settings()

class SystemProjectCreate(BaseModel):
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

@router.get("/systemproject", summary="获取体系类别列表")
async def get_systemprojects():
    """获取所有体系类别"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 先检查表是否存在
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = 'systemproject' AND table_schema = 'dbo'
        """)
        
        if cursor.fetchone()[0] == 0:
            # 表不存在，创建表
            cursor.execute("""
                CREATE TABLE [Abus2020].[dbo].[systemproject] (
                    id INT PRIMARY KEY,
                    name NVARCHAR(100) NOT NULL UNIQUE
                )
            """)
            conn.commit()
            return {
                "status": "success",
                "data": [],
                "timestamp": datetime.now().isoformat()
            }
        
        # 查询所有体系类别
        cursor.execute("SELECT id, name FROM [Abus2020].[dbo].[systemproject] ORDER BY id")
        systemprojects = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
        
        return {
            "status": "success",
            "data": systemprojects,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as exc:
        print(f"获取体系类别列表失败: {exc}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

@router.post("/systemproject", summary="添加新体系类别")
async def create_systemproject(systemproject: SystemProjectCreate):
    """添加新体系类别"""
    conn = None
    try:
        if not systemproject.name.strip():
            raise HTTPException(status_code=400, detail="体系类别名称不能为空")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 先检查表是否存在，如果不存在则创建
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='systemproject' AND xtype='U')
            CREATE TABLE [Abus2020].[dbo].[systemproject] (
                id INT PRIMARY KEY,
                name NVARCHAR(100) NOT NULL UNIQUE
            )
        """)
        conn.commit()
        
        # 检查是否已存在
        cursor.execute("SELECT COUNT(*) FROM [Abus2020].[dbo].[systemproject] WHERE name = ?", systemproject.name.strip())
        if cursor.fetchone()[0] > 0:
            raise HTTPException(status_code=400, detail="体系类别名称已存在")
        
        print(f"准备插入体系类别: name={systemproject.name.strip()}")
        
        # 插入新体系类别，让数据库自动生成id（如果是IDENTITY列）
        # 或者使用 IDENTITY_INSERT 来手动插入
        try:
            # 尝试直接插入（适用于IDENTITY列）
            cursor.execute("INSERT INTO [Abus2020].[dbo].[systemproject] (name) VALUES (?)", systemproject.name.strip())
            conn.commit()
        except Exception as e:
            # 如果失败，尝试使用手动ID方式
            print(f"自动插入失败，尝试手动ID方式: {e}")
            cursor.execute("SELECT ISNULL(MAX(id), 0) + 1 FROM [Abus2020].[dbo].[systemproject]")
            next_id = cursor.fetchone()[0]
            
            # 启用 IDENTITY_INSERT
            cursor.execute("SET IDENTITY_INSERT [Abus2020].[dbo].[systemproject] ON")
            cursor.execute("INSERT INTO [Abus2020].[dbo].[systemproject] (id, name) VALUES (?, ?)", next_id, systemproject.name.strip())
            cursor.execute("SET IDENTITY_INSERT [Abus2020].[dbo].[systemproject] OFF")
            conn.commit()
        
        return {
            "status": "success",
            "message": "体系类别添加成功",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as exc:
        print(f"创建体系类别失败: {exc}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

@router.delete("/systemproject/{systemproject_id}", summary="删除体系类别")
async def delete_systemproject(systemproject_id: int):
    """删除指定体系类别"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查体系类别是否存在
        cursor.execute("SELECT COUNT(*) FROM [Abus2020].[dbo].[systemproject] WHERE id = ?", systemproject_id)
        if cursor.fetchone()[0] == 0:
            raise HTTPException(status_code=404, detail="体系类别不存在")
        
        # 删除体系类别
        cursor.execute("DELETE FROM [Abus2020].[dbo].[systemproject] WHERE id = ?", systemproject_id)
        conn.commit()
        
        return {
            "status": "success",
            "message": "体系类别删除成功",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as exc:
        print(f"删除体系类别失败: {exc}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

@router.put("/systemproject/{systemproject_id}", summary="更新体系类别")
async def update_systemproject(systemproject_id: int, systemproject: SystemProjectCreate):
    """更新指定体系类别"""
    conn = None
    try:
        if not systemproject.name.strip():
            raise HTTPException(status_code=400, detail="体系类别名称不能为空")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查体系类别是否存在
        cursor.execute("SELECT COUNT(*) FROM [Abus2020].[dbo].[systemproject] WHERE id = ?", systemproject_id)
        if cursor.fetchone()[0] == 0:
            raise HTTPException(status_code=404, detail="体系类别不存在")
        
        # 检查新名称是否与其他体系类别重复
        cursor.execute("SELECT COUNT(*) FROM [Abus2020].[dbo].[systemproject] WHERE name = ? AND id != ?", 
                      systemproject.name.strip(), systemproject_id)
        if cursor.fetchone()[0] > 0:
            raise HTTPException(status_code=400, detail="体系类别名称已存在")
        
        # 更新体系类别
        cursor.execute("UPDATE [Abus2020].[dbo].[systemproject] SET name = ? WHERE id = ?", 
                      systemproject.name.strip(), systemproject_id)
        conn.commit()
        
        return {
            "status": "success",
            "message": "体系类别更新成功",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as exc:
        print(f"更新体系类别失败: {exc}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass
