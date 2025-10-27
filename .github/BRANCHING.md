[200~# Branching Strategy

> This repository follows a Dev → Main workflow model optimized for continuous development and safe releases.
> 

---

### Branch Overview

| Branch | Purpose | Rules |
| --- | --- | --- |
| `main` | **Production-ready code** only. Used for deployment and releases. | Protected branch. No direct commits. |
| `dev` | **Integration branch.** All features and fixes merge here before release. | Default branch. All PRs merge into `dev`. |
| `feature/*` | Individual features or experiments (e.g. `feature/observability`) | Created from `dev`. Merge back via PR. |
| `hotfix/*` | Urgent production fixes. | Created from `main`, merged into both `main` and `dev`. |

---

### Workflow Summary

1. **Start from `dev`**

```bash
git checkout dev
git pull origin dev
git checkout -b feature/<feature-name>
```

1. **Work and Commit**

```bash
# example
git add .
git commit -m "feat(observability): add ray serve inference endpoint"
```

1. **Push and Open PR**

```bash
git push origin feature/<feature-name>
```

Then open a **Pull Request → `dev`**.

1.  **Integration and Testing**
- All new code is merged into `dev`.
- Run tests, linting, and validation pipelines here.

1. **Release to Main**

```bash
# Merge dev → main after QA validation
git checkout main
git merge dev --no-ff -m "release: merge dev into main for v1.0.0"
git push origin main
```

---

### Branch Flow

```
main
 └── dev
       ├── feature/mlflow-tracking
             ├── feature/ray-serve-api
                   └── hotfix/logging-timeout
                   ```

                   ---

### Protection Rules

| Branch | Rule | Description |
| --- | --- | --- |
| `main` | Require PRs + Approvals | Prevents direct push or deletion |
| `dev` | Require PRs | Controls feature merges and avoids broken builds |

---

### Notes

- Use **squash & merge** to keep history clean.
- Prefix commits with a type:
    - `feat:` → New feature
        - `fix:` → Bug fix
            - `docs:` → Documentation
                - `refactor:` → Code cleanup
                    - `chore:` → CI/CD or config updates
                        

                        ---
