### Related Issue

Closes #[ISSUE_NUMBER]

---

### Summary

> Briefly describe what this PR does and why it’s needed.
> 
> 
> Example: Stabilize Ray Serve startup with GPU detection and updated API usage.
> 

---

### Context

> Why is this change required?
> 
- [ ]  Bug fix
- [ ]  New feature
- [ ]  Performance optimization
- [ ]  Code cleanup / refactor
- [ ]  Documentation update
- [ ]  Other (explain below)

---

### Changes

List the major modifications introduced in this PR:

- Updated `serve_app.py` to use `serve.start` + `serve.run`
- Enabled GPU passthrough (`gpus: all`) in `docker-compose.yml`
- Increased `/dev/shm` size for Ray object store stability
- Verified CUDA detection inside container

---

### Validation Steps

Provide reproducible steps to verify the change:

```bash
docker compose down --remove-orphans || true
docker builder prune -f
docker compose build --no-cache ray-inference
docker compose up -d ray-inference

curl -s <http://127.0.0.1:8000/inference/healthz>
curl -s -X POST <http://127.0.0.1:8000/inference/> \\
  -H 'Content-Type: application/json' \\
  -d '{"input":[10,20,30,40]}'
```

---

**Expected output**

```json
{"ok": true, "device": "cuda"}
{"device": "cuda", "output": [20.0, 40.0, 60.0, 80.0]}
```

---

### Verification

```bash
docker exec -it ray-inference bash -lc "ray status"
```

Expected:

```
Usage:
 1.0/16.0 CPU
 1.0/1.0 GPU
```

---

### Commit Summary

```
chore(serve): replace deprecated deploy() with serve.run()
feat(ray): assign GPU per replica (num_gpus=1)
fix(compose): add gpus: all + shm_size: 8g
chore(ray): stabilize Ray Serve with serve.start+serve.run
```

---

### Checklist

- [ ]  Builds locally without errors
- [ ]  Service container starts successfully
- [ ]  Health and inference endpoints respond correctly
- [ ]  GPU is visible and used by Ray Serve
- [ ]  No Ray `/dev/shm` performance warnings
- [ ]  Linked issue auto-closes on merge

---

### Screenshots / Logs (optional)

Attach CLI logs, screenshots, or metrics if available.

---

### Notes for Reviewers

> Mention any follow-ups, edge cases, or TODOs reviewers should be aware of.
> 

```
---

Would you like me to make a **variant for multi-service PRs** (e.g., Airflow + Ray + MLflow combined validation checklist)?
That version is ideal for your `hybrid-mlops-demo` workflow.

```
