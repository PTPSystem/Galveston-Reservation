# Remote Deployment (Linux / systemd via SSH)

This guide and the accompanying files provide an opinionated, scriptable way to deploy the Galveston Reservation System on a Linux server you access with SSH.

> Assumptions (adjust if different):
> - OS: Ubuntu 22.04+ (or other systemd-based distro)
> - App path on server: `/opt/galveston-reservation`
> - Python: System `python3` (>=3.10) available
> - You deploy as user `howardshen` (non‑root) and use `sudo` for privileged steps
> - Your SSH private key already lives in `~/.ssh/` locally

## 1. SSH Config (Local Machine)

Append this block to your local `~/.ssh/config` (create file if missing):

```ssh
Host galveston-prod
    HostName 83.229.35.162
    User howardshen
    IdentityFile ~/.ssh/id_ed25519  # <-- change if your key has a different name
    IdentitiesOnly yes
    ForwardAgent no
    ServerAliveInterval 30
    ServerAliveCountMax 4
    Compression yes
```

Test:
```bash
ssh galveston-prod 'echo OK'
```

## 2. One-Time Remote Prep

Run the provided script (dry-run logic included) to install prerequisites and lay out directories.

```bash
./deploy/scripts/deploy.sh galveston-prod   # from project root (local)
```

What it does remotely (idempotent):

1. Creates `/opt/galveston-reservation` (owned by deploying user)
2. Copies repository (first time: `git clone`; subsequent: `git pull`)
3. Creates Python virtual environment under `.venv/`
4. Installs requirements
5. Installs systemd unit `galveston-reservation.service`
6. Leaves `.env` sample if not present (you must edit real values)

## 3. Environment Configuration

On the server edit `/opt/galveston-reservation/.env` (or create symlink to a secrets store). Never commit production secrets.

Minimal production overrides:

```env
FLASK_ENV=production
DEBUG=False
SECRET_KEY=generate-a-long-random-secret
PORT=8080
HOST=0.0.0.0
```
Plus all Google / Mail settings already shown in `.env.example`.

## 4. Managing the Service

```bash
ssh galveston-prod 'sudo systemctl daemon-reload'
ssh galveston-prod 'sudo systemctl enable galveston-reservation'
ssh galveston-prod 'sudo systemctl start galveston-reservation'
ssh galveston-prod 'sudo systemctl status galveston-reservation'
```

Logs (journal):

```bash
ssh galveston-prod 'journalctl -u galveston-reservation -f'
```

App access (assuming firewall open): `http://83.229.35.162:8080/`

## 5. Updating Code

Pull latest & restart (atomic):
```bash
./deploy/scripts/update.sh galveston-prod
```

## 6. Directory Layout (Remote)

```text
/opt/galveston-reservation
  ├── app/
  ├── .env
  ├── .venv/
  ├── logs/
  ├── secrets/           # service-account.json, client_secrets.json (chmod 600)
  ├── galveston_reservations.db (if using sqlite)
  └── requirements.txt
```

## 7. Switching to Postgres (Optional)

Install server locally or managed instance, add to `.env`:

```env
DATABASE_URL=postgresql+psycopg2://user:pass@db-host:5432/galveston
```

Install driver:

```bash
(.venv) pip install psycopg2-binary
```
Run a migration / recreate DB tables (currently simple `db.create_all()`).

## 8. Security Quick Wins

- Create a dedicated system user (non‑sudo) that owns the app; use `sudo` only for systemd install.
- Restrict secrets: `chmod 600 secrets/*.json`.
- Enable uncomplicated firewall (UFW) restricting to 22, 80, 443 (if reverse proxy), 8080 only internally if behind proxy.
- Fail2Ban for SSH.
- Keep packages patched (`sudo unattended-upgrades`).

## 9. Reverse Proxy (Recommended)

Add Nginx site (example):

```nginx
server {
  listen 80;
  server_name str.ptpsystem.com;
  location /health { proxy_pass http://127.0.0.1:8080/health; }
  location / { proxy_pass http://127.0.0.1:8080; proxy_set_header Host $host; proxy_set_header X-Forwarded-For $remote_addr; }
}
```
Then obtain TLS via Certbot and redirect HTTP→HTTPS.

## 10. Files Added in Repo

See `deploy/` directory for scripts and service unit template.

---

If you need a variant for a different path or Python version, duplicate the service file and adjust `WorkingDirectory` & `ExecStart`.
