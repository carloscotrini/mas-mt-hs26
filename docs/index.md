---
title: Home
nav_order: 1
---

# Master thesis selection — <<TODO: course name>>

Course identifier: `<<TODO: course code / identifier>>`

Up to six master theses are awarded this round in <<TODO: course name>>, each
co-supervised by Carlos and one teaching assistant (TA). Places are filled by a
**publicly verifiable random draw** powered by the
[drand](https://drand.love) randomness beacon. Nobody can predict or influence
who is selected, and anyone can re-check the result.

## Key dates

- **Submissions open:** `<<TODO: open date/time, with timezone>>`
- **Submissions close:** `<<TODO: close date/time, with timezone>>`
- **Draw (drand round published):** shortly after the deadline.

## Start here

- **[How to submit and how the draw works](procedure.md)** — the full procedure.
- **[Teaching assistants and offered topics](#teaching-assistants)** — see below.
- **[Live submissions](submissions.md)** — the public pool, by id and topic.

## Teaching assistants

Each TA supervises one thesis and runs an independent draw over their own pool.

<!-- <<TODO: one link per TA; keep in sync with tas.yml and docs/tas/*.md>> -->
- [Winston](tas/winston.md)
- [Alice](tas/alice.md)

## Verify the draw yourself

After the draw, check out the `draw` tag and run:

```bash
pip install -r requirements.txt
python verify_draw.py
```
