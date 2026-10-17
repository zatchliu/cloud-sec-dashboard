# Put this repo on GitHub so Actions can run

Goal: a **public** GitHub repo, `main` pushed, and the **ci** workflow visible
under the **Actions** tab. Signed commits, branch protection, and required PRs
are not part of this project.

## 1. Log in with the GitHub CLI

```bash
export PATH="$HOME/.local/bin:$PATH"
gh auth login
```

Choose GitHub.com. HTTPS or SSH both work. Confirm with `gh auth status`.

## 2. Create the public repo and push `main`

From this project root (do **not** add a README or license on github.com — they
already exist here):

```bash
gh repo create cloud-sec-dashboard --public --source=. --remote=origin --push
```

That creates `https://github.com/<you>/cloud-sec-dashboard`, adds `origin`, and
pushes `main`.

If you already created an empty public repo in the browser:

```bash
git remote add origin git@github.com:<you>/cloud-sec-dashboard.git
git push -u origin main
```

## 3. Watch the workflow

1. Open the repo on GitHub → **Actions**.
2. You should see workflow **CI**, job **ci** (from `.github/workflows/ci.yml`).
3. A push to `main` and a pull request both trigger it.

That is enough to learn GitHub Actions. You can keep committing and pushing
straight to `main`.

Optional later: open a PR from a branch if you want to see the
`pull_request` trigger, not because this repo requires reviews.
