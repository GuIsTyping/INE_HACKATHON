#!/usr/bin/env bash
# ============================================================================
# Pipeline completo: descarga, preprocesamiento, segmentacion y visualizacion.
#
# Levanta el proyecto de cero hasta el servidor local con el mapa interactivo.
# Requisito previo: tener instalado UV (https://docs.astral.sh/uv/getting-started/installation/).
# Si UV no esta disponible, el script intenta instalarlo automaticamente.
#
# Uso:
#     chmod +x ejecutar_pipeline.sh
#     ./ejecutar_pipeline.sh
#
# Autores: Angel David Durazo Bartolini y Jehu Jonathan Ramirez Ramirez
# ============================================================================

set -euo pipefail

ROJO='\033[0;31m'
VERDE='\033[0;32m'
AMARILLO='\033[0;33m'
AZUL='\033[0;34m'
SIN_COLOR='\033[0m'

PUERTO=8765

# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------

paso() {
    echo ""
    echo -e "${AZUL}=== $1 ===${SIN_COLOR}"
}

exito() {
    echo -e "${VERDE}  [OK] $1${SIN_COLOR}"
}

aviso() {
    echo -e "${AMARILLO}  [!] $1${SIN_COLOR}"
}

error() {
    echo -e "${ROJO}  [ERROR] $1${SIN_COLOR}"
    exit 1
}

# ---------------------------------------------------------------------------
# 0. Directorio raiz del proyecto
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
echo "Directorio del proyecto: $SCRIPT_DIR"

# ---------------------------------------------------------------------------
# 1. Verificar e instalar UV
# ---------------------------------------------------------------------------

paso "1/7  Verificando UV"

if command -v uv &> /dev/null; then
    exito "UV encontrado: $(uv --version)"
else
    aviso "UV no encontrado. Instalando..."
    if command -v curl &> /dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
    elif command -v wget &> /dev/null; then
        wget -qO- https://astral.sh/uv/install.sh | sh
    else
        error "Se necesita curl o wget para instalar UV. Instala UV manualmente: https://docs.astral.sh/uv/getting-started/installation/"
    fi
    # Agregar UV al PATH de la sesion actual
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
    if ! command -v uv &> /dev/null; then
        error "No se pudo instalar UV. Instalalo manualmente y vuelve a ejecutar."
    fi
    exito "UV instalado: $(uv --version)"
fi

# ---------------------------------------------------------------------------
# 2. Instalar Python 3.12 y dependencias
# ---------------------------------------------------------------------------

paso "2/7  Configurando entorno (Python 3.12 + dependencias)"

uv python install 3.12 2>/dev/null || true
exito "Python 3.12 disponible"

uv sync
exito "Dependencias instaladas"

# ---------------------------------------------------------------------------
# 3. Crear directorios de datos
# ---------------------------------------------------------------------------

paso "3/7  Creando estructura de directorios"

mkdir -p DATA/RAW/ZIPS
mkdir -p DATA/RAW/marco_geoestadistico
mkdir -p DATA/PREPROCESSED/fichas
mkdir -p DATA/DOCS

exito "Directorios listos"

# ---------------------------------------------------------------------------
# 4. Descarga inicial
# ---------------------------------------------------------------------------

paso "4/7  Descarga de datos (ZIPs, PDFs, shapefile)"
echo "  Esto puede tardar varios minutos en la primera ejecucion..."

uv run python -I src/descarga_inicial.py

exito "Descarga completa"

# ---------------------------------------------------------------------------
# 5. Preprocesamiento
# ---------------------------------------------------------------------------

paso "5/7  Preprocesamiento (consolidacion, historial, ECEG)"
echo "  Consolidacion federal: ~55M filas con PyArrow (puede tardar ~5 min)..."

uv run python -I src/preprocesamiento.py

exito "Preprocesamiento completo"

# ---------------------------------------------------------------------------
# 6. Segmentacion
# ---------------------------------------------------------------------------

paso "6/7  Segmentacion (clases latentes + subperfiles)"
echo "  LCA con 20 inicios por k, bootstrap de estabilidad..."

uv run python -I src/segmentacion.py

exito "Segmentacion completa"

# ---------------------------------------------------------------------------
# 7. Visualizacion
# ---------------------------------------------------------------------------

paso "7/7  Visualizacion (fichas, mapas, tablas)"
echo "  Generando fichas PNG, PDF, mapa estatico e interactivo..."

uv run python -I src/visualizacion.py

exito "Visualizacion completa"

# ---------------------------------------------------------------------------
# Resumen y servidor local
# ---------------------------------------------------------------------------

echo ""
echo -e "${VERDE}============================================${SIN_COLOR}"
echo -e "${VERDE}  Pipeline completo.${SIN_COLOR}"
echo -e "${VERDE}============================================${SIN_COLOR}"
echo ""
echo "Salidas en DATA/PREPROCESSED/fichas/:"
ls -lh DATA/PREPROCESSED/fichas/ 2>/dev/null || echo "  (directorio vacio o no encontrado)"
echo ""
echo -e "${AZUL}Iniciando servidor local en puerto ${PUERTO}...${SIN_COLOR}"
echo -e "Abrir en el navegador: ${VERDE}http://localhost:${PUERTO}/mapa_clases_latentes.html${SIN_COLOR}"
echo "Presiona Ctrl+C para detener el servidor."
echo ""

cd DATA/PREPROCESSED/fichas
uv run python -m http.server "$PUERTO"
