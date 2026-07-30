from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import os
import glob
import re
import openpyxl

router = APIRouter()

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "workshop_realTime_inventory")

def find_latest_file():
    pattern = os.path.join(DATA_DIR, "*.xlsx")
    files = [f for f in glob.glob(pattern) if not os.path.basename(f).startswith("~$")]
    if not files:
        return None, None
    files.sort(key=lambda f: os.path.basename(f))
    latest = files[-1]
    basename = os.path.splitext(os.path.basename(latest))[0]
    match = re.match(r"(\d{4})(\d{2})(\d{2})", basename)
    if match:
        update_time = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    else:
        update_time = basename
    return latest, update_time

def read_excel(filepath):
    wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    if not rows:
        return []
    headers = [str(h).strip() if h else "" for h in rows[0]]
    data = []
    for row in rows[1:]:
        if all(cell is None for cell in row):
            continue
        record = {}
        for i, h in enumerate(headers):
            val = row[i] if i < len(row) else None
            record[h] = val
        data.append(record)
    return data

@router.get("/workshopRealTimeInventory", summary="车间实时库存")
async def get_inventory(存放位置: Optional[str] = None):
    try:
        filepath, update_time = find_latest_file()
        if not filepath:
            return {"status": "success", "data": [], "total_count": 0, "total_inventory": 0, "update_time": "无数据"}
        all_data = read_excel(filepath)
        filtered = [r for r in all_data if r.get("库存") and float(r["库存"] or 0) > 0]
        if 存放位置:
            filtered = [r for r in filtered if str(r.get("存放位置") or "") == 存放位置]
        total_inventory = sum(float(r.get("库存") or 0) for r in filtered)
        result = []
        for r in filtered:
            result.append({
                "item_no": r.get("item_no") or "",
                "产品名称": r.get("产品名称") or "",
                "产品规格": r.get("产品规格") or "",
                "库存": float(r.get("库存") or 0),
                "存放位置": r.get("存放位置") or "",
                "备注": r.get("备注") or "",
            })
        unique_存放位置 = sorted(set(str(r.get("存放位置") or "") for r in all_data if r.get("存放位置")))
        return {"status": "success", "data": result, "total_count": len(result), "total_inventory": total_inventory, "update_time": update_time, "存放位置列表": unique_存放位置}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"服务器错误: {exc}")
