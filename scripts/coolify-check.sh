#!/usr/bin/env bash
# Verifica que el compose del repo cumple el contrato Coolify del MVP Hefesto.
#   - Servicios sin profiles: no ports, no container_name, no privileged/cap_add/devices,
#     no network_mode/pid/ipc host, no security_opt unconfined, binds solo dentro del repo
#     y nunca docker.sock.
#   - Sin `name:` a nivel raiz (Coolify pone el nombre).
#   - Para bases supabase-pg: DB_NAME y DB_SSLMODE son parametrizables y aparecen en el render.
#
# Uso: bash scripts/coolify-check.sh
# Salida: exit 0 si todo cumple; exit 1 si hay violaciones (con mensaje servicio: motivo).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Contrato: lista de compose a verificar. compose.bootstrap.yaml y servicios en profiles quedan fuera.
COMPOSE_FILES=("compose.yaml")

# Variables de host/URL: reciben valor de ejemplo no secreto.
HOST_VARS=("DOMAIN" "DB_HOST")

# Variables parametrizadas del contrato supabase-pg (deben verse en el render).
PG_VARS=("DB_NAME" "DB_SSLMODE")

TMPDIR_LOCAL="${TMPDIR:-/tmp}"
TMP_ENV="$(mktemp "${TMPDIR_LOCAL%/}/coolify-check.XXXXXX.env")"
trap 'rm -f "$TMP_ENV"' EXIT

failed=0

is_in_list() {
    local needle="$1"; shift
    for item in "$@"; do
        [ "$item" = "$needle" ] && return 0
    done
    return 1
}

