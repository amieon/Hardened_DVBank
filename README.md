# Hardened DVBank — 认证、授权与交易安全加固实验

> 基于开源教学靶场 **DVBank Lab** 进行漏洞复现与安全加固。
> Fork 自 [mamgad/DVBLab](https://github.com/mamgad/DVBLab)。原项目说明见 [`README_DVBank_original.md`](./README_DVBank_original.md)。

## 项目简介

DVBank 是一个**故意留有安全漏洞**的迷你银行 Web 应用(React 前端 + Flask 后端 + SQLite),用于学习 Web 安全。本仓库在原项目基础上,完成了「复现漏洞 → 加固 → 回归验证」的完整安全工程流程。

⚠️ **仅供本地学习使用,严禁对任何未授权系统进行测试。**

## 技术栈

- 前端:React
- 后端:Python / Flask + SQLAlchemy
- 数据库:SQLite
- 部署:Docker / docker-compose

## 快速开始

```bash
# 克隆
git clone https://github.com/amieon/Hardened_DVBank.git
cd Hardened_DVBank

# 启动（首次构建较慢）
./run.sh

# 访问
# 前端: http://localhost:3000
# 后端 API: http://localhost:5000
```

测试账号:`alice` / `password123`(其余 bob、charlie… 同口令)。

> 注:加固后口令存储已改为带盐哈希,如遇旧数据无法登录,删除 `backend/vulnerable_bank.db*` 后重启,由程序自动重建种子数据。

## 完成的安全加固

| 编号 | 漏洞 | 加固措施 |
|------|------|----------|
| F-1 | 登录接口 SQL 注入(字符串拼接) | 改用参数化查询 |
| F-2 | 口令明文/弱哈希(无盐 MD5) | 改用 Werkzeug PBKDF2 带盐哈希 |
| F-3 | 交易列表对象级越权(IDOR) | 强制以当前登录用户查询,并参数化 |
| F-4 | 转账金额未校验(负数/超精度) | 校验正数、精度、余额,并事务化 |
| F-5 | JWT 密钥硬编码 | 改为从环境变量读取强随机密钥 |
| F-6 | 管理员接口越权 + 信息泄露 | 增加角色校验,移除响应中的口令哈希 |

详细的漏洞复现、修复前后对比与回归验证见实验报告。

## 致谢与许可

- 原始靶场:[mamgad/DVBLab](https://github.com/mamgad/DVBLab)
- 本仓库为课程学习用途,遵循原项目许可。

## 免责声明

本项目仅用于安全教育与本地实验。请勿将任何技术用于未经授权的系统;发现真实系统漏洞应走负责任披露流程。