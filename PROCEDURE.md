# Selection procedure

This document is the authoritative specification of how master thesis places
are awarded in <<TODO: course name>>. It is written for participants with
BSc-level Python knowledge and **no cryptographic background**.

> The same text is published on the project website at
> [`docs/procedure.md`](docs/procedure.md); the two are kept identical.

## 1. Overview

Up to six theses are awarded, each co-supervised by Carlos and one teaching
assistant (TA). Each TA collects submissions independently and runs an
independent draw over their own pool. The draws share one public random seed
but are otherwise separate.

## 2. Submission window

- **Opens:** `<<TODO: open date/time, with timezone>>`
- **Closes:** `<<TODO: close date/time, with timezone>>`

Submissions received outside this window are not considered.

## 3. How to submit

There are two paths. Choose exactly one.

- **Path A — pick an offered topic.** Browse the TA profiles and their offered
  topics on the project website. Email the relevant TA stating the topic you
  want.
- **Path B — propose your own idea.** Email the TA whose research area fits
  your idea with a short description (a few sentences is enough).

### One email per participant

Each participant may enter **only one pool** with **one submission**. Do not
email several TAs. If multiple submissions from the same participant are
detected, all of them are voided.

## 4. Confirmations

After you submit you receive **two** confirmations:

1. **Receipt** — the TA acknowledges your email was received.
2. **Pool entry** — the TA confirms you are in the pool and tells you your
   **assigned id** (a 16-character hex string). From this point your submission
   appears, by id and topic only, in the public list at
   [`submissions/`](submissions/) and on the website. Your name is never
   published.

If you do not receive the second confirmation before the deadline, your
submission is not in the pool — follow up with the TA.

## 5. The draw

After the deadline:

1. Each TA's pool is frozen and committed under the `post-deadline` tag.
2. A pre-announced public random value (see below) is published by drand.
3. `selection.py` computes, for every submission, a score and ranks each pool.
   Rank 1 is the selected participant; ranks 2, 3, … form the ordered backup
   list.

### How the randomness is turned into a ranking (no crypto needed)

For each submission the script computes a number called a **score**:

```python
score = sha256(f"{beacon_value}|{ta}|{submission_id}")
```

- `beacon_value` is the single public random string from drand (the same for
  everyone).
- `ta` is the TA's slug; `submission_id` is your assigned id.
- `sha256` is a standard hash function: it turns its input into a 64-character
  hexadecimal string that is effectively impossible to predict or steer.

Within each pool, submissions are sorted by their score from smallest to
largest. The smallest score wins (rank 1). Because the random `beacon_value` is
unknown when ids are assigned, and unknown to everyone until drand publishes it,
every submission has an equal `1/n` chance of being rank 1, where `n` is the
size of that pool. (This fairness property is tested in
[`tests/test_selection.py`](tests/test_selection.py).)

### Where the random value comes from

The random value is one **round** of [drand](https://drand.love), a public
randomness beacon run by a group of independent organisations (the League of
Entropy). Each round produces a value that no single party can predict or
control, together with a cryptographic signature proving it is genuine.

- **Chosen drand round:** `<<TODO: round number>>` — chosen so that it is
  published roughly five minutes after the submission deadline.

Because the round number is committed in the `pre-deadline` tag *before*
submissions open, and the round's value only exists *after* the deadline,
nobody can know the outcome while submissions are still open.

## 6. Acceptance and the 48-hour window

The rank-1 participant in each pool is offered the place. They have **48 hours**
from notification to accept or decline.

- **Accept:** the place is theirs.
- **Decline or no response within 48 hours:** the offer rolls down to the next
  rank.

## 7. Roll-down policy for declined slots

If a slot is declined or expires, it passes to the next-ranked submission in
the **same** TA's pool (rank 2, then rank 3, and so on), each with its own
48-hour window. Slots never move between TAs. If a pool is exhausted, the TA may
re-open or leave the slot unfilled at their discretion.

## 8. Verifiability

Anyone can audit the draw after the `draw` tag is published:

```bash
pip install -r requirements.txt
python verify_draw.py
```

This recomputes the ranking from the frozen submissions and beacon, checks it
against the published `result.json`, and verifies the drand signature. It is
fully deterministic and works offline once `beacon.json` is present.
