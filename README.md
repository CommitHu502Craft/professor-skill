<div align="center">

# 大学老师.skill

### 老师蒸馏 + 期末求生

> A professor-distilled skill for finals survival

> "这题我上课讲过。"
>
> "老师，您上课一共讲了 187 页 PPT。"
>
> "所以你们更应该自己总结。"

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Status](https://img.shields.io/badge/status-beta-orange)
![Positioning](https://img.shields.io/badge/positioning-review--first-black)
![UseCase](https://img.shields.io/badge/use%20case-%E6%9C%9F%E6%9C%AB%E5%A4%8D%E4%B9%A0%20%2B%20%E8%80%81%E5%B8%88%E6%A8%A1%E6%8B%9F-blue)

<br>

你的老师不会给你划重点。<br>
你的助教不会半夜回你消息。<br>
你的学长毕业了，重点也跟着毕业了。<br>
你的课程资料散落在群文件、课件、作业、往年题和聊天记录里。<br>

**将混乱的课程上下文，蒸馏成一个真正能陪你过期末的 Skill。**

<br>

提供 `syllabus`、`课件`、`作业`、`往年题`、`课堂转写`、`学长笔记` 和你的主观判断<br>
生成一个真正懂这门课的 `Professor Skill`<br>
它知道这门课哪里最爱考，知道老师喜欢怎么问，知道助教会怎么扣分，也知道你离挂科还有多远

<br>

**欢迎加入赛博划重点。**

老师不划重点，那就自己造一个会划重点的老师。

[30 秒看懂](#30-秒看懂) · [效果示例](#效果示例) · [为什么不是普通复习资料整理器](#为什么不是普通复习资料整理器) · [工作流程](#工作流程) · [快速开始](#快速开始)

</div>

---

## 30 秒看懂

`大学老师.skill` 不是普通的笔记总结器。

它会把一门课的 `课件`、`作业`、`往年题`、`课堂转写`、`学长笔记` 和你的主观判断，整理成三个可复用产物：

- `persona.md`：老师会怎么讲、怎么提示、怎么答疑
- `course.md`：这门课真正的核心结构、题型信号和常见陷阱
- `review_guide.md`：面向期末冲刺的高密度复习资料

它不承诺“精准押题”。
它做的是：把零散课程上下文压缩成一个更像老师 / 助教 / 学长混合体的复习入口。

## 生成产物预览

```text
professor-workspace/
├── persona.md
├── course.md
├── review_guide.md
├── materials_manifest.md
└── source_brief.md

review_guide.md
├── 30 秒总结
├── Must Know
├── 高频题型
├── 老师可能会这么问
├── 高频扣分点
└── 考前一晚清单

review_guide.md
- 高频考点：特征值、二次型、正定矩阵
- 高频题型：证明题、计算题、解释题
- 扣分提醒：只写结论不给依据，通常拿不到高分
```

## 效果示例

> 场景：学生问“这章会不会考？”

```text
你：老师，这章会考吗？

大学老师.skill：
会，但不是整章都会考。

高优先级先看这三块：
1. 特征值与对角化：历年题出现频率高，且作业第 4 题和期末大题结构接近
2. 二次型标准化：老师上课反复强调“配方法”和“合同变换”的区别
3. 正定矩阵判别：助教批注里多次要求写出判别依据，不接受只写结论

如果你今晚只剩 2 小时：
先看特征值题型，再背二次型步骤，最后过一遍判别条件。
```

> 它不是普通笔记总结器，更像一个期末周随叫随到的老师 / 助教 / 学长混合体。

## 为什么不是普通复习资料整理器

| 普通总结器 | 大学老师.skill |
|------|------|
| 压缩内容 | 识别题型、重点、扣分点 |
| 会讲知识点 | 会模拟老师提问方式 |
| 输出通用笔记 | 输出 `persona.md / course.md / review_guide.md` |
| 容易一本正经瞎猜 | 明确标注低置信度和材料缺口 |

## 工作流程

```text
课程材料
(slides / exams / assignments / transcripts / chats / notes)
    ↓
文本抽取与清洗
    ↓
证据摘要与频率信号整理
    ↓
老师风格 / 课程结构 / 复习重点建模
    ↓
生成：
- persona.md
- course.md
- review_guide.md
```

## 设计原则

- 没有考试材料时，不假装押题
- 没有聊天和转写时，不强行模拟人格
- 材料越接近真实教学现场，结果越可信
- 优先输出高置信度重点，而不是看起来很完整的废话

## 当前状态

- ✅ 老师工作区脚手架
- ✅ `pdf / pptx / docx` 文本抽取
- ✅ 材料清单与证据摘要
- ✅ 单命令构建流程
- ✅ 严格校验，避免空模板伪装成可用结果
- ⏳ 扫描件 OCR 支持
- ⏳ 图片 / 音频输入链路
- ⏳ 更多课程模板与公开示例

## 支持的材料类型

> 当前版本优先支持可提取文本的课程资料。扫描件、图片和音频请先转换为文本后再导入。

| 类型 | 自动抽取正文 | 用途 |
|------|:------------:|------|
| `pdf` | ✅ | 提取知识结构、题型和说明 |
| `pptx` | ✅ | 提取标题、要点、重复强调内容 |
| `docx` | ✅ | 提取作业、讲义、课程通知 |
| `txt / md / csv / json / srt` | ✅ | 提取转写、聊天记录、结构化文本 |
| `ppt / key` | ⚠️ | 只收录，不自动解析正文 |
| 扫描版 PDF / 图片 / 音频 | ⚠️ | 只建议先转成文本再导入 |

## 快速开始

### 0. 安装依赖

```bash
python -m pip install -r requirements.txt
```

或者：

```bash
uv pip install -r requirements.txt
```

### 在 Skill 环境中调用

```text
Use $professor-skill to create a university professor skill from slides, exams, transcripts, and chat logs.
```

### 1. 初始化老师工作区

```bash
python tools/professor_writer.py --name "刘老师" --course "线性代数" --school "某大学" --department "数学学院"
```

这会自动创建：

- `materials/`
- `meta.json`
- `persona.md`
- `course.md`
- `review_guide.md`

### 2. 把资料放进 `materials/`

建议优先放这些：

- `materials/exams/`
- `materials/assignments/`
- `materials/transcripts/`
- `materials/chats/`
- `materials/slides/`
- `materials/syllabus/`

### 3. 一键构建

```bash
python tools/build_professor_outputs.py "<professor-dir>"
```

这个命令会自动完成：

- 文档抽取
- 材料清单生成
- 证据摘要生成
- `persona.md / course.md / review_guide.md` 构建
- 最终校验

如果你想先验证整个项目链路，直接运行：

```bash
python tools/smoke_test.py
```

## 安装

### Claude Code

> 仓库本身就是一个 skill 目录。安装后用 `$professor-skill` 调用。

```bash
# 安装到当前项目（在 git 仓库根目录执行）
mkdir -p .claude/skills
git clone https://github.com/CommitHu502Craft/professor-skill.git .claude/skills/professor-skill

# 或安装到全局（所有项目都能用）
git clone https://github.com/CommitHu502Craft/professor-skill.git ~/.claude/skills/professor-skill
```

## 核心能力

- 证据驱动的重点识别，而不是只压缩原文
- 老师风格与问法模拟，而不是通用答疑口吻
- 高频扣分点提炼，而不是只列知识点目录
- 材料不足时主动降级，而不是一本正经乱猜
- 输出 `persona.md / course.md / review_guide.md` 三份结构化产物

## 项目结构

```text
professor-skill/
├── SKILL.md
├── agents/openai.yaml
├── prompts/
├── references/
├── tools/
└── professors/
    └── example_linear-algebra-liu/
```

## 注意事项

- 原材料质量决定结果质量：`历年题 + 作业 + 讲课转写` 通常明显好于只有 PPT
- 没有考试材料时，复习资料会降级为低置信度总结，不会假装“精准押题”
- 没有聊天或转写时，老师人格部分会更保守
- 扫描件、图片和音频目前不做自动正文识别
- 公开发布或共享前，请确认你上传的材料不包含未授权内容

## 合规、版权与使用边界

- 本项目用于教学资料整理、学习辅助和风格模拟，不提供法律意见，也不保证任何特定用途下的合规性
- 使用者应自行确保其导入、处理、存储、分享和发布的材料具有合法来源，并已获得必要授权或符合适用的合理使用、教学使用或其他法律例外
- 请勿上传、分发或公开发布未经授权的课件、试卷、作业答案、教师内部材料、群聊记录、录音转写、个人信息或其他受版权、隐私权、肖像权、保密义务或学校规章限制的内容
- 请勿将本项目用于伪造教师身份、生成虚假官方通知、冒充助教答疑、规避课程管理规则、批量搬运受版权保护内容，或实施任何学术不端行为
- 生成结果可能包含不完整、过时、误判或推断性内容，不应被视为官方教学意见、评分标准、考试承诺或教师本人表达
- 仓库作者与贡献者不对用户导入内容的合法性、生成结果的准确性，或用户基于本项目实施的上传、传播、考试、教学、合规或侵权行为承担责任
- 如果相关学校、教师、平台或内容权利人要求删除特定材料、示例或衍生内容，请优先删除并停止继续传播

## 示例

完整示例老师目录见 [professors/example_linear-algebra-liu](./professors/example_linear-algebra-liu)。

## 免责声明

这是一个教学资料整理与风格模拟项目，按“现状”提供，不附带任何明示或默示担保。请仅在你确认材料来源合法、用途合规且不侵犯他人权利的前提下使用。
