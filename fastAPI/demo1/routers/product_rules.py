from datetime import datetime
import os

import pandas as pd
import pyodbc
from fastapi import APIRouter, HTTPException

router = APIRouter()

DB_SERVER = os.getenv("DB_SERVER_REPORT", "192.168.10.200")
DB_DATABASE = os.getenv("DB_DATABASE_REPORT", "APS_SUO")
DB_USERNAME = os.getenv("DB_USERNAME_REPORT", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD_REPORT", "5tgb^YHN7ujm*IK<")

TABLE_NAME = os.getenv("DB_TABLE_PRODUCT_RULES", "[dbo].[ProductRules]")


def pick_first_existing(columns: list[str], candidates: list[str]) -> str | None:
    for col in candidates:
        if col in columns:
            return col
    return None


def get_db_connection():
    conn_str = (
        f"DRIVER={{SQL Server}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};"
        f"UID={DB_USERNAME};PWD={DB_PASSWORD};"
    )
    try:
        return pyodbc.connect(conn_str)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"数据库连接失败: {exc}")


@router.get(
    "/productRules",
    summary="生产线资源表",
    description="查询 APS.APS_SUO.dbo.ProductRules 生产线资源明细",
)
async def get_product_rules(
    page: int = 1,
    pageSize: int = 200,
    line: str | None = None,
    product: str | None = None,
):
    conn = None
    try:
        conn = get_db_connection()
        offset = (page - 1) * pageSize

        df_columns = pd.read_sql(f"SELECT TOP 1 * FROM {TABLE_NAME}", conn).columns.tolist()
        line_col = pick_first_existing(df_columns, ["生产线编号", "生产线", "LineType", "Line", "产线", "线体", "ResourceExternalId"])
        product_col = pick_first_existing(df_columns, ["料品名称", "产品", "ProductName", "Productname", "ItemName"])

        where_conditions = ["1=1"]
        params: list[str] = []

        if line and line_col:
            where_conditions.append(f"[{line_col}] = ?")
            params.append(line)

        if product and product_col:
            where_conditions.append(f"[{product_col}] = ?")
            params.append(product)

        where_clause = " AND ".join(where_conditions)

        count_sql = f"SELECT COUNT(*) AS total FROM {TABLE_NAME} WHERE {where_clause}"
        count_df = pd.read_sql(count_sql, conn, params=params)
        total = int(count_df.iloc[0]["total"])

        data_sql = f"""
        SELECT *
        FROM {TABLE_NAME}
        WHERE {where_clause}
        ORDER BY 1
        OFFSET {offset} ROWS
        FETCH NEXT {pageSize} ROWS ONLY
        """
        df = pd.read_sql(data_sql, conn, params=params)
        df = df.fillna("")

        for col in df.select_dtypes(include=["datetime", "datetimetz"]):
            df[col] = df[col].astype(str)

        return {
            "status": "success",
            "data": df.to_dict(orient="records"),
            "total": total,
            "page": page,
            "pageSize": pageSize,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
    finally:
        if conn:
            conn.close()


@router.get(
    "/productRules/line-options",
    summary="生产线编号选项",
    description="从 ProductRules 中提取生产线编号/线体编码选项，供前端筛选使用",
)
async def get_product_rule_line_options():
    conn = None
    try:
        conn = get_db_connection()
        df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)
        if df.empty:
            return {"status": "success", "data": [], "timestamp": datetime.now().isoformat()}

        candidate_columns = ["生产线编号", "生产线", "LineType", "Line", "产线", "线体", "ResourceExternalId"]
        target_col = pick_first_existing(df.columns.tolist(), candidate_columns)

        if not target_col:
            # 找不到常见字段时回退到第一列，保证页面不报错
            target_col = df.columns[0]

        values = (
            df[target_col]
            .dropna()
            .astype(str)
            .map(str.strip)
            .loc[lambda s: s != ""]
            .drop_duplicates()
            .sort_values()
            .tolist()
        )

        return {
            "status": "success",
            "column": target_col,
            "data": values,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
    finally:
        if conn:
            conn.close()


@router.get(
    "/productRules/linkage-options",
    summary="生产线与产品联动选项",
    description="返回生产线可生产的产品、产品可用生产线的双向映射",
)
async def get_product_rule_linkage_options():
    conn = None
    try:
        conn = get_db_connection()
        df = pd.read_sql(f"SELECT * FROM {TABLE_NAME}", conn)
        if df.empty:
            return {
                "status": "success",
                "lineColumn": "",
                "productColumn": "",
                "lineOptions": [],
                "productOptions": [],
                "lineToProducts": {},
                "productToLines": {},
                "timestamp": datetime.now().isoformat(),
            }

        line_candidates = ["生产线编号", "生产线", "LineType", "Line", "产线", "线体", "ResourceExternalId"]
        product_candidates = ["料品名称", "产品", "ProductName", "Productname", "ItemName"]
        line_col = pick_first_existing(df.columns.tolist(), line_candidates)
        product_col = pick_first_existing(df.columns.tolist(), product_candidates)

        if not line_col or not product_col:
            raise HTTPException(status_code=500, detail="ProductRules缺少生产线或产品字段，无法构建联动")

        pair_df = df[[line_col, product_col]].copy()
        pair_df[line_col] = pair_df[line_col].fillna("").astype(str).str.strip()
        pair_df[product_col] = pair_df[product_col].fillna("").astype(str).str.strip()
        pair_df = pair_df[(pair_df[line_col] != "") & (pair_df[product_col] != "")]
        pair_df = pair_df.drop_duplicates()

        line_to_products: dict[str, list[str]] = {}
        product_to_lines: dict[str, list[str]] = {}

        for _, row in pair_df.iterrows():
            line = row[line_col]
            product = row[product_col]

            if line not in line_to_products:
                line_to_products[line] = []
            if product not in line_to_products[line]:
                line_to_products[line].append(product)

            if product not in product_to_lines:
                product_to_lines[product] = []
            if line not in product_to_lines[product]:
                product_to_lines[product].append(line)

        for key in line_to_products:
            line_to_products[key].sort()
        for key in product_to_lines:
            product_to_lines[key].sort()

        return {
            "status": "success",
            "lineColumn": line_col,
            "productColumn": product_col,
            "lineOptions": sorted(line_to_products.keys()),
            "productOptions": sorted(product_to_lines.keys()),
            "lineToProducts": line_to_products,
            "productToLines": product_to_lines,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise exc
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
    finally:
        if conn:
            conn.close()
