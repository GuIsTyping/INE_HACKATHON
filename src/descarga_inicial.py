"""
Descarga inicial de todos los recursos del proyecto.

Datasets de la plataforma CCPC del INE (ZIPs con CSVs), Estadisticas Censales
a Escalas Geoelectorales 2020 del INEGI (indicadores del censo por seccion),
shapefile municipal de CONABIO/INEGI y documentos informativos del hackaton (PDFs).

Estructura de salida:
    DATA/RAW/ZIPS/                  ZIPs descargados
    DATA/RAW/<dataset>/             CSVs extraidos por dataset
    DATA/RAW/marco_geoestadistico/  Shapefile municipal 2022
    DATA/DOCS/                      PDFs y documentos de referencia

Uso:
    uv run python src/descarga_inicial.py

Autores: Angel David Durazo Bartolini y Jehu Jonathan Ramirez Ramirez
"""

import zipfile
from pathlib import Path

import requests
from tqdm import tqdm

# ---------------------------------------------------------------------------
# 1. Rutas
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
DIR_ZIPS = ROOT / "DATA" / "RAW" / "ZIPS"
DIR_RAW = ROOT / "DATA" / "RAW"
DIR_DOCS = ROOT / "DATA" / "DOCS"
DIR_GEO = ROOT / "DATA" / "RAW" / "marco_geoestadistico"

# ---------------------------------------------------------------------------
# 2. Directorios
# ---------------------------------------------------------------------------

SUBDIRS_RAW = [
    "conteos2009",
    "conteos2012",
    "conteos2015",
    "conteos2018",
    "conteos2021",
    "conteos2024",
    "conteosPJ2025",
    "voto_anticipado_2024",
    "prision_preventiva_2024",
    "eceg_2020",
]


def crear_directorios():
    DIR_ZIPS.mkdir(parents=True, exist_ok=True)
    DIR_DOCS.mkdir(parents=True, exist_ok=True)
    DIR_GEO.mkdir(parents=True, exist_ok=True)
    (ROOT / "DATA" / "PREPROCESSED").mkdir(parents=True, exist_ok=True)
    for d in SUBDIRS_RAW:
        (DIR_RAW / d).mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 3. URLs de datasets (ZIPs)
# ---------------------------------------------------------------------------

DATASETS = {
    "conteos2009": "https://ine.mx/wp-content/uploads/2022/04/DatosAbiertos_DECEyEC_ConteosCensales2009.zip",
    "conteos2012": "https://ine.mx/wp-content/uploads/2022/04/DatosAbiertos_DECEyEC_ConteosCensales2012.zip",
    "conteos2015": "https://ine.mx/wp-content/uploads/2022/04/DatosAbiertos_DECEyEC_ConteosCensales2015.zip",
    "conteos2018": "https://ine.mx/wp-content/uploads/2022/04/DatosAbiertos_DECEyEC_ConteosCensales2018.zip",
    "conteos2021": "https://ine.mx/wp-content/uploads/2022/04/DatosAbiertos_DECEyEC_ConteosCensales2021.zip",
    "conteos2024": "https://ine.mx/wp-content/uploads/2025/08/DatosAbiertos_DECEyEC_ConteosCensales2024.zip",
    "conteosPJ2025": "https://ine.mx/wp-content/uploads/2026/09/DatosAbiertos_DECEyEC_ConteosCensalesPJ2025.zip",
    "voto_anticipado_2024": "https://ine.mx/wp-content/uploads/2025/08/DatosAbiertos_DECEyEC_ConteosCensales_VotoAnticipado2024.zip",
    "prision_preventiva_2024": "https://ine.mx/wp-content/uploads/2025/08/DatosAbiertos_DECEyEC_ConteosCensales_PrisionPreventiva2024.zip",
    "eceg_2020": "https://www.inegi.org.mx/contenidos/programas/ccpv/2020/datosabiertos/geoelectorales/eceg_2020_csv.zip",
}

