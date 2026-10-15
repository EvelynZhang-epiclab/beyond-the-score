"""Build the two static articles. Run with Python 3; no dependencies required."""
from pathlib import Path
from html import escape
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/report.json').read_text())
PUB = json.loads((ROOT / 'data/publication.json').read_text())
LANG = 'zh'

def t(zh, en):
    return zh if LANG == 'zh' else en

def p(zh, en, cls=''):
    return f'<p class="{cls}">{t(zh, en)}</p>'

def h3(id, zh, en):
    return f'<h3 id="{id}" data-toc>{t(zh, en)}</h3>'

def section(id, zh, en, body, cls=''):
    return f'<section id="{id}" class="{cls}" data-toc><h2>{t(zh, en)}</h2>{body}</section>'

def table(headers, rows, caption):
    head = ''.join(f'<th scope="col">{h}</th>' for h in headers)
    body = ''
    for row in rows:
        cells = ''.join(f'<th scope="row">{v}</th>' if i == 0 else f'<td>{v if v is not None else "—"}</td>' for i, v in enumerate(row))
        body += f'<tr>{cells}</tr>'
    return f'<div class="table-scroll" role="region" aria-label="{escape(caption)}" tabindex="0"><table><caption>{caption}</caption><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'

def detail(zh, en, body):
    return f'<details class="research-detail"><summary>{t(zh, en)}</summary>{body}</details>'

def figure(src, alt, caption):
    return f'<figure class="figure"><button type="button" data-zoom aria-label="{t("放大", "Enlarge")}: {escape(alt)}"><img loading="lazy" src="{src}" alt="{escape(alt)}"></button><figcaption>{caption}<span class="zoom-label" aria-hidden="true">{t("放大", "Enlarge")} ↗</span></figcaption></figure>'

def video(id, title):
    return f'<figure><video controls playsinline muted preload="none" poster="assets/rbm/{id}-poster.jpg" src="assets/rbm/{id}-replay.mp4" aria-label="{escape(title)}"></video><figcaption>{title}</figcaption></figure>'

def metrics():
    configs = DATA['table3_study_ranks']
    charts = []
    for title, unit, key, maximum, digits in [
        (t('独立质量排序', 'Independent ranking'), 'Kendall τa ↑', 'kendall_tau_a', 1, 4),
        (t('直接偏好判断', 'Direct preference'), t('准确率 % ↑', 'Accuracy % ↑'), 'preference_pct', 100, 1),
        (t('进度相关性', 'Progress correlation'), 'VOC ×100 ↑', 'voc_x100', 100, 1),
    ]:
        rows = ''
        for i, (name, value) in enumerate(zip(['Astra · low', 'GPT-5.6-sol · low', 'DeepSeek-V4.1-Flash · max'], configs[key])):
            rows += f'<div class="study-row"><span>{name}</span><div class="study-track" aria-hidden="true"><i class="{"primary" if i == 0 else ""}" style="width:{value / maximum * 100}%"></i></div><b>{value:.{digits}f}</b></div>'
        charts.append(f'<div class="study-chart"><h4>{title}<small>{unit}</small></h4>{rows}<div class="chart-axis"><span>0</span><span>{maximum}</span></div></div>')
    cap = t('图 2. 本研究三个零样本配置的结果。条形均从 0 起绘制。数值为点估计，未提供置信区间；推理设置不同，也不代表等计算预算比较。', 'Figure 2. The three zero-shot configurations evaluated in this study. All bars start at zero. These are point estimates without confidence intervals. Reasoning settings differ; this is not an equal-compute comparison.')
    return f'<figure class="study-figure">{"".join(charts)}<figcaption>{cap}</figcaption></figure>'

def ranking_chart():
    r = DATA['ranking_decomposition']
    labels = [t('正确顺序', 'Correct order'), t('平分', 'Tie'), t('颠倒', 'Inversion')]
    out = '<div class="stack-key">' + ''.join(f'<span><i></i>{x}</span>' for x in labels) + '</div>'
    for i, label in enumerate([t('零样本', 'Zero-shot'), t('三参考轨迹 ICL', 'Three-reference ICL')]):
        values = [r[k][i] for k in ['correct_strict_order_weight_pct', 'tie_weight_pct', 'inversion_weight_pct']]
        desc = ' · '.join(f'{l} {v:.2f}%' for l, v in zip(labels, values))
        bars = ''.join(f'<span style="width:{v}%"></span>' for v in values)
        out += f'<div class="stack-heading"><strong>{label}</strong><span>τa {r["tau_a"][i]:.4f}</span></div><div class="outcome-stack" role="img" aria-label="{desc}">{bars}</div><p class="stack-values">{desc}</p>'
    cap = t('图 4. 与报告得分一致的加权成对结果，非独立轨迹对的未加权计数。τa 等于正确顺序权重减去颠倒权重。', 'Figure 4. Weighted pair outcomes consistent with the reported scores, not unweighted counts of independent pairs. τa equals the correct-order weight minus the inversion weight.')
    return f'<figure class="study-figure">{out}<figcaption>{cap}</figcaption></figure>'

def diagnosis():
    return f'''<figure class="diagnosis"><div class="diagnosis-header"><span>ROBOFAIL · 57 {t('个问题', 'questions')}</span><div class="switch" role="group" aria-label="{t('选择评测条件', 'Evaluation condition')}"><button type="button" data-condition="0" aria-pressed="true">{t('零样本', 'Zero-shot')}</button><button type="button" data-condition="1" aria-pressed="false">{t('五示例 ICL', 'Five-example ICL')}</button></div></div>
    <div class="diagnosis-body" aria-live="polite" aria-atomic="true"><div class="accuracy"><b><span id="accuracy">64.91</span><small>%</small></b><span>{t('整体准确率', 'Overall accuracy')}</span><div class="diag-numbers"><div>{t('失败召回率', 'Failure recall')}<strong id="recall">94.12%</strong></div><div>{t('正确判断', 'Correct answers')}<strong id="correct">37 / 57</strong></div><div>{t('误报', 'False alarms')}<strong id="false-alarms">18</strong></div><div>{t('漏检', 'Misses')}<strong id="misses">2</strong></div></div></div>
    <div class="matrix" role="group" aria-label="{t('混淆矩阵', 'Confusion matrix')}"><span></span><span class="label">{t('预测成功', 'Predicted success')}</span><span class="label">{t('预测失败', 'Predicted failure')}</span><span class="label">{t('实际成功', 'Reference success')}</span><div class="cell"><b data-cell>5</b>{t('正确成功', 'Correct success')}</div><div class="cell error"><b data-cell>18</b>{t('误报', 'False alarm')}</div><span class="label">{t('实际失败', 'Reference failure')}</span><div class="cell error"><b data-cell>2</b>{t('漏检', 'Miss')}</div><div class="cell"><b data-cell>32</b>{t('正确失败', 'Correct failure')}</div></div></div>
    <figcaption>{t('图 5. 同一组 57 个问题上的成败判断。失败为正类；误报指实际成功但预测失败，漏检指实际失败但预测成功。这是离线分类，未测量在线报警时间。', 'Figure 5. Classification on the same 57 questions, treating failure as positive. A false alarm is a reference success predicted as failure; a miss is a reference failure predicted as success. This is offline classification, not a timestamped online alarm.')}</figcaption></figure>'''

