"""
Preprocesamiento de datos - Consolidacion, indicadores de historial y escolaridad.

Etapa 1: Consolida los CSVs extraidos (por descarga_inicial.py) en archivos Parquet.
Etapa 2: Construye tablas de historial de participacion por seccion y por celda
          demografica (seccion x sexo x grupo de edad) con indicadores conductuales.
Etapa 3: Procesa la escolaridad e internet por seccion desde la ECEG 2020.

Entrada: DATA/RAW/ (CSVs extraidos)
Salida:  DATA/PREPROCESSED/
    conteos_federal_2009_2024.parquet   ~55M filas (6 elecciones federales)
    conteos_pj2025.parquet              ~9.8M filas (eleccion judicial 2025)
    voto_anticipado_2024.parquet        3,449 filas
    prision_preventiva_2024.parquet     26,563 filas
    secciones_historial.parquet         ~55k secciones con indicadores
    celdas_historial.parquet            ~657k celdas con indicadores
    secciones_eceg_2020.parquet         ~69k secciones con escolaridad e internet

Uso:
    uv run python src/preprocesamiento.py

Autores: Angel David Durazo Bartolini y Jehu Jonathan Ramirez Ramirez
"""

import gc
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
DIR_RAW = ROOT / "DATA" / "RAW"
DIR_PREPROCESSED = ROOT / "DATA" / "PREPROCESSED"

# ---------------------------------------------------------------------------
# Parametros
# ---------------------------------------------------------------------------

ANOS = [2009, 2012, 2015, 2018, 2021, 2024]
COLS_ANOS = [f"P{a}" for a in ANOS]
PRESIDENCIALES = ["P2012", "P2018", "P2024"]
INTERMEDIAS = ["P2009", "P2015", "P2021"]

CORTES_EDAD = [17, 24, 29, 39, 49, 59, 69, 79, 200]
ETIQUETAS_EDAD = ["18-24", "25-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80+"]

# Tamano minimo de una celda (SV + NV) en cada eleccion para que su tasa sea estable
MIN_VOTANTES = 20

REGIONES = {
    "Noroeste": [2, 3, 8, 10, 25, 26],
    "Noreste": [5, 19, 28],
    "Occidente": [1, 6, 11, 14, 16, 18, 32],
    "Centro": [9, 13, 15, 17, 21, 22, 24, 29],
    "Sur-Sureste": [4, 7, 12, 20, 23, 27, 30, 31],
}
REGION_POR_EDO = {edo: region for region, edos in REGIONES.items() for edo in edos}

FEDERALES = [
    "conteos2009", "conteos2012", "conteos2015",
    "conteos2018", "conteos2021", "conteos2024",
]

# Esquema explicito para el parquet federal: tipos fijos independientes del CSV
SCHEMA_FEDERAL = pa.schema([
    ("AELEC", pa.int64()), ("FELECCION", pa.string()),
    ("EDOCVE", pa.int64()), ("EDONOM", pa.string()),
    ("MPIOCVE", pa.int64()), ("MPIONOM", pa.string()),
    ("SECCIÓN", pa.int64()), ("TIPOSEC", pa.string()),
    ("DEF", pa.string()), ("DEL", pa.string()),
    ("SEXO", pa.int64()), ("EDAD", pa.int64()),
    ("LN", pa.int64()), ("SV", pa.int64()),
    ("NV", pa.int64()), ("NS", pa.int64()),
])

# Columnas de la ECEG que se necesitan
COLUMNAS_ECEG = [
    "ENTIDAD", "SECCIÓN", "POBTOT", "P_15YMAS",
    "P_18YMAS", "P_18YMAS_F", "P_18YMAS_M",
    "GRAPROES", "GRAPROES_F", "GRAPROES_M",
    "P18YM_PB", "P18YM_PB_F", "P18YM_PB_M",
    "VIVPARH_CV", "VPH_INTER",
]


# ===================================================================
# Etapa 1: Consolidacion de CSVs a Parquet
# ===================================================================

def consolidar_csvs(nombre):
    """Lee y concatena todos los CSVs de un dataset extraido."""
    carpeta = DIR_RAW / nombre
    csvs = sorted(carpeta.rglob("*.csv"))
    partes = []
    for csv in tqdm(csvs, desc=nombre):
        # DEF y DEL tienen tipos mixtos: se leen siempre como string
        df = pd.read_csv(csv, encoding="utf-8-sig", dtype={"DEF": str, "DEL": str})
        partes.append(df)
    return pd.concat(partes, ignore_index=True)


