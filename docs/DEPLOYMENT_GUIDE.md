# 🚀 Guía de Despliegue en Hostinger VPS - Westforce Removals

## 📋 Resumen del Análisis

### Stack Tecnológico Identificado
- **Backend**: Django 4.2 LTS + Gunicorn
- **Base de Datos**: PostgreSQL 15
- **Reverse Proxy**: Traefik v3 con SSL automático (Let's Encrypt)
- **Frontend**: Django Templates + TailwindCSS + Alpine.js
- **Contenedores**: Docker + Docker Compose

### Arquitectura de Producción
```
Internet → Traefik (443/SSL) → Django/Gunicorn (8000) → PostgreSQL (5432)
                ↓
         Let's Encrypt (certificados automáticos)
```

### Dominio
- **Dominio**: westforceremovals.com (registrado en Namecheap)
- **DNS Actual**: Configuración parking de Namecheap (necesita cambiar)

---

## 🔧 PRE-REQUISITOS

### 1. Información del VPS Hostinger
Necesitas obtener:
- [ ] **IP del VPS**: `___.___.___.__` 
- [ ] **Usuario SSH**: (normalmente `root` inicialmente)
- [ ] **Contraseña SSH** o clave SSH

### 2. Herramientas Locales
```bash
# Verificar que tienes SSH
ssh -V

# Verificar Docker (opcional, para pruebas locales)
docker --version
```

---

## 📝 PLAN DE DESPLIEGUE (PASO A PASO)

### FASE 1: Configuración del VPS Hostinger

#### 1.1. Conectar al VPS
```bash
# Conexión inicial (reemplaza IP_VPS con tu IP)
ssh root@IP_VPS
```

#### 1.2. Ejecutar Setup Inicial
El repo de infrastructure ya tiene un script optimizado:
```bash
# En el servidor Hostinger
cd /tmp
git clone https://github.com/gmartincor/infrastructure.git
cd infrastructure
chmod +x scripts/setup-inicial.sh
sudo ./scripts/setup-inicial.sh
```

Este script configura:
- ✅ Actualiza el sistema
- ✅ Instala Docker y Docker Compose
- ✅ Crea usuario `deploy` con permisos sudo limitados
- ✅ Configura firewall UFW (puertos 22, 80, 443)
- ✅ Configura Fail2ban (protección SSH)
- ✅ Configura Swap (2GB)
- ✅ Crea red Docker `traefik-public`
- ✅ Crea estructura de directorios

#### 1.3. Copiar Clave SSH (desde tu máquina local)
```bash
# Desde tu máquina local
ssh-copy-id -i ~/.ssh/id_ed25519.pub deploy@IP_VPS

# Probar conexión
ssh deploy@IP_VPS
```

---

### FASE 2: Configurar DNS en Namecheap

#### 2.1. Registros DNS Necesarios
En Namecheap → Domain List → westforceremovals.com → Advanced DNS:

| Type | Host | Value | TTL |
|------|------|-------|-----|
| A | @ | `IP_VPS` | Automatic |
| A | www | `IP_VPS` | Automatic |
| CNAME | traefik | westforceremovals.com | Automatic |

#### 2.2. Eliminar Registros Actuales
**ELIMINAR estos registros parking existentes:**
- CNAME Record: `www` → parkingpage.namecheap.com
- URL Redirect: `@` → http://www.westforceremovals.com/

#### 2.3. Verificar Propagación DNS
```bash
# Esperar 5-30 minutos y verificar
dig +short westforceremovals.com
dig +short www.westforceremovals.com

# Debería mostrar la IP del VPS
```

---

### FASE 3: Configurar Infraestructura Global

#### 3.1. Mover Infrastructure al Servidor
```bash
# Como usuario deploy en el servidor
ssh deploy@IP_VPS

# Clonar o mover el repo de infrastructure
cd /opt
sudo git clone https://github.com/gmartincor/infrastructure.git
sudo chown -R deploy:deploy /opt/infrastructure
```

#### 3.2. Configurar Variables Globales
```bash
cd /opt/infrastructure
cp .env.example .env
nano .env
```

Editar con estos valores:
```env
COMPANY_NAME=TRIPCORM
TIMEZONE=Australia/Perth
DOMAIN_BASE=westforceremovals.com
LETSENCRYPT_EMAIL=westforce.analytics@gmail.com
```

#### 3.3. Preparar Certificados Traefik
```bash
cd /opt/infrastructure/traefik
touch acme.json
chmod 600 acme.json
```

#### 3.4. Iniciar Traefik Global
```bash
cd /opt/infrastructure/traefik
docker compose up -d

# Verificar estado
docker logs traefik -f
```

---

### FASE 4: Desplegar Westforce

#### 4.1. Clonar Repositorio
```bash
ssh deploy@IP_VPS
cd /opt
sudo mkdir -p projects
sudo chown deploy:deploy projects
cd projects
git clone https://github.com/gmartincor/westforce.git
cd westforce
```

#### 4.2. Configurar Variables de Entorno
```bash
cp .env.production.example .env
nano .env
```

**Variables CRÍTICAS a configurar:**
```env
# Genera una clave secreta segura
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")

# Password seguro para PostgreSQL
DB_PASSWORD=$(openssl rand -base64 24)

# Copiar los valores generados al .env
```

#### 4.3. Crear Directorios Necesarios
```bash
mkdir -p logs backups config/traefik/dynamic
```

#### 4.4. Construir y Desplegar
```bash
# Build de la imagen
docker compose -f docker-compose.prod.yml build

# Iniciar servicios
docker compose -f docker-compose.prod.yml up -d

# Ver logs
docker compose -f docker-compose.prod.yml logs -f
```

#### 4.5. Verificar Despliegue
```bash
# Estado de contenedores
docker compose -f docker-compose.prod.yml ps

# Health check
curl http://localhost:8000/health/

# Logs de la aplicación
docker compose -f docker-compose.prod.yml logs web
```

---

### FASE 5: Verificación Final

#### 5.1. Verificar HTTPS
```bash
# Desde cualquier máquina con internet
curl -I https://westforceremovals.com
curl -I https://www.westforceremovals.com
```

#### 5.2. Verificar Certificado SSL
```bash
echo | openssl s_client -servername westforceremovals.com \
  -connect westforceremovals.com:443 2>/dev/null | \
  openssl x509 -noout -dates
```

#### 5.3. Verificar Redirecciones
- HTTP → HTTPS ✓
- www → non-www ✓

---

## 🔄 CI/CD con GitHub Actions

### Secrets Requeridos en GitHub
En el repositorio `gmartincor/westforce` → Settings → Secrets:

| Secret | Valor |
|--------|-------|
| `HOSTINGER_SSH_KEY` | Tu clave privada SSH (codificada en base64) |
| `HOSTINGER_HOST` | IP del VPS Hostinger |
| `HOSTINGER_USER` | `deploy` |

### Codificar Clave SSH
```bash
cat ~/.ssh/id_ed25519 | base64 -w 0
# Copiar el resultado como HOSTINGER_SSH_KEY
```

---

## 🛠️ Comandos Útiles

### Gestión de Contenedores
```bash
# Ver estado
docker compose -f docker-compose.prod.yml ps

# Ver logs en tiempo real
docker compose -f docker-compose.prod.yml logs -f

# Reiniciar todo
docker compose -f docker-compose.prod.yml restart

# Parar todo
docker compose -f docker-compose.prod.yml down

# Rebuild y redesplegar
docker compose -f docker-compose.prod.yml up -d --build
```

### Backup de Base de Datos
```bash
# Backup manual
docker compose -f docker-compose.prod.yml --profile backup run db-backup
```

### Django Management Commands
```bash
# Entrar al contenedor
docker compose -f docker-compose.prod.yml exec web bash

# Dentro del contenedor:
python manage.py createsuperuser
python manage.py shell
python manage.py migrate
```

---

## ⚠️ TROUBLESHOOTING

### Error: Certificado SSL no generado
```bash
# Verificar logs de Traefik
docker logs traefik 2>&1 | grep -i acme

# Verificar que DNS apunta correctamente
dig +short westforceremovals.com
```

### Error: Aplicación no responde
```bash
# Ver logs de la aplicación
docker compose -f docker-compose.prod.yml logs web --tail=100

# Verificar que está escuchando
docker compose -f docker-compose.prod.yml exec web curl localhost:8000/health/
```

### Error: Base de datos no conecta
```bash
# Ver logs de PostgreSQL
docker compose -f docker-compose.prod.yml logs postgres

# Verificar conexión
docker compose -f docker-compose.prod.yml exec postgres pg_isready
```

---

## 📊 Monitorización

### Uptime Kuma (Opcional)
```bash
cd /opt/infrastructure/monitoring/uptime-kuma
docker compose up -d
```

### Healthchecks.io
Ya configurado en las variables de entorno. El script de heartbeat se ejecuta cada minuto.

---

## 🎯 Checklist Final

- [ ] VPS Hostinger configurado
- [ ] DNS configurado en Namecheap
- [ ] Traefik funcionando
- [ ] Westforce desplegado
- [ ] HTTPS funcionando
- [ ] Health check respondiendo
- [ ] Backup configurado
- [ ] CI/CD configurado (opcional)

---

**Desarrollado para TRIPCORM** 🚀
