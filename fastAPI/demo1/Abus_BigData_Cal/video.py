from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import os
import pyodbc
from datetime import datetime
import shutil
from typing import Optional, List

router = APIRouter()

def get_db_connection():
    conn_str = (
        "DRIVER={SQL Server};"
        "SERVER=192.168.41.57;"
        "DATABASE=Abus2020;"
        "UID=sa;"
        "PWD=3518i;"
    )
    try:
        return pyodbc.connect(conn_str)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"数据库连接失败: {exc}")

def get_video_dir():
    upload_dir = r"D:\\uploads\\john"
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir

@router.post("/video/upload", summary="上传视频文件")
async def upload_video(
    file: UploadFile = File(...),
    类别: str = Form(...),
    细分项目: str = Form(...),
    文件名称: str = Form(...),
    制作日期: str = Form(...),
    负责人: str = Form(default="admin"),
    备注: str = Form(default="")
):
    """上传视频文件并保存记录到数据库"""
    conn = None
    try:
        # 验证必填字段
        if not all([类别, 细分项目, 文件名称, 制作日期]):
            raise HTTPException(status_code=400, detail="请填写所有必填字段")
        
        # 验证文件类型
        allowed_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.3gp', '.m4v']
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file_ext}")
        
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]  # 精确到毫秒
        unique_filename = f"{timestamp}{file_ext}"
        
        # 保存文件
        video_dir = get_video_dir()
        file_path = os.path.join(video_dir, unique_filename)
        file_url = f"/static/uploads/{unique_filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 保存到数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 插入文件记录
        insert_sql = """
        INSERT INTO [Abus2020].[dbo].[FolderCategories​] 
        ([类别], [细分项目], [文件名称], [制作日期], [负责人], [文件类型], [备注])
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        # 将文件URL存储在备注字段中
        备注_with_url = file_url
        if 备注:
            备注_with_url += f" | 备注: {备注}"
        
        cursor.execute(insert_sql, (
            类别, 
            细分项目, 
            文件名称, 
            制作日期, 
            负责人, 
            file_ext[1:],  # 去掉点号
            备注_with_url
        ))
        conn.commit()
        
        return {
            "status": "success",
            "message": "视频上传成功",
            "data": {
                "filename": unique_filename,
                "url": file_url,
                "size": file.size if hasattr(file, 'size') else 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as exc:
        print(f"视频上传失败: {exc}")
        # 如果数据库插入失败，删除已上传的文件
        try:
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        raise HTTPException(status_code=500, detail=f"视频上传失败: {exc}")
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

@router.get("/video/{video_id}", summary="获取视频信息")
async def get_video(video_id: int):
    """获取视频文件信息"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT [id], [类别], [细分项目], [文件名称], [制作日期], [负责人], [文件类型], [备注]
            FROM [Abus2020].[dbo].[FolderCategories​]
            WHERE [id] = ? AND [文件类型] IN ('mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm', '3gp', 'm4v')
        """, video_id)
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="视频不存在")
        
        # 从备注字段中提取文件URL
        备注 = row[7] or ""
        url = ""
        if 备注:
            parts = 备注.split(' | ')
            if parts[0].startswith('/static/videos/') or parts[0].startswith('/static/uploads/'):
                url = parts[0]
        
        return {
            "status": "success",
            "data": {
                "id": row[0],
                "类别": row[1] or "",
                "细分项目": row[2] or "",
                "文件名称": row[3] or "",
                "制作日期": row[4].strftime('%Y-%m-%d') if row[4] else "",
                "负责人": row[5] or "",
                "文件类型": row[6] or "",
                "url": url
            }
        }
        
    except HTTPException:
        raise
    except Exception as exc:
        print(f"获取视频信息失败: {exc}")
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass 