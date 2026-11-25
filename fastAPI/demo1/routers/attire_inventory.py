from __future__ import annotations

import io
import os
import re
import urllib.parse
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd
import pymssql
import pyodbc
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from openpyxl import Workbook

router = APIRouter(prefix="/attireInventory", tags=["attireInventory"])

# 数据库配置 - APS_SUO
DB_APS_SUO_SERVER = os.getenv("DB_APS_SUO_SERVER", "192.168.10.200")
DB_APS_SUO_DATABASE = os.getenv("DB_APS_SUO_DATABASE", "APS_SUO")
DB_APS_SUO_USERNAME = os.getenv("DB_APS_SUO_USERNAME", "sa")
DB_APS_SUO_PASSWORD = os.getenv("DB_APS_SUO_PASSWORD", "5tgb^YHN7ujm*IK<")

# 数据库配置 - APS_Result
DB_APS_RESULT_SERVER = os.getenv("DB_APS_RESULT_SERVER", "192.168.10.200")
DB_APS_RESULT_DATABASE = os.getenv("DB_APS_RESULT_DATABASE", "APS_Result")
DB_APS_RESULT_USERNAME = os.getenv("DB_APS_RESULT_USERNAME", "sa")
DB_APS_RESULT_PASSWORD = os.getenv("DB_APS_RESULT_PASSWORD", "5tgb^YHN7ujm*IK<")

# 数据库配置 - department2020
DB_DEPARTMENT_SERVER = os.getenv("DB_DEPARTMENT_SERVER", "192.168.41.57")
DB_DEPARTMENT_DATABASE = os.getenv("DB_DEPARTMENT_DATABASE", "department2020")
DB_DEPARTMENT_USERNAME = os.getenv("DB_DEPARTMENT_USERNAME", "sa")
DB_DEPARTMENT_PASSWORD = os.getenv("DB_DEPARTMENT_PASSWORD", "3518i")

# 数据库配置 - ERP
DB_ERP_SERVER = os.getenv("DB_ERP_SERVER", "192.168.1.1")
DB_ERP_DATABASE = os.getenv("DB_ERP_DATABASE", "huayueerp")
DB_ERP_USERNAME = os.getenv("DB_ERP_USERNAME", "sa")
DB_ERP_PASSWORD = os.getenv("DB_ERP_PASSWORD", "3518i")

# 业务配置
START_DATE = os.getenv("START_DATE", "2026-08-14")
ISSUE_START_DATE = os.getenv("ISSUE_START_DATE", "2026-08-13")
REPORT_START_DATETIME = os.getenv("REPORT_START_DATETIME", "2026-08-14 12:00:00")
ERP_MAPPING_START_DATE = os.getenv("ERP_MAPPING_START_DATE", "2026-01-01")

ISSUE_AREA = os.getenv("ISSUE_AREA", "中间件+待发料")
AUTO_AREA = os.getenv("AUTO_AREA", "自动机")
MANUAL_AREA = os.getenv("MANUAL_AREA", "手工线")
AUTO_IN_OP = os.getenv("AUTO_IN_OP", "装拨套中间件")
AUTO_OUT_OP_PREFIX = os.getenv("AUTO_OUT_OP_PREFIX", "OP-")
DIRECT_AUTO_RESOURCE_MIN = os.getenv("DIRECT_AUTO_RESOURCE_MIN", "ZQ-03-013")

CACHE_DIR = Path(__file__).parent.parent.parent / "data" / "cache"
CACHE_FILE = CACHE_DIR / "inventory_snapshot.xlsx"

# SQL 查询
OPENING_SQL = """
SELECT
    [料品编码] AS item_no,
    [型号规格] AS model_spec,
    [只数] AS qty,
    [盘点区域] AS area
FROM [APS_SUO].[dbo].[AttireInventory]
"""

