# OES Backend

> 项目参考 [tiangolo/full-stack-fastapi-template](https://github.com/tiangolo/full-stack-fastapi-template) 重构并实现标准工程化，作为后续后端 REST 应用的开发模板。

---

* 项目类型：插件
* 项目描述：偏差单筛选(OES)的后端实现，使用 Bert 模型对上传的 excel 文件进行批量分类处理，使用 FastAPI 框架实现 RESTful API。
* 项目负责人：王克
* 项目开发：王克、李鸿基、吕焮
* Python 版本：3.11

## 项目结构

```plain
├── main.py                     项目入口
├── error.py                    业务错误定义
├── api                         FastAPI 实现的 RESTful API 部分
│   ├── app.py                  FastAPI 应用初始化
│   └── task                    任务管理 API 实现
│       ├── __init__.py
│       ├── router.py           任务管理 API 路由配置
│       └── handlers            RESTful API 业务实现
├── plugins                     通用插件
│   ├── logger                  日志插件
│   ├── auth                    鉴权插件
│   └── s3connector             s3服务器连接器
├── conf                        项目配置
│   ├── __init__.py
│   ├── conf.py                 配置文件相关定义
│   └── config-template.yaml    配置文件模版
├── scripts                     项目脚本
├── services                    各服务模块
│   ├── bertmodel               Bert 模型相关实现
│   ├── filemanager             文件管理相关实现
│   └── taskmanager             任务管理相关实现
├── tests                       测试用例
├── alembic                     数据库迁移相关实现
├── alembic.ini                 数据库迁移配置文件
├── core.models                      模型文件
├── data                        数据文件
├── requirements.txt            依赖文件
├── Dockerfile                  Docker 镜像构建文件
├── pyproject.toml              项目配置
└── README.md                   项目说明文档
```

## 如何开发

## 1. 安装依赖

你可能需要首先依照公司 Python 开发规范创建并配置 `.conda` 虚拟环境。

```shell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

## 2. 配置文件

设置 `conf/config.yaml` 文件，具体配置项请参考 `conf/config-template.yaml` 文件。

## 3. 启动项目

```shell
python main.py
```

## 4. 测试

测试所有功能：

```shell
pytest
```

测试某一个功能：

```shell
pytest tests/...
```

## 如何协作

`main` 分支是稳定分支，`dev` 分支是开发分支，`feature/*` 分支是新功能分支，`bugfix/*` 分支是修复 bug 分支。

`main` 分支不允许直接修改，所有开发都应该基于 `dev` 分支进行，然后合并到 `main` 分支。

当你需要添加新的功能时，请基于 `dev` 分支创建新分支 `feature/*`，然后在新分支上进行开发，开发完成后，请合并到 `dev` 分支。

当你需要修复已知 bug 时，请基于 `dev` 分支创建新分支 `bugfix/*`，然后在新分支上进行修复，修复完成后，请合并到 `dev` 分支。

合并分支时会进行代码审查，确保代码质量。

负责人请在合并分支时，记得更新 `CHANGELOG.md` 文件，并在 `README.md` 文件中更新项目说明。负责人需要监督并确保开发过程中，代码质量和文档更新，并及时对开发人员的不规范行为进行指正，否则造成的影响由负责人承担。
