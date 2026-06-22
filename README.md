# portwright.io

Source + deploy pipeline for the **portwright.io** static site (private).

## Layout

```
public/                 # what ships to portwright.io (HTML + assets)
  ai-it-alerts.html     # AI/IT security alerts editorial page
  assets/portwr-clem.png
tools/security-check.py # stdlib static security scan
.htmlhintrc             # HTML validation rules
.github/workflows/publish.yml
```

## Pipeline (`.github/workflows/publish.yml`)

```
push / PR to main
   ├─ validate   (htmlhint — syntactically correct?)
   └─ security   (tools/security-check.py — secrets / mixed-content / js: URIs)
        │  both must pass
        ▼
   deploy  →  PAUSES at the `production` approval gate
        │     (you click "Approve and deploy" in the Actions tab)
        ▼
   rsync public/ → portwright.io droplet over SSH
```

- **You are the gate.** The `production` environment requires your approval, so
  nothing publishes until you review and click approve. A change is "approved"
  only once it is syntactically correct (validate), clean (security), **and** you
  say so.
- PR runs execute validate + security only — they never deploy.
- Deploy **skips gracefully** until the secrets below exist, so the pipeline is
  green from day one.

## One-time setup — `production` environment secrets

Settings → Environments → **production** → Secrets:

| Secret | Required | Meaning |
|---|---|---|
| `PORTWRIGHT_HOST` | yes | Droplet hostname or IP |
| `PORTWRIGHT_SSH_KEY` | yes | **Private** SSH key for the droplet (PEM) |
| `PORTWRIGHT_USER` | no | SSH user (default `root`) |
| `PORTWRIGHT_PATH` | no | Web root (default `/var/www/portwright.io`) |
| `PORTWRIGHT_KNOWN_HOSTS` | recommended | Pinned `known_hosts`; else `ssh-keyscan` (TOFU) |

The required reviewer on `production` is configured separately (repo owner).

## Local checks

```bash
npx --yes htmlhint --config .htmlhintrc "public/**/*.html"
python3 tools/security-check.py
```
