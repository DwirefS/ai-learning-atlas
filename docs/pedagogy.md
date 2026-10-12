# Pedagogy: how an Atlas lesson is built (v8)

The Atlas started as a curated map of external resources. In v8 it also **teaches on-site**: each of the 129 subjects is a full lesson. Curated resources are still there, now annotated, but they come after the lesson instead of replacing it.

This note covers what we took from six well-known learning platforms and how each idea shows up in the Atlas. The descriptions are of publicly visible course structure, not of any internal research.

## What we studied

| Platform | Pattern we borrowed | Where it shows up in the Atlas |
|---|---|---|
| **Khan Academy** ([khanacademy.org](https://www.khanacademy.org/)) | Course → unit → lesson hierarchy. Short explanations followed by practice. A **mastery system** with visible levels (Attempted / Familiar / Proficient / Mastered) earned through practice, not through viewing. | Home **course map** (track → level → lesson tiles). Each lesson shows a mastery level: **Familiar** (opened, or ≥ 1/3 of the quiz correct), **Proficient** (≥ 80% correct), **Mastered** (100% correct plus every subtopic ticked). Tiles are colored by mastery. |
| **DeepLearning.AI** short courses ([deeplearning.ai](https://www.deeplearning.ai/short-courses/)) | Short, focused lessons on one tool or technique, each paired with runnable code next to the explanation. | One subject = one focused lesson with a 2–5 minute reading time. Every lesson has a worked example, and many have a code snippet or an interactive explainer right beside the text. |
| **Hugging Face courses** ([huggingface.co/learn](https://huggingface.co/learn)) | Chapters split into sections, with code inline and a quiz closing each chapter. Open and free. | Lessons split into fixed sections. Every lesson ends with a quiz that explains each answer. Content is CC BY 4.0 and works offline. |
| **fast.ai** Practical Deep Learning ([course.fast.ai](https://course.fast.ai/)) | **Top-down, code-first** teaching: see the whole thing working first, then dig into the parts ("play the whole game"). | Lessons open with **Intuition** (the whole picture in plain words). Then comes **How it works** (the mechanism step by step), then a concrete worked example, and only then the deeper topics and subtopics. |
| **Google Machine Learning Crash Course** ([developers.google.com/machine-learning/crash-course](https://developers.google.com/machine-learning/crash-course)) | Interactive visualizations and exercises where you change parameters and watch the effect. Short knowledge checks. | 11 dependency-free **interactive explainers** (sliders, inputs and buttons that drive live SVG), embedded in the lessons that use them and collected in the **Explainers** playground. |
| **Microsoft Learn** ([learn.microsoft.com/training](https://learn.microsoft.com/training/)) | Learning paths → modules → units, with a **knowledge check** at the end of each module. Visible duration estimates, and XP plus achievements for motivation. | Untimed **learning paths** and **role paths** made of lessons. Each lesson shows a **reading time** (words ÷ 200). Quizzes act as knowledge checks. **XP, ranks and badges** are kept from earlier versions and now tie to mastery. |

## The lesson template

Every lesson has the same order, so learners always know where they are:

1. **Why it matters**: one sentence of motivation.
2. **💡 Intuition**: the big picture in everyday language, with no jargon assumed (fast.ai top-down).
3. **⚙️ How it works**: the mechanism as a short paragraph plus numbered steps.
4. **🗺️ Diagram**: one Mermaid diagram per lesson in a consistent light, friendly theme. Each diagram has written alt text, used as the figure caption and as `aria-label`.
5. **🧪 Interactive explainer** (where relevant): a live simulation to experiment with (Google MLCC).
6. **🧮 Worked example**: concrete numbers or a code snippet. All arithmetic is hand-checked.
7. **📚 Topics**: every topic gets a solid paragraph. Key subtopics get a 1–3 sentence explanation (at least two per topic), each with a checkbox for progress.
8. **⚠️ Common mistakes**: at least three, because naming the trap is half of avoiding it.
9. **🏢 In the enterprise**: a realistic, illustrative scenario of how the idea is used at work. These are composites, not claims about named companies.
10. **✅ Key takeaways**: at least three lines to remember.
11. **📝 Quiz**: at least three questions, each answer explained whether right or wrong (Khan, Hugging Face, Microsoft Learn knowledge checks). Quiz results drive mastery.
12. **🔗 Annotated resources**: each link says *why* to read it and gives its **level** (Intro / Intermediate / Advanced / Reference).
13. **Hands-on lab, deep-dive concept cards, and prev/next navigation.**

The build (`scripts/build_v8.py`) **enforces this bar** for all 129 lessons and fails if any lesson is short:

- Intuition ≥ 40 words.
- ≥ 3 how-steps.
- Example ≥ 40 words.
- ≥ 3 mistakes.
- Enterprise ≥ 25 words.
- ≥ 3 takeaways.
- A diagram with alt text.
- ≥ 3 quiz questions, each with an explanation.
- Every resource has a why and a level.
- Every topic has ≥ 60 words and ≥ 2 subtopic explanations.

## Accuracy rules

- Worked-example math is recomputed by hand. Examples use round, clearly assumed inputs ("at $3 per 1M tokens"), not quoted vendor prices.
- Product features are described only at the level of public documentation. Regulatory dates point readers to the official text, because timelines have been amended.
- Enterprise examples are illustrative composites and say what they assume.
- Resource annotations come from the type of source (paper, spec, official docs, course, practitioner blog), so no summary claims anything a page might not say.
- Interactive explainers label their simplifications. For example, the tokenizer is "illustrative, not a real BPE", the attention demo uses "toy vectors" and RAG uses "lexical scoring".

## Accessibility and UX

- Deep-linkable hash routes: `#/`, `#/track/<id>`, `#/lesson/<id>`, `#/roles`, `#/projects`, `#/paths`, `#/capstones`, `#/concepts`, `#/glossary`, `#/playground`.
- Skip link, visible focus rings, native form controls (keyboard-operable), `aria-live` result regions in quizzes and explainers, alt text for every diagram, and reduced-motion support.
- Mobile reading typography: about 17px body and 1.7 line-height, with no horizontal overflow (checked in headless Chrome at 390px wide).
- Fully static and offline (Mermaid is bundled), so it is ready for GitHub Pages.
