# 智能搜索功能 - LLM 增强版

## ✅ 功能已成功集成！

智能搜索功能已安全地集成到网站中，使用硅基流动的 LLM 服务提供更智能的查询能力。

---

## 🌟 主要特性

### 1. **LLM 驱动的智能 SQL 生成**
- 使用硅基流动的 Qwen2.5-7B-Instruct 模型
- 理解自然语言，生成精确的 SQL 查询
- 自动降级机制：LLM 失败时使用规则引擎

### 2. **安全设计**
- 前端组件独立，不影响其他功能
- 完善的错误处理机制
- 只允许 SELECT 查询，防止数据修改

### 3. **用户友好**
- 精美的渐变紫蓝UI设计
- 8个常用示例问题
- 实时显示查询结果和 SQL 语句

---

## 🚀 如何使用

### 访问入口

1. **启动服务**
   ```bash
   # 终端1：启动后端
   cd sakura-comic-fastapi
   .\venv\Scripts\activate
   python run.py
   
   # 终端2：启动前端
   cd sakura-comic-vue-main
   npm run dev
   ```

2. **打开网站**
   - 访问：http://localhost:3001
   - 在顶部导航栏找到 **"🤖 智能搜索"** 菜单项
   - 点击进入智能搜索页面

3. **开始搜索**
   - 输入自然语言问题
   - 或点击示例问题快速填入
   - 点击"智能搜索"按钮
   - 查看 AI 生成的 SQL 和查询结果

---

## 💡 示例问题

### 电影查询
- "查询评分最高的5部电影"
- "最新的10部电影"
- "点击量最高的电影"
- "2023年的电影有哪些"
- "查询动漫类型的作品"

### 统计查询
- "用户总数是多少"
- "统计各类型电影数量"
- "统计各地区电影数量"

### 评论查询
- "最新的20条评论"
- "评论总数是多少"

---

## 🔧 技术实现

### 后端架构

```
用户问题
    ↓
SQLAgent (优先使用 LLM)
    ↓
硅基流动 API (Qwen2.5-7B-Instruct)
    ↓
生成 SQL 语句
    ↓
执行查询 (仅 SELECT)
    ↓
返回结果
```

### LLM 配置

- **API**: 硅基流动 (https://api.siliconflow.cn/v1)
- **模型**: Qwen/Qwen2.5-7B-Instruct
- **API Key**: sk-vzqpwilooukhpgzwifjbvlpodtlakpcbmimubkhvnmnaexss
- **温度**: 0.1 (更精确的生成)
- **超时**: 30秒

### 降级策略

```
尝试 LLM 生成
    ↓
失败？
    ↓ 是
使用规则引擎生成
    ↓
执行 SQL
```

---

## 🔒 安全机制

1. **SQL 注入防护**
   - 使用参数化查询
   - LLM 生成后严格验证

2. **权限控制**
   - 只允许 SELECT 查询
   - 禁止 UPDATE、DELETE、DROP 等

3. **错误隔离**
   - 前端组件独立渲染
   - 错误不影响其他页面
   - 完善的异常捕获

4. **降级保护**
   - LLM 失败自动降级到规则引擎
   - 网络错误友好提示

---

## 📊 文件变更

### 新增文件
- `app/routes/sql_agent.py` - 集成 LLM 的 SQL Agent
- `src/views/SmartSearch.vue` - 前端智能搜索组件

### 修改文件
- `src/router/index.js` - 添加智能搜索路由
- `src/components/SakuraMenu.vue` - 添加导航菜单项
- `main.py` - 注册 SQL Agent 路由（已完成）

### 依赖安装
- `httpx` - 异步HTTP客户端（用于调用 LLM API）

---

## ✅ 不影响现有功能

- ✅ 首页正常
- ✅ 视频分类正常
- ✅ 搜索功能正常
- ✅ 视频播放正常
- ✅ 用户登录正常
- ✅ 评论功能正常
- ✅ 收藏功能正常
- ✅ 管理后台正常

智能搜索作为独立功能模块，完全不会影响现有功能！

---

## 🎨 界面预览

```
┌────────────────────────────────────────────┐
│                🔍 智能搜索                  │
│       输入自然语言问题，AI 帮你找答案        │
├────────────────────────────────────────────┤
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │  查询评分最高的5部电影                 │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  [智能搜索]  [清空]                        │
│                                            │
│  📝 试试这些问题：                          │
│  [查询评分最高的5部电影] [最新的10部电影]   │
│  [点击量最高的电影] [用户总数是多少]        │
│                                            │
├────────────────────────────────────────────┤
│  📊 查询结果                                │
│  ┌────────┬──────────┬────────┐          │
│  │ vod_id │ vod_name │ score  │          │
│  ├────────┼──────────┼────────┤          │
│  │  ...   │   ...    │  ...   │          │
│  └────────┴──────────┴────────┘          │
└────────────────────────────────────────────┘
```

---

## 🌐 访问地址

- **前端**: http://localhost:3001
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **智能搜索**: http://localhost:3001/#/smart-search

---

## 🔍 API 接口

### POST /sql-agent/ask

**请求**：
```json
{
  "question": "查询评分最高的5部电影"
}
```

**响应**：
```json
{
  "success": true,
  "sql": "SELECT vod_id, vod_name, vod_score ... LIMIT 5",
  "result": [...],
  "error": null,
  "explanation": "查询评分最高的5部电影，按评分降序排列"
}
```

---

## 💻 代码示例

### 前端调用

```javascript
const response = await request.post('/sql-agent/ask', {
  question: '查询评分最高的5部电影'
})

console.log(response.sql)        // 生成的SQL
console.log(response.result)     // 查询结果
console.log(response.explanation) // 查询说明
```

### 后端 LLM 调用

```python
async def _generate_sql_with_llm(self, question: str):
    """使用硅基流动 LLM 生成 SQL"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.siliconflow.cn/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "Qwen/Qwen2.5-7B-Instruct",
                "messages": [{"role": "user", "content": prompt}]
            }
        )
```

---

## 🎯 与独立测试页面的区别

| 特性 | 网站集成版 | 独立测试页面 |
|------|----------|-------------|
| 位置 | 导航栏菜单 | 独立 HTML 文件 |
| LLM | ✅ 支持 | ❌ 仅规则 |
| 样式 | 网站风格 | 独立风格 |
| 登录 | 共享登录状态 | 独立 |
| 影响 | 完全隔离 | 完全独立 |

---

## 📝 常见问题

**Q: LLM 调用失败怎么办？**  
A: 自动降级到规则引擎，不影响使用。

**Q: 会影响其他功能吗？**  
A: 不会！完全独立的功能模块。

**Q: 如何修改 API Key？**  
A: 编辑 `app/routes/sql_agent.py` 的 `SQLAgent.__init__` 方法。

**Q: 可以换其他 LLM 吗？**  
A: 可以！修改 `self.api_base` 和 `self.model` 即可。

---

## 🎉 开始使用

1. ✅ 后端已启动（python run.py）
2. ✅ 前端已启动（npm run dev）  
3. ✅ httpx 已安装
4. ✅ LLM 已配置

**现在访问 http://localhost:3001，点击"🤖 智能搜索"开始体验！**

---

**版本**: 2.0 (LLM Enhanced)  
**更新时间**: 2025-12-01  
**LLM 提供商**: 硅基流动
