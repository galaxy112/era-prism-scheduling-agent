# ERA + PRISM Lab Scheduling Agent

这是一个面试小作业 Demo：把 ERA 的“生成 -> 执行 -> 评分 -> 改进”闭环，和 PRISM 的“结构化协议 -> 模拟验证 -> 反馈修复”思想，迁移到一个虚构实验室排程问题。

它不是 ERA 或 PRISM 的完整复现，也不接真实设备。目标是用最小可运行系统说明：我能读懂论文思想，拆出边界，并把它落成一个能验证、能解释、能演示的工程闭环。

## 运行方式

环境要求：Python 3.10+，无第三方运行依赖。

```bash
python -m scheduling_agent.experiment --problem examples/lab_problem.json --protocol-out examples/best_protocol.json
```

运行测试：

```bash
python -m unittest discover -s tests
```

查看报告：

```text
reports/report.html
```

面试准备问题文档：

```text
reports/interview_questions.docx
```

## 问题设置

虚构实验室有三个单容量资源：

- `MIXER`
- `INCUBATOR`
- `READER`

其中 `INCUBATOR` 在 `[8, 10)` 停机。四个批次 A-D 分别有固定步骤和截止时间，定义在 `examples/lab_problem.json`。

评分公式沿用题面建议：

```text
1000 * 硬约束错误数 + 总完工时间 + 3 * 总延期时间
```

这个公式故意让硬约束错误非常贵，使系统优先学会“可行”，然后再追求更低完工时间和延期。

## ERA 如何迁移

ERA 的核心不是“某个具体搜索算法”，而是让 AI 生成或改写候选代码，再用执行结果和评分作为反馈，筛选出更好的候选。

本 Demo 中对应为：

- 候选生成：`scheduling_agent/candidates.py` 中的离线模板候选。
- 执行：每个候选生成一个完整排程。
- 验证：`validator.py` 检查资源冲突、步骤顺序、设备停机。
- 评分：`scorer.py` 计算统一分数。
- 选择：`experiment.py` 保留当前最低分候选。
- 改进：`repair_conflicts` 使用上一轮验证反馈修复停机冲突。

为了保证可复现，本 Demo 不调用真实 LLM API。离线模板候选模拟 ERA 式候选生成过程，重点展示闭环机制。

## PRISM 如何迁移

PRISM 的核心是把实验流程变成结构化协议，并用仿真模型对协议进行验证，再根据反馈修复。

本 Demo 中对应为：

- 结构化协议：`protocol.py` 将排程转为 JSON step list。
- 轻量模拟器：`simulator.py` 重新加载协议并验证硬约束。
- 反馈：模拟器复用验证器输出，说明结构化协议是否仍然可执行。

这相当于把“自然语言/代码里的排程结果”变成一个更接近机器执行层的协议表示。

## 示例输出摘要

完整输出见 `examples/sample_output.txt`。关键过程如下：

```text
[1] naive_batch_order
    Score: 1152
    downtime_conflict: A.1 overlaps INCUBATOR downtime [8,10)

[2] repair_conflicts
    Score: 215
    Validator feedback: no hard-constraint errors

[4] deadline_priority
    Score: 143
    Validator feedback: no hard-constraint errors

PRISM-style structured protocol simulation:
  PASSED
```

这展示了一次从“候选失败”到“收到反馈并改进”的闭环。

## 代码结构

```text
scheduling_agent/
  models.py          # 数据模型
  problem_loader.py  # JSON 问题读取
  baseline.py        # 基线贪心排程
  candidates.py      # 候选算法库
  validator.py       # 硬约束验证
  scorer.py          # 评分器
  protocol.py        # 排程转结构化协议
  simulator.py       # 协议复验
  experiment.py      # CLI 和闭环执行
examples/
  lab_problem.json
  sample_output.txt
  best_protocol.json
reports/
  report.html
  interview_questions.docx
tests/
```

## 已知限制

- 没有完整复现 ERA 的树搜索、代码生成和大规模实验评估。
- 没有完整复现 PRISM 的智能仿真建模，也没有接真实机器人或设备。
- 候选算法是可解释的离线模板，不是真实 LLM 在线生成。
- 排程算法不保证数学最优，只保证能展示验证反馈、评分和改进闭环。
- 轻量模拟器复用硬约束验证逻辑，没有模拟真实实验物理过程。

## 下一步

如果继续扩展，可以优先做四件事：

1. 接入真实 LLM API，让候选算法由模型生成，但必须沙箱执行和测试。
2. 增加局部搜索或启发式搜索，例如 swap batch order、critical path repair。
3. 把协议模拟器扩展为状态机，加入样本状态、失败概率和设备准备时间。
4. 增加可视化甘特图，方便面试演示和错误定位。

## GitHub 推送

如果需要推送到远程仓库：

```bash
git remote add origin <YOUR_GITHUB_REMOTE_URL>
git push -u origin main
```
