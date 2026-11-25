from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from numpy import isin
from pydantic import BaseModel
import pyodbc
from pydantic_settings import BaseSettings
from fastapi import APIRouter
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
import pandas as pd
from datetime import datetime

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
    projectContent: str

class ProjectUpdate(BaseModel):
    projectName: str
    status: str

class ProjectEdit(BaseModel):
    projectName: str
    projectContent: str
    date: str  

@router.post("/personal/add", 
         summary="添加新项目",
         description="添加新的项目到数据库")
async def add_project(project: ProjectCreate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        current_date = datetime.now().strftime('%Y/%m/%d')

        query = """
        INSERT INTO 个人项目表 (日期, 项目名, 项目内容, 状态)
        VALUES (?, ?, ?, '未结案')
        """
        cursor.execute(query, (current_date, project.projectName, project.projectContent))
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}"
        )

@router.post("/personal/update", 
         summary="更新项目状态",
         description="更新项目的结案状态")
async def update_project_status(project: ProjectUpdate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        UPDATE 个人项目表
        SET 状态 = ?
        WHERE 项目名 = ?
        """
        cursor.execute(query, (project.status, project.projectName))
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

@router.post("/personal/edit", 
         summary="修改项目内容",
         description="修改已有项目的内容")
async def edit_project(project: ProjectEdit):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        UPDATE 个人项目表
        SET 项目内容 = ?
        WHERE 项目名 = ? AND 日期 = ?
        """
        cursor.execute(query, (project.projectContent, project.projectName, project.date))
        
        if cursor.rowcount == 0:
            insert_query = """
            INSERT INTO 个人项目表 (日期, 项目名, 项目内容, 状态)
            VALUES (?, ?, ?, '未结案')
            """
            cursor.execute(insert_query, (project.date, project.projectName, project.projectContent))
        
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "项目内容修改成功",
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

@router.post("/personal", 
         summary="项目数据",
         description="获取项目信息")
async def get_project_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
         SELECT 
            日期,
            项目名,
            项目内容,
            状态 
        FROM 个人项目表
        ORDER BY 日期 DESC, 项目名
        """
       
        cursor.execute(query)
        
        columns = [column[0] for column in cursor.description]
        
        rows = cursor.fetchall()
        
        df = pd.DataFrame.from_records(rows, columns=columns)

        if df.empty:
            cursor.close()
            conn.close()
            return {
                "status": "success",
                "data": [],
                "total": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        df['日期'] = pd.to_datetime(df['日期'])
        
        content_pivot = pd.pivot_table(
            df,
            values='项目内容',
            index='日期',
            columns='项目名',
            aggfunc='first',
            fill_value=pd.NA
        )
        latest_date = content_pivot.index.max()
        # print('最新日期：', latest_date)

        # 各列在最新日期是否有内容
        has_content_in_latest = content_pivot.loc[latest_date].notna().astype(int)
        # print('最新日期内容存在性：', has_content_in_latest)

        # 计算每列非空值的数量
        non_empty_counts = content_pivot.notna().sum()
        # print('非空值数量：', non_empty_counts)

        # 复合排序：先按最新日期内容存在性，再按非空总数
        combined_sort = (has_content_in_latest * 1e6) + non_empty_counts
        sorted_columns = combined_sort.sort_values(ascending=False).index
        
        content_pivot = content_pivot[sorted_columns]

        latest_status = df.groupby('项目名')['状态'].last()
        def fill_status(column_name):
            latest =latest_status.get(column_name, '未结案')
            return latest if latest=='结案' else '未结案'  
        status_pivot = pd.pivot_table(
            df,
            values='状态',
            index='日期',
            columns='项目名',
            aggfunc='first',
            # fill_value='未结案'
        )

        for col in status_pivot.columns:
            status_pivot[col] = status_pivot[col].fillna(fill_status(col))
        # print(status_pivot)
        status_pivot = status_pivot[sorted_columns]

        closed_projects = []
        for col in status_pivot.columns:
            if (status_pivot[col] == '结案').any():
                closed_projects.append(col)

        active_columns = [col for col in sorted_columns if col not in closed_projects]

        new_column_order = active_columns + closed_projects

        content_pivot = content_pivot[new_column_order]
        status_pivot = status_pivot[new_column_order]

        content_pivot = content_pivot.reset_index()
        status_pivot = status_pivot.reset_index()

        content_pivot['日期'] = content_pivot['日期'].dt.strftime('%Y/%m/%d')
        status_pivot['日期'] = status_pivot['日期'].dt.strftime('%Y/%m/%d')

        content_pivot.columns = [str(col) for col in content_pivot.columns]
        status_pivot.columns = [str(col) for col in status_pivot.columns]

        result = content_pivot.to_dict('records')
        
        for i, row in enumerate(result):
            status_row = status_pivot.iloc[i].to_dict()
            for project_name, status in status_row.items():
                if project_name != '日期':
                    row[f'{project_name}_状态'] = status

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