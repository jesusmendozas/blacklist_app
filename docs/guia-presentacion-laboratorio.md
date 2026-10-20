# Guía de presentación — Laboratorio blacklist_email

Documento listo para usar en la exposición oral del laboratorio. Incluye estructura de diapositivas, guion sugerido, demo en vivo y checklist.

**Integrantes:** Juan Camilo Díaz Zapateiro · Rafael de Jesús Beleño Castellanos · Yeison de Jesús Arrieta Venera · Jesús Felipe Mendoza Salcedo

**Repositorio:** [https://github.com/jesusmendozas/blacklist_app](https://github.com/jesusmendozas/blacklist_app)

**Informe técnico de pruebas:** [`informe-pruebas-integracion.md`](./informe-pruebas-integracion.md)

---

## Qué pueden hacer para presentar (opciones)

| Opción | Cuándo usarla | Qué preparar |
|--------|---------------|--------------|
| **A. Diapositivas + demo en vivo** (recomendada) | Exposición en clase / defensa del lab | 8–12 slides + API levantada + Postman/Newman |
| **B. Solo demo guiada** | Tiempo corto o profesor pide “muéstrenlo” | Guion de la sección *Demo en vivo* |
| **C. Walkthrough del repo** | Defensa en GitHub / Zoom compartiendo pantalla | Abrir Actions, colección Postman e informe en `/docs` |
| **D. Video corto (3–5 min)** | Entrega asíncrona | Grabar: ping → POST → GET → Newman → Actions en verde |

Esta guía asume la **opción A**.

---

## Estructura sugerida (≈ 10–12 minutos)

| # | Slide / momento | Tiempo | Quién (sugerido) |
|---|-----------------|--------|------------------|
| 1 | Portada y contexto | 30 s | Cualquiera |
| 2 | Problema / objetivo del lab | 1 min | Integrante 1 |
| 3 | Arquitectura del microservicio | 1–2 min | Integrante 2 |
| 4 | API (endpoints + auth) | 1–2 min | Integrante 2 |
| 5 | **Demo en vivo** | 3–4 min | Integrante 3 |
| 6 | Pruebas unitarias (pytest) | 1 min | Integrante 4 |
| 7 | Pruebas de integración (Postman + Newman + CI) | 2 min | Integrante 4 / 1 |
| 8 | Despliegue (Docker / Render) | 30–45 s | Integrante 1 |
| 9 | Resultados y cierre | 30–45 s | Cualquiera |
| — | Preguntas | resto | Todos |

Ajusten los nombres de “Integrante N” a su preferencia; lo importante es que **una sola persona maneje la demo** para no perder tiempo cambiando de laptop.

---

## Contenido de cada diapositiva (copiar a PowerPoint / Google Slides)

### 1. Portada

- Título: **Microservicio `blacklist_email`**
- Subtítulo: Laboratorio — pruebas de integración y CI
- Nombres del equipo
- Enlace del repositorio (QR opcional)

### 2. Problema / objetivo

**Qué decir:**

> Necesitamos un microservicio que permita a otras apps reportar emails maliciosos o no deseados y consultar si un email está bloqueado, de forma segura y confiable.

**Objetivos del laboratorio (checklist en pantalla):**

1. Implementar el servicio (Flask + Postgres).
2. Proteger endpoints con Bearer token.
3. Validar con pruebas unitarias e integración.
4. Automatizar la suite Postman con Newman en GitHub Actions.
5. Documentar el proceso en `/docs`.

### 3. Arquitectura

Diagrama simple (cajas):

```text
Cliente (Postman / otra API)
        │  Bearer Token
        ▼
┌───────────────────┐
│  Flask /blacklists│
│  router → service │
│  → repository     │
└─────────┬─────────┘
          ▼
┌───────────────────┐
│   PostgreSQL      │
│   tabla blacklists│
└───────────────────┘
```

**Capas a mencionar (una frase cada una):**

- **Rutas** (`blacklist_router`): HTTP, status codes.
- **Servicio**: reglas de negocio (duplicados, consulta).
- **Repositorio / modelo**: persistencia en Postgres.
- **Middleware**: Bearer token.
- **Infra:** Docker Compose (app + DB) y CI en GitHub Actions.

### 4. API — capacidades

| Método | Ruta | Auth | Qué hace |
|--------|------|------|----------|
| `GET` | `/blacklists/ping` | No | Health (`pong`) |
| `POST` | `/blacklists` | Bearer | Agregar email |
| `GET` | `/blacklists/<email>` | Bearer | ¿Está bloqueado? |

**Body de creación (ejemplo):**

```json
{
  "email": "spam@ejemplo.com",
  "app_uuid": "123e4567-e89b-12d3-a456-426614174000",
  "blocked_reason": "Spam detectado"
}
```

**Errores que deben mencionar (muestra madurez):** `401`, `400`, `409`, `404`.

### 5. Demo en vivo (guion paso a paso)

**Antes de la clase (checklist técnico):**

```bash
cd blacklist_app
docker compose up -d --build
curl http://localhost:3000/blacklists/ping
# → {"message":"pong"}
```

Tener abiertos en pestañas:

1. Terminal con Docker arriba.
2. Postman (colección importada) **o** Newman listo.
3. GitHub → pestaña **Actions** → workflow `pruebas_integracion`.
4. Este informe / la guía (por si preguntan detalle).

**Durante la demo (orden exacto):**

1. **Ping** — `GET /blacklists/ping` → `pong` (servicio vivo).
2. **Crear** — `POST /blacklists` con token válido → `201`.
3. **Consultar bloqueado** — `GET /blacklists/<email>` → `blocked: true` + razón.
4. **Consultar libre** — email que no existe → `blocked: false`.
5. **Auth** — mismo POST sin token o con token malo → `401`.
6. **Duplicado** — mismo email otra vez → `409`.
7. **Newman (opcional si hay tiempo):**

```bash
npx newman run postman/Blacklist_App.postman_collection.json \
  -e postman/Blacklist_App_Local.postman_environment.json
```

   Resultado a decir en voz alta: **15 requests · 64 assertions · 0 fallos**.

8. **CI** — mostrar un run verde del job `pruebas_integracion` en GitHub Actions.

Si Docker falla en el momento: no improvisen. Digan *“tenemos evidencia en CI y en el informe”* y abran Actions + el PDF/MD del informe.

### 6. Pruebas unitarias

- Framework: **pytest** (+ cobertura ≥ 90%).
- Capas cubiertas: middleware, service, repository, schemas, validation, errores.
- Comando:

```bash
pytest tests/unit/
# o suite completa:
pytest
```

**Frase corta:** “Las unitarias validan la lógica por capas; las de integración validan el contrato HTTP de punta a punta.”

### 7. Pruebas de integración (punto fuerte del lab)

Flujo a dibujar en una sola slide:

```text
Postman (colección)
    → export .json
    → Newman local
    → job GitHub Actions: pruebas_integracion
    → informe en /docs
```

Carpetas de la colección (de arriba hacia abajo):

1. Health Check  
2. Flujo principal (crear + consultar)  
3. Errores 401  
4. Errores 400  
5. 409 / 404  

**Evidencia numérica:** 15 requests, 64 assertions, 0 fallos (local y CI).

### 8. Despliegue / operación

- **Local:** `docker compose up -d --build` (app en `:3000`, Postgres en `:5433`).
- **Cloud:** Blueprint `render.yaml` (servicio web + Postgres).
- **CI:** cada push/PR ejecuta el stack en el runner y corre Newman.

### 9. Resultados y cierre

Bullet final:

- Microservicio funcional con auth Bearer.
- Suite unitaria + integración automatizada.
- CI reproducible en GitHub Actions.
- Documentación en el repositorio.

Cierre:

> Quedamos atentos a preguntas. El detalle paso a paso está en `docs/informe-pruebas-integracion.md`.

---

## Guion oral compacto (≈ 2 minutos si solo tienen voz)

> Presentamos el microservicio **blacklist_email**. Expone tres capacidades: ping de salud, agregar un email a la lista negra y consultar si un email está bloqueado. Los endpoints de escritura y consulta van protegidos con Bearer token.
>
> La arquitectura es Flask por capas — rutas, servicio, repositorio — con PostgreSQL. Corremos todo con Docker Compose.
>
> Validamos de dos formas: pruebas unitarias con pytest, y una colección Postman que Newman ejecuta también en GitHub Actions en el job `pruebas_integracion`. Esa suite cubre el flujo feliz y los errores 401, 400, 409 y 404: 15 requests, 64 assertions, cero fallos.
>
> El proceso quedó documentado en `/docs` y el código está en el repositorio del equipo. Ahora mostramos una demo rápida.

---

## Preguntas frecuentes del profesor (prepárense)

| Pregunta | Respuesta corta |
|----------|-----------------|
| ¿Por qué Bearer y no JWT completo? | El lab pide un token estático compartido vía `BEARER_TOKEN`; el middleware valida el header `Authorization: Bearer …`. |
| ¿Qué pasa si el email ya existe? | El servicio responde **409 Conflict**. |
| ¿Cómo evitan que Newman falle por datos viejos? | Scripts en la colección generan emails únicos (`created_email` / `run_email`) por ejecución. |
| ¿Qué prueba el CI que no prueben las unitarias? | El contrato HTTP real contra app + Postgres en contenedores (auth, status codes, body). |
| ¿Dónde está la evidencia? | Actions (job verde), output de Newman, e `informe-pruebas-integracion.md`. |
| ¿Cómo se despliega? | Docker local; en cloud, Render con `render.yaml`. |

---

## Checklist del día de la presentación

**Material**

- [ ] Diapositivas exportadas (PDF de respaldo en USB / Drive).
- [ ] Repo clonado y branch `master` actualizado.
- [ ] Docker Desktop / daemon funcionando.
- [ ] Postman con colección + environment importados **o** Newman vía `npx`.
- [ ] Pestaña Actions abierta con un run exitoso reciente.
- [ ] Token de demo: `dev-token-change-in-production` (el del environment).

**Roles**

- [ ] Quién presenta arquitectura.
- [ ] Quién hace la demo (una sola laptop).
- [ ] Quién responde sobre pruebas / CI.
- [ ] Quién cierra y toma preguntas.

**Plan B (sin internet / sin Docker)**

- [ ] Capturas o video corto de Newman + Actions en verde.
- [ ] PDF del informe de integración.

---

## Cómo armar las slides en 15 minutos

1. Abrir Google Slides / PowerPoint → tema limpio (fondo claro, tipografía grande).
2. Crear **9 slides** con los títulos de la sección *Contenido de cada diapositiva*.
3. Pegar solo tablas y bullets de esta guía (máximo 5 líneas por slide).
4. En la slide de arquitectura, dibujar las 3 cajas (Cliente → Flask → Postgres).
5. En la slide de resultados, poner en grande: **15 / 64 / 0**.
6. Última slide: enlace del repo + “¿Preguntas?”.

No llenen slides con código largo; el código se ve en la demo o en el informe.

---

## Enlaces útiles durante la exposición

| Recurso | Ruta / URL |
|---------|------------|
| Repo | https://github.com/jesusmendozas/blacklist_app |
| Actions | https://github.com/jesusmendozas/blacklist_app/actions |
| Informe de integración | `docs/informe-pruebas-integracion.md` |
| Colección Postman | `blacklist_app/postman/Blacklist_App.postman_collection.json` |
| Workflow CI | `.github/workflows/pruebas_integracion.yml` |

---

## Resumen: qué entregar / mostrar

1. **Presentación oral** con esta estructura.  
2. **Demo** de la API (y Newman si alcanza el tiempo).  
3. **CI en verde** del job `pruebas_integracion`.  
4. **Documento técnico** ya versionado: `docs/informe-pruebas-integracion.md`.
