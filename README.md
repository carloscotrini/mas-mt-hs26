# Master thesis selection — <<TODO: course name>>

This repository runs the master thesis selection for Carlos's course. Up to six
theses are awarded this round, each co-supervised by Carlos and one teaching
assistant (TA). Because demand usually exceeds the number of slots, places are
filled by a **publicly verifiable random draw**: nobody — not the TAs, not
Carlos — can influence or predict who is selected, and anyone can re-check the
result themselves.

Everything needed to audit the process lives in this repository, which is
public and append-only.

## How the procedure works (three phases)

The fairness of the draw rests on three time-stamped, signed Git tags. Each one
"locks in" a commitment **before** the information that could be used to game it
becomes available.

1. **`pre-deadline`** — created *before* submissions open. It fixes the draw
   script (`selection.py`), the verification tooling, and the exact drand round
   number that will supply the randomness. At this point the random value does
   not yet exist, so the rules are fixed without knowing the outcome.
2. **`post-deadline`** — created *after* submissions close but *before* the
   chosen drand round is published. It fixes the full list of submissions. At
   this point the participants are fixed without knowing the random value.
3. **`draw`** — created *after* the drand round is published. It records the
   beacon value and the computed `result.json`. Now both halves are public and
   the result is fully determined.

Because the submissions are frozen before the randomness exists, and the
randomness is fixed by an external beacon nobody controls, the outcome cannot
be steered.

## How to submit

See **[PROCEDURE.md](PROCEDURE.md)** for the full rules, and the project
website (GitHub Pages) for the TA profiles and offered topics:

> <<TODO: https://<org-or-user>.github.io/mas-mt-hs26/ >>

## How to verify the draw

After the `draw` tag is published, check out that tag and run a single command:

```bash
pip install -r requirements.txt
python verify_draw.py
```

It recomputes the ranking from the frozen submissions and beacon, compares it
to the published `result.json`, and verifies the beacon's cryptographic
signature. It exits `0` only if everything matches.

## About the randomness

The random seed comes from [drand](https://drand.love), a public distributed
randomness beacon operated by the League of Entropy; no single party can
predict or control its output.
