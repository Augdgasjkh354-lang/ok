# 模型与 effort 选择（来源：claude.dev/blog/which-claude-model-should-you-build-with）

## 默认
- 不确定时：Opus 5.5 + medium（Claude Code 默认）
- 先调 effort，再换模型；effort 只加思考，不加知识

## 按任务选
- 大多数工程/调试/多 PR 功能：Opus 5.5，medium → high
- 范围明确的修 bug、按 spec 做功能：Sonnet 5.5，medium → high
- 聊天/交互：Sonnet 5.5（简单高频用 Haiku 5.5），low/medium
- 分类/路由/打标签/抽取：Haiku 5.5，medium
- 子代理（找文件、读日志、总结）：Haiku 5.5 或 Sonnet 5.5
- 文档/表格/幻灯片：Sonnet 5.5，high（复杂财务模型用 Opus）
- 大型重构/迁移/架构/指挥多个子代理、深度研究：Fable 5.2，medium → high

## 卡住时升级顺序
1. 先给它自检手段（测试/构建/脚本）
2. effort 升一级
3. 换上一级模型，从较低 effort 开始
- 超过 high 后再加一级，成本可能接近换大模型：先试 Fable high，再考虑 Opus xhigh/max

## 混用规则
- 改代码和关键判断留在主模型；子代理只做出错容易发现的活
- 在自然断点换模型，换前 /compact（缓存属于原模型）
- 往下换模型会丢掉之前的推理
- 繁重阅读交给便宜子代理，主上下文只留决策
- 只有任务超出一个上下文窗口才值得拆给多个 worker；单链依赖任务别拆

## 常用命令
/model 换模型　/effort status 看 effort　/usage 看花费　/compact 换模型前压缩
