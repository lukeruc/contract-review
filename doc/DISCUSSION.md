# 讨论与待解决问题

本文档记录项目当前正在讨论的设计问题、测试发现和待决策事项。已解决的问题移入 DESIGN.md 或 TECHNICAL-DESIGN.md，不再保留于此。


我希望简单和复杂模式在工作的最后都多产生一个报告，审核工作报告，报告的内容为本次工作的流程，合同的主要内容，需要注意的主要的修改点。
请你分析这个适合使用一个task agent来撰写还是主agent直接完成工作。同样的我希望报告同时已.md和.html来交付。

> **分析：Architect 直接完成，不需要 Task Agent。**
> 
> 原因有三：
> 
> 1. **信息来源是会话元信息**。这份报告的核心内容——本次工作创建了几个 Task Agent、每个 Agent 做了什么、经过了几轮 Review、遇到了什么问题——只有 Architect 知道。没有一份输入文件记录了这些会话过程。Architect 是唯一的信息源，创建 Task Agent 反而需要 Architect 先把这些信息写下来交给它。
> 
> 2. **不是法律分析，是工作记录**。这和初步情况报告（T-PR）有本质区别：T-PR 分析的是合同的商务条件、法律机制和条款关系，需要解读三份初设文档，工作量大且独立。审核工作报告只记录"做了什么"——哪些阶段完成了、发现了几条风险、修改了几条条款。这是摘要工作，Architect 经历全流程后自然掌握。
> 
> 3. **篇幅短，上下文成本低**。初步情况报告 2000-4000 字需要专项处理。审核工作报告的核心内容——合同概要（2-3 句）、工作流程（列表）、主要修改点（几条）——加起来通常不超过 1000 字。Architect 直接写完即可，创建 Task Agent 的 overhead 反而更大。
> 
> **建议方案**：Architect 在两个 workflow 的对话续接步骤中，除 agent/CLAUDE.md 和 agent/index.md 外，同时产出 `output/audit-work-report.md` 和 `output/audit-work-report.html`。用 .md 撰写，生成一份简洁的 .html 供用户阅读。


我不希望篇幅这么短，这应该是一个内容适中的报告，需要包含重要的修改的点。
我同意应该由architect直接完成。
请你分析有关该报告的要求是应该放到reference中定义还是在skill.md中直接定义

> **分析：放在 workflow 文件中定义。**
>
> `references/` 不适合——references 下的文件是给 Task Agent 用的参考示例，Architect 读取后注入 sub-agent。这份报告由 Architect 直接撰写，没有 sub-agent 参与，reference 文件用不上。
>
> `SKILL.md` 也不适合——SKILL.md 定义的是总控行为（角色、bootstrap、工具表、决策上报），不宜填充具体产出物的格式要求，否则会膨胀。
>
> workflow 文件是最合适的位置——Architect 在执行到对话续接阶段时读取 workflow 中的步骤说明，其中定义除 agent/CLAUDE.md 和 agent/index.md 外还需产出 `output/audit-work-report.md` + `.html`，并列出报告应包含的内容结构。格式要求随阶段定义，Architect 在做的当下看到，不需要跨文件查找。

认同你的观点，开始工作