# Topic taxonomy policy

Use the smallest durable taxonomy that makes the paper list easier to navigate.

## Decision order

1. **Existing topic:** Use an existing file when its title or established contents cover the paper's primary research question. Prefer this even if the file is broad.
2. **Existing subsection:** Use an existing heading when possible. Propose a new subsection only when at least three repository papers form a recognizable method, task, or system branch inside that topic.
3. **New topic proposal:** Propose a new file only when all required gates below pass.
4. **Misc:** Use `topics/misc.md` for a relevant isolated item that has no durable cluster. Do not use it to avoid making a real taxonomy decision.

## Required gates for a new topic

A proposal must satisfy all of these:

- **Coherent scope:** It names a research problem, method family, embodiment, or evaluation area—not a single paper, model, lab, venue, year, or fashionable phrase.
- **Repository density:** At least five papers already present in README or the current batch fit the scope. Three may suffice only for a clearly central and fast-growing Robotics direction.
- **Independent evidence:** Seed papers come from at least two independent research groups.
- **Distinct navigation value:** The papers cannot be represented cleanly as one subsection of an existing topic, and the proposed file would make discovery materially easier.
- **Durability:** The name and scope are likely to remain useful for at least a year.
- **Seedable structure:** At least three seed papers can be added immediately, with sensible ordering or two meaningful subsections when applicable.

If any gate is uncertain, record a watchlist proposal in the classification log and ask the user rather than creating the topic.

## Overlap and granularity

- Assign one primary topic by default and no more than two topics total.
- A second topic must expose a different useful axis, such as `Humanoid` plus `Robot Foundation Models`; keyword overlap alone is insufficient.
- Prefer a subsection over a new file for a narrow method family inside a mature topic.
- Do not merge, rename, split, or delete existing topic files during routine classification.
- Treat inconsistent historical taxonomy as context, not permission for a broad cleanup.

## Proposal contract

For each proposed topic, provide:

- proposed filename and display name;
- one-sentence inclusion scope and explicit exclusions;
- related existing topics and why they are insufficient;
- at least three named seed papers and the total repository-paper count found;
- suggested initial headings, if any;
- recommendation: `create`, `watch`, or `use existing subsection`.

Only after explicit approval may the agent create `topics/<slug>.md`, seed it with approved papers, and add it to the README Topics index.
