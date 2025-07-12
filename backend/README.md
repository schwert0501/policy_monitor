# 财税政策管理系统 - 后端

这是财税政策管理系统的后端部分，使用 Python Flask 框架开发。

## 技术栈

- Python 3.11
- Flask 框架
- MySQL 数据库
- MinIO 对象存储（可选，也支持本地存储）

## 项目结构

```
backend/
├── app/                    # 应用主目录
│   ├── config/             # 配置文件
│   ├── models/             # 数据模型
│   ├── routes/             # API 路由
│   ├── utils/              # 工具类
│   └── __init__.py         # 应用初始化
├── uploads/                # 本地文件上传目录
├── venv/                   # Python 虚拟环境
├── init_db.py              # 数据库初始化脚本
├── requirements.txt        # 依赖包列表
├── run.py                  # 应用入口
└── README.md               # 项目说明
```

## 环境设置

1. 确保已安装 Python 3.11
2. 创建并激活虚拟环境：

```bash
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或者
venv\Scripts\activate  # Windows
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

4. 配置数据库：
   - 创建 MySQL 数据库
   - 修改 `app/config/config.py` 中的数据库连接信息

## 运行应用

1. 初始化数据库（可选，用于生成测试数据）：

```bash
python init_db.py
```

2. 启动应用：

```bash
python run.py
```

应用将在 http://localhost:5000 运行。

## API 接口

### 分类接口

- `GET /api/categories` - 获取所有分类
- `GET /api/categories/<id>` - 获取指定分类
- `POST /api/categories` - 创建分类
- `PUT /api/categories/<id>` - 更新分类
- `DELETE /api/categories/<id>` - 删除分类
- `GET /api/categories/stats` - 获取分类统计数据

### 政策接口

- `GET /api/policies` - 获取政策列表（支持筛选）
- `GET /api/policies/<id>` - 获取指定政策
- `POST /api/policies` - 创建政策
- `PUT /api/policies/<id>` - 更新政策
- `DELETE /api/policies/<id>` - 删除政策
- `GET /api/policies/trends` - 获取政策趋势数据

## 存储配置

系统支持两种存储方式：

1. 本地存储：文件存储在本地 `uploads` 目录
2. MinIO 对象存储：文件存储在 MinIO 服务中

通过修改 `app/config/config.py` 中的 `STORAGE_TYPE` 参数可以切换存储方式。 