# ---------------------------------------------------------------------------
# 4. URLs de informacion adicional (PDFs)
# ---------------------------------------------------------------------------

DOCUMENTOS = {
    "Convocatoria_Hackaton.pdf": "https://ine.mx/wp-content/uploads/2026/09/Convocatoria_Hackaton-1.pdf",
    "Carta_declaratoria_decir_verdad.pdf": "https://ine.mx/wp-content/uploads/2026/09/Carta-declaratoria-de-decir-la-verdad_Hackaton.pdf",
    "Carta_cesion_derechos.pdf": "https://ine.mx/wp-content/uploads/2026/09/Carta-de-cesion-de-derechos_Hackaton-1.pdf",
    "Manual_Conteos_Censales_2009_2024.pdf": "https://ine.mx/wp-content/uploads/2025/06/Manual-Conteos-Censales-2009-2024.pdf",
}

# ---------------------------------------------------------------------------
# 4b. URLs de geometrias (Shapefiles)
# ---------------------------------------------------------------------------

GEOMETRIAS = {
    "mun22gw.zip": "http://www.conabio.gob.mx/informacion/gis/maps/geo/mun22gw.zip",
}

# ---------------------------------------------------------------------------
# 5. Funciones de descarga y extraccion
# ---------------------------------------------------------------------------

def descargar(url: str, destino: Path):
    if destino.exists():
        print(f"  Ya existe: {destino.name}")
        return
    print(f"  Descargando {destino.name}...")
    resp = requests.get(url, stream=True, timeout=300)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    with open(destino, "wb") as f:
        with tqdm(total=total, unit="B", unit_scale=True, desc=destino.name) as bar:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
                bar.update(len(chunk))


def extraer_zip(zip_path: Path, destino: Path):
    csvs = list(destino.rglob("*.csv"))
    if csvs:
        print(f"  {destino.name}: ya extraido ({len(csvs)} CSVs)")
        return
    print(f"  Extrayendo {zip_path.name} -> {destino.name}/")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(destino)
    csvs = list(destino.rglob("*.csv"))
    print(f"  {len(csvs)} CSVs extraidos.")

# ---------------------------------------------------------------------------
# 6. Ejecucion
# ---------------------------------------------------------------------------

def main():
    print("=== Creando directorios ===")
    crear_directorios()

    print("\n=== Descargando datasets (ZIPs) ===")
    for nombre, url in DATASETS.items():
        archivo = url.split("/")[-1]
        descargar(url, DIR_ZIPS / archivo)

    print("\n=== Descargando documentos (PDFs) ===")
    for nombre_local, url in DOCUMENTOS.items():
        descargar(url, DIR_DOCS / nombre_local)

    print("\n=== Descargando geometrias (Shapefiles) ===")
    for nombre_local, url in GEOMETRIAS.items():
        descargar(url, DIR_GEO / nombre_local)

    print("\n=== Extrayendo ZIPs ===")
    for nombre, url in DATASETS.items():
        archivo = url.split("/")[-1]
        extraer_zip(DIR_ZIPS / archivo, DIR_RAW / nombre)

    print("\n=== Extrayendo geometrias ===")
    for nombre_local in GEOMETRIAS:
        zip_path = DIR_GEO / nombre_local
        if zip_path.exists():
            extraer_zip(zip_path, DIR_GEO)

    print("\n=== Inventario ===")
    for nombre in DATASETS:
        carpeta = DIR_RAW / nombre
        csvs = list(carpeta.rglob("*.csv"))
        total_mb = sum(f.stat().st_size for f in csvs) / 1024 / 1024
        print(f"  {nombre}: {len(csvs)} CSVs, {total_mb:.1f} MB")

    print("\nDocumentos en DATA/DOCS/:")
    for f in sorted(DIR_DOCS.glob("*.pdf")):
        print(f"  {f.name} ({f.stat().st_size / 1024:.0f} KB)")

    print("\nDescarga inicial completa.")


if __name__ == "__main__":
    main()
