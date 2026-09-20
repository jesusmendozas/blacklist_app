# Informe: pruebas de integración del servicio blacklist_email

## Integrantes

- Juan Camilo Díaz Zapateiro
- Rafael de Jesús Beleño Castellanos
- Yeison de Jesús Arrieta Venera
- Jesús Felipe Mendoza Salcedo

---

## Repositorio

- **GitHub:** [https://github.com/jesusmendozas/blacklist_app](https://github.com/jesusmendozas/blacklist_app)
- **Colección Postman (exportada):** [`blacklist_app/postman/Blacklist_App.postman_collection.json`](../blacklist_app/postman/Blacklist_App.postman_collection.json)
- **Entorno Postman local:** [`blacklist_app/postman/Blacklist_App_Local.postman_environment.json`](../blacklist_app/postman/Blacklist_App_Local.postman_environment.json)
- **Workflow CI:** [`.github/workflows/pruebas_integracion.yml`](../.github/workflows/pruebas_integracion.yml)

---

## Objetivo

Documentar el paso a paso realizado para:

1. Crear la colección Postman con las capacidades del servicio `blacklist_email`.
2. Exportar la colección en formato `.json`.
3. Ejecutar Newman de manera local para validar la colección.
4. Añadir el job de GitHub Actions `pruebas_integracion` que instala Newman y ejecuta la colección.
5. Publicar este informe dentro de `/docs` junto con el enlace del repositorio.

---

## Capacidades del servicio cubiertas

El microservicio expone estas capacidades (prefijo `/blacklists`):

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| `GET` | `/blacklists/ping` | No | Health check (`{"message":"pong"}`) |
| `POST` | `/blacklists` | Bearer | Agregar un email a la blacklist |
| `GET` | `/blacklists/<email>` | Bearer | Consultar si un email está bloqueado |

La colección también cubre errores esperados: `401` (sin token / token inválido / esquema incorrecto), `400` (validación), `409` (email duplicado) y `404` (ruta inexistente).

---

## Paso a paso realizado

### 1. Crear la colección en Postman

Se armó la colección **Blacklist App API** con carpetas ordenadas para ejecutarlas de arriba a abajo:

1. **Health Check** — `GET /blacklists/ping` (sin autenticación).
2. **Blacklist - Flujo principal** — crear entrada y consultar (bloqueado / no bloqueado).
3. **Errores de autenticación (401)** — sin header, token inválido, esquema `Basic`.
4. **Errores de validación (400)** — sin body, email inválido, UUID inválido, campos faltantes, `blocked_reason` demasiado largo.
5. **Conflictos y rutas inexistentes** — `409` por duplicado y `404` global.

Variables usadas:

- `base_url` → `http://localhost:3000`
- `bearer_token` → debe coincidir con `BEARER_TOKEN` del entorno (default: `dev-token-change-in-production`)
- `app_uuid` → UUID de la aplicación que reporta
- `created_email` / `run_email` → se generan por script para que la colección sea re-ejecutable

La autenticación Bearer está definida a nivel de colección; el request `Ping` la desactiva con `noauth`.

### 2. Exportar el `.json` de la colección

Los archivos exportados viven en el repositorio:

```text
blacklist_app/postman/
├── Blacklist_App.postman_collection.json
└── Blacklist_App_Local.postman_environment.json
```

Cómo exportarlos de nuevo desde Postman (si se editan):

1. Abrir Postman → Collections → **Blacklist App API**.
2. Menú `...` → **Export** → Collection v2.1 → guardar el `.json`.
3. Environments → **Blacklist App - Local** → Export → guardar el entorno.

### 3. Ejecutar Newman de manera local

#### 3.1 Prerrequisitos

- Docker Desktop instalado y en ejecución.
- Node.js / npm (para Newman), o usar `npx`.

#### 3.2 Levantar el servicio

Desde la carpeta de la aplicación:

```bash
cd blacklist_app
docker compose up -d --build
```

Verificar health:

```bash
curl http://localhost:3000/blacklists/ping
# Esperado: {"message":"pong"}
```

#### 3.3 Instalar y ejecutar Newman

```bash
npm install -g newman
# o sin instalar globalmente:
npx newman run postman/Blacklist_App.postman_collection.json \
  -e postman/Blacklist_App_Local.postman_environment.json
```

#### 3.4 Resultado esperado

- Requests ejecutados: **15**
- Assertions: **64**
- Fallos: **0**

Al terminar las pruebas locales:

```bash
docker compose down
```

### 4. Job de GitHub Actions: `pruebas_integracion`

Se añadió el workflow [`.github/workflows/pruebas_integracion.yml`](../.github/workflows/pruebas_integracion.yml) con un job llamado exactamente **`pruebas_integracion`**.

El job hace lo siguiente:

1. Hace checkout del repositorio.
2. Construye y levanta el stack con `docker compose up -d --build` (app + Postgres).
3. Espera a que `/blacklists/ping` responda `pong`.
4. Instala Node.js 20.
5. Instala Newman con `npm install -g newman`.
6. Ejecuta la colección exportada contra `http://localhost:3000`.
7. Baja el stack con `docker compose down -v` (también en fallo, `if: always()`).

Se dispara en:

- `push` a `master` / `main`
- `pull_request`
- `workflow_dispatch` (ejecución manual desde la pestaña Actions)

Cómo verlo en GitHub:

1. Abrir [https://github.com/jesusmendozas/blacklist_app/actions](https://github.com/jesusmendozas/blacklist_app/actions)
2. Seleccionar el workflow **pruebas_integracion**
3. Revisar el job y los logs de Newman

### 5. Publicación del informe

Este documento se versionó en:

```text
docs/informe-pruebas-integracion.md
```

junto con el enlace del repositorio indicado al inicio.

---

## Cómo importar la colección en Postman (resumen rápido)

1. Abrir Postman.
2. **Import** → seleccionar `Blacklist_App.postman_collection.json`.
3. Importar también `Blacklist_App_Local.postman_environment.json`.
4. Activar el entorno **Blacklist App - Local (docker-compose)**.
5. Con el stack arriba (`docker compose up -d`), usar **Collection Runner** o Newman.

---

## Evidencia de validación

| Prueba | Resultado |
|--------|-----------|
| Suite unitaria/integración pytest (50 tests) | Pasó (~97% cobertura) |
| Newman local contra contenedor + Postgres | 15 requests / 64 assertions / 0 fallos |
| Job CI `pruebas_integracion` | Workflow versionado en este repositorio |

---

## Comandos de referencia (copia rápida)

```bash
# Clonar
git clone https://github.com/jesusmendozas/blacklist_app.git
cd blacklist_app/blacklist_app

# Levantar API
docker compose up -d --build

# Newman local
npx newman run postman/Blacklist_App.postman_collection.json \
  -e postman/Blacklist_App_Local.postman_environment.json

# Bajar
docker compose down
```
