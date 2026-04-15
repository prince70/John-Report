# 这个是查询员工信息表的
from fastapi import HTTPException, Depends, status, Query
from fastapi import FastAPI
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import pyodbc
from pydantic_settings import BaseSettings
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from datetime import datetime, date
import io
import urllib.parse
import pandas as pd

router = APIRouter()
security = HTTPBasic()

@router.post("/people/clear_cache",
         summary="清除缓存",
         description="清除所有people相关的缓存数据")
async def clear_people_cache():
    """清除缓存，使下次请求重新查询数据库"""
    await FastAPICache.clear()
    return {"status": "success", "message": "缓存已清除"}

#  表 erp_obas_emp
DB_SERVER = "192.168.41.57"
DB_DATABASE = "department2020"
DB_USERNAME = "sa"
DB_PASSWORD = "3518i"

def get_db_connection():
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USERNAME};PWD={DB_PASSWORD}"
    return pyodbc.connect(conn_str)


def _to_json_value(value):
    """将可能不可 JSON 序列化的值转为安全类型（避免前端收不到数据）"""
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if hasattr(value, "__class__") and value.__class__.__name__ == "Timestamp":
        return str(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if hasattr(value, "__float__") and not isinstance(value, (bool, int)):
        try:
            return float(value)
        except (TypeError, ValueError):
            return str(value)
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _query_people_data(conn):
    cursor = conn.cursor()
    query = """
    SELECT
        ISNULL(emp_name, '未登记') AS 姓名,
        CASE WHEN sex = 1 THEN '男' WHEN sex = 2 THEN '女' ELSE '未登记' END AS 性别,
        CASE
            WHEN birth_date IS NULL THEN '未登记'
            ELSE CAST(
                DATEDIFF(YEAR, birth_date, GETDATE()) -
                CASE WHEN DATEADD(YEAR, DATEDIFF(YEAR, birth_date, GETDATE()), birth_date) > GETDATE() THEN 1 ELSE 0 END
                AS VARCHAR)
        END AS 年龄,
        CASE WHEN married = 1 THEN '是' WHEN married = 0 THEN '否' ELSE '未登记' END AS 是否已婚,
        CAST(in_date AS DATE) AS 入职时间,
        CASE WHEN 退休返聘 = 1 THEN '是' WHEN 退休返聘 IS NULL THEN '否' ELSE '未登记' END AS 是否退休返聘,
        ISNULL(职务, '未登记') AS 职务,
        CASE
            WHEN study_level = '01' THEN '小学'
            WHEN study_level = '02' THEN '初中'
            WHEN study_level = '03' THEN '中专'
            WHEN study_level = '04' THEN '高中'
            WHEN study_level = '05' THEN '大专'
            WHEN study_level = '06' THEN '本科'
            WHEN study_level = '07' THEN '研究生'
            WHEN study_level = '08' THEN '中技'
            WHEN study_level = '09' THEN '硕士'
            ELSE '未登记'
        END AS 学历,
        ISNULL(gra_sch_code, '未登记') AS 毕业学校,
        ISNULL(special, '未登记') AS 专业,
        ISNULL(card_no, '未登记') AS 工卡号,
        ISNULL(emp_item_no, '未登记') AS 工号,
        ISNULL(部门, '未登记') AS 部门,
        CASE WHEN IsFront = 1 THEN '是' WHEN IsFront = 0 THEN '否' ELSE '未登记' END AS 是否前线员工,
        ISNULL(workshop, '未登记') AS 车间,
        ISNULL([分区], '未登记') AS 分区,
        ISNULL([工位], '未登记') AS 工位,
        ISNULL([线别], '未登记') AS 线别,
        ISNULL([所属技工], '未登记') AS 所属技工,
        ISNULL([所属上级], '未登记') AS 所属上级,
        ISNULL(tp, '未登记') AS 联系方式,
        ISNULL(id_code, '未登记') AS 身份证,
        ISNULL(family_addr, '未登记') AS 居住地址,
        ISNULL(mail, '未登记') AS 电子邮箱,
        ISNULL(亲属关系, '未登记') AS 亲属关系,
        ISNULL(宿舍房号, '未登记') AS 宿舍房号
    FROM erp_obas_emp
    """

    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()

    result = []
    for row in rows:
        row_dict = {}
        for i, value in enumerate(row):
            row_dict[columns[i]] = _to_json_value(value)
        result.append(row_dict)

    cursor.close()
    return result


def _match_age_range(age_text, age_range):
    if not age_range:
        return True
    try:
        age = int(age_text)
    except (TypeError, ValueError):
        return age_range == "未登记"

    if age_range.endswith("以上"):
        try:
            lower = int(age_range.replace("以上", ""))
            return age >= lower
        except ValueError:
            return True
    if "-" in age_range:
        lo, hi = age_range.split("-", 1)
        try:
            return int(lo) <= age <= int(hi)
        except ValueError:
            return True
    return True


def _apply_people_filters(
    data,
    name=None,
    emp_no=None,
    card_no=None,
    gender=None,
    age_range=None,
    education=None,
    department=None,
    workshop=None,
    zone=None,
    is_frontline=None,
    married=None,
):
    result = []
    for item in data:
        if name and name not in str(item.get("姓名", "")):
            continue
        if emp_no and emp_no not in str(item.get("工号", "")):
            continue
        if card_no and card_no not in str(item.get("工卡号", "")):
            continue
        if gender and str(item.get("性别", "")) != gender:
            continue
        if education and str(item.get("学历", "")) != education:
            continue
        if department and str(item.get("部门", "")) != department:
            continue
        if workshop and str(item.get("车间", "")) != workshop:
            continue
        if zone and zone not in str(item.get("分区", "")):
            continue
        if is_frontline and str(item.get("是否前线员工", "")) != is_frontline:
            continue
        if married and str(item.get("是否已婚", "")) != married:
            continue
        if not _match_age_range(item.get("年龄", ""), age_range):
            continue
        result.append(item)
    return result


@router.get("/people/debug",
         summary="调试接口",
         description="检查数据库连接与表是否有数据，不经过缓存")
async def people_debug():
    """用于排查「无法获取数据」：先调此接口确认库和表是否正常"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM erp_obas_emp")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return {
            "status": "success",
            "message": "数据库连接正常",
            "table": "erp_obas_emp",
            "row_count": count,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "数据库连接或查询失败",
            "detail": str(e),
        }


@router.get("/people/workshops", 
         summary="获取车间列表",
         description="获取所有不重复的车间列表")
@cache(expire=72000)
async def get_workshops():
    """获取所有车间列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT DISTINCT workshop
        FROM erp_obas_emp
        WHERE workshop IS NOT NULL AND workshop != ''
        ORDER BY workshop
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        workshops = [row[0] for row in rows]
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": workshops
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取车间列表失败: {str(e)}"
        )

