from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Iterable, Optional
from urllib.parse import quote

import pandas as pd
import pymssql
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from io import BytesIO

router = APIRouter()


@dataclass(frozen=True)
class DbConfig:
    name: str
    server: str
    database: str
    user: str
    password: str
    charset: str = "utf8"


DF1_ERP = DbConfig("DF1_ERP", "192.168.1.1", "huayueerp", "sa", "3518i", "cp936")
DF2_APS = DbConfig("DF2_APS", "192.168.10.200", "APS_SUO", "sa", "5tgb^YHN7ujm*IK<", "cp936")
DF3_WORK = DbConfig("DF3_DF4_WORK", "192.168.41.57", "department2020", "sa", "3518i")

APS_BACKUP_OBJECT_ID = 2083590561
APS_BACKUP_ORDER_COL_ID = 7
APS_BACKUP_PLAN_START_COL_ID = 12
APS_BACKUP_PLAN_FINISH_COL_ID = 13

PGD_WORKORDER_TABLE = "PGD_WorkOrder_01"
PGD_ORDER_COL_ID = 6
PGD_PLAN_START_COL_ID = 13
PGD_PLAN_FINISH_COL_ID = 14

ERP_SELECTED_COLUMNS = ["订单编号", "订单日期", "客户名称", "创建日期", "审核日期", "审核人", "确定交期"]
WORKORDER_SELECTED_COLUMNS = [
    "PublishDate", "工单编号", "生产车间", "锁类分区", "生产线编号",
    "订单批号", "料品编码", "料品名称", "料品类别", "规格型号",
    "订单数量", "计划开始时间", "计划完成时间", "计划产量", "确定交期",
]

FINISHED_TABLES = {
    "报工_锁芯_SX": "APS_FinishedQty_SX",
    "报工_锁梁_SL": "APS_FinishedQty_SL",
    "报工_锁体开料_ST": "APS_FinishedQty_ST",
    "报工_钥匙_Key": "APS_FinishedQty_Key",
}


def connect(config: DbConfig):
    return pymssql.connect(
        server=config.server, user=config.user, password=config.password,
        database=config.database, login_timeout=8, timeout=60, charset=config.charset,
    )


def make_unique_columns(columns: Iterable[str]) -> list[str]:
    seen: dict[str, int] = {}
    result = []
    idx = 0
    for column in columns:
        name = str(column).strip() if column else ""
        if not name:
            name = f"col_{idx}"
        idx += 1
        if name not in seen:
            seen[name] = 0
            result.append(name)
            continue
        seen[name] += 1
        result.append(f"{name}_{seen[name]}")
    return result


def query_df(conn, sql: str, params: tuple = ()) -> pd.DataFrame:
    cursor = conn.cursor()
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    if cursor.description is None:
        return pd.DataFrame()
    columns = make_unique_columns(col[0] for col in cursor.description)
    return pd.DataFrame.from_records(rows, columns=columns)


def placeholders(values: list[str]) -> str:
    return ", ".join(["%s"] * len(values))


def order_filter_sql(column_name: str, order_numbers: list[str], prefix: bool) -> tuple[str, tuple]:
    if prefix:
        conditions = " OR ".join([f"{column_name} LIKE %s" for _ in order_numbers])
        return f"({conditions})", tuple(f"{order_number}%" for order_number in order_numbers)
    return f"{column_name} IN ({placeholders(order_numbers)})", tuple(order_numbers)


def query_erp_many(conn, order_numbers: list[str], prefix: bool) -> pd.DataFrame:
    where_sql, params = order_filter_sql("o2.sheet_lot", order_numbers, prefix)
    sql = f"""
    SELECT o2.sheet_lot AS order_no, o1.sheet_date AS order_date,
           cust.cust_name AS customer_name, o1.create_date AS create_date,
           o1.audit_date AS audit_date, o1.audit_user AS audit_user,
           o2.affirm_date_comfirm AS confirmed_delivery_date
    FROM dbo.osal_ord2 AS o2
    LEFT JOIN dbo.osal_ord1 AS o1 ON o1.sheet_no = o2.sheet_no
    LEFT JOIN dbo.obas_cust AS cust ON cust.cust_no = o1.cust_no
    WHERE {where_sql}
    ORDER BY o2.sheet_lot, o2.seq_no
    """
    df = query_df(conn, sql, params)
    df = df.rename(columns={
        "order_no": "订单编号", "order_date": "订单日期", "customer_name": "客户名称",
        "create_date": "创建日期", "audit_date": "审核日期", "audit_user": "审核人",
        "confirmed_delivery_date": "确定交期",
    })
    for column in ERP_SELECTED_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    return df[ERP_SELECTED_COLUMNS]


