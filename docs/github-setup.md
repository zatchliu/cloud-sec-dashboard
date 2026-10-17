# GitHub and git signing (you do these)

The agent does not change GitHub account settings. Complete this checklist so
Phase 0 exit criteria can pass: **CI green on a PR**, **`main` protected**,
**hooks block a fake secret**.

## 1. SSH commit signing

GitHub already uses SSH for `git push`. Signing with the same key type avoids
GPG agent issues on WSL.

1. If you do not have an ed25519 key:

   ```bash
   ssh-keygen -t ed25519 -C "your-github-email@example.com"
   ```

2. Copy the **public** key (`~/.ssh/id_ed25519.pub`).
3. GitHub → **Settings → SSH and GPG keys**:
   - **New SSH key** (Authentication key) if not already added.
   - **New SSH key** again, type **Signing Key**, paste the same public key.
4. Enable signing in git:

   ```bash
   git config --global gpg.format ssh
   git config --global user.signingkey ~/.ssh/id_ed25519.pub
   git config --global commit.gpgsign true
   ```

5. Confirm a commit shows **Verified** on GitHub after you push.

Do **not** enable “Require signed commits” on `main` until you have at least
one verified commit, or you can lock yourself out.

## 2. Create the public repository

From the project root, after you have a local commit:

```bash
gh auth login
gh repo create cloud-sec-dashboard --public --source=. --remote=origin --push
```

Or in the GitHub UI: **New repository**, **Public**, **do not** add a README
or license on GitHub (this repo already has them). Then:

```bash
git remote add origin git@github.com:<you>/cloud-sec-dashboard.git
git push -u origin main
```

## 3. Repository settings

**Settings → General**

- Enable **Issues**.
- Disable **Wikis** if you will not use them.

**Settings → Actions → General**

- Allow GitHub Actions (default for public repos is fine).
- Do **not** add AWS keys or other secrets in Phase 0. Logs are public.

## 4. Protect `main` (ruleset)

**Settings → Rules → Rulesets → New branch ruleset**

- Enforcement: **Active**
- Target branches: include `main` (or `refs/heads/main` depending on UI)
- Enable:
  - Restrict deletions
  - Block force pushes
  - Require a pull request before merging (required approvals: **0** while
    solo; still require the PR itself)
  - Require status checks to pass: add the check named **`ci`** (the GitHub
    Actions job). You can add this after the first workflow run so the check
    name exists.
- Bypass: allow **Administrators** only while you learn, then turn bypass off
  so even you cannot push straight to `main`.

Skip required reviewers (a second human would block a solo repo). Skip
required signed commits until signing is verified.

**Why:** `main` is the production-of-record branch. Force-push and direct
commits destroy auditability.

## 5. Squash merges

**Settings → General → Pull Requests**

- Enable **Allow squash merging** (matches ADR-0001).
- Optionally disable merge commits and rebase merges to keep one style.

## 6. First PR (exit criteria)

```bash
git checkout -b feat/phase-0-bootstrap
# commit locally with a Conventional Commit, e.g. chore: bootstrap phase 0
git push -u origin feat/phase-0-bootstrap
gh pr create --fill
```

Wait until the **ci** check is green, then squash-merge.

Prove gitleaks (use a **fake** key; never a real one). Gitleaks allowlists the
AWS documentation example `AKIAIOSFODNN7EXAMPLE`, so that string will **not**
fail the hook. Build a 20-character `AKIA…` token that is not that example:

```bash
# writes AKIA + ABCDEFGHIJKLMNOP as one token; do not paste a real key
printf 'AKIA%s\n' 'ABCDEFGHIJKLMNOP' > leak-test.txt
git add leak-test.txt
git commit -m "chore: should fail gitleaks"
# expect Detect hardcoded secrets to fail; then:
rm leak-test.txt
```

## Auth for `gh`

```bash
gh auth login    # HTTPS or SSH; GitHub.com
gh auth status
```
