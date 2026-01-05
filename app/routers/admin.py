"""
管理 API 路由
提供 Mock 规则的增删改查接口
"""
import os
import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
from app.store import rule_store, MockRule

router = APIRouter()


@router.post("/restart")
async def restart_service():
    """重启服务"""
    os._exit(0)


class RuleCreate(BaseModel):
    """创建规则请求"""
    path: str
    method: str = "GET"
    description: str = ""
    response_body: dict = {}
    status_code: int = 200
    delay: float = 0


class RuleUpdate(BaseModel):
    """更新规则请求"""
    path: Optional[str] = None
    method: Optional[str] = None
    description: Optional[str] = None
    response_body: Optional[dict] = None
    status_code: Optional[int] = None
    delay: Optional[float] = None


@router.get("/rules")
async def list_rules():
    """获取所有规则"""
    return {"rules": [r.model_dump() for r in rule_store.get_all()]}


@router.post("/rules")
async def create_rule(data: RuleCreate):
    """创建新规则"""
    rule = MockRule(
        id=str(uuid.uuid4())[:8],
        path=data.path,
        method=data.method.upper(),
        description=data.description,
        response_body=data.response_body,
        status_code=data.status_code,
        delay=data.delay
    )
    rule_store.add(rule)
    return {"message": "规则创建成功", "rule": rule.model_dump()}


@router.get("/rules/{rule_id}")
async def get_rule(rule_id: str):
    """获取单个规则"""
    rule = rule_store.get(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    return rule.model_dump()


@router.put("/rules/{rule_id}")
async def update_rule(rule_id: str, data: RuleUpdate):
    """更新规则"""
    existing = rule_store.get(rule_id)
    if not existing:
        raise HTTPException(status_code=404, detail="规则不存在")

    updated = MockRule(
        id=rule_id,
        path=data.path if data.path is not None else existing.path,
        method=(data.method.upper() if data.method else existing.method),
        description=data.description if data.description is not None else existing.description,
        response_body=data.response_body if data.response_body is not None else existing.response_body,
        status_code=data.status_code if data.status_code is not None else existing.status_code,
        delay=data.delay if data.delay is not None else existing.delay
    )
    rule_store.update(rule_id, updated)
    return {"message": "规则更新成功", "rule": updated.model_dump()}


@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str):
    """删除规则"""
    if rule_store.delete(rule_id):
        return {"message": "规则删除成功"}
    raise HTTPException(status_code=404, detail="规则不存在")