def query_dynamic_chinese_table_many(
    conn, object_id: int, order_col_id: int, order_numbers: list[str],
    prefix: bool, order_by_col_ids: tuple[int, ...] = (),
) -> pd.DataFrame:
    like_flag = 1 if prefix else 0
    values_sql = ", ".join(["(%s)"] * len(order_numbers))
    sql = f"""
    CREATE TABLE #order_filter(value nvarchar(100) NOT NULL);
    INSERT INTO #order_filter(value) VALUES {values_sql};
    DECLARE @table_name nvarchar(300), @order_col sysname, @order_by nvarchar(max) = N'', @sql nvarchar(max);
    SELECT @table_name = QUOTENAME(SCHEMA_NAME(schema_id)) + N'.' + QUOTENAME(name) FROM sys.tables WHERE object_id = %s;
    SELECT @order_col = name FROM sys.columns WHERE object_id = %s AND column_id = %s;
    SELECT @order_by = STUFF((SELECT N', t.' + QUOTENAME(name) FROM sys.columns
        WHERE object_id = %s AND column_id IN (%s, %s, %s) ORDER BY column_id
        FOR XML PATH(''), TYPE).value('.', 'nvarchar(max)'), 1, 2, N'');
    SET @sql = N'SELECT t.* FROM ' + @table_name + N' AS t WHERE EXISTS (SELECT 1 FROM #order_filter f WHERE t.'
        + QUOTENAME(@order_col)
        + CASE WHEN %s = 1 THEN N' LIKE f.value + N''%%''' ELSE N' = f.value' END + N')'
        + CASE WHEN @order_by <> N'' THEN N' ORDER BY ' + @order_by ELSE N'' END;
    EXEC sp_executesql @sql;
    DROP TABLE #order_filter;
    """
    padded_ids = tuple(order_by_col_ids[:3]) + (0,) * (3 - len(order_by_col_ids[:3]))
    params = tuple(order_numbers) + (object_id, object_id, order_col_id, object_id, *padded_ids, like_flag)
    return query_df(conn, sql, params)


def query_aps_backup_many(conn, order_numbers: list[str], prefix: bool) -> pd.DataFrame:
    df = query_dynamic_chinese_table_many(
        conn, APS_BACKUP_OBJECT_ID, order_col_id=APS_BACKUP_ORDER_COL_ID,
        order_numbers=order_numbers, prefix=prefix,
        order_by_col_ids=(APS_BACKUP_PLAN_START_COL_ID, APS_BACKUP_PLAN_FINISH_COL_ID),
    )
    expected_columns = [
        "id", "update_date", "工单编号", "生产车间", "生产线编号", "订单批号",
        "料品编码", "料品名称", "规格型号", "订单数量", "计划开始时间",
        "计划完成时间", "计划产量", "确定交期", "OpExternalId",
    ]
    if len(df.columns) == len(expected_columns):
        df.columns = expected_columns
    return df


def query_pgd_workorder_many(conn, order_numbers: list[str], prefix: bool) -> pd.DataFrame:
    table_sql = "SELECT object_id FROM sys.tables WHERE name = %s"
    object_df = query_df(conn, table_sql, (PGD_WORKORDER_TABLE,))
    if object_df.empty:
        raise RuntimeError(f"找不到表：{PGD_WORKORDER_TABLE}")
    object_id = int(object_df.iloc[0, 0])
    df = query_dynamic_chinese_table_many(
        conn, object_id, order_col_id=PGD_ORDER_COL_ID,
        order_numbers=order_numbers, prefix=prefix,
        order_by_col_ids=(PGD_PLAN_START_COL_ID, PGD_PLAN_FINISH_COL_ID),
    )
    for column in WORKORDER_SELECTED_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    return df[WORKORDER_SELECTED_COLUMNS]


