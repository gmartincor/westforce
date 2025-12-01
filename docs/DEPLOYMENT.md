# 🚀 Despliegue en Hetzner Cloud - Westforce Removals

## Resumen

**Servidor**: CX23 (2 vCPU, 4GB RAM, 40GB SSD) - ~€4.08/mes + ~€0.82 backups  
**Dominio**: westforceremovals.com  
**Stack**: Django + PostgreSQL + Traefik (SSL automático)

## Arquitectura

```
Internet → Traefik (SSL) → Django (Gunicorn) → PostgreSQL
                                    ↓
                              Volúmenes Docker
```

## Despliegue Rápido

### 1. Preparar servidor (una vez)
```bash
# Desde tu máquina local
make setup
```

### 2. Configurar variables
```bash
ssh deploy@TU_IP
cd /opt/westforce/app
cp .env.hetzner.example .env
nano .env  # Editar valores
```

### 3. Desplegar
```bash
docker compose -f docker-compose.prod.yml up -d
```

## Comandos Útiles

| Comando | Descripción |
|---------|-------------|
| `make deploy` | Desplegar en producción |
| `make prod-logs` | Ver logs de producción |
| `make prod-status` | Estado de los servicios |
| `make backup` | Backup manual de BD |
| `make rollback` | Revertir cambios |

## Variables Requeridas (.env)

```env
SECRET_KEY=<generar-clave-segura>
DB_PASSWORD=<password-seguro>
ACME_EMAIL=<tu-email>
HEALTHCHECK_HEARTBEAT_URL=<url-healthchecks.io>
HEALTHCHECK_FAILURE_URL=<url-healthchecks.io/fail>
RESEND_API_KEY=<api-key>
```

## GitHub Actions Secrets

| Secret | Valor |
|--------|-------|
| `HETZNER_SSH_KEY` | Clave privada SSH (base64) |
| `HETZNER_HOST` | IP del servidor |
| `HETZNER_USER` | deploy |

## Monitorización

1. Crear cuenta en [Healthchecks.io](https://healthchecks.io)
2. Crear check `westforce-heartbeat` (1 min)
3. Copiar URLs al `.env`
4. Ejecutar: `sudo /opt/westforce/scripts/setup-monitoring.sh`

## DNS

```
A     @     → IP_SERVIDOR
A     www   → IP_SERVIDOR
```

## Rollback

Si hay problemas, usa `make rollback` para volver a una versión anterior.
