---
name: doc-opt
description: "Tersely professionalize documents: strip filler, use mermaid/SVG diagrams, make citations jumpable."
disable-model-invocation: true
argument-hint: "Files or paths to optimize"
---

# Doc Opt

Optimize named markdown documents in place. Default targets: `.md` / `.mdx`. Other formats only when named.

## Contract

- Touch the named files; never sweep the repo.
- Compression removes redundancy, never facts.
- Code fences, frontmatter, commands, and quoted output stay byte-identical.
- Structural moves (delete a section, reorder, merge diagrams) get a plan first, edits second.
- End with a change report: files, change categories, `待补充来源`, self-check evidence.

## Style (L2 by default)

L1 strips filler only; L3 goes telegraphic. Move up or down only when the user names the level.

- Delete words that carry no information: filler, hedging, throat-clearing.
- Short declarative sentences. Active voice. Verbs over nominalizations.
- Lists and tables when the content enumerates.
- Keep technical terms exact; keep headings unless the heading is the problem.

Filler to cut on sight:

| ZH | EN |
| --- | --- |
| 其实、值得注意的是、让我们来看看、不得不说、说白了、众所周知 | basically, actually, of course, it's worth noting, let's dive in |

`just` and `其实` get judged per sentence: they stay only when literal ("only") or when they mark a real contrast.

## Diagrams

Default: mermaid. Match the type to the relation: flowchart, sequence, state, class, ER, gantt, pie.

SVG covers what mermaid cannot express or where layout needs control — annotated architecture, custom positioning. Inline SVG for small diagrams; a sibling `.svg` file plus a link for large or reused ones.

ASCII art and image diagrams appear only when the user explicitly asks. Existing ASCII diagrams convert to mermaid/SVG when the mapping is lossless; ambiguous semantics get a question first. Screenshots stay: add a caption and a jumpable citation.

## Citations

A bare number (`[1]`) is not a citation. Every reference is jumpable or self-contained:

| Target | Form |
| --- | --- |
| Section of the same document | `[label](#anchor)` |
| File elsewhere in the repo | `[label](relative/path.md#anchor)` |
| External source | `[label](https://full-url)` |

Without a stable target, carry the source inside the sentence ("per the MCP spec, ..."). A source that cannot be identified goes into a `待补充来源` list at the document end and into the change report.

## Workflow

1. Read the targets whole. Mark frontmatter and code that must not move.
2. Plan structural changes; wait for confirmation.
3. Rewrite: style, then diagrams, then citations.
4. Run the self-check.
5. Report files, change categories, `待补充来源`, self-check evidence.

## Self-check

Run before reporting; put evidence in the report. Substitute the target paths for `<files>`; ignore hits inside code fences.

```bash
# filler survivors — expect no hits
rg -n "其实|值得注意的是|让我们来看看|说白了|basically|actually|of course|worth noting" <files>

# bare numeric citations — expect no hits
rg -n '\[\d+\]' <files>

# ASCII diagrams — expect no hits unless the user asked for them
rg -n '[┌┐└┘├┤│─]|\+--' <files>

# mermaid fences — count them; each needs a declaration line and a closing fence
rg -n '^```mermaid' <files>
```

`EXAMPLES.md` holds before/after pairs: style (ZH/EN), ASCII→mermaid, citation forms, mermaid vs SVG selection.
