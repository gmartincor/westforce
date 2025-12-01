# 🚀 Plan de Implementación en Hetzner - Westforce Removals

## 📋 Resumen Ejecutivo

| Aspecto | Detalle |
|---------|---------|
| **Servidor** | Hetzner CX23 (2 vCPU, 4GB RAM, 40GB SSD) |
| **Costo mensual** | ~€4.08 + €0.82 backups = **~€4.90/mes** |
| **Dominio** | westforceremovals.com |
| **Stack** | Django 4.2 LTS + PostgreSQL 15 + Traefik 3 + Gunicorn |
| **SSL** | Let's Encrypt (automático via Traefik) |
| **CI/CD** | GitHub Actions |
| **Monitorización** | Healthchecks.io (guillermomc007@gmail.com) |
| **Mantenimiento** | 🤖 **CERO** - Todo automatizado |

---

## 🤖 Características de CERO MANTENIMIENTO

Este despliegue está configurado para funcionar sin intervención manual:

| Característica | Implementación | Frecuencia |
|----------------|----------------|------------|
| **Auto-reinicio de contenedores** | Docker `restart: unless-stopped` | Automático |
| **Auto-recovery de la app** | Script healthcheck con reinicio tras 3 fallos | Cada 1 min |
| **Watchdog de Docker** | Monitorea y reinicia contenedores caídos | Cada 2 min |
| **Auto-reinicio del demonio Docker** | Systemd service override | Automático |
| **Alertas de recursos** | Pings a healthchecks.io cuando CPU/RAM/Disco alto | Cada 5 min |
| **Alertas de escalado** | Notifica cuando considerar upgrade del plan | Umbral 75%+ |
| **Backups automáticos** | Base de datos + media files | Diario 3:00 AM |
| **Limpieza de disco** | Elimina cache/logs antiguos si disco >80% | Diario 4:00 AM |
| **Limpieza Docker** | Prune de imágenes/contenedores antiguos | Semanal |
| **Actualizaciones seguridad** | Unattended-upgrades | Automático |
| **Rotación de logs** | Logrotate para todos los logs | Diario |

---

## 📊 Arquitectura del Sistema

```
┌──────────────────────────────────────────────────────────────────┐
│                        INTERNET                                   │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Hetzner CX23 Server                            │
│                  (2 vCPU, 4GB RAM, 40GB SSD)                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                      UFW Firewall                          │  │
│  │               (80, 443, SSH permitidos)                    │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              │                                    │
│                              ▼                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                    Traefik v3.2                            │  │
│  │   • SSL automático (Let's Encrypt)                        │  │
│  │   • Redirect HTTP → HTTPS                                 │  │
│  │   • Rate limiting                                         │  │
│  │   • Security headers                                      │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              │                                    │
│           ┌──────────────────┴──────────────────┐                │
│           ▼                                      ▼                │
│  ┌─────────────────────┐            ┌─────────────────────────┐  │
│  │   Django + Gunicorn │            │   PostgreSQL 15         │  │
│  │   (3 workers)       │◄──────────►│   (384MB limit)         │  │
│  │   (1.5GB limit)     │            │                         │  │
│  └─────────────────────┘            └─────────────────────────┘  │
│           │                                      │                │
│           ▼                                      ▼                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                  Docker Volumes                              │ │
│  │   • postgres_data  • media_data  • static_data  • traefik   │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Servicios Externos                             │
│   • GitHub (código + CI/CD)                                       │
│   • Healthchecks.io (monitorización)                             │
│   • Resend (email transaccional)                                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Plan de Implementación por Fases

### **FASE 0: Pre-requisitos** ⏱️ 15 min
*Estado: ✅ Completado parcialmente*

#### Checklist:
- [x] Cuenta Hetzner creada
- [ ] Documentos verificados por Hetzner (en proceso)
- [x] Dominio westforceremovals.com comprado
- [x] Clave SSH generada localmente
- [x] Cuenta GitHub con repositorio configurado
- [ ] Cuenta Healthchecks.io creada

#### Acciones pendientes:
```bash
# 1. Verificar clave SSH local
ls -la ~/.ssh/id_ed25519.pub

