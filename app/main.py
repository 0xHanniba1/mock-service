"""
Mock Service - 独立的模拟服务端
用于模拟第三方系统（支付网关、短信服务、外部数据源等）
"""
import time
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.routers import admin
from app.store import rule_store


app = FastAPI(
    title="Mock Service",
    description="独立的 Mock 服务，用于模拟第三方系统接口",
    version="1.0.0"
)

# 注册管理路由（不在 docs 中展示）
app.include_router(admin.router, prefix="/admin", include_in_schema=False)


@app.get("/health", include_in_schema=False)
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "mock-service"}


def register_mock_routes():
    """根据规则注册 Mock 路由"""
    for rule in rule_store.get_all():
        # 创建路由处理函数
        def make_handler(r):
            async def handler():
                if r.delay > 0:
                    time.sleep(min(r.delay, 30))
                return JSONResponse(status_code=r.status_code, content=r.response_body)
            return handler

        # 注册路由
        app.add_api_route(
            path=rule.path,
            endpoint=make_handler(rule),
            methods=[rule.method],
            tags=["Mock 接口"],
            summary=rule.description or rule.path,
            response_class=JSONResponse
        )


# 启动时注册规则路由
register_mock_routes()