def consolidar_federal():
    """Consolida las 6 elecciones federales en un solo Parquet.

    Usa PyArrow ParquetWriter con un row group por ano para evitar cargar
    los ~55M de filas en memoria simultaneamente.
    """
    salida = DIR_PREPROCESSED / "conteos_federal_2009_2024.parquet"
    if salida.exists():
        n = pq.ParquetFile(salida).metadata.num_rows
        print(f"  Ya existe: {salida.name} ({n:,} filas)")
        return

    writer = pq.ParquetWriter(salida, SCHEMA_FEDERAL)
    total = 0
    for nombre in FEDERALES:
        df = consolidar_csvs(nombre)
        n = len(df)
        total += n
        print(f"  {nombre}: {n:,} filas")
        table = pa.Table.from_pandas(df, schema=SCHEMA_FEDERAL, preserve_index=False)
        writer.write_table(table)
        del df, table
        gc.collect()
    writer.close()
    print(f"  Total: {total:,} filas ({salida.stat().st_size / 1024**2:.1f} MB)")


def consolidar_pj2025():
    """Consolida la eleccion del Poder Judicial 2025."""
    salida = DIR_PREPROCESSED / "conteos_pj2025.parquet"
    if salida.exists():
        n = pd.read_parquet(salida, columns=["EDOCVE"]).shape[0]
        print(f"  Ya existe: {salida.name} ({n:,} filas)")
        return

    # PJ2025 usa CJ y DEJ en lugar de DEL; DEF puede tener tipos mixtos
    carpeta = DIR_RAW / "conteosPJ2025"
    csvs = sorted(carpeta.rglob("*.csv"))
    partes = []
    for csv in tqdm(csvs, desc="conteosPJ2025"):
        partes.append(pd.read_csv(csv, encoding="utf-8-sig", dtype={"DEF": str, "CJ": str, "DEJ": str}))
    df = pd.concat(partes, ignore_index=True)
    df.to_parquet(salida, index=False)
    print(f"  conteos_pj2025.parquet: {len(df):,} filas")
    del df


def consolidar_extras():
    """Consolida voto anticipado y prision preventiva (2024)."""
    extras = ["voto_anticipado_2024", "prision_preventiva_2024"]
    for nombre in extras:
        salida = DIR_PREPROCESSED / f"{nombre}.parquet"
        if salida.exists():
            print(f"  Ya existe: {salida.name}")
            continue
        carpeta = DIR_RAW / nombre
        csvs = sorted(carpeta.rglob("*.csv"))
        partes = [pd.read_csv(c, encoding="utf-8-sig") for c in csvs]
        df = pd.concat(partes, ignore_index=True)
        df.to_parquet(salida, index=False)
        print(f"  {salida.name}: {len(df):,} filas")


def etapa_consolidacion():
    """Etapa 1: consolida todos los CSVs en archivos Parquet."""
    print("=== Etapa 1: Consolidacion de CSVs a Parquet ===")
    DIR_PREPROCESSED.mkdir(parents=True, exist_ok=True)

    print("\nDataset federal (2009-2024):")
    consolidar_federal()

    print("\nDataset PJ 2025:")
    consolidar_pj2025()

    print("\nDatasets complementarios:")
    consolidar_extras()
    gc.collect()


# ===================================================================
# Etapa 2: Tablas de historial (secciones y celdas)
# ===================================================================

def indicadores(ancha):
    """Calcula indicadores conductuales a partir de las 6 tasas de participacion.

    - promedio: nivel general de participacion 2009-2024.
    - desviacion: variabilidad entre elecciones.
    - brecha_pres: diferencia entre elecciones presidenciales e intermedias,
      mide la dependencia del tipo de eleccion.
    - tendencia: pendiente en puntos por eleccion (si sube o baja con el tiempo).
    """
    valores = ancha[COLS_ANOS].to_numpy()
    x = np.arange(len(ANOS)) - (len(ANOS) - 1) / 2
    return pd.DataFrame({
        "promedio": valores.mean(axis=1),
        "desviación": valores.std(axis=1, ddof=1),
        "brecha_pres": (
            ancha[PRESIDENCIALES].mean(axis=1).to_numpy()
            - ancha[INTERMEDIAS].mean(axis=1).to_numpy()
        ),
        "tendencia": (
            (valores - valores.mean(axis=1, keepdims=True)) @ x / (x ** 2).sum()
        ),
    }, index=ancha.index)


