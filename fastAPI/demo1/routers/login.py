# 登录更改密码相关的
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import pyodbc
import hashlib
from fastapi import APIRouter

router = APIRouter()
security = HTTPBasic()

DB_SERVER = "192.168.41.57"
DB_DATABASE = "department2020"
DB_USERNAME = "sa"
DB_PASSWORD = "3518i"
# [登录验证]表
def get_db_connection():
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USERNAME};PWD={DB_PASSWORD}"
    return pyodbc.connect(conn_str)

# 密码哈希生成函数  使用的是 SHA-256 加密（不是 MD5）
def generate_sha256_hash(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest().upper()

class UserLogin(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

@router.post("/login")
def login(user: UserLogin):
    try:
        if not user.username or not user.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名和密码不能为空"
            )

        conn = get_db_connection()
        cursor = conn.cursor()
        input_hash = generate_sha256_hash(user.password)
        
        cursor.execute("""
            SELECT id, username 
            FROM [登录验证] 
            WHERE username = ? AND password_hash = ?
        """, (user.username, input_hash))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的用户名或密码"
            )
        
        # 根据用户名判断角色
        role = "file_viewer" if result.username.lower() == "eva" else "normal"
            
        return {
            "status": "success",
            "code": 200,
            "data": {
                "user_id": result.id,
                "username": result.username,
                "role": role,  # 新增角色字段
                "token": generate_sha256_hash(f"{result.id}{result.username}{input_hash}")
            },
            "message": "登录成功"
        }
        
    except HTTPException as e:
        raise e
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
    finally:
        if 'conn' in locals():
            conn.close()

@router.post("/change-password")
def change_password(request: ChangePasswordRequest, username: str):
    conn = None  # 在 try 外部定义，避免作用域问题
    try:
        # 验证所有必填字段
        if not username or username.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名不能为空"
            )
        
        if not request.old_password or not request.old_password.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码不能为空"
            )
        
        if not request.new_password or not request.new_password.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="新密码不能为空"
            )
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 安全日志：只记录用户名和哈希值，不记录明文密码
        print(f"修改密码请求 - 用户名: {username}")
        
        old_hash = generate_sha256_hash(request.old_password)
        
        cursor.execute("""
            SELECT id 
            FROM [登录验证] 
            WHERE username = ? AND password_hash = ?
        """, (username, old_hash))
        
        user_result = cursor.fetchone()
        if not user_result:
            print(f"修改密码失败 - 用户名: {username} (旧密码验证失败)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="旧密码不正确"
            )
        
        new_hash = generate_sha256_hash(request.new_password)
        
        cursor.execute("""
            UPDATE [登录验证] 
            SET password_hash = ?
            WHERE username = ?
        """, (new_hash, username))
        conn.commit()
        
        print(f"密码修改成功 - 用户名: {username}")
        return {"status": "密码修改成功"}
        
    except HTTPException:
        # 重新抛出 HTTPException，不做额外处理
        raise
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        print(f"数据库错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"密码更新失败: {str(e)}"
        )
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"服务器错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}"
        )
    finally:
        if conn:
            conn.close()