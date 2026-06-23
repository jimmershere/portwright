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
                  ... continuous feedback; these NEVER deploy.

YOU click "Run workflow" (Actions → Publish portwright.io)   ← the gate
   ├─ validate   (re-run)
   ├─ security   (re-run)
   └─ deploy     rsync public/ → portwright.io droplet over SSH
```

- **You are the gate.** Deploy runs *only* on a manual trigger, so nothing
  publishes until you choose to. Because deploy depends on validate + security,
  a manual run still re-checks first — a change ships only when it is
  syntactically correct, clean, **and** you said go.
- Push/PR runs execute validate + security only — they never deploy.
- Deploy **skips gracefully** until the secrets below exist, so the pipeline is
  green from day one.

> Note: this manual gate is used because the repo is **private on the free
> plan**, where GitHub's "Approve and deploy" *environment* gate isn't
> available. On GitHub Pro this can be upgraded to that click-to-approve pause.

## One-time setup — repository secrets

Settings → Secrets and variables → Actions → **New repository secret**:

| Secret | Required | Meaning |
|---|---|---|
| `PORTWRIGHT_HOST` | yes | Droplet hostname or IP |
| `PORTWRIGHT_SSH_KEY` | yes | **Private** SSH key for the droplet (PEM) |
| `PORTWRIGHT_USER` | no | SSH user (default `root`) |
| `PORTWRIGHT_PATH` | no | Web root (default `/var/www/portwright`, the nginx docroot) |
| `PORTWRIGHT_KNOWN_HOSTS` | recommended | Pinned `known_hosts`; else `ssh-keyscan` (TOFU) |

## Local checks

```bash
npx --yes htmlhint --config .htmlhintrc "public/**/*.html"
python3 tools/security-check.py
```
