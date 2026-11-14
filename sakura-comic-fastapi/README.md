# Sakura Comic FastAPI

这是一个使用FastAPI重构的樱花动漫后端API服务，基于原Flask项目重构而来。

## 功能特点

- 用户认证（登录、注册）
- 视频信息查询（列表、详情）
- 评论系统（发布、回复评论）
- 视频收藏功能
- 定时数据更新任务

## 技术栈

- **后端框架**: FastAPI 0.104.0
- **数据库ORM**: SQLAlchemy 2.0.23
- **认证**: JWT (JSON Web Token)
- **数据验证**: Pydantic 2.5.0
- **定时任务**: APScheduler 3.10.4
- **数据库**: SQLite (可配置为其他数据库)

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env` 文件并根据需要修改配置：

```bash
cp .env.example .env
# 编辑 .env 文件，设置数据库连接等配置
```

### 3. 初始化数据库

```bash
python init_db.py
```

### 4. 运行应用

```bash
python run.py
```

应用将在 `http://127.0.0.1:8000` 上运行。

### 5. 访问API文档

打开浏览器访问：`http://127.0.0.1:8000/docs`，查看交互式API文档。

## API接口

### 认证接口
- `POST /auth/login` - 用户登录
- `POST /auth/register` - 用户注册
- `GET /auth/user` - 获取当前用户信息
- `GET /auth/api/check` - 验证token是否有效

### 视频信息接口
- `GET /vod_list` - 获取视频列表
- `GET /vod_detail` - 获取视频详情

### 评论接口
- `GET /show/comment/{vod_id}` - 展示视频评论
- `POST /publish/comment/{vod_id}` - 发表评论
- `POST /reply/comment/{comment_id}` - 回复评论

### 收藏接口
- `GET /collection/show` - 展示用户收藏
- `GET /collection/is_collection` - 检查视频是否已收藏
- `GET /collection/add` - 添加视频到收藏

## 项目结构

```
sakura-comic-fastapi/
├── app/                    # 应用主目录
│   ├── config.py           # 配置管理
│   ├── models/             # 数据库模型
│   ├── routes/             # API路由
│   ├── task/               # 定时任务
│   └── utils/              # 工具函数
├── config/                 # 配置文件目录
│   └── logging.yaml        # 日志配置
├── main.py                 # 应用入口
├── init_db.py              # 数据库初始化脚本
├── run.py                  # 运行脚本
├── requirements.txt        # 依赖列表
└── .env                    # 环境变量配置
```

## 注意事项

1. 本项目默认使用SQLite数据库，生产环境建议使用MySQL或PostgreSQL
2. 生产环境部署时，请修改`.env`中的`SECRET_KEY`为安全的随机字符串
3. 定时任务需要确保只启动一次，避免重复执行
4. 请根据实际需要修改日志配置和存储路径

## License

MIT