def construir_historial_secciones(df):
    """Construye la tabla de historial por seccion electoral.

    Solo se conservan secciones con participacion valida en las 6 elecciones.
    Una seccion-ano con SV + NV = 0 tiene todo su padron como NS (cuadernillos
    no disponibles) y se descarta.
    """
    # Agregar a seccion x ano
    sec_ano = df.groupby(["EDOCVE", "SECCIÓN", "AELEC"])[["LN", "SV", "NV"]].sum().reset_index()
    sec_ano["PART"] = sec_ano["SV"] / (sec_ano["SV"] + sec_ano["NV"]) * 100

    # Filtrar secciones con las 6 elecciones
    sec_ano = sec_ano.dropna(subset=["PART"])
    n_anos = sec_ano.groupby(["EDOCVE", "SECCIÓN"])["AELEC"].transform("size")
    sec_ano = sec_ano[n_anos == len(ANOS)]

    # Pivotar a formato ancho
    secciones = sec_ano.pivot(index=["EDOCVE", "SECCIÓN"], columns="AELEC", values="PART")
    secciones.columns = COLS_ANOS
    del sec_ano

    # Indicadores conductuales
    secciones = secciones.join(indicadores(secciones))

    # Atributos de la seccion (tipo y lista nominal 2024)
    attr_2024 = (
        df[df["AELEC"] == 2024]
        .groupby(["EDOCVE", "SECCIÓN"], observed=True)
        .agg(TIPOSEC=("TIPOSEC", "first"), LN2024=("LN", "sum"))
    )
    secciones = secciones.join(attr_2024)
    secciones["REGIÓN"] = secciones.index.get_level_values("EDOCVE").map(REGION_POR_EDO)

    # Participacion PJ 2025 por seccion
    pj = pd.read_parquet(
        DIR_PREPROCESSED / "conteos_pj2025.parquet", columns=["EDOCVE", "SECCIÓN", "SV", "NV"]
    )
    pj = pj.groupby(["EDOCVE", "SECCIÓN"])[["SV", "NV"]].sum()
    pj_part = (pj["SV"] / (pj["SV"] + pj["NV"]) * 100).rename("P_PJ2025")
    pj_part.index = pj_part.index.set_levels([
        pj_part.index.levels[0].astype("int8"),
        pj_part.index.levels[1].astype("int32"),
    ])
    secciones = secciones.join(pj_part)
    del pj, pj_part

    n = len(secciones)
    print(f"  Secciones con historial completo: {n:,}")

    secciones.reset_index().to_parquet(
        DIR_PREPROCESSED / "secciones_historial.parquet", index=False
    )
    return secciones


def construir_historial_celdas(df, attr_2024):
    """Construye la tabla de historial por celda (seccion x sexo x grupo de edad).

    Se exigen las 6 elecciones y al menos MIN_VOTANTES personas (SV + NV) en cada
    una para que la tasa sea estable. La celda no sigue a las mismas personas:
    cada ano el grupo de edad se renueva.
    """
    claves = ["EDOCVE", "SECCIÓN", "SEXO", "GRUPO_EDAD"]

    # Agregar a celda x ano
    cel_ano = df.groupby(claves + ["AELEC"], observed=True)[["SV", "NV"]].sum()
    cel_ano["VOTANTES"] = cel_ano["SV"] + cel_ano["NV"]
    cel_ano["PART"] = cel_ano["SV"] / cel_ano["VOTANTES"] * 100

    # Pivotar y filtrar
    celdas = cel_ano["PART"].unstack("AELEC")
    min_vot = cel_ano["VOTANTES"].unstack("AELEC").min(axis=1)
    celdas.columns = COLS_ANOS
    completas = celdas.notna().all(axis=1)
    grandes = min_vot >= MIN_VOTANTES
    celdas = celdas[completas & grandes]
    del cel_ano, min_vot

    # Indicadores conductuales
    celdas = celdas.join(indicadores(celdas)).reset_index()

    # Tipo de seccion y region
    celdas = celdas.merge(
        attr_2024[["TIPOSEC"]], left_on=["EDOCVE", "SECCIÓN"], right_index=True, how="left"
    )
    celdas["REGIÓN"] = celdas["EDOCVE"].map(REGION_POR_EDO)

    n = len(celdas)
    print(f"  Celdas con historial completo: {n:,}")

    celdas.to_parquet(DIR_PREPROCESSED / "celdas_historial.parquet", index=False)


