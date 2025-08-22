# Docker / Compose Deployment

This adds containerization for the Flask app plus optional Postgres + Metabase stack.

## Components

| Service | Purpose | Port (Host) |
|---------|---------|-------------|
| app | Flask (waitress) | 8080 |
| db | Postgres 16 | 5432 (internal only) |
| metabase | Analytics UI | 3000 |

## 1. Install Docker Engine (Ubuntu 22.04)

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
docker version
```

## 2. Prepare Secrets

Place Google credential file locally at `./secrets/service-account.json` (not committed). Compose bind-mounts it read-only.

## 3. Environment

Edit `.env.container` with real values (SECRET_KEY, SMTP, etc.). Do not put DB password changes unless you reflect them in `compose.yaml`.

## 4. Build & Start

```bash
docker compose build app
docker compose up -d
docker compose ps
```

Access:
- App: http://<server-ip>:8080/
- Metabase: http://<server-ip>:3000/

## 5. First-Time Metabase Setup
In browser, complete setup wizard. Add a **new database** using host `db`, db name `galveston`, user `app`, password `app_pass`.

Access:
- App: http://SERVER_IP:8080/
- Metabase: http://SERVER_IP:3000/

## 6. Migrations / DB Schema
Current app auto-creates tables on startup (SQLite originally). With Postgres, it will connect via `DATABASE_URL`. Add `psycopg2-binary` if needed:

```bash
docker compose exec app pip install psycopg2-binary
```

Then rebuild image or bake into `requirements.txt` later.

## 7. Logs
App logs inside container (`docker logs <app-container>`). Mounted volume `app-logs` retains log files if your code writes to `/app/logs`.

## 8. Updating

```bash
git pull
docker compose build app
docker compose up -d
```

## 9. Adding Reverse Proxy & TLS
Later you can add Traefik or Nginx container to terminate TLS on 80/443 and route to app & Metabase; remove direct port mappings when that’s in place.

## 10. Backups
- Postgres: `docker compose exec db pg_dump -U app galveston > backup.sql`
- Metabase application data: volume `metabase-data` (snapshot via `docker run --rm -v metabase-data:/data -v $PWD:/backup busybox tar czf /backup/metabase-data.tgz /data`).

```bash
```bash
docker compose down         # stop
docker compose down -v      # stop + remove volumes (IRREVERSIBLE)
```

---
Evolve this by adding proper migrations (Alembic) and secrets management (Docker secrets or Vault) before production hardening.
