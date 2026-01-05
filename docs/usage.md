# Mock Service 使用文档

## 快速开始

### 启动服务

```bash
docker compose up -d
```

### 停止服务

```bash
docker compose down
```

### 重启服务

```bash
docker compose restart
```

## 服务地址

| 功能 | 地址 |
|------|------|
| 管理页面 | http://127.0.0.1:9000/admin |
| API 文档 | http://127.0.0.1:9000/docs |
| 健康检查 | http://127.0.0.1:9000/health |

## 添加 Mock 规则

### 方式一：管理页面（推荐）

1. 访问 http://127.0.0.1:9000/admin
2. 点击「+ 新增 Mock 规则」
3. 填写规则信息：
   - **请求方法**: GET / POST / PUT / DELETE
   - **请求路径**: 如 `/mock/api/user/info`
   - **描述**: 接口描述
   - **响应内容**: JSON 格式，如 `{"success": true}`
   - **状态码**: HTTP 状态码，默认 200
   - **响应延迟**: 模拟慢响应，单位秒
4. 点击「保存」
5. 点击「重启服务」使规则生效

### 方式二：API 调用

```bash
# 新增规则
curl -X POST http://127.0.0.1:9000/admin/rules \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/mock/api/order/create",
    "method": "POST",
    "description": "创建订单",
    "response_body": {"order_id": "ORD123", "status": "created"},
    "status_code": 200
  }'

# 重启服务
curl -X POST http://127.0.0.1:9000/admin/restart
```

## 调用 Mock 接口

规则生效后，可直接调用：

```bash
# 示例：调用上面创建的订单接口
curl -X POST http://127.0.0.1:9000/mock/api/order/create
# 返回: {"order_id": "ORD123", "status": "created"}
```

也可在 http://127.0.0.1:9000/docs 页面直接测试。

## 管理规则

### 查看所有规则

```bash
curl http://127.0.0.1:9000/admin/rules
```

### 编辑规则

在管理页面点击规则行的「编辑」按钮，修改后保存并重启服务。

### 删除规则

在管理页面点击规则行的「删除」按钮，确认后重启服务。

## 在测试中使用

### 配置被测系统

将被测系统的第三方服务地址指向 Mock 服务：

```python
# config.py
# 生产环境
# PAYMENT_API = "https://real-payment.com/api"

# 测试环境
PAYMENT_API = "http://127.0.0.1:9000/mock"
```

### 自动化测试示例

```python
import requests

def test_order_create():
    resp = requests.post("http://127.0.0.1:9000/mock/api/order/create")
    assert resp.status_code == 200
    assert resp.json()["order_id"] == "ORD123"
```

## 常见场景

### 模拟成功响应

```json
{
  "path": "/mock/api/pay",
  "method": "POST",
  "response_body": {"success": true, "transaction_id": "TXN001"},
  "status_code": 200
}
```

### 模拟失败响应

```json
{
  "path": "/mock/api/pay",
  "method": "POST",
  "response_body": {"success": false, "error": "余额不足"},
  "status_code": 400
}
```

### 模拟超时

```json
{
  "path": "/mock/api/slow",
  "method": "GET",
  "response_body": {"data": "ok"},
  "delay": 5
}
```

## 数据持久化

规则存储在 `data/mock_rules.json`，重启服务不会丢失。

如需备份，复制该文件即可。