def etapa_historial():
    """Etapa 2: construye tablas de historial por seccion y por celda."""
    print("\n=== Etapa 2: Historial de participacion ===")

    pq_secciones = DIR_PREPROCESSED / "secciones_historial.parquet"
    pq_celdas = DIR_PREPROCESSED / "celdas_historial.parquet"
    if pq_secciones.exists() and pq_celdas.exists():
        ns = pd.read_parquet(pq_secciones, columns=["EDOCVE"]).shape[0]
        nc = pd.read_parquet(pq_celdas, columns=["EDOCVE"]).shape[0]
        print(f"  Ya existen: secciones ({ns:,}), celdas ({nc:,})")
        return

    # Cargar dataset federal completo
    columnas = ["AELEC", "EDOCVE", "SECCIÓN", "TIPOSEC", "SEXO", "EDAD", "LN", "SV", "NV"]
    tipos = {
        "AELEC": "int16", "EDOCVE": "int8", "SECCIÓN": "int32", "TIPOSEC": "category",
        "SEXO": "int8", "EDAD": "int16", "LN": "int16", "SV": "int16", "NV": "int16",
    }
    print("  Cargando dataset federal...")
    df = pd.read_parquet(
        DIR_PREPROCESSED / "conteos_federal_2009_2024.parquet", columns=columnas
    ).astype(tipos)

    # Excluir SEXO = 2 (no binario, solo 105 personas en 2024)
    df = df[df["SEXO"] < 2]

    # Variables derivadas
    df["GRUPO_EDAD"] = pd.cut(df["EDAD"], bins=CORTES_EDAD, labels=ETIQUETAS_EDAD)
    df["REGIÓN"] = df["EDOCVE"].map(REGION_POR_EDO).astype("category")

    print("\n  Historial por seccion:")
    secciones = construir_historial_secciones(df)

    # Atributos de 2024 para las celdas
    attr_2024 = (
        df[df["AELEC"] == 2024]
        .groupby(["EDOCVE", "SECCIÓN"], observed=True)
        .agg(TIPOSEC=("TIPOSEC", "first"), LN2024=("LN", "sum"))
    )

    print("\n  Historial por celda:")
    construir_historial_celdas(df, attr_2024)

    del df, secciones, attr_2024
    gc.collect()


# ===================================================================
# Etapa 3: Escolaridad e internet (ECEG 2020)
# ===================================================================

def etapa_eceg():
    """Etapa 3: procesa la escolaridad de la ECEG 2020 del INEGI.

    La ECEG contiene indicadores del Censo 2020 por seccion electoral.
    Se extraen: grado promedio de escolaridad (por sexo), porcentaje con
    educacion posbasica (por sexo) y porcentaje de viviendas con internet.
    """
    print("\n=== Etapa 3: Escolaridad e internet (ECEG 2020) ===")

    salida = DIR_PREPROCESSED / "secciones_eceg_2020.parquet"
    if salida.exists():
        n = pd.read_parquet(salida, columns=["EDOCVE"]).shape[0]
        print(f"  Ya existe: {salida.name} ({n:,} filas)")
        return

    archivo = DIR_RAW / "eceg_2020" / "conjunto_de_datos" / "INE_SECCION_2020.csv"
    eceg = pd.read_csv(archivo, encoding="latin1", usecols=COLUMNAS_ECEG)
    eceg = eceg.rename(columns={"ENTIDAD": "EDOCVE"})

    # -6 es codigo de confidencialidad del INEGI; 0 en P_15YMAS indica sin poblacion
    valores = eceg.columns.drop(["EDOCVE", "SECCIÓN"])
    eceg[valores] = eceg[valores].mask(eceg[valores] < 0)
    sin_poblacion = eceg["P_15YMAS"].fillna(0) == 0
    eceg.loc[sin_poblacion, ["GRAPROES", "GRAPROES_F", "GRAPROES_M"]] = np.nan

    # Porcentaje con educacion posbasica (18 anos y mas, por sexo)
    for sufijo in ["", "_F", "_M"]:
        denominador = eceg[f"P_18YMAS{sufijo}"].where(eceg[f"P_18YMAS{sufijo}"] > 0)
        eceg[f"PCT_POSBASICA{sufijo}"] = eceg[f"P18YM_PB{sufijo}"] / denominador * 100

    # Porcentaje de viviendas con internet
    eceg["PCT_INTERNET"] = (
        eceg["VPH_INTER"] / eceg["VIVPARH_CV"].where(eceg["VIVPARH_CV"] > 0) * 100
    )

    columnas_salida = [
        "EDOCVE", "SECCIÓN", "POBTOT", "P_15YMAS", "P_18YMAS",
        "GRAPROES", "GRAPROES_F", "GRAPROES_M",
        "PCT_POSBASICA", "PCT_POSBASICA_F", "PCT_POSBASICA_M", "PCT_INTERNET",
    ]
    eceg[columnas_salida].to_parquet(salida, index=False)
    print(f"  {salida.name}: {len(eceg):,} secciones")
    print(f"  Secciones sin poblacion de 15+: {sin_poblacion.sum()}")


# ===================================================================
# Orquestador
# ===================================================================

def main():
    etapa_consolidacion()
    etapa_historial()
    etapa_eceg()

    print("\n=== Inventario de archivos generados ===")
    for f in sorted(DIR_PREPROCESSED.glob("*.parquet")):
        n = pd.read_parquet(f, columns=[pd.read_parquet(f).columns[0]]).shape[0]
        print(f"  {f.name}: {n:,} filas ({f.stat().st_size / 1024**2:.1f} MB)")
    print("\nPreprocesamiento completo.")


if __name__ == "__main__":
    main()
