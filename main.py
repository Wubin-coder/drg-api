from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine, Base
import crud

import logging
import time
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="医保DRG模拟审核接口")

# 配置日志
logging.basicConfig(
    filename='api.log',  # 日志输出到文件
    level=logging.INFO,  # 记录 INFO 及以上级别
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

#添加中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # 执行实际的路由函数
    response = await call_next(request)

    # 计算耗时
    process_time = time.time() - start_time

    # 记录日志
    logging.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")

    return response

#添加全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # 记录异常日志
    logging.error(f"Unhandled exception: {exc}", exc_info=True)

    # 返回通用错误信息（避免暴露内部细节）
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error, please try again later."}
    )

# 依赖项：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- 请求和响应的数据模型 ----------
class ReviewRequest(BaseModel):
    case_id: str  # 病案号
    diagnosis_code: str  # 诊断编码（如 "阑尾炎"）
    procedure_code: str  # 手术编码（如 "阑尾切除术"）
    age: int  # 年龄
    complications: str = ""  # 并发症（可选，默认为空）
    total_cost: float  # 总费用


class ReviewResponse(BaseModel):
    case_id: str
    drg_group_code: str  # 匹配到的DRG分组编码
    drg_group_name: str  # 分组名称
    standard_cost: float  # 标准费用（权重 × 基础价格）
    actual_cost: float  # 实际费用
    difference: float  # 差值（实际 - 标准）
    review_result: str  # 审核结果：正常 / 偏高 / 异常


# ---------- 模拟DRG分组规则函数 ----------
def mock_drg_group(diagnosis: str, procedure: str, age: int) -> str:
    """
    根据诊断、手术、年龄模拟DRG分组
    这是一个非常简化的规则，真实情况要复杂得多
    """
    # 简单的关键词匹配（实际项目中会用诊断编码如 ICD-10）
    if "阑尾" in diagnosis or "K35" in diagnosis:
        return "RA23"
    elif "剖宫产" in procedure or "O82" in procedure:
        return "RB14"
    elif "肺炎" in diagnosis or "J15" in diagnosis:
        if age > 65:
            return "FC09"
        else:
            return "FC08"  # 假设存在这个分组
    else:
        return "ZZ99"  # 未知分组


# ---------- 接口1：根路径 ----------
@app.get("/")
def root():
    return {"message": "DRG API 已启动"}


# ---------- 接口2：获取所有DRG分组 ----------
@app.get("/drg_list")
def read_drg_list(db: Session = Depends(get_db)):
    """
    返回所有DRG分组
    """
    drg_items = crud.get_all_drg(db)
    return drg_items


# ---------- 接口3：核心审核接口 ----------
@app.post("/review_case", response_model=ReviewResponse)
def review_case(request: ReviewRequest, db: Session = Depends(get_db)):
    """
    接收病例信息，模拟DRG分组和费用审核
    """
    try:
        # 1. 根据诊断、手术、年龄匹配DRG分组编码
        group_code = mock_drg_group(
            request.diagnosis_code,
            request.procedure_code,
            request.age
        )

        # 2. 从数据库查询该分组的详细信息
        drg_item = crud.get_drg_by_code(db, group_code)

        if drg_item:
            standard_cost = drg_item.weight * drg_item.base_price
            group_name = drg_item.group_name
        else:
            # 未匹配到分组，记录警告但继续执行（用默认值）
            logging.warning(f"Group code {group_code} not found in database")
            standard_cost = 5000.0
            group_name = "未分组"

        # 3. 计算费用差异
        diff = request.total_cost - standard_cost

        # 4. 确定审核结果
        if diff < 0:
            result = "正常"
        elif diff <= standard_cost * 0.2:
            result = "偏高"
        else:
            result = "异常"

        # 5. 返回结果
        return ReviewResponse(
            case_id=request.case_id,
            drg_group_code=group_code,
            drg_group_name=group_name,
            standard_cost=round(standard_cost, 2),
            actual_cost=request.total_cost,
            difference=round(diff, 2),
            review_result=result
        )

    except Exception as e:
        # 捕获并记录业务处理中的异常
        logging.error(f"Error processing review_case: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

# 这段代码让你可以直接用 python main.py 运行
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)