def rouge_chart():
    r = DATA['rouge_decomposition']
    out = '<div class="stack-key rouge-key">' + ''.join(f'<span><i></i>{x}</span>' for x in [t('正确成功项', 'Correct-success term'), t('失败解释项', 'Failure-explanation term')]) + '</div>'
    for i, label in enumerate([t('零样本', 'Zero-shot'), t('外部五示例', 'External five-example')]):
        values = [r['success_terms'][i], r['failure_explanation_terms'][i]]
        bars = ''.join(f'<span style="width:{v / .55 * 100}%">{v:.4f}</span>' for v in values)
        desc = f'{label}: {values[0]:.4f} + {values[1]:.4f}'
        out += f'<div class="stack-heading"><strong>{label}</strong><span>{t("综合得分", "Composite score")} {DATA["table7_robofail_errors"]["composite_rouge_l"][i]:.3f}</span></div><div class="rouge-stack" role="img" aria-label="{desc}">{bars}</div>'
    cap = t('图 6. 综合 ROUGE-L 的组成，两项均以 57 为分母。两条形使用相同的 0–0.55 刻度。分项和总分分别取整，末位可能有舍入差异。', 'Figure 6. Components of composite ROUGE-L, both divided by 57. Both bars use a 0–0.55 scale. Components and totals are rounded separately and may differ in the last decimal.')
    return f'<figure class="study-figure">{out}<div class="chart-axis full"><span>0</span><span>0.55</span></div><figcaption>{cap}</figcaption></figure>'