# Si no existe, crearla:
ssh-keygen -t ed25519 -C "tu-email@ejemplo.com"

# 2. Copiar la clave pública para Hetzner
cat ~/.ssh/id_ed25519.pub
```

---

### **FASE 1: Provisión del Servidor** ⏱️ 30 min
*Estado: ⏳ Pendiente (esperando verificación de Hetzner)*

#### 1.1 Crear servidor en Hetzner Cloud Console

1. Ir a https://console.hetzner.cloud
2. Crear proyecto: `westforce-production`
3. **Security → SSH Keys**: Añadir tu clave pública SSH
4. **Servers → Create Server**:
   - **Location**: Helsinki (hel1) - mejor latencia para Australia/Europa
   - **Image**: Ubuntu 24.04 LTS
   - **Type**: CX23 (€0.0056/hora)
   - **Networking**: IPv4 + IPv6
   - **SSH Key**: Seleccionar la clave añadida
   - **Backups**: ✅ Activar (recomendado)
   - **Name**: `westforce-prod`
5. Click "Create & Buy Now"
6. **Anotar la IP pública**: `_______________`

#### 1.2 Ejecutar setup inicial

```bash
# Desde tu máquina local, ejecutar el script interactivo:
cd /path/to/westforce
./scripts/hetzner/00-interactive-setup.sh

# O manualmente:
# 1. Conectar al servidor
ssh root@TU_IP_SERVIDOR

# 2. Ejecutar script de hardening
curl -sSL https://raw.githubusercontent.com/gmartincor/westforce/hetzner/scripts/hetzner/01-server-setup.sh | bash
```

#### 1.3 Verificar setup

```bash
# Conectar como usuario deploy
ssh deploy@TU_IP_SERVIDOR

# Verificar Docker
docker --version
docker compose version

# Verificar firewall
sudo ufw status
```

---

### **FASE 2: Configuración DNS** ⏱️ 15 min + propagación
*Estado: ⏳ Pendiente*

#### 2.1 Configurar registros DNS

En tu proveedor de dominios (donde compraste westforceremovals.com), añade:

| Tipo | Nombre | Valor | TTL |
|------|--------|-------|-----|
| A | @ | TU_IP_SERVIDOR | 3600 |
| A | www | TU_IP_SERVIDOR | 3600 |
| AAAA | @ | TU_IPv6_SERVIDOR (si aplica) | 3600 |
| AAAA | www | TU_IPv6_SERVIDOR (si aplica) | 3600 |

#### 2.2 Verificar propagación

```bash
# Verificar resolución DNS
dig +short westforceremovals.com A
dig +short www.westforceremovals.com A

# Verificación global
# Visitar: https://www.whatsmydns.net/#A/westforceremovals.com
```

⚠️ **Nota**: La propagación DNS puede tardar hasta 48 horas, aunque normalmente es de minutos.

---

### **FASE 3: Configuración de Variables de Entorno** ⏱️ 20 min
*Estado: ⏳ Pendiente*

#### 3.1 Generar secretos

```bash
# Generar SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(50))"

# Generar DB_PASSWORD
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 3.2 Configurar .env en el servidor

```bash
# Conectar al servidor
ssh deploy@TU_IP_SERVIDOR

# Clonar repositorio (si no se ha hecho)
git clone https://github.com/gmartincor/westforce.git /opt/westforce/app
cd /opt/westforce/app
git checkout hetzner

# Crear archivo .env
cp .env.hetzner.example .env
nano .env
```

#### 3.3 Variables a configurar

```env
# OBLIGATORIOS - Generar valores únicos
SECRET_KEY=<tu-secret-key-generado>
DB_PASSWORD=<tu-db-password-generado>

# SSL
ACME_EMAIL=westforce.analytics@gmail.com

# OPCIONAL pero recomendado
RESEND_API_KEY=<obtener-de-resend.com>

# MONITORIZACIÓN (configurar después de crear checks)
HEALTHCHECK_HEARTBEAT_URL=<url-de-healthchecks.io>
HEALTHCHECK_FAILURE_URL=<url-de-healthchecks.io>/fail
```

