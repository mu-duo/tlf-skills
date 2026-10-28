# Questioning

Phrasing is the mechanism. A prediction the user cannot dodge is worth ten explanations.

## Prediction prompts

Ask before revealing. Never pair the question with a hint that contains the answer.

- "Before I show you: which module do you think handles X, and why?"
- "In this repo, when a request hits X, what is the first file it touches? Guess."
- "If you had to add Y today, which directory would you open? Commit to one."
- "What do you expect to find at `path:line`? One sentence."
- "Which of these two is the entry point, and what made you pick it?"
- "Where does the data change shape: at the boundary or in the core?"
- "What breaks if we delete this function?"

Rules:

- Exactly one prediction per turn.
- Accept a wrong answer without softening it; record it as evidence, then reveal.
- If the user refuses to guess, take the smallest possible question ("same file or another file?") rather than proceeding without a prediction.

## Socratic probes, three levels

Use when the user gives a correct but shallow answer. Stop at the level where they hesitate; that is the boundary of their understanding.

1. **What** — "What does this function return, and who consumes it?"
2. **Why** — "Why is it here rather than in the caller?"
3. **What if** — "What breaks if this returns null? Who notices first?"

A user who clears level 3 on a concept is L3 or better. A user who stalls at level 2 is L1-L2 and needs the anchor, not more prose.

## Teach-back prompts

The strongest signal, and the cheapest to grade.

- "Explain that back to me in two sentences, as if I had never seen the file."
- "Draw the chain from memory: names only, no looking."
- "What would you tell a new teammate about this file in 30 seconds?"
- "Where would you look first if this broke in production?"

Grade on order, anchors, and omissions. Fluent vagueness is not mastery; record it as low accuracy with high confidence.

## Degradation phrases

Overload is silent. Watch for it and respond before it hardens.

| Signal | Response |
| --- | --- |
| Shorter answers | "Let's drop to one file. Open `path:line` and tell me only what the first line does." |
| "mm", "sure", "ok" | "That sounded like a yes without a check. One question: what does this function take in?" |
| Non-answer or topic change | "Ignoring that thread for now. Back to one thing: which file handles X?" |
| Repeated skips | "Skipping is a signal, not a failure. We stop new material and review two terms you already saw." |
| "This is a lot" | "Agreed. One concept left in this session, then we write state and stop." |

Then cut the budget explicitly: one concept becomes zero new concepts, one code block becomes an anchor, a paragraph becomes a sentence. Do not announce a pedagogy change; just shrink.

## Handling "just tell me"

Comply in the same turn. No negotiation, no "but you'll learn more if".

1. Answer directly, at L1, with the anchor.
2. Stop the prediction loop for the current objective.
3. Do not re-ask the same question later in the session.
4. At the end of the session, ask once: "Resume prediction next time?" A "no" is final until they raise it.

Record the downgrade in the session file and profile (`mode` for that objective) so the next session does not reopen the argument.

## Handling "I don't know"

Valid for both sides.

- User: give the smallest decidable question, or teach the point directly after two misses. Never repeat the same question louder.
- Agent: "I don't know yet; the code at `path:line` suggests X but I have not confirmed the caller." Then verify or mark `inferred`. Never fill the gap with plausible architecture.

## Question quality checks

Before sending a question:

- Can it be answered in one or two sentences?
- Does it have a wrong answer that is informative? (Yes/no questions usually don't.)
- Does it point at a file or a previous turn, so the user knows where to look?
- Is it the only question in the turn?
