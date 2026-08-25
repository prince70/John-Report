from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings
import os
import pyodbc
from datetime import datetime

router = APIRouter()
# 与file.vue相关 是细分项目的
class Settings(BaseSettings):
    db_server: str = os.getenv("DB_SERVER", "192.168.41.57")
    db_database: str = os.getenv("DB_DATABASE", "Abus2020")
    db_username: str = os.getenv("DB_USERNAME", "sa")
    db_password: str = os.getenv("DB_PASSWORD", "3518i")

auth_settings = Settings()

class MiniProductCreate(BaseModel):
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

@router.get("/miniproduct", summary="获取细分项目列表")
async def get_miniproducts():
    """获取所有细分项目"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 先检查表是否存在，如果不存在则创建
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='miniproject' AND xtype='U')
            CREATE TABLE [Abus2020].[dbo].[miniproject] (
                id INT PRIMARY KEY,
                name NVARCHAR(100) NOT NULL UNIQUE
            )
        """)
        conn.commit()
        
        cursor.execute("SELECT id, name FROM [Abus2020].[dbo].[miniproject] ORDER BY name")
        miniproducts = []
        seen_names = set()
        for row in cursor.fetchall():
            name = (row[1] or '').strip()
            if not name or name in seen_names:
                continue
            miniproducts.append({"id": row[0], "name": name})
            seen_names.add(name)

        # 兼容历史数据：补充文件表中已存在但未维护到 miniproject 表的细分项目
        cursor.execute("""
            SELECT DISTINCT [细分项目]
            FROM [Abus2020].[dbo].[FolderCategories​]
            WHERE [细分项目] IS NOT NULL AND LTRIM(RTRIM([细分项目])) <> ''
            ORDER BY [细分项目]
        """)
        derive_id = -1
        for row in cursor.fetchall():
            name = (row[0] or '').strip()
            if not name or name in seen_names:
                continue
            miniproducts.append({"id": derive_id, "name": name})
            seen_names.add(name)
            derive_id -= 1
        
        return {
            "status": "success",
            "data": miniproducts,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as exc:
        print(f"获取细分项目失败: {exc}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

@router.post("/miniproduct", summary="添加新细分项目")
async def create_miniproduct(miniproduct: MiniProductCreate):
    """添加新细分项目"""
    conn = None
    try:
        if not miniproduct.name.strip():
            raise HTTPException(status_code=400, detail="细分项目名称不能为空")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 先检查表是否存在，如果不存在则创建
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='miniproject' AND xtype='U')
            CREATE TABLE [Abus2020].[dbo].[miniproject] (
                id INT PRIMARY KEY,
                name NVARCHAR(100) NOT NULL UNIQUE
            )
        """)
        conn.commit()
        
        # 检查是否已存在
        cursor.execute("SELECT COUNT(*) FROM [Abus2020].[dbo].[miniproject] WHERE name = ?", miniproduct.name.strip())
        if cursor.fetchone()[0] > 0:
            raise HTTPException(status_code=400, detail="细分项目名称已存在")
        
        # 插入新细分项目，id 自增
        cursor.execute("INSERT INTO [Abus2020].[dbo].[miniproject] (name) VALUES (?)", miniproduct.name.strip())
        conn.commit()
        
        return {
            "status": "success",
            "message": "细分项目添加成功",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as exc:
        print(f"创建细分项目失败: {exc}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

@router.delete("/miniproduct/{miniproduct_id}", summary="删除细分项目")
async def delete_miniproduct(miniproduct_id: int):
    """删除细分项目"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查细分项目是否存在
        cursor.execute("SELECT COUNT(*) FROM [Abus2020].[dbo].[miniproject] WHERE id = ?", miniproduct_id)
        if cursor.fetchone()[0] == 0:
            raise HTTPException(status_code=404, detail="细分项目不存在")
        
        # 删除细分项目
        cursor.execute("DELETE FROM [Abus2020].[dbo].[miniproject] WHERE id = ?", miniproduct_id)
        conn.commit()
        
        return {
            "status": "success",
            "message": "细分项目删除成功",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as exc:
        print(f"删除细分项目失败: {exc}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

@router.get("/miniproduct/test", summary="测试数据库连接")
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