for compose_file in "${COMPOSE_FILES[@]}"; do
    compose_path="$REPO_ROOT/$compose_file"
    if [ ! -f "$compose_path" ]; then
        echo "ERROR: $compose_path no existe" >&2
        exit 2
    fi

    echo "=== $compose_file ==="

    # Extraer ${VAR} (forma simple) del compose y deduplicar.
    mapfile -t VARS < <(grep -oE '\$\{[A-Z_][A-Z0-9_]*' "$compose_path" | sed 's/^\${//' | sort -u || true)

    # Generar .env temporal con valores ficticios no secretos.
    : > "$TMP_ENV"
    for v in "${VARS[@]}"; do
        if is_in_list "$v" "${HOST_VARS[@]}" "${PG_VARS[@]}"; then
            continue
        fi
        echo "$v=x1234567890abcdef1234567890abcdef" >> "$TMP_ENV"
    done
    for v in "${HOST_VARS[@]}"; do
        echo "$v=https://ejemplo.invalid" >> "$TMP_ENV"
    done
    # supabase-pg: valores concretos para validar parametrizacion.
    echo "DB_NAME=mvp_prueba" >> "$TMP_ENV"
    echo "DB_SSLMODE=disable" >> "$TMP_ENV"

    # Renderizar el compose. stderr se descarta (warnings del daemon); si falla, mensaje generico.
    if ! RENDER_JSON="$(docker compose --project-directory "$REPO_ROOT" \
            -f "$compose_path" \
            --env-file "$TMP_ENV" \
            config --format json 2>/dev/null)"; then
        echo "FAIL: docker compose config no se pudo renderizar; revisar sintaxis/anclas de $compose_file"
        failed=1
        continue
    fi

    # Contrato 2: sin 'name:' forzado en raiz ni en volumenes/redes del compose fuente.
    # Coolify autoderiva el nombre del proyecto; el render siempre trae name derivado.
    if grep -qE '^name:|^[[:space:]]+name:' "$compose_path"; then
        echo "FAIL: compose contiene 'name:' forzado (raiz/volumenes/redes); Coolify asigna el nombre"
        failed=1
    fi

    # Walk services sin profiles: contrato 1.
    while IFS= read -r svc; do
        [ -z "$svc" ] && continue

        PORTS_LEN=$(echo "$RENDER_JSON" | jq -r ".services.\"$svc\".ports // [] | length")
        if [ "$PORTS_LEN" != "0" ]; then
            echo "FAIL: $svc: 'ports' definido (debe ser 'expose')"
            failed=1
        fi

        CN=$(echo "$RENDER_JSON" | jq -r ".services.\"$svc\".container_name // empty")
        if [ -n "$CN" ]; then
            echo "FAIL: $svc: container_name='$CN'"
            failed=1
        fi

        PRIV=$(echo "$RENDER_JSON" | jq -r ".services.\"$svc\".privileged // false")
        if [ "$PRIV" = "true" ]; then
            echo "FAIL: $svc: privileged=true"
            failed=1
        fi

        CAPADD_LEN=$(echo "$RENDER_JSON" | jq -r ".services.\"$svc\".cap_add // [] | length")
        if [ "$CAPADD_LEN" != "0" ]; then
            echo "FAIL: $svc: cap_add definido"
            failed=1
        fi

        DEVICES_LEN=$(echo "$RENDER_JSON" | jq -r ".services.\"$svc\".devices // [] | length")
        if [ "$DEVICES_LEN" != "0" ]; then
            echo "FAIL: $svc: devices definido"
            failed=1
        fi

        NM=$(echo "$RENDER_JSON" | jq -r ".services.\"$svc\".network_mode // empty")
        if [ "$NM" = "host" ]; then
            echo "FAIL: $svc: network_mode=host"
            failed=1
        fi

        PID=$(echo "$RENDER_JSON" | jq -r ".services.\"$svc\".pid // empty")
        if [ "$PID" = "host" ]; then
            echo "FAIL: $svc: pid=host"
            failed=1
        fi

        IPC=$(echo "$RENDER_JSON" | jq -r ".services.\"$svc\".ipc // empty")
        if [ "$IPC" = "host" ]; then
            echo "FAIL: $svc: ipc=host"
            failed=1
        fi

        SECOPTS=$(echo "$RENDER_JSON" | jq -r ".services.\"$svc\".security_opt // [] | join(\" \")")
        if echo "$SECOPTS" | grep -q "unconfined"; then
            echo "FAIL: $svc: security_opt incluye unconfined"
            failed=1
        fi

        while IFS= read -r src; do
            [ -z "$src" ] && continue
            # Comprobar que src cae dentro de REPO_ROOT respetando limite de directorio:
            # src igual a REPO_ROOT, o REPO_ROOT/<algo>. Rechaza prefijos compartidos
            # tipo /home/.../hefesto-actas-hedgedoc-supabase-evil.
            case "$src/" in
                "$REPO_ROOT"/) ;;
                "$REPO_ROOT"/*) ;;
                *)
                    echo "FAIL: $svc: bind fuera del repo: $src"
                    failed=1
                    ;;
            esac
            case "$src" in
                *docker.sock*)
                    echo "FAIL: $svc: bind a docker.sock"
                    failed=1
                    ;;
            esac
        done < <(echo "$RENDER_JSON" | jq -r ".services.\"$svc\".volumes // [] | .[] | select(.type==\"bind\") | .source")
    done < <(echo "$RENDER_JSON" | jq -r '.services | to_entries[] | select((.value.profiles // []) | length == 0) | .key')

    # Contrato 3 (supabase-pg): DB_NAME y DB_SSLMODE deben estar parametrizados en el compose
    # (referencia ${DB_NAME...} / ${DB_SSLMODE...}) y su valor debe fluir al render vivo
    # (no sirve un "mvp_prueba" hardcoded en cualquier lado).
    for v in DB_NAME DB_SSLMODE; do
        if ! grep -q "\${${v}" "$compose_path"; then
            echo "FAIL: compose no referencia \${${v}} (parametrizacion obligatoria)"
            failed=1
        fi
    done

    DB_NAME_VALUE=$(echo "$RENDER_JSON" | jq -r '.services.app.environment.CMD_DB_DATABASE // empty')
    if [ "$DB_NAME_VALUE" != "mvp_prueba" ]; then
        echo "FAIL: CMD_DB_DATABASE en render = '$DB_NAME_VALUE' (esperado 'mvp_prueba')"
        failed=1
    fi

    # DB_SSLMODE debe estar expuesto al servicio web (lo lee ops/config.cjs).
    DB_SSLMODE_VALUE=$(echo "$RENDER_JSON" | jq -r '.services.app.environment.CMD_DB_SSLMODE // empty')
    if [ "$DB_SSLMODE_VALUE" != "disable" ]; then
        echo "FAIL: CMD_DB_SSLMODE en render = '$DB_SSLMODE_VALUE' (esperado 'disable')"
        failed=1
    fi
done

if [ "$failed" -ne 0 ]; then
    echo "=== coolify-check: FAIL ==="
    exit 1
fi
echo "=== coolify-check: OK ==="