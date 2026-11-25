# Branch protection for `main`

## Required CI check name

From workflow `ci.yml`, job `test` (displayed in GitHub as **test**).

Verify after a PR run:

```bash
gh run list --branch <your-branch> --limit 1
gh run view <run-id> --json jobs -q '.jobs[].name'
```

## Enable protection (repository admin)

```bash
gh api repos/learner-enthusiast/video-toolkit/branches/main/protection \
  --method PUT \
  --field required_status_checks[strict]=true \
  --field required_status_checks[contexts][]=test \
  --field enforce_admins=true \
  --field required_pull_request_reviews[required_approving_review_count]=0 \
  --field restrictions=null
```

If `gh` reports insufficient permissions, configure in GitHub: **Settings → Branches → Add rule for `main`** with required status check **test**, strict up-to-date, block force pushes.

## Current status

Run:

```bash
gh api repos/learner-enthusiast/video-toolkit/branches/main/protection 2>&1 | head -20
```

Document the result in `docs/optimization/post-hardening-status.md` when protection is applied.