def article():
    takeaways = [
        t('<strong>Astra 能区分不同质量的机器人执行。</strong>零样本排序 τa 为 0.8166，直接偏好准确率为 92.4%；在本研究的三个通用模型配置中，这两项结果的点估计最高。', '<strong>Astra distinguishes execution quality without task-specific fine-tuning.</strong> Zero-shot ranking τa is 0.8166 and direct preference accuracy is 92.4%, the highest point estimates among the three general-purpose configurations tested here.'),
        t('<strong>上下文示例对不同判断的影响并不一致。</strong>进度 VOC 从 93.6 升至 94.2，排序 τa 却从 0.8166 降至 0.7953。开瓶案例中，更高的进度相关性还伴随更差的终点估计。', '<strong>Context examples have mixed effects.</strong> Progress VOC rises from 93.6 to 94.2, while ranking τa falls from 0.8166 to 0.7953. In a bottle-opening example, higher progress correlation also accompanies a worse endpoint estimate.'),
        t('<strong>RoboFail 准确率提高，但失败召回率下降。</strong>五示例条件的准确率为 85.96%，零样本为 64.91%；误报由 18 个降至 2 个，漏检由 2 个增至 6 个。后端版本一致性未确认，不能将差异完全归因于示例。', '<strong>Higher RoboFail accuracy comes with lower failure recall.</strong> Accuracy is 85.96% with five examples versus 64.91% zero-shot. False alarms fall from 18 to 2, but misses rise from 2 to 6. Backend consistency is unconfirmed, so the difference cannot be attributed solely to examples.'),
        t('<strong>综合解释分数的增量主要来自成功判断。</strong>ROUGE-L 从 0.185 升至 0.499，其中约 89.3% 的增量来自正确成功项；这一变化不等于失败原因解释的同等改善。', '<strong>Most of the composite explanation-score gain comes from success recognition.</strong> ROUGE-L rises from 0.185 to 0.499; about 89.3% of the gain comes from the correct-success term, rather than the failure-explanation term.'),
    ]
    out = section('takeaways', 'Key takeaways · 主要发现', 'Key takeaways', '<ul>' + ''.join(f'<li>{x}</li>' for x in takeaways) + '</ul>', 'key-takeaways')

    body = p('我们研究 GPT-6 Astra 能否根据视觉观测评价机器人的执行。在 RBM 轨迹数据和 AHA 改编的 RoboFail 上，我们测试了四种判断：独立轨迹评分、两条轨迹的直接比较、任务进度估计，以及子任务成败判断与解释。模型通过提示接收任务和观测，没有针对这些评测任务进行专门微调。', 'We study whether GPT-6 Astra can assess robot execution from visual observations. On RBM trajectory data and the AHA adaptation of RoboFail, we evaluate four interfaces: independent trajectory scoring, direct comparison of two trajectories, progress estimation, and subtask success classification with explanations. Tasks and observations are supplied through prompts, without fine-tuning for these evaluations.')
    body += p('Astra 在执行质量比较上取得了较高得分。进一步分析则显示，进度相关性、排序区分度、失败召回率和解释质量并不总是一起改善。本文按评估接口介绍结果，并结合具体案例分析这些差异。实验均为离线评估，尚未检验评审反馈能否改善策略学习或闭环执行。', 'Astra obtains strong execution-quality scores in this evaluation. Further analysis shows that progress correlation, ranking discrimination, failure recall, and explanation quality do not always improve together. We present the results by interface and examine these differences through individual cases. All experiments are offline; we have not tested whether critic feedback improves policy learning or closed-loop execution.')
    out += section('overview', '概览', 'Overview', body)

    body = p('机器人评审员的输出可以用于比较轨迹、估计任务进展，或检查一个子任务是否完成。这些用途依赖不同的判断能力。我们将它们分别评估，避免用单一分数概括模型的全部表现。', 'A robot critic may compare trajectories, estimate progress, or check whether a subtask has finished. These uses require different judgments. We evaluate them separately rather than summarize all of them with one score.')
    body += table(
        [t('评估接口', 'Interface'), t('模型输入', 'Model input'), t('评测范围', 'Evaluation support')],
        [
            [t('独立质量排序', 'Independent ranking'), t('任务描述与单条轨迹的 8 帧', 'Task text and eight frames from one trajectory'), t('567 条轨迹；41 个来源–任务组', '567 trajectories; 41 source–task groups')],
            [t('直接偏好判断', 'Direct preference'), t('同一请求中的两条轨迹', 'Two trajectories in the same request'), t('1,192 组固定轨迹对', '1,192 fixed pairs')],
            [t('进度估计', 'Progress estimation'), t('任务描述、当前及之前的观测', 'Task text, current and preceding observations'), t('105 条成功轨迹；5 个评估位置', '105 successful trajectories; five evaluation positions')],
            [t('子任务诊断', 'Subtask diagnosis'), t('原始关键帧拼图与子任务问题', 'Original keyframe montage and subtask question'), t('15 组轨迹中的 57 个问题', '57 questions from 15 trajectory groups')],
        ], t('表 1. 四种评估接口。样本数不等于独立机器人试验次数。', 'Table 1. Four evaluation interfaces. Counts are not numbers of independent robot trials.'))
    body += p('进度与排序实验使用 RBM-EVAL-OOD 的六个数据来源。排序的参考质量顺序为成功高于次优、次优高于失败。偏好实验单独使用 1,192 组固定轨迹对；现有记录没有完整说明这些轨迹对的划分组成。RoboFail 的 57 个问题中，23 个子任务标注为成功，34 个标注为失败。', 'Progress and ranking use six sources from RBM-EVAL-OOD. The reference quality order is success above suboptimal above failure. Preference is evaluated separately on 1,192 fixed pairs, whose split composition is not fully documented in the available record. The 57 RoboFail questions include 23 reference-success and 34 reference-failure subtasks.')
    body += h3('trajectory-cases', '1.1 同一任务下的三种执行', '1.1 Three executions of the same task')
    body += p('下面三条轨迹的任务都是“把蓝色杯子放进水槽”。Q0041 将杯子放入水槽并松开；Q0039 的模型解释认为杯子在转移中滑落，仍处于槽外；Q0037 搬动了另一物体，蓝色杯子没有移动。保存的模型进度估计分别到达 1.00、从 0.55 回落至 0.40，以及降回 0。', 'All three trajectories below share the instruction “Put blue cup in sink.” Q0041 places and releases the cup in the sink. For Q0039, the model describes the cup slipping during transfer and remaining outside the basin. Q0037 moves another object while the blue cup stays in place. The saved progress estimates reach 1.00, fall from 0.55 to 0.40, and return to 0, respectively.')
    body += '<div class="demo">' + ''.join(video(id, title) for id, title in [
        ('q0041', t('Q0041 · 成功', 'Q0041 · Success')),
        ('q0039', t('Q0039 · 次优', 'Q0039 · Suboptimal')),
        ('q0037', t('Q0037 · 失败', 'Q0037 · Failure'))]) + '</div>'
    body += p('图 1. 保存观测的采样帧回放，展示时间不等于原始执行时间。案例在评测后选取，不代表错误频率。初始进度 0 由协议固定，其余进度为模型输出，非人工完成度标注；模型解释未经独立物理原因验证。', 'Figure 1. Replays of stored sampled frames; playback time is not original execution time. These cases were selected post hoc and do not estimate error frequency. Initial progress is fixed at zero by protocol. Subsequent scores are model outputs, not human completion annotations; model explanations are not independently verified physical causes.', 'fine')
    body += f'<a class="inline-link" href="evidence.html#trajectories">{t("查看逐帧输入与原始模型回答（英文）", "Inspect observations and original model responses")} ↗</a>'
    out += section('setup', '1. 研究设置', '1. Study design', body)

    body = p('独立评分时，模型分别观察每条轨迹，再根据分数进行排序。Astra 的 Kendall τa 为 <strong>0.8166</strong>。这一指标衡量预测顺序与参考质量顺序的一致性，错误颠倒和预测平分都会降低得分。直接偏好判断则让模型同时观察两条轨迹，选择较优执行；Astra 的准确率为 <strong>92.4%</strong>。由于输入方式不同，偏好准确率不能解释为独立评分的排序准确率。', 'For independent scoring, the model observes each trajectory separately and the scores determine a ranking. Astra obtains Kendall τa of <strong>0.8166</strong>. This metric measures agreement with reference quality order; inversions and predicted ties reduce the score. In direct preference, the model sees both trajectories and selects the better execution, reaching <strong>92.4%</strong> accuracy. Because the input interfaces differ, preference accuracy is not the accuracy of ordering independently computed scores.')
    body += metrics()
    body += p('在本研究的三个零样本通用模型配置中，Astra 的三项指标点估计均最高。相对 GPT-5.6-sol，排序 τa 高 0.0666，偏好准确率高 1.7 个百分点，进度 VOC 高 0.1。数值差距最明显的是独立质量排序。当前没有重复调用方差或置信区间，因此这些差异不作统计显著性解释。', 'Astra has the highest point estimate on all three metrics among the three zero-shot general-purpose configurations tested here. Relative to GPT-5.6-sol, the gaps are 0.0666 in ranking τa, 1.7 percentage points in preference accuracy, and 0.1 in progress VOC. The clearest numerical separation is in independent ranking. Repeat-call variance and confidence intervals are unavailable, so these differences are descriptive rather than significance claims.')
    body += h3('literature', '2.1 与已有工作的比较', '2.1 Comparison with prior work')
    body += p('RynnValue-8B 报告排序 τa 为 0.675；Robometer 论文版报告 τa 为 0.655、偏好准确率为 82.5%、进度 VOC 为 94.8。Astra 的排序与偏好数值较高，但进度 VOC 低于这一 Robometer 记录。', 'RynnValue-8B reports ranking τa of 0.675. The Robometer paper reports τa of 0.655, preference accuracy of 82.5%, and progress VOC of 94.8. Astra’s ranking and preference values are numerically higher, while its progress VOC is lower than this Robometer record.')
    body += p('这些文献值没有在本研究的样本上复测。RynnValue 描述了 976 条 OOD 轨迹，而这里评分的是 567 条；外部偏好评测在每个 OOD 来源使用 500 组不同质量轨迹对，本研究则使用组成未完全记录的 1,192 组固定对。样本、输入与聚合方式未对齐，不能据此得出统一协议下的领先结论。', 'These literature values were not rerun on our samples. RynnValue describes a 976-trajectory OOD suite, whereas this study scores 567 trajectories. External preference evaluation uses 500 different-quality pairs per OOD source; our study uses 1,192 fixed pairs with incompletely documented composition. Sample, input, and aggregation differences prevent a matched-protocol superiority claim.')
    rows = [[escape(r[0]), t('本研究', 'This study') if r[1] == 'study' else escape(r[1]), f'{r[2]:.1f}' if r[2] is not None else None, f'{r[3]:.4f}' if r[3] is not None else None, f'{r[4]:.1f}' if r[4] is not None else None] for r in DATA['table2_rbm']['rows']]
    more = table([t('配置', 'Configuration'), t('来源', 'Source'), 'VOC ×100 ↑', 'τa ↑', t('偏好 % ↑', 'Preference % ↑')], rows, t('完整 RBM 结果：保留不同来源与版本。', 'Full RBM results, retaining distinct sources and versions.'))
    more += p('Robometer 论文版与网站版分别报告 VOC 94.8 / 94.0、τa 0.655 / 0.643，分别保留，不合并。名称中的 RBM-1M 和 RoboReward data 指训练数据。空项表示没有核实的数值；ICL 不作为额外模型，也不与零样本结果择优拼接。', 'The Robometer paper and website report VOC of 94.8 / 94.0 and τa of 0.655 / 0.643, respectively; both versions are retained. RBM-1M and RoboReward data in configuration names refer to training data. Missing values are not imputed. ICL is neither counted as an additional model nor selectively combined with zero-shot results.')
    for file, zh, en in [('01_ranking.png', '独立排序完整结果', 'Full independent-ranking results'), ('02_preference.png', '直接偏好完整结果', 'Full direct-preference results'), ('03_progress.png', '进度相关性完整结果', 'Full progress-correlation results')]:
        more += figure('assets/figures/' + file, t(zh, en), t('完整来源图；跨论文数值不是同协议排名。', 'Original source chart; cross-paper values are not matched-protocol rankings.'))
    body += detail('完整结果与文献图表', 'Full results and literature charts', more)
    out += section('results', '2. 轨迹质量与偏好', '2. Trajectory quality and preference', body)

    body = p('我们还测试了在请求中加入带答案的示例。上下文学习（ICL）不更新模型参数；不同评估接口使用不同的示例构造。进度估计使用一条相同或相近任务的训练轨迹，包含六个阶段评分。排序使用随机选取的高、中、低分训练轨迹各一条，不要求与测试任务相同。中等参考分数不等于测试集的“次优”标签。这两种配置不构成等上下文长度比较，直接偏好判断没有报告 ICL 结果。', 'We also test demonstrations supplied in the request. In-context learning (ICL) does not update model parameters, and the example construction differs by interface. Progress uses one same- or similar-task training trajectory with six stage scores. Ranking uses three randomly selected high-, middle-, and low-score training trajectories, without requiring a task match. The middle reference score is not the test set’s suboptimal label. These are not equal-context comparisons, and no ICL preference result is reported.')
    body += h3('progress', '3.1 进度相关性与终点估计', '3.1 Progress correlation and endpoint estimates')
    body += p('在 105 条成功轨迹上，Astra 的零样本 VOC 为 93.6。预测只使用当前及之前的画面，并与时间参考序列比较。VOC 使用 ×100 标度，描述预测进度与时间的相关性，不表示完成度判断的准确率。任务可能长时间停留在准备阶段，最后才发生关键状态变化，语义进度不必随时间均匀增长。', 'Across 105 successful trajectories, zero-shot Astra obtains VOC of 93.6. Predictions use only current and preceding frames and are compared with a time reference. VOC is reported on a ×100 scale and measures progress–time correlation, not completion accuracy. A task can remain in preparation for a long period before a late state change; semantic progress need not increase uniformly with time.')
    body += p('单轨迹 ICL 将总体 VOC 提高到 94.2，时间参考 MSE 从 0.0402 降到 0.0390。但逐轨迹变化并不一致：58 条的 VOC 提高、35 条下降、12 条不变。在报告的香蕉转移任务中，19 条轨迹有 18 条下降、1 条不变；58 条 VOC 提高的轨迹中，也有 11 条的 MSE 变差。', 'With single-trajectory ICL, aggregate VOC rises to 94.2 and time-reference MSE falls from 0.0402 to 0.0390. Per-trajectory changes are mixed: VOC improves on 58 trajectories, declines on 35, and is unchanged on 12. In the reported banana-transfer task, 18 of 19 trajectories decline and one is unchanged. Of the 58 trajectories with higher VOC, 11 have worse MSE.')
    body += '<div class="feature-case">' + video('t098', t('T098 · 开瓶任务', 'T098 · Open the bottle')) + '<div>'
    body += p('开瓶案例 T098 的公开终点标签是成功。零样本给出 1.00 的终点分数，ICL 给出 0.35。ICL 的 VOC 更高，但终点分数距离公开成功标签更远，时间参考 MSE 约为零样本的 3.22 倍。', 'The public terminal label for bottle-opening case T098 is success. Zero-shot gives a terminal score of 1.00, while ICL gives 0.35. ICL has higher VOC, but its endpoint score is farther from the public success label and its time-reference MSE is about 3.22 times larger.') + '</div></div>'
    body += table([t('条件', 'Condition'), t('终点分数', 'Terminal score'), t('VOC（未缩放）↑', 'VOC (unscaled) ↑'), 'MSE ↓'], [[t('零样本', 'Zero-shot'), '1.00', '0.9051', '0.0407'], [t('单轨迹 ICL', 'Single-trajectory ICL'), '0.35', '0.9536', '0.1312']], t('图 3 / 表 2. 开瓶案例的两种评估结果。', 'Figure 3 / Table 2. Two evaluations of the bottle-opening case.'))
    body += p('该案例在评测后选取，用于说明两项指标可能不一致，不估计这种错误的频率。公开成功标签保持不变，实际完成状态未经过独立重判。MSE 同样使用时间参考，非人工语义完成度。', 'This post-hoc example illustrates a disagreement between metrics; it does not estimate how often that disagreement occurs. We retain the public success label without independently adjudicating visual completion. MSE also uses the time reference, not human semantic-completion annotations.', 'fine')
    body += h3('ranking-context', '3.2 排序中的平分与颠倒', '3.2 Ties and inversions in ranking')
    body += p('加入三条参考轨迹后，τa 从 0.8166 降至 0.7953。41 个来源–任务组中，8 组提高、10 组下降、23 组不变。按与得分一致的成对权重分解，颠倒由 4.78% 减少到 3.68%，但平分由 8.78% 增加到 13.11%，正确严格顺序由 86.44% 减少到 83.21%。', 'With three reference trajectories, τa falls from 0.8166 to 0.7953. Of 41 source–task groups, eight improve, ten decline, and 23 remain unchanged. Under score-consistent pair weighting, inversions fall from 4.78% to 3.68%, but ties rise from 8.78% to 13.11% and correct strict orders fall from 86.44% to 83.21%.')
    body += ranking_chart()
    body += p('因此，较少的颠倒没有转化为更好的排序。更多平分使模型无法区分原本有质量差别的执行，抵消了颠倒减少带来的收益。该分解说明分数如何变化，尚不能确定示例影响判断的具体机制。', 'Fewer inversions therefore do not produce a better ranking. More ties leave executions of different quality indistinguishable and offset the reduction in inversions. The decomposition explains the score change, but does not identify the mechanism by which examples affect judgment.')
    out += section('context', '3. 进度估计与上下文示例', '3. Progress estimation and context examples', body)

    body = p('RoboFail 要求模型根据关键帧拼图判断子任务是否成功，并解释失败。零样本条件识别出 34 个失败中的 32 个，失败召回率为 94.12%；同时将 23 个成功中的 18 个判为失败，整体准确率为 37 / 57，即 64.91%。', 'RoboFail asks the model to classify subtask success from a keyframe montage and explain failures. Zero-shot detects 32 of 34 failures, giving 94.12% failure recall. It also misclassifies 18 of 23 successes as failures, yielding overall accuracy of 37 / 57, or 64.91%.')
    body += p('五个外部图像–问题–答案示例条件下，模型答对 49 / 57，准确率为 85.96%。正确成功判断从 5 个增加到 21 个，正确失败判断从 32 个减少到 28 个。总共增加的 12 个正确答案，来自多识别出 16 个成功，同时少识别出 4 个失败。', 'With five external image–question–answer examples, the model answers 49 / 57 correctly, or 85.96%. Correct-success judgments rise from 5 to 21, while correct-failure judgments fall from 32 to 28. The net gain of 12 correct answers consists of 16 additional successes recognized and four fewer failures detected.')
    body += diagnosis()
    body += p('成功样本的误报率从 78.26% 降到 8.70%，失败样本的漏检率则从 5.88% 升到 17.65%。五示例条件更善于认可成功，但更容易漏掉失败。实际应用中如何取舍，需要考虑误报干预和失败漏检的成本；本研究没有测量这些成本。', 'The false-alarm rate on successful subtasks falls from 78.26% to 8.70%, while the miss rate on failures rises from 5.88% to 17.65%. The five-example condition recognizes success more often, but also misses more failures. The practical choice depends on the costs of unnecessary intervention and missed failures, which are not measured here.')
    body += p('这一比较仍有两项限制。五个示例报告为与测试轨迹不重叠，但不保证环境、机器人形态、近重复样本或预训练数据独立。另外，两种条件请求相同模型名和 low 推理设置，返回模型标识却存在差异，后端快照一致性尚未确认。因此，观察到的差值不能作为 ICL 的独立因果效应。', 'Two limitations apply. The five demonstrations are reported as disjoint from test trajectories, which does not establish environment, embodiment, near-duplicate, or pretraining independence. Also, returned model identifiers differ despite the same requested model name and low reasoning setting. Backend snapshot consistency is unconfirmed, so the observed difference does not isolate a causal effect of ICL.', 'method-note')
    more = table([t('配置', 'Configuration'), t('来源', 'Source'), t('准确率 % ↑', 'Accuracy % ↑'), 'ROUGE-L ↑'], [[escape(r[0]), t('本研究', 'This study') if r[1] == 'study' else escape(r[1]), f'{r[2]:.2f}', f'{r[3]:.3f}'] for r in DATA['table5_robofail_aha']['rows']], t('本研究与 AHA 文献记录；精确问题集合对齐未验证。', 'This study and published AHA records; exact question alignment is unverified.'))
    more += p('外部结果未在本研究的 57 个问题上重跑或独立重评分。AHA-13B 的 Vicuna 与 Llama-2 版本单独保留。文献中的零分按原记录呈现，不解释为模型本身完全没有相关能力。', 'External results were not rerun or independently rescored on our 57 questions. The Vicuna and Llama-2 variants of AHA-13B remain separate. Published zero scores are retained without interpreting them as intrinsic inability.')
    more += figure('assets/figures/04_robofail_icl.png', t('子任务成败判断完整结果', 'Full subtask classification results'), t('本研究与文献值分开呈现，非统一样本排名。', 'Study and literature values are separated, not ranked on a common sample.'))
    more += figure('assets/figures/05_robofail_icl.png', t('综合 ROUGE-L 完整结果', 'Full composite ROUGE-L results'), t('综合分数包含成败分类项，其定义见下一节。', 'The composite includes a classification term; see the definition in the next section.'))
    more += p('Guardian 使用 153 个执行样本与 30 个规划样本；PRIMO 使用 Cosmos 筛选的 100 个样本。它们与本研究的评测范围不同，且没有 Astra 在这两套数据上的结果。下列文献记录分别列示，不与本研究的 85.96% 合并排名。', 'Guardian uses 153 execution and 30 planning examples; PRIMO uses 100 Cosmos-curated examples. These supports differ from ours, and no Astra result is available on either. The literature records below remain separate from our 85.96% result.')
    more += table([t('配置', 'Configuration'), t('执行准确率 %', 'Execution accuracy %'), t('规划准确率 %', 'Planning accuracy %')], DATA['table6_other_adaptations']['guardian']['rows'], t('Guardian v4，Tables 1/2。+GF 表示使用 GuardianFail-36k 训练。', 'Guardian v4, Tables 1/2. +GF denotes training on GuardianFail-36k.'))
    more += table([t('配置', 'Configuration'), t('准确率 %', 'Accuracy %')], DATA['table6_other_adaptations']['primo']['rows'], 'PRIMO, Table 3 / Appendix A.3.')
    body += detail('完整结果与不同 RoboFail 评测版本', 'Full results and distinct RoboFail adaptations', more)
    out += section('failure', '4. 子任务成败判断', '4. Subtask success and failure', body)

    body = p('五示例条件的综合 ROUGE-L 从 0.185 增加到 0.499。这个指标不只衡量失败解释。按 AHA 评测规则，正确成功回答计 1 分，正确失败回答按解释与参考答案的词干化 ROUGE-L F1 计分，成败标签错误则计 0 分。所有问题得分相加后除以 57。评分使用原始英文回答，不使用本文的中文转述。', 'Composite ROUGE-L rises from 0.185 to 0.499 in the five-example condition. This metric does not measure failure explanations alone. Under the AHA rules, a correct success answer receives 1; a correct failure receives stemmed ROUGE-L F1 against the reference explanation; and a label disagreement receives 0. Scores are summed and divided by 57. Evaluation uses the original English answers, not the Chinese paraphrases in this article.')
    body += f'<div class="formula" role="math" aria-label="{t("综合得分等于正确成功数加上正确失败的解释分数总和，再除以57", "Composite score equals correct successes plus summed explanation scores for correctly detected failures, divided by 57")}">R = ({t("正确成功数 + 正确失败的解释分数之和", "correct successes + summed explanation scores for correct failures")}) / 57</div>'
    body += rouge_chart()
    body += p('正确成功项从 0.0877 增至 0.3684，增量约为 16 / 57 = 0.2807，占报告总增量 0.3144 的约 89.3%。失败解释项从 0.0969 增至 0.1305，占剩余约 10.7%。因此，0.499 不能读作“49.9% 的失败解释正确”；大部分增量来自识别成功，而非失败解释项。', 'The correct-success term rises from 0.0877 to 0.3684. Its increase, 16 / 57 ≈ 0.2807, accounts for about 89.3% of the reported total gain of 0.3144. The failure-explanation term rises from 0.0969 to 0.1305, accounting for the remaining 10.7%. A score of 0.499 therefore does not mean that 49.9% of failure explanations are correct. Most of the gain comes from recognizing success.')
    body += p('解释项还取决于哪些失败被检测到，以及回答与参考文本的词汇重合度。它无法独立区分语义正确的改写和措辞相似但原因错误的回答。要评价失败原因是否可信，需要额外的语义核验与物理证据。', 'The explanation term also depends on which failures are detected and on lexical overlap with reference text. It does not independently distinguish a correct paraphrase from a similarly worded but incorrect diagnosis. Assessing the stated cause requires additional semantic review and physical evidence.')
    body += h3('knob-case', '5.1 抓旋钮案例', '5.1 The knob-grasping case')
    body += figure('assets/robofail/case-055-input.jpg', t('抓旋钮子任务的原始模型输入拼图', 'Original model-input montage for the knob-grasping subtask'), t('图 7. RoboFail 第 55 号案例的原始输入。白格表示尚未发生的后续子任务，可放大查看。', 'Figure 7. Original input for RoboFail case 55. White cells represent future subtasks. Open the image to inspect it at full size.'))
    body += table([t('来源', 'Source'), t('判断与解释', 'Judgment and explanation')], [
        [t('参考答案', 'Reference'), t('失败：夹爪没有闭合。', 'Failure: the gripper did not close.')],
        [t('零样本', 'Zero-shot'), t('判断失败；解释为抓取位置不对，没有建立稳固抓取。', 'Predicts failure, but describes an incorrect grasp location and no secure grasp.')],
        [t('五示例', 'Five-example'), t('判断已经成功抓住旋钮。', 'Predicts that the robot successfully grasped the knob.')],
    ], t('表 3. 保存回答的中文转述；原始回答可在案例页查看。', 'Table 3. Paraphrases of saved responses; original wording is available on the case page.'))
    body += p('零样本的标签与参考一致，解释却没有指出参考答案中的夹爪闭合问题。五示例条件则把同一个失败子任务判为成功。这个案例说明标签判断和原因解释需要分别核查，但不足以估计整体错误分布，也不验证任一模型解释所声称的物理原因。', 'The zero-shot label agrees with the reference, but its explanation does not identify the gripper-closure issue in the reference answer. The five-example condition predicts success for the same failed subtask. This case illustrates why labels and explanations need separate review; it neither estimates aggregate error frequency nor verifies the physical cause stated by either response.')
    body += f'<a class="inline-link" href="evidence.html#failure-cases">{t("查看关键帧、原始回答与源视频", "View keyframes, original responses, and source video")} ↗</a>'
    out += section('explanations', '5. 失败解释与综合得分', '5. Failure explanations and composite scores', body)

    body = p('这些结果支持将 Astra 用作机器人行为离线评估的研究对象：它能在当前样本上区分执行质量，跟踪进度变化，并识别不少失败。与此同时，示例对各项指标的影响不同。进度评估需要同时检查终点判断，排序需要检查平分，成败分类需要分别报告误报与漏检，解释则需要超出词汇重合度的验证。', 'These results support further study of Astra for offline robot assessment: it distinguishes execution quality, tracks progress, and detects many failures in the evaluated samples. The effects of examples nevertheless differ across metrics. Progress evaluation should include endpoint judgments; ranking should include ties; classification should report false alarms and misses separately; and explanations need validation beyond lexical overlap.')
    body += h3('limitations', '6.1 研究局限', '6.1 Limitations')
    body += p('<strong>评测范围。</strong>实验没有用评审反馈训练或控制策略，没有测量强化学习样本效率、在线失败定位、恢复行为或闭环成功率。离线得分尚不能证明可靠的接触状态推理、因果失败诊断或奖励模型部署安全性。', '<strong>Scope.</strong> No policy is trained or controlled using the critic. We do not measure reinforcement-learning sample efficiency, online failure localization, recovery, or closed-loop success. Offline scores do not establish reliable contact-state reasoning, causal diagnosis, or reward-model deployment safety.')
    body += p('<strong>统计与实验控制。</strong>57 个 RoboFail 问题来自 15 组轨迹，排序对也可能共享轨迹与任务。当前记录没有量化重复调用波动或抽样不确定性，小幅差异不能解释为已确定的提升。RoboFail 后端差异和示例选择影响仍需单独控制。', '<strong>Statistics and experimental control.</strong> The 57 RoboFail questions share 15 trajectory groups, and ranking pairs may share trajectories and tasks. Repeat-call variation and sampling uncertainty are not quantified, so small differences are not established improvements. RoboFail backend differences and example-selection effects also require separate control.')
    body += p('<strong>标签与案例。</strong>定性案例在评测后选取，不用于判断主要错误类型的频率。标签歧义、观测不足和模型错误都可能影响结果；缺少独立盲评时，不能凭模型解释判定参考标签错误。本文保留原有公开标签。', '<strong>Labels and cases.</strong> Qualitative cases were selected post hoc and do not estimate the prevalence of failure types. Label ambiguity, limited visual evidence, and model error can all affect outcomes. Without independent blind review, model rationales do not establish that a reference label is wrong. We retain the released labels.')
    more = p('现有材料包含评估规模、示例构造、聚合结果和部分案例。完整独立复现仍需补齐六个来源与样本清单、偏好划分组成、输入帧身份和分辨率、完整提示词与示例身份、请求及返回模型版本、运行日期、输出预算与采样设置，以及解析、拒答、重试和缺失输出规则。', 'The available materials provide evaluation counts, demonstration constructions, aggregates, and selected cases. Full independent reproduction still requires source and sample manifests, preference split composition, input-frame identities and resolution, complete prompts and demonstration identities, requested and returned model versions, run dates, output budgets and sampling settings, and parsing, refusal, retry, and missing-output rules.')
    more += p('还需要评分器版本、聚合权重、并列分数约定与逐样本预测，以便审计得分，并在保留轨迹或来源–任务依赖的条件下估计不确定性。补齐材料不会自动消除后端或示例选择的混杂影响，材料缺失本身也不证明底层实验无效。', 'Scorer versions, aggregation weights, tie conventions, and per-sample predictions are also needed for score audits and uncertainty estimates that preserve trajectory or source–task dependence. Completing the release would not itself resolve backend or example-selection confounds; missing materials are also not evidence that the underlying experiments are invalid.')
    body += detail('复现材料的范围', 'Reproducibility status', more)
    body += h3('next-steps', '6.2 后续验证', '6.2 Next validation steps')
    body += p('下一步是在确认同一模型快照、固定输入和示例选取规则的条件下重复比较；随后对完成状态和失败解释进行独立标注，覆盖遮挡、模糊和低可观测性案例。最后，在固定初始策略、算法和交互预算下，用独立于评审员的成功标准检验反馈是否改善学习。该实验还应报告反馈成本，并检查策略是否利用评分漏洞。', 'The next step is to repeat comparisons under a confirmed common model snapshot with fixed inputs and demonstration-selection rules. Independent annotation of completion and failure explanations should then cover occluded, ambiguous, and low-observability cases. Finally, feedback should be tested with a fixed initial policy, algorithm, and interaction budget, using a success measure independent of the critic. That experiment should report feedback cost and check for reward exploitation.')
    out += section('outlook', '6. 讨论与局限', '6. Discussion and limitations', body)
    out += resources()
    return out