---

### **FASE 4: Primer Despliegue** ⏱️ 15 min
*Estado: ⏳ Pendiente*

#### 4.1 Desplegar la aplicación

```bash
# En el servidor como usuario deploy
cd /opt/westforce/app

# Crear directorios necesarios
mkdir -p logs backups config/traefik/dynamic

# Iniciar servicios
docker compose -f docker-compose.prod.yml up -d

# Ver logs en tiempo real
docker compose -f docker-compose.prod.yml logs -f
```

#### 4.2 Verificar despliegue

```bash
# Ver estado de los contenedores
docker compose -f docker-compose.prod.yml ps

# Probar health check local
curl http://localhost:8000/health/

# Esperar a que Traefik obtenga el certificado SSL (1-2 min)
# Luego probar desde internet
curl -I https://westforceremovals.com
```

#### 4.3 Crear superusuario

```bash
docker exec -it westforce-web python manage.py createsuperuser
```

---

### **FASE 5: Configuración de Monitorización** ⏱️ 15 min
*Estado: ✅ Cuenta creada - Configurar checks*

#### 5.1 Tu cuenta de Healthchecks.io

✅ **Cuenta ya creada**: guillermomc007@gmail.com
- Dashboard: https://healthchecks.io/projects/
- Check existente: "My First Check"
- URL: `https://hc-ping.com/94648cf3-09f9-4934-8c59-c8190064bb1c`

#### 5.2 Configurar integraciones de alerta

1. Ve a https://healthchecks.io → **Integrations**
2. Añade **Email** → guillermomc007@gmail.com
3. (Opcional) Añade **Telegram** o **Slack** para alertas móviles

#### 5.3 Renombrar y configurar el check existente

1. Ve a https://healthchecks.io/checks/
2. Click en "My First Check" → Edit
3. Configura:
   - **Name**: `westforce-heartbeat`
   - **Schedule**: `* * * * *` (Simple → Every 1 minute)
   - **Grace Time**: 5 minutes
   - **Tags**: `westforce, production, health`

#### 5.4 (Opcional) Crear checks adicionales

Para monitoreo más granular, crea estos checks adicionales:

| Check | Schedule | Grace | URL a usar |
|-------|----------|-------|------------|
| `westforce-backup` | `0 3 * * *` | 1 hora | Nueva URL |
| `westforce-resources` | `*/5 * * * *` | 10 min | Nueva URL |

#### 5.5 El .env ya está pre-configurado

El archivo `.env.hetzner.example` ya tiene tu URL de healthchecks.io:

```env
# Ya incluido en .env.hetzner.example
HEALTHCHECK_HEARTBEAT_URL=https://hc-ping.com/94648cf3-09f9-4934-8c59-c8190064bb1c
HEALTHCHECK_FAILURE_URL=https://hc-ping.com/94648cf3-09f9-4934-8c59-c8190064bb1c/fail
```

#### 5.6 Activar scripts de monitorización

```bash
# Como root en el servidor
sudo /opt/westforce/app/scripts/hetzner/03-setup-monitoring.sh
```

Esto instalará:
- ✅ Healthcheck cada 1 minuto (con auto-recovery)
- ✅ Monitoreo de recursos cada 5 minutos
- ✅ Watchdog de Docker cada 2 minutos
- ✅ Backups diarios a las 3:00 AM
- ✅ Limpieza de disco diaria a las 4:00 AM
- ✅ Actualizaciones de seguridad automáticas

---

### **FASE 6: Configuración CI/CD** ⏱️ 10 min
*Estado: ⏳ Pendiente*

#### 6.1 Configurar secrets en GitHub

1. Ir a: `https://github.com/gmartincor/westforce/settings/secrets/actions`
2. Añadir los siguientes secrets:

| Secret | Valor |
|--------|-------|
| `HETZNER_HOST` | IP de tu servidor |
| `HETZNER_USER` | `deploy` |
| `HETZNER_SSH_KEY` | Tu clave privada SSH en base64 |

```bash
# Para obtener la clave privada en base64:
cat ~/.ssh/id_ed25519 | base64 -w 0
```

