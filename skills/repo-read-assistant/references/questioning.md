# Questioning

Conversation verifies a model the user has already read. It does not deliver the model. Every prompt below assumes a brief was handed over first.

## Say it plainly

The user has not read this skill. Its vocabulary is for you, not for them.

| Internal | Say instead |
| --- | --- |
| brief, layer | "the page I wrote for you" / "this pass" |
| model check | "a few questions" |
| prediction | "before you look: what do you expect?" |
| elaboration vs disclosure | nothing — never name the method |
| budget | nothing — just be brief |
| spine, chain | "the path a request takes" |
| L0-L4 | nothing — never grade out loud |
| anchor | "open `path:line`" |

Rules:

- One item per question. A four-way matching task is an exam, not a check.
- Ask about something the user just read, said, or asked about.
- Offer the exit every time: "or say you don't know."
- If the user asks a direct question, answer it first. Never hold an answer hostage to a check.
- On first contact, say once, in one sentence: "Read this, then I'll ask a few questions — wrong answers find the gaps." Then never name the method again.

## One question to hold while reading

Before handing over a brief, give exactly one question. It is not answered in chat; the user holds it while reading and reports afterward. With zero model, a prediction produces only "I don't know" — so do not ask the user to predict content they have not read.

Good questions point at the layer, not at a detail:

- "While you read, keep asking: which step in the loop would you change first, and what would it disturb?"
- "Hold this: where does a request change shape, and which module owns that change?"
- "As you read: why is this split into two services instead of one?"
- "Keep one question: what would break first if the queue stopped draining?"

Rules:

- Exactly one question, one sentence.
- It must be answerable from the brief, not from prior knowledge.
- Do not gate the file on an answer. Hand over the path and the question together.
- If the user answers it immediately, acknowledge briefly and let them read; the real check comes after.

## Model checks after reading

Three questions, in this order. They test the model, not recall of names.

**1. Locate.** "For <feature>, where would you start, and what are the two files after that?" Wrong path means the map layer did not land, regardless of how well they explain the idea.

**2. Predict impact.** "If we changed <X> here, what else moves, and who notices first?" This tests relations: a right-facts, wrong-relations model fails here and caps at L2.

**3. Explain why — and why not.** "Why is it built this way rather than <the obvious alternative>, and what does that choice cost?" The second half is the real question. A design choice with no cost is a slogan.

Phrasing:

- "Without the page: what are the steps a typical task goes through?"
- "Which entity connects <A> and <B>, and what does it carry between them?"
- "What would you have to touch to add <Y>, and what might break silently?"
- "What did the designer decide not to support here, and what does that buy?"

Rules:

- Ask all three in one message, numbered. They are one check, not three turns.
- Accept a wrong answer without softening it. Record it, then correct.
- If all three are right, record evidence and move on; do not invent a fourth.
- If the first two fail, stop. The model is not there; correct the brief before asking more.

## Teach-back and whiteboard prompts

The strongest signal, and the cheapest to grade.

- "Explain that back to me in two sentences, as if I had never seen the repo."
- "Draw the model from memory: one sentence, the loop, the nouns, the seams."
- "What would you tell a new teammate in 30 seconds?"
- "Redraw the loop on a blank page, then mark where you are least sure."

Grade on order, relations, and omissions. Fluent vagueness is not mastery; record it as low accuracy with high confidence. A drawing with the right boxes and wrong arrows is L2 at most.

## Overload handling

Brief overload and chat overload are different problems.

| Signal | Likely cause | Response |
| --- | --- | --- |
| "This is a lot" after reading | brief is too dense for its layer | split it, or move detail down a layer; do not shorten prose |
| Stops mid-brief | cap exceeded in spirit | cut the brief to its layer and say what moved down |
| Short or "mm" replies in chat | chat turn too long | shrink to one question, <=150 words |
| Non-answer or topic change | check is above the model | drop to a locate question |
| Repeated skips | user is done for the day | stop, write state, resume next sitting |

Never respond to overload by compressing the brief into prose. Density is a layer problem: move the detail to `02-structure.md` or `03-operations.md`, or split the layer.

## Handling "just tell me"

Comply in the same turn. No negotiation.

1. Answer directly, referencing the brief's anchor.
2. Stop checks for the current brief.
3. Do not re-ask the same question later in the session.
4. At the end of the session, ask once: "Want the questions next time?" A "no" is final until they raise it.

Record the downgrade in the session note and profile, so the next session does not reopen the argument.

## Handling "I don't know"

Valid for both sides.

- User: give the smallest decidable question ("same file or another file?"), or point at the brief section that answers it. After two misses on one point, correct the brief directly.
- Agent: "I don't know yet; the code at `path:line` suggests X but I have not confirmed the caller." Then verify or mark `inferred`. Never fill the gap with plausible architecture.

## Question quality checks

Before sending a question:

- Can it be answered in one or two sentences?
- Does it have a wrong answer that is informative? (Yes/no usually does not.)
- Does it point at a brief section or a file, so the user knows where to look?
- Is it the only question in the turn?
- Does it respect the cap: three questions per brief check, one per chat turn?