@router.get("", response_class=HTMLResponse)
async def admin_page():
    """管理页面"""
    html = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mock 服务管理</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #333; margin-bottom: 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: 500; color: #555; }
        input, select, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        textarea { height: 100px; font-family: monospace; }
        .btn { padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; margin-right: 10px; }
        .btn-primary { background: #007bff; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        .btn-warning { background: #fd7e14; color: white; }
        .btn:hover { opacity: 0.9; }
        .alert { padding: 12px 16px; border-radius: 4px; margin-bottom: 15px; display: none; }
        .alert-warning { background: #fff3cd; color: #856404; border: 1px solid #ffc107; }
        .alert.show { display: block; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: 600; }
        .method { display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 12px; font-weight: bold; }
        .method-get { background: #28a745; color: white; }
        .method-post { background: #007bff; color: white; }
        .method-put { background: #ffc107; color: black; }
        .method-delete { background: #dc3545; color: white; }
        .path { font-family: monospace; color: #666; }
        .actions button { margin-right: 5px; padding: 5px 10px; font-size: 12px; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); }
        .modal.active { display: flex; align-items: center; justify-content: center; }
        .modal-content { background: white; padding: 30px; border-radius: 8px; width: 500px; max-width: 90%; }
        .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .close { font-size: 24px; cursor: pointer; color: #999; }
        .row { display: flex; gap: 15px; }
        .row .form-group { flex: 1; }
        .empty { text-align: center; padding: 40px; color: #999; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Mock 服务管理</h1>

        <div id="restart-alert" class="alert alert-warning">
            规则已修改，需要重启服务才能生效！
            <button class="btn btn-warning" onclick="restartService()" style="margin-left: 15px;">重启服务</button>
        </div>

        <div class="card">
            <button class="btn btn-primary" onclick="openModal()">+ 新增 Mock 规则</button>
            <button class="btn btn-warning" onclick="restartService()">重启服务</button>
        </div>

        <div class="card">
            <h3 style="margin-bottom: 15px;">已配置的规则</h3>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>方法</th>
                        <th>路径</th>
                        <th>描述</th>
                        <th>状态码</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody id="rules-table">
                    <tr><td colspan="6" class="empty">加载中...</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <div id="modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 id="modal-title">新增 Mock 规则</h3>
                <span class="close" onclick="closeModal()">&times;</span>
            </div>
            <form id="rule-form">
                <input type="hidden" id="rule-id">
                <div class="row">
                    <div class="form-group">
                        <label>请求方法</label>
                        <select id="method">
                            <option value="GET">GET</option>
                            <option value="POST">POST</option>
                            <option value="PUT">PUT</option>
                            <option value="DELETE">DELETE</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>状态码</label>
                        <input type="number" id="status_code" value="200">
                    </div>
                </div>
                <div class="form-group">
                    <label>请求路径 (如: /api/sms/send)</label>
                    <input type="text" id="path" placeholder="/api/xxx" required>
                </div>
                <div class="form-group">
                    <label>描述</label>
                    <input type="text" id="description" placeholder="接口描述">
                </div>
                <div class="form-group">
                    <label>响应内容 (JSON)</label>
                    <textarea id="response_body" placeholder='{"success": true, "message": "ok"}'></textarea>
                </div>
                <div class="form-group">
                    <label>响应延迟 (秒)</label>
                    <input type="number" id="delay" value="0" step="0.1" min="0">
                </div>
                <button type="submit" class="btn btn-primary">保存</button>
                <button type="button" class="btn btn-secondary" onclick="closeModal()">取消</button>
            </form>
        </div>
    </div>

    <script>
        const API_BASE = '/admin';

        function showRestartAlert() {
            document.getElementById('restart-alert').classList.add('show');
        }

        async function restartService() {
            if (!confirm('确定要重启服务吗？')) return;
            try {
                await fetch(`${API_BASE}/restart`, { method: 'POST' });
            } catch (e) {
                // 服务重启会断开连接，忽略错误
            }
            alert('服务正在重启，请稍后刷新页面...');
            setTimeout(() => location.reload(), 3000);
        }

        async function loadRules() {
            const resp = await fetch(`${API_BASE}/rules`);
            const data = await resp.json();
            const tbody = document.getElementById('rules-table');

            if (data.rules.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="empty">暂无规则，点击上方按钮添加</td></tr>';
                return;
            }

            tbody.innerHTML = data.rules.map(rule => `
                <tr>
                    <td>${rule.id}</td>
                    <td><span class="method method-${rule.method.toLowerCase()}">${rule.method}</span></td>
                    <td class="path">${rule.path}</td>
                    <td>${rule.description || '-'}</td>
                    <td>${rule.status_code}</td>
                    <td class="actions">
                        <button class="btn btn-secondary" onclick="editRule('${rule.id}')">编辑</button>
                        <button class="btn btn-danger" onclick="deleteRule('${rule.id}')">删除</button>
                    </td>
                </tr>
            `).join('');
        }

        function openModal(rule = null) {
            document.getElementById('modal').classList.add('active');
            document.getElementById('modal-title').textContent = rule ? '编辑规则' : '新增 Mock 规则';

            if (rule) {
                document.getElementById('rule-id').value = rule.id;
                document.getElementById('method').value = rule.method;
                document.getElementById('path').value = rule.path;
                document.getElementById('description').value = rule.description || '';
                document.getElementById('response_body').value = JSON.stringify(rule.response_body, null, 2);
                document.getElementById('status_code').value = rule.status_code;
                document.getElementById('delay').value = rule.delay;
            } else {
                document.getElementById('rule-form').reset();
                document.getElementById('rule-id').value = '';
                document.getElementById('status_code').value = '200';
                document.getElementById('delay').value = '0';
            }
        }

        function closeModal() {
            document.getElementById('modal').classList.remove('active');
        }

        async function editRule(id) {
            const resp = await fetch(`${API_BASE}/rules/${id}`);
            const rule = await resp.json();
            openModal(rule);
        }

        async function deleteRule(id) {
            if (!confirm('确定要删除这条规则吗？')) return;
            await fetch(`${API_BASE}/rules/${id}`, { method: 'DELETE' });
            loadRules();
            showRestartAlert();
        }

        document.getElementById('rule-form').addEventListener('submit', async (e) => {
            e.preventDefault();

            let responseBody = {};
            try {
                const bodyText = document.getElementById('response_body').value.trim();
                if (bodyText) responseBody = JSON.parse(bodyText);
            } catch (err) {
                alert('响应内容必须是有效的 JSON 格式');
                return;
            }

            const data = {
                method: document.getElementById('method').value,
                path: document.getElementById('path').value,
                description: document.getElementById('description').value,
                response_body: responseBody,
                status_code: parseInt(document.getElementById('status_code').value),
                delay: parseFloat(document.getElementById('delay').value) || 0
            };

            const ruleId = document.getElementById('rule-id').value;
            const url = ruleId ? `${API_BASE}/rules/${ruleId}` : `${API_BASE}/rules`;
            const method = ruleId ? 'PUT' : 'POST';

            await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            closeModal();
            loadRules();
            showRestartAlert();
        });

        loadRules();
    </script>
</body>
</html>
    """
    return html
