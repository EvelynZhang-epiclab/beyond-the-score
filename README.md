# Beyond the Score · Simple AI

Astra 能否成为机器人的“评审员”？涵盖机器人执行质量、任务进度、失败识别与解释的完整研究博客。

- index.html / en.html：完整中文和英文研究博客，2026-10-15 更新；切换语言时保留当前章节。
- blog.css / blog.js：响应式样式、目录、图表放大和混淆矩阵切换。
- evidence.html：保留的旧版交互结果页；当前文章已移除入口，相关案例直接嵌入正文。
- data/：结构化评测结果、指标定义及保存的案例。
- assets/figures/：五张原始完整 baseline 对比图，已在对应正文默认展开；数值明细保留在折叠表中。
- data/publication.json：作者顺序、机构、更新日期和发布状态。
- scripts/build_blog.py：从同一份结果数据生成双语文章，运行 `python3 scripts/build_blog.py` 更新两页。

网站部署使用已生成的静态 HTML/CSS/JavaScript，无需服务器端构建，可通过 GitHub Pages 发布。

作者：Jinhao Zhang、Yuwei Zhang、Weitao Zhou、xxx、xxx（后两项为占位）。Code 和 arXiv 暂标为 coming soon。正文不提供技术报告下载链接。

本地预览：python3 -m http.server 8000，然后访问 http://localhost:8000/ 。

内容依据已核验的 2026-09-23 评测记录、2026-10-14 博客稿和既有案例扩写。此版本未增加新的聚合实验结果。报告 PDF 保留在仓库历史材料中，网页不再提供下载入口。

本版补充 action policy 与 critic 的研究动机、benchmark 选择、各评估维度的重要性、指标公式、文献比较范围和非学习解析参照；案例移入对应结果章节。强化学习部分为后续计划，尚无闭环训练或策略收益结果。
