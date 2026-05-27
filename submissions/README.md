# Submission pools

This directory holds the canonical, append-only record of submissions, with
**one JSON file per TA**: `submissions/<ta_slug>.json`. The TA slugs are listed
in [`../tas.yml`](../tas.yml).

## Conventions

- Each file is a JSON **array**. It is `[]` before any submissions arrive.
- A TA appends one object per confirmed submission. The object schema is:

  ```json
  {
    "id": "a1f3c9d2b7e4f8a0",
    "topic": "Provable convergence of Adam in convex settings",
    "submitted_at": "2026-06-10T14:23:00Z"
  }
  ```

  - `id` — a 16-character hex id from `scripts/assign_id.py`. Unique across
    **all** pools.
  - `topic` — the thesis topic title.
  - `submitted_at` — the UTC timestamp of confirmation (`...Z`).
- **Participant names are never stored here.** Only ids, topics, and
  timestamps are public.
- Files are append-only: never edit or remove an existing entry once the
  `post-deadline` tag is created.

## Adding a submission

A TA runs, from the repository root:

```
python scripts/assign_id.py --topic "Topic title here"
```

and pastes the printed JSON object into their own `submissions/<ta_slug>.json`,
then opens a pull request. Each TA owns (via `CODEOWNERS`) only their own pool
file.
