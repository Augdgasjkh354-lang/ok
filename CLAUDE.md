# CLAUDE.md

本项目的开发约定、兼容性红线、实机经验和与玩家的协作方式都写在 AGENTS.md，**动手之前先读它**：

@AGENTS.md

补充（针对 Claude Code）：
- 构建、检查的命令都在仓库根目录运行：`python build_v09.py && python generate_localization.py && python tests/verify_v09.py && python tests/test_merge_localization.py`。
- 这里没有 Windows 和战团客户端，所有改动都只能做静态验证。说明里一律标「待实机验收」，直到玩家确认为止。
- 给玩家的文件（试玩包、合并好的汉化）放在 scratchpad，用 SendUserFile 发送；不要把玩家上传的原版语言文件提交进仓库。
- 玩家习惯用中文交流：回复简短直接，一次一步，并说明怎么核对结果。