#### 6.2 Configurar environment en GitHub

1. Ir a: `https://github.com/gmartincor/westforce/settings/environments`
2. Crear environment: `production`
3. Añadir URL: `https://westforceremovals.com`

#### 6.3 Verificar CI/CD

```bash
# Hacer un commit de prueba
git add .
git commit -m "test: verify CI/CD pipeline"
git push origin hetzner

# Verificar en GitHub Actions que el workflow se ejecute correctamente
```

---

### **FASE 7: Verificación Final** ⏱️ 15 min
*Estado: ⏳ Pendiente*

#### 7.1 Checklist de verificación

- [ ] `https://westforceremovals.com` carga correctamente
- [ ] `https://www.westforceremovals.com` redirige a no-www
- [ ] Certificado SSL válido (candado verde)
- [ ] Health check responde: `/health/`
- [ ] Admin accesible: `/admin/`
- [ ] Formulario de cotización funciona
- [ ] Emails se envían correctamente (si Resend configurado)
- [ ] Healthchecks.io recibe pings correctamente
- [ ] CI/CD funciona (push → deploy automático)

#### 7.2 Comandos de verificación

```bash
# Verificar SSL
openssl s_client -connect westforceremovals.com:443 -servername westforceremovals.com < /dev/null 2>/dev/null | openssl x509 -noout -dates

# Verificar headers de seguridad
curl -I https://westforceremovals.com

# Verificar health check
curl https://westforceremovals.com/health/

# Verificar logs
docker compose -f docker-compose.prod.yml logs --tail=100 web
```

---

## 🔧 Comandos de Mantenimiento

### Operaciones diarias

```bash
# Ver logs en tiempo real
docker compose -f docker-compose.prod.yml logs -f

# Ver estado de servicios
docker compose -f docker-compose.prod.yml ps

# Reiniciar servicios
docker compose -f docker-compose.prod.yml restart

# Ver uso de recursos
docker stats
```

### Backup manual

```bash
# Ejecutar backup
docker compose -f docker-compose.prod.yml --profile backup run --rm db-backup

# Ver backups
ls -lh /opt/westforce/backups/
```

### Rollback

```bash
# Ejecutar script de rollback
./scripts/hetzner/rollback.sh
```

### Actualización

```bash
# Desde la rama main o hetzner
git pull origin hetzner
docker compose -f docker-compose.prod.yml up -d --build
```

---

## 💰 Costos Mensuales Estimados

| Servicio | Costo |
|----------|-------|
| Hetzner CX23 | €4.08 |
| Backups (20%) | €0.82 |
| **Total hosting** | **€4.90/mes** |
| Dominio (anual/12) | ~€1.00/mes |
| Healthchecks.io | Gratis (tier básico) |
| Resend | Gratis (hasta 3000 emails/mes) |
| **Total estimado** | **~€6/mes** |

---

## 🆘 Troubleshooting

### El sitio no carga

```bash
# Verificar DNS
dig +short westforceremovals.com

# Verificar contenedores
docker compose -f docker-compose.prod.yml ps

# Ver logs
docker compose -f docker-compose.prod.yml logs
```

### SSL no funciona

```bash
# Verificar Traefik
docker compose -f docker-compose.prod.yml logs traefik

# Verificar certificados
docker exec westforce-traefik cat /letsencrypt/acme.json | jq '.letsencrypt.Certificates'
```

### Base de datos no conecta

```bash
# Verificar PostgreSQL
docker compose -f docker-compose.prod.yml logs postgres

# Conectar a la BD
docker exec -it westforce-postgres psql -U westforce -d westforce_removals
```

### Memoria insuficiente

```bash
# Ver uso de memoria
free -h
docker stats --no-stream

# Si es necesario, reducir workers de Gunicorn en .env:
# GUNICORN_WORKERS=2
```

---

## 📞 Contacto y Soporte

- **Hetzner**: https://console.hetzner.cloud/support
- **GitHub Issues**: https://github.com/gmartincor/westforce/issues
- **Healthchecks.io**: https://healthchecks.io

---

*Última actualización: Diciembre 2024*
