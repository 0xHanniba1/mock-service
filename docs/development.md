# Mock Service 开发文档

## 项目结构

```
mock-service/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI 应用入口
│   ├── store.py          # 规则存储模块
│   └── routers/
│       ├── __init__.py
│       └── admin.py      # 管理 API 和页面
├── data/
│   └── mock_rules.json   # 规则持久化存储
├── docs/
│   ├── development.md    # 开发文档
│   └── usage.md          # 使用文档
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## 技术栈

- **语言**: Python 3.13
- **框架**: FastAPI
- **部署**: Docker

## 核心模块说明

### 1. main.py

应用入口，负责：
- 初始化 FastAPI 应用
- 注册管理路由
- 启动时从 `store.py` 加载规则并动态注册路由

```python
def register_mock_routes():
    """启动时根据规则注册路由"""
    for rule in rule_store.get_all():
        app.add_api_route(
            path=rule.path,
            endpoint=make_handler(rule),
            methods=[rule.method],
            ...
        )
```

### 2. store.py

规则存储模块，提供：
- `MockRule`: 规则数据模型
- `RuleStore`: 规则的增删改查和持久化

规则结构：
```python
class MockRule:
    id: str              # 规则 ID
    path: str            # 请求路径
    method: str          # 请求方法 (GET/POST/PUT/DELETE)
    description: str     # 描述
    response_body: dict  # 响应内容
    status_code: int     # HTTP 状态码
    delay: float         # 响应延迟（秒）
```

### 3. admin.py

管理模块，提供：
- `/admin` - 管理页面 (HTML)
- `/admin/rules` - 规则 CRUD API
- `/admin/restart` - 重启服务

## 规则生效机制

1. 用户在管理页面添加/编辑/删除规则
2. 规则保存到 `data/mock_rules.json`
3. 用户点击"重启服务"
4. 服务重启时从 JSON 文件加载规则并注册路由
5. 新规则在 `/docs` 中可见并可调用

## 本地开发

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --port 9000
```

## 扩展开发

### 添加新的管理功能

在 `app/routers/admin.py` 中添加新的路由：

```python
@router.get("/your-feature")
async def your_feature():
    return {"message": "new feature"}
```

### 修改规则存储方式

如需改用数据库存储，修改 `app/store.py` 中的 `RuleStore` 类，替换 `_load()` 和 `_save()` 方法。