ISSUE_SQL = """
SELECT
    a.[sheet_no],
    a.[sheet_date],
    a.[sheet_sta] AS header_sheet_sta,
    a.[audit_date],
    a.[audit_user],
    a.[create_date],
    a.[user_no],
    a.[rem] AS header_rem,
    a.[create_user],
    a.[已发料],
    a.[车间已确认],
    b.[sheet_lot],
    b.[sheet_sta] AS detail_sheet_sta,
    b.[unit_no],
    b.[unit_rate],
    b.[sheet_qty] AS issue_qty,
    b.[rem] AS detail_rem,
    b.[define1],
    b.[define2],
    b.[define3],
    b.[define4],
    b.[define5] AS item_no,
    b.[draw_no],
    b.[SO_sheet_lot],
    b.[确定交期],
    b.[needQty],
    b.[MoExternalId],
    b.[OPExternalId],
    b.[totalRequiredQty],
    b.[ScheduledStartDate],
    b.[锁体盆数],
    b.[part_name]
FROM [APS_Result].[dbo].[oscm_other1] a
LEFT JOIN [APS_Result].[dbo].[oscm_other2] b
    ON a.sheet_no = b.sheet_no
WHERE a.sheet_date > ?
  AND a.sheet_no LIKE '%ST%'
  AND b.define4 LIKE 'ZQ-03%'
"""

REPORT_SQL = """
SELECT
    a.*,
    dbo.RemoveChineseChars(a.ItemExternalId) AS item_no,
    b.OpExternalId,
    b.确定交期
FROM APS_FinishedQty a
LEFT JOIN 派工单_backup b
    ON a.JobExternalId = b.工单编号
WHERE a.FinishedDate > ?
  AND b.生产车间 = '装嵌车间-铝门锁区'
"""

MAPPING_SQL = """
SELECT
    a.sheet_lot AS order_lot,
    a.short_lot AS short_lot,
    obas_part_1.item_no AS product_item_no,
    obas_part_1.part_name AS product_part_name,
    obas_part_2.item_no AS semi_item_no,
    obas_part_2.part_spec AS semi_part_spec
FROM osal_ord2 a
INNER JOIN dbo.obas_part AS obas_part_1
    ON a.part_no = obas_part_1.part_no
INNER JOIN dbo.obom_stru2 AS obom_stru2_1
    ON obom_stru2_1.parent_part = obas_part_1.part_no
INNER JOIN dbo.obas_part AS obas_part_2
    ON obom_stru2_1.child_part = obas_part_2.part_no
WHERE obas_part_1.item_no LIKE '1%'
  AND obas_part_1.act_sw = 1
  AND obas_part_2.act_sw = 1
  AND obas_part_2.part_name LIKE '%锁体%'
  AND a.affirm_date > ?
"""

DIRECT_AUTO_ASSIGNMENT_SQL = """
SELECT
    item_no AS product_item_no,
    ResourceExternalid AS resource_external_id
FROM [Capabilityassignment]
WHERE item_no IS NOT NULL
  AND ResourceExternalid LIKE 'ZQ-03-%'
"""


@dataclass(frozen=True)
class RefreshResult:
    cache_file: Path
    refreshed_at: datetime
    opening_rows: int
    issue_rows: int
    report_rows: int
    mapping_rows: int
    inventory_rows: int


def get_db_connection(server: str, database: str, username: str, password: str):
    conn = pymssql.connect(
        server=server,
        user=username,
        password=password,
        database=database,
        login_timeout=30,
        timeout=120,
        charset="UTF-8",
    )
    return conn


def read_sql(server: str, database: str, username: str, password: str, sql: str, params: tuple = ()) -> pd.DataFrame:
    pymssql_sql = sql.replace("?", "%s")
    conn = get_db_connection(server, database, username, password)
    try:
        cursor = conn.cursor()
        cursor.execute(pymssql_sql, params or ())
        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()
        return pd.DataFrame.from_records(rows, columns=columns)
    finally:
        conn.close()


