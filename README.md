# 卡拉迪亚：烽烟与暗流 (Ashfall)

《骑马与砍杀：战团》（Mount & Blade: Warband）原版增强 Mod，继承 FewerBandits v7.5。

**当前源码版本：v0.9「路上的旧人」**。本仓库已完整导入 v0.9 源码，包括历史版本基线、构建脚本、汉化工具和静态验证脚本（原始源码包共 770 个文件）。

## 项目状态

- Module System 构建与静态兼容审计已完成。
- **Windows 游戏客户端、旧存档兼容及实际中文显示尚未实测**。
- 已有玩法：宫廷政治、村庄战乱、难民与逃兵、军粮运输、匪帮、围城战及战后治理、领主巡防、地方传闻、旧人重逢。
- 原版地图、王国及基本兵种体系保持不变，不依赖 WSE2。

## 源码与构建

在仓库根目录使用 Python 3：

```bash
python build_v09.py
python generate_localization.py
python tests/verify_v09.py
```

构建结果输出至 `game-data/`。本仓库包含需要的 `baseline/`、`build/`、`sources/`、`localization/` 等目录。

详见：

- [AGENTS.md](AGENTS.md) — 项目开发规范与存档兼容约束
- [中文编译与汉化指南.md](中文编译与汉化指南.md) — 中文编译、翻译文件与合并工具说明
- [README_ASHFALL_V09.md](README_ASHFALL_V09.md) — v0.9 功能与构建说明

## 原始源码归档

[下载 v0.9 完整源码归档（tar.zst）](archives/ashfall-v0.9-source.tar.zst)

归档为 ZIP 同源的无损固实压缩版本，SHA-256：

```
e0d0e97d7c619971f6e9156823684b2fcec46c59b226df9fa0398a8c077ba255
```

仓库中的展开源码由 [GitHub Actions 自动导入流程](.github/workflows/import-ashfall.yml) 从该归档验证后生成，保留所有历史基线和目录结构。

## 开发原则

以原版玩家体验、自然中文、角色动机与选择后果为核心；新增功能应复用现有体系，避免重复属性、无意义事件、保存数据编号重排。