def query_finished_many(table_name: str):
    def _query(conn, order_numbers: list[str], prefix: bool) -> pd.DataFrame:
        where_sql, params = order_filter_sql("OrderNumber", order_numbers, prefix)
        sql = f"SELECT * FROM dbo.{table_name} WHERE {where_sql} ORDER BY FinishedDate, JobExternalId"
        return query_df(conn, sql, params)
    return _query


def pick_column(df: pd.DataFrame, column: str, default: str = "") -> pd.Series:
    if column in df.columns:
        return df[column]
    return pd.Series([default] * len(df), index=df.index)


def normalize_workorder_key(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().replace("\u3000", " ")
    text = re.sub(r"\s*\|\s*", "|", text)
    return text


def combine_finished_records(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    frames = []
    for sheet_name in FINISHED_TABLES:
        df = sheets.get(sheet_name, pd.DataFrame())
        if df.empty:
            continue
        frame = df.copy()
        frame.insert(0, "报工来源", sheet_name)
        frames.append(frame)
    if not frames:
        return pd.DataFrame()
    frames = [frame.dropna(axis=1, how="all") for frame in frames]
    return pd.concat(frames, ignore_index=True, sort=False)


def build_first_backup_full_lookup(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    backup = sheets.get("DF2_排产备份", pd.DataFrame())
    if backup.empty or "工单编号" not in backup.columns:
        return pd.DataFrame()
    sort_columns = [c for c in ("工单编号", "update_date", "id", "计划开始时间") if c in backup.columns]
    backup_sorted = backup.copy()
    backup_sorted["工单编号匹配键"] = backup_sorted["工单编号"].apply(normalize_workorder_key)
    if "update_date" in backup_sorted.columns:
        backup_sorted["_update_date_sort"] = pd.to_datetime(backup_sorted["update_date"], errors="coerce")
        sort_columns = ["工单编号", "_update_date_sort"] + [c for c in sort_columns if c not in ("工单编号", "update_date")]
    backup_sorted = backup_sorted.sort_values(by=sort_columns, kind="stable")
    first_backup = backup_sorted.drop_duplicates(subset=["工单编号匹配键"], keep="first")
    return first_backup.drop(columns=["_update_date_sort"], errors="ignore")


def add_source_prefix(df: pd.DataFrame, prefix: str, keep_columns: tuple[str, ...] = ()) -> pd.DataFrame:
    frame = df.copy()
    rename_map = {c: f"{prefix}{c}" for c in frame.columns if c not in keep_columns}
    return frame.rename(columns=rename_map)


def query_many_from_config(config: DbConfig, query_func, order_numbers: list[str], prefix: bool) -> pd.DataFrame:
    with connect(config) as conn:
        return query_func(conn, order_numbers, prefix)


def build_full_workorder_summary(sheets: dict[str, pd.DataFrame], finished_records: pd.DataFrame) -> pd.DataFrame:
    workorder = sheets.get("DF3_派工单", pd.DataFrame())
    if workorder.empty:
        return pd.DataFrame()

    work = workorder.copy()
    work["订单批号匹配键"] = pick_column(work, "订单批号").astype(str).str.strip()
    work["工单编号匹配键"] = pick_column(work, "工单编号").apply(normalize_workorder_key)

    erp = sheets.get("DF1_ERP订单明细", pd.DataFrame()).copy()
    if not erp.empty and "订单编号" in erp.columns:
        erp["订单批号匹配键"] = erp["订单编号"].astype(str).str.strip()
        erp = erp.drop_duplicates(subset=["订单批号匹配键"], keep="first")
    else:
        erp = pd.DataFrame(columns=["订单批号匹配键"])

    backup = build_first_backup_full_lookup(sheets)
    if backup.empty:
        backup = pd.DataFrame(columns=["工单编号匹配键"])

    if finished_records.empty:
        finished = pd.DataFrame(columns=["OrderNumber", "工单编号匹配键"])
    else:
        finished = finished_records.copy()
        finished["订单批号匹配键"] = finished["OrderNumber"].astype(str).str.strip()
        finished["工单编号匹配键"] = finished["JobExternalId"].apply(normalize_workorder_key)

    helper_columns = {"查询订单批号"}
    erp_columns = [c for c in erp.columns if c not in {"订单批号匹配键", *helper_columns}]
    work_columns = [c for c in work.columns if c not in {"订单批号匹配键", "工单编号匹配键", *helper_columns}]
    backup_columns = [c for c in backup.columns if c not in {"工单编号匹配键", *helper_columns}]
    finished_columns = [c for c in finished.columns if c not in {"订单批号匹配键", "工单编号匹配键", *helper_columns}]

    erp_prefixed = add_source_prefix(erp[["订单批号匹配键", *erp_columns]], "订单明细_", keep_columns=("订单批号匹配键",))
    backup_prefixed = add_source_prefix(backup[["工单编号匹配键", *backup_columns]], "排产备份_", keep_columns=("工单编号匹配键",))
    work_prefixed = add_source_prefix(work[["订单批号匹配键", "工单编号匹配键", *work_columns]], "派工单_", keep_columns=("订单批号匹配键", "工单编号匹配键"))
    finished_prefixed = add_source_prefix(finished[["订单批号匹配键", "工单编号匹配键", *finished_columns]], "报工_", keep_columns=("订单批号匹配键", "工单编号匹配键"))

    merged = work_prefixed.merge(erp_prefixed, how="left", on="订单批号匹配键")
    merged = merged.merge(backup_prefixed, how="left", on="工单编号匹配键")
    merged = merged.merge(finished_prefixed, how="left", on=["订单批号匹配键", "工单编号匹配键"])

    ordered_columns = [
        *[f"订单明细_{c}" for c in erp_columns],
        *[f"排产备份_{c}" for c in backup_columns],
        *[f"派工单_{c}" for c in work_columns],
        *[f"报工_{c}" for c in finished_columns],
    ]
    result = merged[[c for c in ordered_columns if c in merged.columns]]
    sort_columns = [c for c in (
        "订单明细_affirm_date_comfirm", "订单明细_确定交期", "派工单_确定交期",
        "派工单_订单批号", "派工单_计划开始时间", "报工_FinishedDate",
    ) if c in result.columns]
    if sort_columns:
        result = result.sort_values(by=sort_columns, kind="stable", ignore_index=True)
    return result


@router.get("/workorderSummary", summary="派工单汇总查询")
async def get_workorder_summary(
    订单编号: str = Query(..., description="订单编号，模糊搜索"),
    开始时间: Optional[str] = Query(None, description="开始时间，年-月"),
    结束时间: Optional[str] = Query(None, description="结束时间，年-月"),
    工单编号: Optional[str] = Query(None, description="工单编号，模糊搜索"),
    姓名: Optional[str] = Query(None, description="姓名，模糊搜索"),
):
    try:
        order_numbers = [订单编号.strip()]
        start_time = (开始时间 or "").strip()
        end_time = (结束时间 or "").strip()
        workorder_no = (工单编号 or "").strip()
        emp_name = (姓名 or "").strip()

        sheets: dict[str, pd.DataFrame] = {}
        tasks = {
            "DF1_ERP订单明细": (DF1_ERP, query_erp_many),
            "DF2_排产备份": (DF2_APS, query_aps_backup_many),
            "DF3_派工单": (DF3_WORK, query_pgd_workorder_many),
        }
        for sheet_name, table_name in FINISHED_TABLES.items():
            tasks[sheet_name] = (DF3_WORK, query_finished_many(table_name))

        max_workers = min(len(tasks), 7)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_sheet = {
                executor.submit(query_many_from_config, config, query_func, order_numbers, True): sheet_name
                for sheet_name, (config, query_func) in tasks.items()
            }
            for future in as_completed(future_to_sheet):
                sheets[future_to_sheet[future]] = future.result()

        finished_records = combine_finished_records(sheets)
        workorder_summary = build_full_workorder_summary(sheets, finished_records)

        time_col = "派工单_计划开始时间"
        if not workorder_summary.empty and time_col in workorder_summary.columns:
            workorder_summary["_计划开始"] = pd.to_datetime(workorder_summary[time_col], errors="coerce")
            if start_time:
                workorder_summary = workorder_summary[workorder_summary["_计划开始"] >= pd.Timestamp(start_time)]
            if end_time:
                workorder_summary = workorder_summary[workorder_summary["_计划开始"] < pd.Timestamp(end_time) + pd.offsets.MonthEnd(1)]
            workorder_summary = workorder_summary.drop(columns=["_计划开始"])

        wo_col = "派工单_工单编号"
        if not workorder_summary.empty and workorder_no and wo_col in workorder_summary.columns:
            workorder_summary = workorder_summary[workorder_summary[wo_col].astype(str).str.contains(workorder_no, na=False)]

        emp_col = "报工_emp_name"
        if not workorder_summary.empty and emp_name and emp_col in workorder_summary.columns:
            workorder_summary = workorder_summary[workorder_summary[emp_col].astype(str).str.contains(emp_name, na=False)]

        records = workorder_summary.fillna("").to_dict(orient="records")
        for i, record in enumerate(records, start=1):
            record["序列号"] = i
        return {"status": "success", "data": records, "total_count": len(records)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")


@router.get("/workorderSummaryExport", summary="派工单汇总导出")
async def export_workorder_summary(
    订单编号: str = Query(...),
    开始时间: Optional[str] = Query(None),
    结束时间: Optional[str] = Query(None),
    工单编号: Optional[str] = Query(None),
    姓名: Optional[str] = Query(None),
):
    try:
        order_numbers = [订单编号.strip()]
        start_time = (开始时间 or "").strip()
        end_time = (结束时间 or "").strip()
        workorder_no = (工单编号 or "").strip()
        emp_name = (姓名 or "").strip()

        sheets: dict[str, pd.DataFrame] = {}
        tasks = {
            "DF1_ERP订单明细": (DF1_ERP, query_erp_many),
            "DF2_排产备份": (DF2_APS, query_aps_backup_many),
            "DF3_派工单": (DF3_WORK, query_pgd_workorder_many),
        }
        for sheet_name, table_name in FINISHED_TABLES.items():
            tasks[sheet_name] = (DF3_WORK, query_finished_many(table_name))

        max_workers = min(len(tasks), 7)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_sheet = {
                executor.submit(query_many_from_config, config, query_func, order_numbers, True): sheet_name
                for sheet_name, (config, query_func) in tasks.items()
            }
            for future in as_completed(future_to_sheet):
                sheets[future_to_sheet[future]] = future.result()

        finished_records = combine_finished_records(sheets)
        workorder_summary = build_full_workorder_summary(sheets, finished_records)

        time_col = "派工单_计划开始时间"
        if not workorder_summary.empty and time_col in workorder_summary.columns:
            workorder_summary["_计划开始"] = pd.to_datetime(workorder_summary[time_col], errors="coerce")
            if start_time:
                workorder_summary = workorder_summary[workorder_summary["_计划开始"] >= pd.Timestamp(start_time)]
            if end_time:
                workorder_summary = workorder_summary[workorder_summary["_计划开始"] < pd.Timestamp(end_time) + pd.offsets.MonthEnd(1)]
            workorder_summary = workorder_summary.drop(columns=["_计划开始"])

        wo_col = "派工单_工单编号"
        if not workorder_summary.empty and workorder_no and wo_col in workorder_summary.columns:
            workorder_summary = workorder_summary[workorder_summary[wo_col].astype(str).str.contains(workorder_no, na=False)]

        emp_col = "报工_emp_name"
        if not workorder_summary.empty and emp_name and emp_col in workorder_summary.columns:
            workorder_summary = workorder_summary[workorder_summary[emp_col].astype(str).str.contains(emp_name, na=False)]

        if workorder_summary.empty:
            workorder_summary = pd.DataFrame(columns=["说明"])
            workorder_summary.loc[0] = ["无匹配数据"]

        for col in workorder_summary.columns:
            if workorder_summary[col].dtype == "datetime64[ns]" or pd.api.types.is_datetime64_any_dtype(workorder_summary[col]):
                workorder_summary[col] = workorder_summary[col].dt.strftime("%Y-%m-%d %H:%M:%S").fillna("")
            else:
                workorder_summary[col] = workorder_summary[col].astype(str).replace("NaT", "").replace("nan", "")

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            workorder_summary.to_excel(writer, index=False, sheet_name="派工单汇总")
        output.seek(0)

        filename = f"派工单汇总_{订单编号}.xlsx"
        encoded_filename = quote(filename)
        headers = {"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"导出失败: {exc}")