def resources():
    links = [
        ('evidence.html#trajectories', t('交互案例与原始回答（英文）', 'Interactive cases and original responses'), False),
        ('data/report.json', t('完整结果与指标定义', 'Result tables and metric definitions'), True),
        ('data/rbm-cases.json', t('轨迹案例数据', 'Trajectory case data'), True),
        ('data/robofail-cases.json', t('RoboFail 案例数据', 'RoboFail case data'), True),
    ]
    body = '<ul class="resource-links">' + ''.join(f'<li><a href="{url}" {"download" if download else ""}>{label} {"↓" if download else "↗"}</a></li>' for url, label, download in links) + '</ul>'
    refs = [
        ('https://arxiv.org/abs/2603.02115', 'Robometer', t('论文 v1，Tables XIII、XVI、XVII。', 'Paper v1, Tables XIII, XVI, XVII.')),
        ('https://robometer.github.io/', 'RBM-EVAL-OOD', t('项目网站的详细 OOD 表，与论文版分别记录。', 'Detailed website OOD tables, retained separately from the paper.')),
        ('https://arxiv.org/abs/2608.09853', 'RynnValue', 'Table 2, §4.2.'),
        ('https://aha-vlm.github.io/', 'AHA', t('Tables 3/4；评分实现记录版本：', 'Tables 3/4; recorded scoring-code revision: ') + '<code>0d39c0591566ddaf997be5822f3dead8e08501aa</code>.'),
        ('https://arxiv.org/html/2512.01946v4', 'Guardian', 'v4, Tables 1/2.'),
        ('https://arxiv.org/html/2603.15600', 'PRIMO', 'Table 3, Appendix A.3.'),
    ]
    body += '<ol class="references">' + ''.join(f'<li><a href="{url}" target="_blank" rel="noopener">{name}</a>. {note}</li>' for url, name, note in refs) + '</ol>'
    body += p('完整 RBM 表还列出 GVL、VLAC、RoboReward、ReWiND、RL-VLM-F、TOPReward 与 Robo-Dopamine。其数值来自表内注明的 Robometer 论文或网站记录，不表示这些方法的原论文均评估了 RBM。', 'The full RBM table also includes GVL, VLAC, RoboReward, ReWiND, RL-VLM-F, TOPReward, and Robo-Dopamine. Their numbers come from the identified Robometer paper or website records; this does not imply that each method’s original paper evaluated RBM.', 'fine')
    body += detail('其他方法文献', 'Additional method references', '<ul class="references">' + ''.join(f'<li><a href="{url}" target="_blank" rel="noopener">{name}</a></li>' for url, name in [
        ('https://arxiv.org/abs/2509.15937','VLAC'), ('https://arxiv.org/abs/2601.00675','RoboReward'), ('https://arxiv.org/abs/2505.10911','ReWiND'), ('https://arxiv.org/abs/2402.03681','RL-VLM-F'), ('https://arxiv.org/abs/2602.19313','TOPReward'), ('https://arxiv.org/abs/2512.23703','Robo-Dopamine')]) + '<li>GVL: Vision Language Models Are In-Context Value Learners. ICLR, 2025.</li></ul>')
    body += p('实验与文献数值沿用已核验的 2026 年 9 月 23 日记录，结合 10 月 14 日中文稿和已有案例整理。网页更新不增加新的聚合实验结果，文献值不代表实时榜单。', 'Experimental and literature values follow the verified September 23, 2026 record, incorporating the October 14 Chinese draft and existing cases. This webpage revision adds no new aggregate experiments. Literature values are a dated snapshot, not a live leaderboard.', 'fine')
    return section('resources', '数据与参考文献', 'Data and references', body)

