# Manual GitHub configuration

The repository contents are in version control, but several settings must be
applied by hand in the GitHub UI (or via the API). This file lists every such
step. Do them once, before creating the `pre-deadline` tag.

## 1. Repository basics

- **Visibility:** Public. (Settings → General → Danger Zone → Change visibility.)
- **Default branch:** `main`. (Settings → General → Default branch.)

## 2. Collaborators

(Settings → Collaborators and teams.)

- Add **Carlos** (`<<TODO: @carlos-github-handle>>`) as **Admin**.
- Add **each TA** with **Write** access. The TA slugs and names are listed in
  [`tas.yml`](tas.yml).

## 3. Branch protection on `main`

(Settings → Branches → Add branch ruleset / protection rule for `main`.)

- [x] Require a pull request before merging.
- [x] Require at least **one approving review**.
- [x] Require **status checks** to pass before merging — select the
      `verify` workflow (from `.github/workflows/verify.yml`).
- [x] Require **signed commits**.
- [x] **Do not allow force pushes**.
- [x] **Do not allow branch deletion**.

`CODEOWNERS` (in `.github/`) is enforced automatically when "Require review
from Code Owners" is enabled — turn that on as well.

## 4. Tag protection

(Settings → Tags → New rule, or a repository ruleset targeting tags.)

Protect the three release tags so they cannot be moved or deleted once pushed:

- `pre-deadline`
- `post-deadline`
- `draw`

A pattern such as `pre-deadline`, `post-deadline`, `draw` (or a single ruleset
matching all three) is sufficient. Restrict tag creation/deletion to admins.

## 5. Signing keys

Every collaborator signs their commits, and the three release tags are signed.

1. Each collaborator registers a **GPG** or **SSH signing key** on their GitHub
   account (Settings → SSH and GPG keys).
2. Each configures local signing, e.g. for SSH:

   ```bash
   git config gpg.format ssh
   git config user.signingkey ~/.ssh/id_ed25519.pub
   git config commit.gpgsign true
   git config tag.gpgsign true
   ```

3. The three release tags are created with `git tag -s` and pushed:

   ```bash
   git tag -s pre-deadline  -m "Pre-deadline commitment: script, tooling, drand round"
   git tag -s post-deadline -m "Post-deadline commitment: frozen submissions"
   git tag -s draw          -m "Draw: beacon value and computed result"
   git push origin pre-deadline post-deadline draw
   ```

## 6. GitHub Pages

(Settings → Pages.)

- **Source:** Deploy from a branch.
- **Branch:** `main`, folder **`/docs`**.
- After the first build, note the published URL and fill the
  `<<TODO: ...github.io...>>` placeholders in `README.md` and `docs/index.md`.

## 7. Release-tag timeline (operational checklist)

1. Fill TA slugs/names in `tas.yml`; create `submissions/<slug>.json` as `[]`
   and `docs/tas/<slug>.md` for each; fill `CODEOWNERS`.
2. Set the dates in `PROCEDURE.md` / `docs/index.md` and the drand round number.
3. Confirm `python verify_draw.py` exits 0 (placeholder beacon → "nothing to
   verify yet") and `pytest` passes.
4. Tag **`pre-deadline`**. The repo ships placeholder `beacon.json` and
   `result.json` (each marked `"placeholder": true`) only to document their
   final shape; they hold **no draw data** yet. For strict "no draw data at
   pre-deadline" provenance you may `git rm` both placeholders before tagging —
   `verify_draw.py` and the `verify` workflow handle their absence too. Real
   `beacon.json`/`result.json` are committed only at the `draw` tag.
5. Open submissions; TAs append entries via PRs through the window.
6. At the deadline, freeze and tag **`post-deadline`**.
7. After the drand round publishes:
   `python scripts/fetch_beacon.py --round <N> --output beacon.json`,
   then `python selection.py`, then `python verify_draw.py`.
8. Commit `beacon.json` and `result.json`; tag **`draw`**.