@router.get("/people/departments", 
         summary="获取部门列表",
         description="获取所有不重复的部门列表")
@cache(expire=72000)
async def get_departments():
    """获取所有部门列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT DISTINCT 部门
        FROM erp_obas_emp
        WHERE 部门 IS NOT NULL AND 部门 != ''
        ORDER BY 部门
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        departments = [row[0] for row in rows]
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": departments
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取部门列表失败: {str(e)}"
        )

@router.get("/people/zones", 
         summary="获取分区列表",
         description="获取所有不重复的分区列表")
@cache(expire=72000)
async def get_zones():
    """获取所有分区列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT DISTINCT 分区
        FROM erp_obas_emp
        WHERE 分区 IS NOT NULL AND 分区 != ''
        ORDER BY 分区
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        zones = [row[0] for row in rows]
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": zones
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分区列表失败: {str(e)}"
        )

@router.get("/people",
         summary="员工数据",
         description="获取员工统计信息")
@cache(expire=60)
async def get_people_stats():
    print("访问people路由")
    try:
        conn = get_db_connection()
        result = _query_people_data(conn)
        conn.close()
        
        return {
            "status": "success",
            "data": result,
            "total": len(result),
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


@router.get(
    "/people/export",
    summary="导出员工Excel",
    description="按当前筛选条件导出员工信息为Excel文件"
)
async def export_people_excel(
    name: str | None = Query(None, description="姓名（模糊匹配）"),
    emp_no: str | None = Query(None, description="工号（模糊匹配）"),
    card_no: str | None = Query(None, description="工卡号（模糊匹配）"),
    gender: str | None = Query(None, description="性别（精确匹配）"),
    age_range: str | None = Query(None, description="年龄范围，如20-30、50以上、未登记"),
    education: str | None = Query(None, description="学历（精确匹配）"),
    department: str | None = Query(None, description="部门（精确匹配）"),
    workshop: str | None = Query(None, description="车间（精确匹配）"),
    zone: str | None = Query(None, description="分区（模糊匹配）"),
    is_frontline: str | None = Query(None, description="是否前线员工（是/否）"),
    married: str | None = Query(None, description="是否已婚（是/否）"),
):
    try:
        conn = get_db_connection()
        data = _query_people_data(conn)
        conn.close()

        filtered = _apply_people_filters(
            data,
            name=name,
            emp_no=emp_no,
            card_no=card_no,
            gender=gender,
            age_range=age_range,
            education=education,
            department=department,
            workshop=workshop,
            zone=zone,
            is_frontline=is_frontline,
            married=married,
        )

        if not filtered:
            raise HTTPException(status_code=404, detail="没有可导出的数据")

        df = pd.DataFrame(filtered)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="员工信息")

            worksheet = writer.sheets["员工信息"]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    value = "" if cell.value is None else str(cell.value)
                    if len(value) > max_length:
                        max_length = len(value)
                worksheet.column_dimensions[column_letter].width = min(max_length + 2, 60)

        output.seek(0)
        filename = f"员工信息_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        encoded_filename = urllib.parse.quote(filename)

        return StreamingResponse(
            io.BytesIO(output.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出Excel失败: {str(e)}"
        )