def render():
    filename = 'index.html' if LANG == 'zh' else 'en.html'
    title = t('Beyond the Score：GPT-6 Astra 作为机器人评审员的初步评估', 'Beyond the Score: Early Evaluations of GPT-6 Astra as a Robot Critic')
    description = t('机器人轨迹质量、进度估计与失败诊断：GPT-6 Astra 的离线评估结果、上下文示例分析与研究局限。', 'Offline evaluations of GPT-6 Astra as a robot critic: trajectory quality, progress estimation, failure diagnosis, context examples, and limitations.')
    items = [
        ('takeaways', 'Key takeaways', 'Key takeaways', False), ('overview','概览','Overview',False),
        ('setup','1. 研究设置','1. Study design',False), ('trajectory-cases','1.1 执行案例','1.1 Execution examples',True),
        ('results','2. 轨迹质量与偏好','2. Quality and preference',False), ('literature','2.1 已有工作','2.1 Prior work',True),
        ('context','3. 进度与上下文示例','3. Progress and context',False), ('progress','3.1 进度与终点','3.1 Progress and endpoints',True), ('ranking-context','3.2 平分与颠倒','3.2 Ties and inversions',True),
        ('failure','4. 子任务成败判断','4. Subtask classification',False),
        ('explanations','5. 失败解释与得分','5. Explanations and scores',False), ('knob-case','5.1 抓旋钮案例','5.1 Knob-grasping case',True),
        ('outlook','6. 讨论与局限','6. Discussion and limitations',False), ('limitations','6.1 研究局限','6.1 Limitations',True), ('next-steps','6.2 后续验证','6.2 Next steps',True),
        ('resources','数据与参考文献','Data and references',False),
    ]
    toc = ''.join(f'<a class="{"subsection" if sub else ""}" href="#{id}">{t(zh,en)}</a>' for id, zh, en, sub in items)
    langs = ''.join(f'<a data-language-link href="{file}" lang="{lang}" hreflang="{lang}" {"aria-current=\"page\"" if LANG == code else ""}>{label}</a>' for code, lang, file, label in [('zh','zh-CN','index.html','中文'),('en','en','en.html','English')])
    author_meta = ''.join(f'<meta name="citation_author" content="{escape(a)}">' for a in PUB['authors'])
    authors = ', '.join(f'<span>{escape(a)}</span>' for a in PUB['authors'])
    return f'''<!doctype html>
<html lang="{t('zh-CN','en')}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · Simple AI</title><meta name="description" content="{description}"><meta name="theme-color" content="#f8f7f3">
{author_meta}<meta property="og:title" content="{title}"><meta property="og:description" content="{description}"><meta property="og:type" content="article">
<link rel="alternate" hreflang="zh-CN" href="index.html"><link rel="alternate" hreflang="en" href="en.html"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="blog.css"><script src="blog.js" defer></script></head>
<body><a class="skip" href="#takeaways">{t('跳到正文','Skip to article')}</a>
<header class="header"><div class="wrap header-inner"><a class="brand" href="#top" aria-label="Simple AI">SIMPLE<span>·AI</span></a><span class="research">RESEARCH</span><nav class="language-switch" aria-label="{t('语言','Language')}">{langs}</nav></div></header><div id="reading-progress" aria-hidden="true"></div>
<main id="top"><div class="wrap article-shell"><aside class="toc" aria-label="{t('文章目录','Table of contents')}"><p>{t('目录','Contents')}</p><nav>{toc}</nav></aside><article class="article">
<header class="article-title"><p class="publication-meta">RESEARCH BLOG <span>·</span> <time datetime="{PUB['updated']}">{t('2026 年 10 月 15 日','October 15, 2026')}</time></p>
<h1><span class="title-name">Beyond the Score</span><span class="title-description">{t('GPT-6 Astra 作为机器人评审员的初步评估','Early Evaluations of GPT-6 Astra as a Robot Critic')}</span></h1>
<div class="author-block"><p class="authors">{authors}</p><p class="organization">{PUB['organization']}</p></div>
<div class="publication-links" aria-label="{t('研究材料','Research materials')}"><a href="evidence.html#trajectories">{t('交互案例','Gallery')} ↗</a><span class="unreleased">Code <small>(coming soon)</small></span><span class="unreleased">arXiv <small>(coming soon)</small></span></div></header>
{article()}
</article></div></main><footer class="footer wrap"><a class="brand" href="#top">SIMPLE<span>·AI</span></a><span>Beyond the Score · 2026</span><a href="#top">{t('返回顶部','Back to top')} ↑</a></footer>
<dialog id="figure-modal" aria-label="{t('图表大图','Expanded figure')}"><button id="close-figure" type="button" aria-label="{t('关闭大图','Close figure')}">×</button><img id="expanded-figure" alt=""><p id="figure-description"></p></dialog>
</body></html>'''

if __name__ == '__main__':
    for LANG, name in [('zh','index.html'),('en','en.html')]:
        content = render().replace('><', '>\n<')
        (ROOT / name).write_text(content)
        print(f'Built {name}: {len(content.encode())} bytes')