def _clean_item(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _to_qty(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0)


def _normalize_area(value: object) -> str:
    if pd.isna(value):
        return ""
    area = str(value).strip()
    if area == "中间件+代发料":
        return "中间件+待发料"
    return area


def _resource_rank(value: object) -> Optional[int]:
    if pd.isna(value):
        return None
    match = re.match(r"^ZQ-03-(\d+)$", str(value).strip(), flags=re.IGNORECASE)
    if not match:
        return None
    return int(match.group(1))


def _first_nonempty(series: pd.Series) -> str:
    for value in series:
        if not pd.isna(value) and str(value).strip():
            return str(value).strip()
    return ""


def _first_existing_column(columns: Iterable[str], candidates: list) -> str:
    col_set = {str(col).lower(): col for col in columns}
    for candidate in candidates:
        found = col_set.get(candidate.lower())
        if found is not None:
            return found
    raise KeyError(f"未找到数量字段，已尝试: {', '.join(candidates)}")


def _number(value):
    if pd.isna(value):
        return 0
    return float(value)


def _text(value):
    if pd.isna(value):
        return ""
    return str(value)


class InventoryService:
    def __init__(self, cache_file: Optional[Path] = None):
        self.cache_file = cache_file or CACHE_FILE

    def refresh(self) -> RefreshResult:
        opening = self.fetch_opening()
        issues = self.fetch_issues()
        reports = self.fetch_reports()
        mapping = self.fetch_mapping()
        direct_auto_products = self.fetch_direct_auto_products()
        mapping = self.apply_direct_auto_flag(mapping, direct_auto_products)
        movements = self.build_movements(issues, reports, mapping)
        daily_inventory = self.calculate_daily_inventory(opening, movements, mapping)

        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with pd.ExcelWriter(self.cache_file, engine="openpyxl") as writer:
            opening.to_excel(writer, index=False, sheet_name="opening")
            issues.to_excel(writer, index=False, sheet_name="issue_raw")
            reports.to_excel(writer, index=False, sheet_name="report_raw")
            direct_auto_products.to_excel(writer, index=False, sheet_name="direct_auto_products")
            mapping.to_excel(writer, index=False, sheet_name="mapping_raw")
            movements.to_excel(writer, index=False, sheet_name="movements")
            daily_inventory.to_excel(writer, index=False, sheet_name="daily_inventory")

        return RefreshResult(
            cache_file=self.cache_file,
            refreshed_at=datetime.now(),
            opening_rows=len(opening),
            issue_rows=len(issues),
            report_rows=len(reports),
            mapping_rows=len(mapping),
            inventory_rows=len(daily_inventory),
        )

    def fetch_opening(self) -> pd.DataFrame:
        df = read_sql(DB_APS_SUO_SERVER, DB_APS_SUO_DATABASE, DB_APS_SUO_USERNAME, DB_APS_SUO_PASSWORD, OPENING_SQL)
        if df.empty:
            return pd.DataFrame(columns=["item_no", "model_spec", "qty", "area"])
        df["item_no"] = df["item_no"].map(_clean_item)
        df["model_spec"] = df["model_spec"].fillna("").astype(str).str.strip()
        df["area"] = df["area"].map(_normalize_area)
        df["qty"] = _to_qty(df["qty"])
        return df[df["item_no"] != ""]

    def fetch_issues(self) -> pd.DataFrame:
        df = read_sql(DB_APS_RESULT_SERVER, DB_APS_RESULT_DATABASE, DB_APS_RESULT_USERNAME, DB_APS_RESULT_PASSWORD, ISSUE_SQL, (ISSUE_START_DATE,))
        if df.empty:
            return pd.DataFrame()
        df["item_no"] = df["item_no"].map(_clean_item)
        df["issue_qty"] = _to_qty(df["issue_qty"])
        df["sheet_date"] = pd.to_datetime(df["sheet_date"], errors="coerce")
        return df[(df["item_no"] != "") & df["sheet_date"].notna()]

    def fetch_reports(self) -> pd.DataFrame:
        df = read_sql(DB_DEPARTMENT_SERVER, DB_DEPARTMENT_DATABASE, DB_DEPARTMENT_USERNAME, DB_DEPARTMENT_PASSWORD, REPORT_SQL, (REPORT_START_DATETIME,))
        if df.empty:
            return pd.DataFrame()
        qty_col = _first_existing_column(
            df.columns,
            [
                "EachFinishedQty",
                "FinishedQty",
                "FinishedQuantity",
                "finish_qty",
                "qty",
                "数量",
                "报工数量",
                "合格数量",
                "QualityQty",
            ],
        )
        df = df.rename(columns={qty_col: "report_qty"})
        df["item_no"] = df["item_no"].map(_clean_item)
        df["report_qty"] = _to_qty(df["report_qty"])
        df["FinishedDate"] = pd.to_datetime(df["FinishedDate"], errors="coerce")
        df["OpExternalId"] = df["OpExternalId"].fillna("").astype(str).str.strip()
        return df[(df["item_no"] != "") & df["FinishedDate"].notna()]

    def fetch_mapping(self) -> pd.DataFrame:
        df = read_sql(DB_ERP_SERVER, DB_ERP_DATABASE, DB_ERP_USERNAME, DB_ERP_PASSWORD, MAPPING_SQL, (ERP_MAPPING_START_DATE,))
        if df.empty:
            return pd.DataFrame(
                columns=["order_lot", "short_lot", "product_item_no", "semi_item_no", "semi_part_spec"]
            )
        df["product_item_no"] = df["product_item_no"].map(_clean_item)
        df["semi_item_no"] = df["semi_item_no"].map(_clean_item)
        df["semi_part_spec"] = df["semi_part_spec"].fillna("").astype(str).str.strip()
        df["order_lot"] = df["order_lot"].fillna("").astype(str).str.strip()
        df["short_lot"] = df["short_lot"].fillna("").astype(str).str.strip()
        df = df[(df["product_item_no"] != "") & (df["semi_item_no"] != "")]
        return df.drop_duplicates(["order_lot", "short_lot", "product_item_no", "semi_item_no", "semi_part_spec"])

    def fetch_direct_auto_products(self) -> pd.DataFrame:
        df = read_sql(DB_APS_SUO_SERVER, DB_APS_SUO_DATABASE, DB_APS_SUO_USERNAME, DB_APS_SUO_PASSWORD, DIRECT_AUTO_ASSIGNMENT_SQL)
        if df.empty:
            return pd.DataFrame(columns=["product_item_no", "resource_external_id"])
        min_rank = _resource_rank(DIRECT_AUTO_RESOURCE_MIN)
        if min_rank is None:
            raise ValueError(f"DIRECT_AUTO_RESOURCE_MIN 格式必须类似 ZQ-03-013: {DIRECT_AUTO_RESOURCE_MIN}")
        df["product_item_no"] = df["product_item_no"].map(_clean_item)
        df["resource_external_id"] = df["resource_external_id"].fillna("").astype(str).str.strip()
        df["resource_rank"] = df["resource_external_id"].map(_resource_rank)
        df = df[(df["product_item_no"] != "") & df["resource_rank"].notna()]
        df = df[df["resource_rank"] >= min_rank]
        return df.drop_duplicates(["product_item_no", "resource_external_id"])[
            ["product_item_no", "resource_external_id"]
        ]

    def apply_direct_auto_flag(self, mapping: pd.DataFrame, direct_auto_products: pd.DataFrame) -> pd.DataFrame:
        mapping = mapping.copy()
        if mapping.empty:
            mapping["is_direct_auto"] = False
            return mapping
        direct_products = set(direct_auto_products["product_item_no"]) if not direct_auto_products.empty else set()
        mapping["is_direct_auto"] = mapping["product_item_no"].isin(direct_products)
        return mapping

    def build_movements(self, issues: pd.DataFrame, reports: pd.DataFrame, mapping: pd.DataFrame) -> pd.DataFrame:
        frames: list = []

        if not issues.empty:
            issue_mapping = mapping[
                ["order_lot", "product_item_no", "semi_item_no", "is_direct_auto"]
            ].drop_duplicates(["order_lot", "semi_item_no"])
            issue_with_map = issues.merge(
                issue_mapping,
                left_on=["SO_sheet_lot", "item_no"],
                right_on=["order_lot", "semi_item_no"],
                how="left",
            )
            issue_with_map["is_direct_auto"] = issue_with_map["is_direct_auto"].eq(True)

            normal_issue = issue_with_map[~issue_with_map["is_direct_auto"]]
            if not normal_issue.empty:
                frames.append(
                    pd.DataFrame(
                        {
                            "movement_date": normal_issue["sheet_date"].dt.date,
                            "item_no": normal_issue["item_no"],
                            "area": _normalize_area(ISSUE_AREA),
                            "in_qty": normal_issue["issue_qty"],
                            "out_qty": 0,
                            "source": "发料",
                        }
                    )
                )

            direct_auto_issue = issue_with_map[issue_with_map["is_direct_auto"]]
            if not direct_auto_issue.empty:
                frames.append(
                    pd.DataFrame(
                        {
                            "movement_date": direct_auto_issue["sheet_date"].dt.date,
                            "item_no": direct_auto_issue["item_no"],
                            "area": MANUAL_AREA,
                            "in_qty": direct_auto_issue["issue_qty"],
                            "out_qty": 0,
                            "source": "发料-手工线",
                        }
                    )
                )

        if not reports.empty:
            report_mapping = mapping[["product_item_no", "semi_item_no", "is_direct_auto"]].drop_duplicates(
                ["product_item_no", "semi_item_no", "is_direct_auto"]
            )
            report_with_map = reports.merge(
                report_mapping,
                left_on="item_no",
                right_on="product_item_no",
                how="left",
            )
            report_with_map["semi_item_no"] = report_with_map["semi_item_no"].fillna("")
            report_with_map["is_direct_auto"] = report_with_map["is_direct_auto"].eq(True)
            report_with_map = report_with_map[report_with_map["semi_item_no"] != ""]

            auto_in = report_with_map[
                (report_with_map["OpExternalId"] == AUTO_IN_OP) & (~report_with_map["is_direct_auto"])
            ]
            if not auto_in.empty:
                frames.append(
                    pd.DataFrame(
                        {
                            "movement_date": auto_in["FinishedDate"].dt.date,
                            "item_no": auto_in["semi_item_no"],
                            "area": AUTO_AREA,
                            "in_qty": auto_in["report_qty"],
                            "out_qty": 0,
                            "source": "报工-自动机流入",
                        }
                    )
                )

            manual_out = report_with_map[report_with_map["is_direct_auto"]]
            if not manual_out.empty:
                frames.append(
                    pd.DataFrame(
                        {
                            "movement_date": manual_out["FinishedDate"].dt.date,
                            "item_no": manual_out["semi_item_no"],
                            "area": MANUAL_AREA,
                            "in_qty": 0,
                            "out_qty": manual_out["report_qty"],
                            "source": "报工-手工线流出",
                        }
                    )
                )

            auto_out = report_with_map[
                (~report_with_map["is_direct_auto"])
                & report_with_map["OpExternalId"].str.startswith(AUTO_OUT_OP_PREFIX, na=False)
            ]
            if not auto_out.empty:
                frames.append(
                    pd.DataFrame(
                        {
                            "movement_date": auto_out["FinishedDate"].dt.date,
                            "item_no": auto_out["semi_item_no"],
                            "area": AUTO_AREA,
                            "in_qty": 0,
                            "out_qty": auto_out["report_qty"],
                            "source": "报工-自动机流出",
                        }
                    )
                )

        if not frames:
            return pd.DataFrame(columns=["movement_date", "item_no", "area", "in_qty", "out_qty", "source"])

        movements = pd.concat(frames, ignore_index=True)
        movements["in_qty"] = _to_qty(movements["in_qty"])
        movements["out_qty"] = _to_qty(movements["out_qty"])
        return movements.groupby(["movement_date", "item_no", "area", "source"], as_index=False)[
            ["in_qty", "out_qty"]
        ].sum()

    def calculate_daily_inventory(
        self, opening: pd.DataFrame, movements: pd.DataFrame, mapping: pd.DataFrame
    ) -> pd.DataFrame:
        start = pd.to_datetime(START_DATE).date()
        today = date.today()
        dates = pd.date_range(start=start, end=today, freq="D").date

        opening_grouped = opening.groupby(["item_no", "area"], as_index=False).agg(
            opening_qty=("qty", "sum"),
            model_spec=("model_spec", "first"),
        )
        item_specs = (
            opening_grouped.groupby("item_no", as_index=False)
            .agg(model_spec=("model_spec", _first_nonempty))
        )
        if not mapping.empty and "semi_part_spec" in mapping.columns:
            erp_specs = (
                mapping.groupby("semi_item_no", as_index=False)
                .agg(erp_model_spec=("semi_part_spec", _first_nonempty))
                .rename(columns={"semi_item_no": "item_no"})
            )
        else:
            erp_specs = pd.DataFrame(columns=["item_no", "erp_model_spec"])

        if not movements.empty:
            move_items = movements[["item_no", "area"]].drop_duplicates()
            all_keys = pd.concat([opening_grouped[["item_no", "area"]], move_items], ignore_index=True).drop_duplicates()
        else:
            all_keys = opening_grouped[["item_no", "area"]].drop_duplicates()

        calendar = pd.DataFrame({"inventory_date": dates})
        daily = all_keys.merge(calendar, how="cross")
        daily = daily.merge(opening_grouped[["item_no", "area", "opening_qty"]], on=["item_no", "area"], how="left")
        daily["opening_qty"] = daily["opening_qty"].fillna(0)

        if not movements.empty:
            move_daily = movements.groupby(["movement_date", "item_no", "area"], as_index=False)[
                ["in_qty", "out_qty"]
            ].sum()
            move_daily = move_daily.rename(columns={"movement_date": "inventory_date"})
            daily = daily.merge(move_daily, on=["inventory_date", "item_no", "area"], how="left")
        else:
            daily["in_qty"] = 0
            daily["out_qty"] = 0

        daily["in_qty"] = daily["in_qty"].fillna(0)
        daily["out_qty"] = daily["out_qty"].fillna(0)
        daily = daily.sort_values(["item_no", "area", "inventory_date"])
        daily["cum_in_qty"] = daily.groupby(["item_no", "area"])["in_qty"].cumsum()
        daily["cum_out_qty"] = daily.groupby(["item_no", "area"])["out_qty"].cumsum()
        daily["stock_qty"] = daily["opening_qty"] + daily["cum_in_qty"] - daily["cum_out_qty"]
        daily = daily.merge(item_specs, on="item_no", how="left")
        daily = daily.merge(erp_specs, on="item_no", how="left")
        daily["model_spec"] = daily["model_spec"].fillna("").astype(str).str.strip()
        daily["erp_model_spec"] = daily["erp_model_spec"].fillna("").astype(str).str.strip()
        daily["model_spec"] = daily["model_spec"].where(daily["model_spec"] != "", daily["erp_model_spec"])
        return daily[
            [
                "inventory_date",
                "area",
                "item_no",
                "model_spec",
                "opening_qty",
                "in_qty",
                "out_qty",
                "cum_in_qty",
                "cum_out_qty",
                "stock_qty",
            ]
        ]

    def load_inventory(self) -> pd.DataFrame:
        if not self.cache_file.exists():
            self.refresh()
        df = pd.read_excel(self.cache_file, sheet_name="daily_inventory")
        df["inventory_date"] = pd.to_datetime(df["inventory_date"]).dt.date
        df["model_spec"] = df["model_spec"].fillna("")
        df["area"] = df["area"].map(_normalize_area)
        df["item_no"] = df["item_no"].fillna("")
        return df

    def load_movements(self) -> pd.DataFrame:
        if not self.cache_file.exists():
            self.refresh()
        df = pd.read_excel(self.cache_file, sheet_name="movements")
        if not df.empty:
            df["movement_date"] = pd.to_datetime(df["movement_date"]).dt.date
            df["area"] = df["area"].map(_normalize_area)
        return df


inventory_service = InventoryService()


def _inventory_frame(target_date: str, area: str, item_no: str, only_positive: bool) -> pd.DataFrame:
    parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
    df = inventory_service.load_inventory()
    df = df[df["inventory_date"] == parsed_date]
    if area:
        df = df[df["area"].astype(str) == area]
    if item_no:
        df = df[df["item_no"].astype(str).str.contains(item_no, case=False, na=False)]
    if only_positive:
        df = df[df["stock_qty"].round(6) > 0]
    return df.sort_values(["area", "item_no"])


def _movement_frame(target_date: str, area: str, item_no: str) -> pd.DataFrame:
    parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
    df = inventory_service.load_movements()
    if df.empty:
        return df
    df = df[df["movement_date"] == parsed_date]
    if area:
        df = df[df["area"].astype(str) == area]
    if item_no:
        df = df[df["item_no"].astype(str).str.contains(item_no, case=False, na=False)]
    return df.sort_values(["area", "item_no", "source"])


@router.get("/options", summary="获取筛选选项")
def get_options():
    try:
        df = inventory_service.load_inventory()
        latest_date = df["inventory_date"].max() if not df.empty else date.today().isoformat()
        return {
            "ok": True,
            "start_date": START_DATE,
            "latest_date": latest_date,
            "areas": sorted(df["area"].dropna().astype(str).unique().tolist()),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/inventory", summary="查询库存")
def get_inventory(
    target_date: str = Query(default=None, description="日期 YYYY-MM-DD"),
    area: str = Query(default="", description="区域"),
    item_no: str = Query(default="", description="料品编码"),
    only_nonzero: str = Query(default="1", description="只看有库存"),
):
    try:
        if not target_date:
            target_date = date.today().isoformat()
        only_positive = only_nonzero == "1"

        df = _inventory_frame(target_date, area, item_no, only_positive)
        totals = {
            "opening_qty": _number(df["opening_qty"].sum()) if not df.empty else 0,
            "in_qty": _number(df["in_qty"].sum()) if not df.empty else 0,
            "out_qty": _number(df["out_qty"].sum()) if not df.empty else 0,
            "cum_in_qty": _number(df["cum_in_qty"].sum()) if not df.empty else 0,
            "cum_out_qty": _number(df["cum_out_qty"].sum()) if not df.empty else 0,
            "stock_qty": _number(df["stock_qty"].sum()) if not df.empty else 0,
            "rows": int(len(df)),
        }
        rows = [
            {
                "inventory_date": row.inventory_date.isoformat(),
                "area": _text(row.area),
                "item_no": _text(row.item_no),
                "model_spec": _text(row.model_spec),
                "opening_qty": _number(row.opening_qty),
                "in_qty": _number(row.in_qty),
                "out_qty": _number(row.out_qty),
                "cum_in_qty": _number(row.cum_in_qty),
                "cum_out_qty": _number(row.cum_out_qty),
                "stock_qty": _number(row.stock_qty),
            }
            for row in df.itertuples(index=False)
        ]
        return {"ok": True, "totals": totals, "rows": rows}
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式必须是 YYYY-MM-DD")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/movements", summary="查询动作汇总")
def get_movements(
    target_date: str = Query(default=None, description="日期 YYYY-MM-DD"),
    area: str = Query(default="", description="区域"),
    item_no: str = Query(default="", description="料品编码"),
):
    try:
        if not target_date:
            target_date = date.today().isoformat()

        df = _movement_frame(target_date, area, item_no)
        if df.empty:
            return {"ok": True, "rows": []}
        rows = [
            {
                "movement_date": row.movement_date.isoformat(),
                "area": _text(row.area),
                "item_no": _text(row.item_no),
                "source": _text(row.source),
                "in_qty": _number(row.in_qty),
                "out_qty": _number(row.out_qty),
            }
            for row in df.itertuples(index=False)
        ]
        return {"ok": True, "rows": rows}
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式必须是 YYYY-MM-DD")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/export", summary="导出Excel")
def export_excel(
    target_date: str = Query(default=None, description="日期 YYYY-MM-DD"),
    area: str = Query(default="", description="区域"),
    item_no: str = Query(default="", description="料品编码"),
    only_nonzero: str = Query(default="1", description="只看有库存"),
):
    try:
        if not target_date:
            target_date = date.today().isoformat()
        only_positive = only_nonzero == "1"

        inventory_df = _inventory_frame(target_date, area, item_no, only_positive)
        movement_df = _movement_frame(target_date, area, item_no)

        inventory_export = inventory_df.rename(
            columns={
                "inventory_date": "日期",
                "area": "区域",
                "item_no": "料品编码",
                "model_spec": "型号规格",
                "opening_qty": "期初",
                "in_qty": "当日流入",
                "out_qty": "当日流出",
                "cum_in_qty": "累计流入",
                "cum_out_qty": "累计流出",
                "stock_qty": "实时库存",
            }
        )
        inventory_export["日期"] = inventory_export["日期"].astype(str)

        movement_export = movement_df.rename(
            columns={
                "movement_date": "日期",
                "area": "区域",
                "item_no": "料品编码",
                "source": "来源",
                "in_qty": "流入",
                "out_qty": "流出",
            }
        )
        if not movement_export.empty:
            movement_export["日期"] = movement_export["日期"].astype(str)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            inventory_export.to_excel(writer, index=False, sheet_name="库存明细")
            movement_export.to_excel(writer, index=False, sheet_name="当日动作汇总")

            for sheet in writer.book.worksheets:
                sheet.freeze_panes = "A2"
                for column_cells in sheet.columns:
                    max_len = max(len(str(cell.value or "")) for cell in column_cells)
                    sheet.column_dimensions[column_cells[0].column_letter].width = min(max(max_len + 2, 10), 28)

        output.seek(0)
        area_name = area or "全部区域"
        filename = f"锁体实时库存_{target_date}_{area_name}.xlsx"
        encoded_filename = urllib.parse.quote(filename)

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式必须是 YYYY-MM-DD")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/refresh", summary="刷新数据")
def refresh_data():
    try:
        result = inventory_service.refresh()
        return {
            "ok": True,
            "cache_file": str(result.cache_file),
            "refreshed_at": result.refreshed_at.strftime("%Y-%m-%d %H:%M:%S"),
            "opening_rows": result.opening_rows,
            "issue_rows": result.issue_rows,
            "report_rows": result.report_rows,
            "mapping_rows": result.mapping_rows,
            "inventory_rows": result.inventory_rows,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
