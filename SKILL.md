---
name: professor-skill
description: Professor Skill creates a university-course skill from slides, syllabi, exams, transcripts, notes, and chat logs. Use when the user wants a review-first, exam-focused, teacher-style skill that models how a professor highlights topics, writes questions, and deducts points.
---

# Professor Skill

Use this skill when the user wants to build a `大学老师.skill` / `Professor Skill` from real course materials.

The output must stay useful first and funny second:

- Useful enough to help with review, Q&A, and exam prep
- Distinct enough to feel like this specific professor
- Meme-friendly enough that the result is screenshot-worthy

## Core Model

Always separate the professor into two engines:

1. `Course Brain`
   Extract the actual course structure:
   - key topics
   - repeated concepts
   - likely exam scope
   - common question types
   - grading preferences
   - typical mistakes

2. `Teacher Persona`
   Extract the professor's delivery style:
   - catchphrases
   - explanation rhythm
   - patience level
   - response habits
   - classroom humor or sarcasm
   - how they emphasize or downplay topics

The final output should merge both:
`Teacher Persona decides tone. Course Brain decides substance.`

## Workflow

### Step 1: Collect minimum intake

Ask only for the smallest set of details needed to start:

- professor name
- school or department if available
- course name
- what materials the user has
- one-line impression of the professor

If the user already provided files or context, do not repeat questions.

If there is no professor workspace yet, initialize one first:

```text
python ${CLAUDE_SKILL_DIR}/tools/professor_writer.py --name "<teacher>" --course "<course>" --school "<school>" --department "<department>"
```

This creates:

- `meta.json`
- `persona.md`
- `course.md`
- `review_guide.md`
- `materials/` source folders
- `materials_manifest.md`
- `source_brief.md`
- `workflow.md`

### Step 2: Sort material by signal strength

Rank sources before extracting:

1. exams, quizzes, assignments
2. lecture transcripts or lecture notes
3. slides and syllabus
4. group chats, Q&A logs, office-hour notes
5. professor bio, homepage, publication summaries

Use higher-signal sources to determine exam and review content.
Use lower-signal sources to sharpen persona and identity.

When source files have been placed into `materials/`, always run the single-command build pipeline:

```text
python ${CLAUDE_SKILL_DIR}/tools/build_professor_outputs.py "<professor-dir>"
```

This pipeline must:

- extract parseable text from `pdf`, `pptx`, `docx`, and text files into `exports/extracted/`
- refresh `materials_manifest.md`
- refresh `source_brief.md`
- generate `persona.md`, `course.md`, and `review_guide.md`
- validate the workspace before claiming it is ready

Read `materials_manifest.md`, `source_brief.md`, and the highest-signal extracted files first.

If `${CLAUDE_SKILL_DIR}` is unavailable in the runtime, resolve tool paths relative to the skill root directory rather than the caller's working directory.

### Step 3: Build three artifacts

Always generate these three files or sections:

- `persona.md`
- `course.md`
- `review_guide.md`

If the user explicitly wants it, also generate:

- mock exam
- likely key points
- oral-style explanation notes
- teacher-style chat replies

When updating existing artifacts:

- preserve strong evidence already reflected in the files
- replace `[fill me]` placeholders with concrete content
- keep unsupported claims marked as low-confidence inference

### Step 3.5: Refuse fake confidence

If `validate_professor.py` warns that there are no exams, no transcripts, or no indexed sources, you should still help, but explicitly lower confidence and explain which parts are inferred.

### Step 4: Keep the humor disciplined

Humor should come from recognition, not random jokes.

Prefer these patterns:

- "这题上课讲过" energy
- vague but familiar teacher phrasing
- passive-aggressive reminders
- overlong slides, underspecified key points
- exam warnings that feel suspiciously real

Avoid:

- insulting the professor
- fabricated misconduct
- fake official notices
- humor that reduces usefulness

## Legal And Content Guardrails

- Treat imported materials as potentially sensitive by default.
- Do not encourage users to upload or redistribute content they do not have the right to use.
- Do not present generated text as an official notice, grading rule, or statement from the real professor.
- Do not fabricate private facts, misconduct claims, or internal school policies.
- If the user appears to be using private chats, recordings, unpublished materials, or other potentially restricted content without permission, warn briefly and continue only with clearly lawful, minimal assistance.
- When uncertainty exists, prefer summarization, study guidance, and low-confidence caveats over imitation that could be mistaken for the real person.

## Output Requirements

### `persona.md`

Include:

- identity summary
- catchphrases
- speaking style
- how the professor answers vague questions
- how they react to lazy students
- how they signal importance without saying "this will be on the exam"
- boundaries and correction notes

### `course.md`

Include:

- course overview
- chapter map
- likely core topics
- recurring concepts
- known exam styles
- grading preferences or answer expectations
- high-risk confusion points

### `review_guide.md`

This is the student-facing compressed artifact.

It should:

- prioritize likely exam content
- reduce fluff
- explain what to memorize versus what to understand
- include "teacher may ask this way" examples
- include a short "last-night-before-exam" section

## Style Rules

- Respond in the user's language. If the user is writing in Chinese, stay in Chinese.
- Be concrete. Replace generic praise with specific behavioral patterns.
- Do not present guesses as facts. Mark weak inferences clearly.
- If the material is thin, say so and still produce a lightweight version.
- Keep outputs organized and readable. Students should be able to skim them fast.

## Internet Flavor

If the user wants stronger virality or "网感", lean into these angles while staying accurate:

- "老师说不考"
- "PPT 讲了很多，重点像没讲"
- "群里回复比题目更难懂"
- "你以为是人格模拟，实际上是期末自救"

The project should feel like a real tool wrapped in a shareable joke, not a joke wrapped around an empty shell.

## Bundled Resources

- Prompt templates live in `prompts/`
- Material schema guidance lives in `references/materials-schema.md`
- GitHub README positioning guidance lives in `references/github-readme-design.md`
- Local scaffolding/build scripts live in `tools/`
- Example professor data lives in `professors/example_linear-algebra-liu/`
