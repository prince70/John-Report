import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from Abus_BigData_Cal.AssemblyEarlyList import router as AssemblyEarlyList
from routers.login import router as login_router
from routers.personal import router as personal_router
from routers.cost_calculation import router as cost_calculation_router
from routers.apsRequirements import router as apsRequirements_router
from routers.team import router as team_router
from routers.gongxu_sw import router as report_router
from routers.gongxu import router as report_sw_router
from routers.quanliucheng import router as report_temp_router
from routers.cisa_inventory import router as cisa_inventory_router
from routers.product_rules import router as product_rules_router
from HR.people import router as people_router
from Abus_BigData_Cal import home_dashboard
from Abus_BigData_Cal import FinishedQty
from Abus_BigData_Cal.AssemblyFuture8Weeks import router as AssemblyFuture8Weeks
from Warning.AssemblyEarly import router as AssemblyEarly
from All_Process_Cal import allProcessWorkReport
app = FastAPI()

# 初始化缓存 使用内存缓存而不是redis缓存
@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")

# 应用关闭时的清理任务
@app.on_event("shutdown")
async def shutdown():
    pass
# Serve static files (uploaded files etc.)
project_root = os.path.dirname(__file__)
static_dir = os.path.join(project_root, "static")
os.makedirs(static_dir, exist_ok=True)

# 新增：将 /static/uploads 挂载到 D:\\uploads
uploads_abs_dir = r"D:\\uploads"
os.makedirs(uploads_abs_dir, exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory=uploads_abs_dir), name="uploads")

# 原有静态目录挂载
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(login_router)
app.include_router(personal_router)
app.include_router(cost_calculation_router)
app.include_router(apsRequirements_router)
app.include_router(team_router, prefix="/team")
app.include_router(report_router)
app.include_router(report_sw_router, prefix="/report_sw")
app.include_router(report_temp_router, prefix="/report_temp")
app.include_router(cisa_inventory_router, prefix="/cisa_inventory")
app.include_router(product_rules_router)
app.include_router(people_router)
app.include_router(home_dashboard.router)
app.include_router(FinishedQty.router)
app.include_router(AssemblyEarly)
app.include_router(AssemblyEarlyList)
app.include_router(AssemblyFuture8Weeks)
app.include_router(allProcessWorkReport.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8092", "http://127.0.0.1:8092", "http://report.abushardware.com", "http://192.168.10.118:8092"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.get("/")
async def root():
    print('运行')
    return {"status": "API is running!"}


@app.post("/cache/clear")
async def clear_all_cache():
    try:
        await FastAPICache.clear()
        return {"status": "success", "message": "全局缓存已清除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除全局缓存失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app='mains:app', host="0.0.0.0", port=8091)
