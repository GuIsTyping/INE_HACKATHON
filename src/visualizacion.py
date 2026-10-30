"""
Visualizacion - Fichas de perfil, mapa estatico e interactivo.

Genera las visualizaciones finales de la segmentacion:
- Vista general de los 6 perfiles (trayectorias y mapa de burbujas).
- Una ficha por perfil (PNG de alta resolucion) y todas juntas en PDF.
- Mapa estatico del perfil dominante por municipio.
- Mapa interactivo (HTML) con capas estatal y municipal y panel de perfiles.
- Tablas de resumen en CSV.

El cruce de municipios con el shapefile se hace por nombre normalizado, no
por clave: las claves municipales del INE no coinciden con las del INEGI.

Entrada: DATA/PREPROCESSED/ (parquets de preprocesamiento.py y segmentacion.py)
         DATA/RAW/marco_geoestadistico/ (shapefile municipal mun22gw)
Salida:  DATA/PREPROCESSED/fichas/
    vista_general.png
    ficha_perfil_{0..5}.png (200 dpi)
    fichas_perfiles.pdf
    mapa_perfil_dominante.png
    mapa_clases_latentes.html (~12 MB, requiere servirse desde HTTP)
    fichas_resumen_perfiles.csv
    fichas_municipios.csv
    fichas_cruce_municipios.csv

Uso:
    uv run python src/visualizacion.py

Autores: Angel David Durazo Bartolini y Jehu Jonathan Ramirez Ramirez
"""

import difflib
import re
import unicodedata
import warnings
from pathlib import Path

import folium
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyogrio
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch

warnings.filterwarnings("ignore", category=FutureWarning)
plt.rcParams.update({"figure.dpi": 100, "figure.facecolor": "white"})

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
DIR_PREPROCESSED = ROOT / "DATA" / "PREPROCESSED"
DIR_GEO = ROOT / "DATA" / "RAW" / "marco_geoestadistico"
DIR_FICHAS = DIR_PREPROCESSED / "fichas"

# ---------------------------------------------------------------------------
# Parametros
# ---------------------------------------------------------------------------

ELECCIONES = ["P2009", "P2012", "P2015", "P2018", "P2021", "P2024"]
ANOS = [2009, 2012, 2015, 2018, 2021, 2024]
CORTES_EDAD = [17, 24, 29, 39, 49, 59, 69, 79, 200]
ETIQUETAS_EDAD = ["18-24", "25-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80+"]
REGIONES_ORDEN = ["Noroeste", "Noreste", "Occidente", "Centro", "Sur-Sureste"]
LLAVES = ["EDOCVE", "SECCION", "SEXO", "GRUPO_EDAD"]
CORTES_ESC = [0, 8, 10, 12, 30]
TRAMOS_ESC = ["<8", "8-10", "10-12", "12+"]

# Nombres definitivos de los perfiles (elegidos por el equipo)
NOMBRES = {
    0: "Por convencer",
    1: "Constancia que se apaga",
    2: "Generacion en ascenso",
    3: "Paso firme",
    4: "Voces que avanzan",
    5: "Pilar democratico",
}
COLORES_PERFIL = ["#c0392b", "#e67e22", "#d4a017", "#5dade2", "#2e86c1", "#1e8449"]
COLOR_SIN_DATOS = "#d9d9d9"

UMBRAL_CLARA = 0.8
MIN_PERSONAS_ENTIDAD = 20_000
MIN_PERSONAS_MPIO = 1_000
TOL_MUNICIPIO = 0.01
TOL_ESTADO = 0.02
DPI_FICHA = 200

# Umbrales para los descriptores automaticos
UMBRAL_INDICE = 1.4
UMBRAL_SEXO = 60
BANDAS_EDAD = {
    "18-24": "jovenes (18-24)", "25-29": "adultos jovenes (25-39)",
    "30-39": "adultos jovenes (25-39)", "40-49": "adultos (40-59)",
    "50-59": "adultos (40-59)", "60-69": "mayores (60+)",
    "70-79": "mayores (60+)", "80+": "mayores (60+)",
}

EDONOM = {
    1: "Aguascalientes", 2: "Baja California", 3: "Baja California Sur",
    4: "Campeche", 5: "Coahuila", 6: "Colima", 7: "Chiapas", 8: "Chihuahua",
    9: "Ciudad de Mexico", 10: "Durango", 11: "Guanajuato", 12: "Guerrero",
    13: "Hidalgo", 14: "Jalisco", 15: "Mexico", 16: "Michoacan", 17: "Morelos",
    18: "Nayarit", 19: "Nuevo Leon", 20: "Oaxaca", 21: "Puebla", 22: "Queretaro",
    23: "Quintana Roo", 24: "San Luis Potosi", 25: "Sinaloa", 26: "Sonora",
    27: "Tabasco", 28: "Tamaulipas", 29: "Tlaxcala", 30: "Veracruz",
    31: "Yucatan", 32: "Zacatecas",
}

ABREVIATURAS = {"GRAL": "GENERAL", "DR": "DOCTOR"}


# ===================================================================
# Funciones auxiliares
# ===================================================================

def media_ponderada(df, col, por):
    """Promedio ponderado por peso, agrupado por las columnas en `por`."""
    grupos = [df[c] for c in por]
    wx = (df[col] * df["peso"]).groupby(grupos).sum()
    return wx / df["peso"].where(df[col].notna()).groupby(grupos).sum()


def dominante(df, por, col):
    """Categoria con mayor peso dentro de cada grupo."""
    t = df.groupby(por + [col])["peso"].sum()
    return t.groupby(level=por).idxmax().map(lambda x: x[-1])


def resumen(df, por):
    """Resumen ponderado por perfil o subperfil."""
    personas = df.groupby(por)["peso"].sum()
    out = pd.DataFrame({"personas": personas, "pct_pob": personas / df["peso"].sum() * 100})
    pct = ["MUJER", "RURAL_MIXTA", "CLARA", "MENOR_40"]
    for col in ["promedio", "brecha_pres", "tendencia", "P_PJ2025",
                "escolaridad", "pct_posbasica", "pct_internet"] + pct:
        if col in df.columns:
            out[col] = media_ponderada(df, col, por)
    for col in pct:
        if col in out.columns:
            out[col] *= 100
    out["edad_dominante"] = dominante(df, por, "GRUPO_EDAD")
    return out


def sobrerrepresentacion(df, grupo, dim, min_personas):
    """Indice de sobrerrepresentacion de cada perfil/subperfil en cada categoria."""
    t = df.groupby([grupo, dim])["peso"].sum().rename("personas").reset_index()
    t["pct_en_categoria"] = t["personas"] / t.groupby(dim)["personas"].transform("sum") * 100
    pct_nacional = df.groupby(grupo)["peso"].sum() / df["peso"].sum() * 100
    t["índice"] = t["pct_en_categoria"] / t[grupo].map(pct_nacional) * 100
    t = t[t["personas"] >= min_personas]
    return t.sort_values([grupo, "índice"], ascending=[True, False]).reset_index(drop=True)


def normalizar(s):
    """Normaliza un nombre de municipio para cruce: sin acentos, mayusculas, abreviaturas expandidas."""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    return " ".join(ABREVIATURAS.get(p, p) for p in re.sub(r"[^A-Z0-9 ]", " ", s).split())


# ===================================================================
# Carga de datos
# ===================================================================

def cargar_datos():
    """Carga y ensambla todas las tablas necesarias para la visualizacion."""
    print("Cargando datos...")

    # Celdas del historial con peso = SV + NV de 2024
    celdas = pd.read_parquet(DIR_PREPROCESSED / "celdas_historial.parquet")
    celdas["GRUPO_EDAD"] = celdas["GRUPO_EDAD"].astype(str)

    fed24 = pd.read_parquet(
        DIR_PREPROCESSED / "conteos_federal_2009_2024.parquet",
        columns=["EDOCVE", "SECCION", "SEXO", "EDAD", "AELEC", "SV", "NV", "MPIOCVE", "MPIONOM"],
        filters=[("AELEC", "==", 2024)],
    )
    fed24["GRUPO_EDAD"] = pd.cut(fed24["EDAD"], bins=CORTES_EDAD, labels=ETIQUETAS_EDAD)
    fed24["VOTANTES"] = fed24["SV"] + fed24["NV"]
    pesos = (
        fed24.groupby(LLAVES, observed=True)["VOTANTES"]
        .sum().reset_index().rename(columns={"VOTANTES": "peso"})
    )
    pesos["GRUPO_EDAD"] = pesos["GRUPO_EDAD"].astype(str)
    sec_mpio = (
        fed24.groupby(["EDOCVE", "SECCION"])
        .agg(MPIOCVE=("MPIOCVE", "first"), MPIONOM=("MPIONOM", "first"))
        .reset_index()
    )
    del fed24

    secciones = pd.read_parquet(
        DIR_PREPROCESSED / "secciones_historial.parquet",
        columns=["EDOCVE", "SECCION", "P_PJ2025"],
    )
    celdas = (
        celdas.merge(pesos, on=LLAVES, how="left")
        .merge(secciones, on=["EDOCVE", "SECCION"], how="left")
        .merge(sec_mpio, on=["EDOCVE", "SECCION"], how="left")
        .dropna(subset=["peso"])
        .reset_index(drop=True)
    )
    del pesos, secciones, sec_mpio

    # Escolaridad ECEG 2020
    eceg = pd.read_parquet(DIR_PREPROCESSED / "secciones_eceg_2020.parquet")
    celdas = celdas.merge(eceg, on=["EDOCVE", "SECCION"], how="left")
    mujer, hombre = celdas["SEXO"] == 1, celdas["SEXO"] == 0
    celdas["escolaridad"] = np.select(
        [mujer, hombre], [celdas["GRAPROES_F"], celdas["GRAPROES_M"]], celdas["GRAPROES"]
    )
    celdas["pct_posbasica"] = np.select(
        [mujer, hombre], [celdas["PCT_POSBASICA_F"], celdas["PCT_POSBASICA_M"]], celdas["PCT_POSBASICA"]
    )
    celdas["pct_internet"] = celdas["PCT_INTERNET"]
    celdas["tramo_esc"] = pd.cut(
        celdas["escolaridad"], CORTES_ESC, labels=TRAMOS_ESC, right=False
    ).astype(str)
    celdas = celdas.drop(columns=eceg.columns.drop(["EDOCVE", "SECCION"]))
    del eceg

    # Variables derivadas
    celdas["MUJER"] = (celdas["SEXO"] == 1).astype(float)
    celdas["RURAL_MIXTA"] = (celdas["TIPOSEC"].astype(str) != "U").astype(float)
    celdas["MENOR_40"] = celdas["GRUPO_EDAD"].isin(ETIQUETAS_EDAD[:3]).astype(float)
    celdas["entidad"] = celdas["EDOCVE"].map(EDONOM)

    # Perfiles y subperfiles
    lca = pd.read_parquet(
        DIR_PREPROCESSED / "celdas_clases_latentes.parquet",
        columns=LLAVES + ["clase", "prob_clase"],
    )
    sub = pd.read_parquet(
        DIR_PREPROCESSED / "celdas_subperfiles.parquet",
        columns=LLAVES + ["subperfil"],
    )
    celdas = celdas.merge(lca, on=LLAVES, how="left").merge(sub, on=LLAVES, how="left")

    # Renumerar clases por promedio de participacion (0 = menor)
    orden = media_ponderada(celdas, "promedio", ["clase"]).sort_values().index
    celdas["perfil"] = celdas["clase"].map({old: new for new, old in enumerate(orden)}).astype(int)
    celdas["CLARA"] = (celdas["prob_clase"] >= UMBRAL_CLARA).astype(float)

    K = celdas["perfil"].nunique()
    print(f"  Celdas: {len(celdas):,}  perfiles: {K}  subperfiles: {celdas['subperfil'].nunique()}")
    return celdas, K


# ===================================================================
# Descriptores automaticos de perfil
# ===================================================================

def generar_descriptores(celdas, res_perfil, K):
    """Genera un descriptor textual para cada perfil.

    Nivel por promedio (baja/media/media-alta/alta) y rasgos por forma
    (moviliza en presidenciales, estable, en ascenso, en descenso).
    Se agregan rasgos demograficos solo si destacan frente al nacional.
    """
    w_total = celdas["peso"].sum()

    def nombre_auto(r):
        if r["promedio"] < 45:
            partes = ["Baja participacion"]
        elif r["promedio"] < 55:
            partes = ["Participacion media"]
        elif r["promedio"] < 65:
            partes = ["Participacion media-alta"]
        else:
            partes = ["Alta participacion"]
        if r["brecha_pres"] >= 17:
            partes.append("se moviliza en presidenciales")
        elif r["brecha_pres"] <= 10:
            partes.append("estable entre elecciones")
        if r["tendencia"] >= 2.5:
            partes.append("en ascenso")
        elif r["tendencia"] <= -1:
            partes.append("en descenso")
        return ", ".join(partes)

    def indices(col):
        t = celdas.groupby(["perfil", col])["peso"].sum().unstack(fill_value=0)
        pct = t.div(t.sum(axis=1), axis=0)
        return pct / (celdas.groupby(col)["peso"].sum() / w_total), pct * 100

    celdas["banda_edad"] = celdas["GRUPO_EDAD"].map(BANDAS_EDAD)
    celdas["sexo_txt"] = celdas["SEXO"].map({0: "hombres", 1: "mujeres"})
    idx_edad, _ = indices("banda_edad")
    _, pct_sexo = indices("sexo_txt")
    idx_tipo, _ = indices(celdas["TIPOSEC"].astype(str).rename("tipo_txt"))
    idx_region, _ = indices("REGION")

    def rasgos_demograficos(p):
        rasgos = []
        if idx_edad.loc[p].max() >= UMBRAL_INDICE:
            rasgos.append(idx_edad.loc[p].idxmax())
        if pct_sexo.loc[p].max() >= UMBRAL_SEXO:
            rasgos.append(f"mayoria {pct_sexo.loc[p].idxmax()}")
        if "R" in idx_tipo.columns and idx_tipo.loc[p, "R"] >= UMBRAL_INDICE:
            rasgos.append("mas rural")
        if idx_region.loc[p].max() >= UMBRAL_INDICE:
            rasgos.append(f"fuerte en el {idx_region.loc[p].idxmax()}")
        return rasgos

    descriptores = {}
    for p, r in res_perfil.iterrows():
        descriptores[p] = " · ".join([nombre_auto(r)] + rasgos_demograficos(p))

    return descriptores


# ===================================================================
# Cruce municipal por nombre
# ===================================================================

def cruzar_municipios(celdas, gdf_mun):
    """Cruza municipios INE con shapefile INEGI por nombre normalizado.

    Tres pasos: exacto, por contenido (un nombre contiene al otro) y
    aproximado (difflib >= 0.6). Los nombres ambiguos se dejan sin cruce.
    """
    mun_ine = celdas.groupby(["EDOCVE", "MPIOCVE", "MPIONOM"], as_index=False)["peso"].sum()
    mun_ine["nom"] = mun_ine["MPIONOM"].map(normalizar)
    geo = gdf_mun[["EDOCVE", "CVEGEO", "NOMGEO"]].assign(nom=gdf_mun["NOMGEO"].map(normalizar))

    geo_unicos = geo.drop_duplicates(["EDOCVE", "nom"], keep=False)
    ine_unico = ~mun_ine.duplicated(["EDOCVE", "nom"], keep=False).to_numpy()
    cruce = mun_ine.merge(geo_unicos[["EDOCVE", "nom", "CVEGEO"]], on=["EDOCVE", "nom"], how="left")
    cruce.loc[~ine_unico, "CVEGEO"] = np.nan
    cruce["método"] = np.where(cruce["CVEGEO"].notna(), "exacto", "sin cruce")

    for i in cruce.index[cruce["CVEGEO"].isna() & ine_unico]:
        e, nom = cruce.at[i, "EDOCVE"], cruce.at[i, "nom"]
        libres = geo_unicos[
            (geo_unicos["EDOCVE"] == e)
            & ~geo_unicos["CVEGEO"].isin(cruce["CVEGEO"].dropna())
        ]
        contiene = libres[libres["nom"].map(lambda x, n=nom: n in x or x in n)]
        if len(contiene) == 1:
            cruce.at[i, "CVEGEO"] = contiene["CVEGEO"].iloc[0]
            cruce.at[i, "método"] = "contenido"
            continue
        if len(contiene) > 1:
            continue
        cand = difflib.get_close_matches(nom, libres["nom"].tolist(), n=1, cutoff=0.6)
        if cand:
            cruce.at[i, "CVEGEO"] = libres.loc[libres["nom"] == cand[0], "CVEGEO"].iloc[0]
            cruce.at[i, "método"] = "aproximado"

    cruce = cruce.merge(geo[["CVEGEO", "NOMGEO"]], on="CVEGEO", how="left")
    print(f"  Cruce: {cruce['método'].value_counts().to_dict()}")
    return cruce


# ===================================================================
# Vista general
# ===================================================================

def generar_vista_general(res_perfil, tray_perfil, nac_tray, K):
    """Trayectorias de los 6 perfiles y mapa de burbujas (nivel vs brecha)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6.5), gridspec_kw={"width_ratios": [1.3, 1]})

    ax1.plot(ANOS, nac_tray, "s--", color="#999", linewidth=1.5, label="Nacional")
    for p in range(K):
        ax1.plot(ANOS, tray_perfil.loc[p].to_numpy(), "o-", color=COLORES_PERFIL[p], linewidth=2.5,
                 label=f"P{p} ({res_perfil.loc[p, 'pct_pob']:.0f}%)")
    ax1.set_xticks(ANOS)
    ax1.set_ylabel("% participacion (ponderada)")
    ax1.set_title("Trayectoria de participacion por perfil")
    ax1.grid(axis="y", alpha=0.3)
    ax1.legend(fontsize=9, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.08), frameon=False)

    for p, r in res_perfil.iterrows():
        ax2.scatter(r["promedio"], r["brecha_pres"], s=r["pct_pob"] * 120,
                    color=COLORES_PERFIL[p], alpha=0.85, edgecolor="#333", linewidth=0.8)
        ax2.annotate(f"P{p}", (r["promedio"], r["brecha_pres"]), ha="center", va="center",
                     fontsize=11, fontweight="bold", color="white")
    ax2.set_xlabel("Promedio de participacion 2009-2024 (%)")
    ax2.set_ylabel("Brecha presidencial (puntos)")
    ax2.set_title("Nivel contra sensibilidad a presidenciales")
    ax2.grid(alpha=0.3)
    ax2.margins(0.15)

    leyenda = "\n".join(f"P{p}: {NOMBRES[p]}" for p in range(K))
    fig.text(0.5, -0.02, leyenda, ha="center", va="top", fontsize=10, color="#333")
    plt.tight_layout()
    fig.savefig(DIR_FICHAS / "vista_general.png", dpi=DPI_FICHA, bbox_inches="tight")
    plt.close(fig)
    print("  vista_general.png")


# ===================================================================
# Mapa estatico
# ===================================================================

def generar_mapa_estatico(gmun, gdf_edo, K):
    """Mapa del perfil dominante por municipio (gris = sin datos)."""
    fig, ax = plt.subplots(figsize=(15, 10))
    gmun.plot(ax=ax, color=COLOR_SIN_DATOS, linewidth=0)
    for p in range(K):
        sel = gmun[gmun["suficiente"] & (gmun["perfil_dom"] == p)]
        sel.plot(ax=ax, color=COLORES_PERFIL[p], linewidth=0)
    gdf_edo.boundary.plot(ax=ax, color="white", linewidth=0.7)
    ax.legend(
        handles=[Patch(color=COLORES_PERFIL[p], label=f"P{p}: {NOMBRES[p]}") for p in range(K)]
        + [Patch(color=COLOR_SIN_DATOS, label="Sin datos suficientes")],
        loc="lower left", fontsize=9, frameon=False,
    )
    ax.set_title("Perfil dominante por municipio", fontsize=14)
    ax.set_axis_off()
    plt.tight_layout()
    fig.savefig(DIR_FICHAS / "mapa_perfil_dominante.png", dpi=DPI_FICHA, bbox_inches="tight")
    plt.close(fig)
    print("  mapa_perfil_dominante.png")


# ===================================================================
# Fichas de perfil (PNG + PDF)
# ===================================================================

def barras_vs_nacional(ax, etiquetas, valores, nacional, color, titulo):
    """Barras horizontales comparando perfil (color) con nacional (gris)."""
    yp = np.arange(len(etiquetas))
    ax.barh(yp, nacional, color="#e0e0e0", height=0.7)
    ax.barh(yp, valores, color=color, alpha=0.85, height=0.45)
    for i, (v, n) in enumerate(zip(valores, nacional)):
        ax.text(max(v, n) + 0.5, i, f"{v:.1f} ({v - n:+.1f})", va="center", fontsize=8)
    ax.set_yticks(yp, etiquetas)
    ax.invert_yaxis()
    ax.set_xlabel("% del perfil")
    ax.set_title(titulo, fontsize=11)
    ax.set_xlim(0, max(max(valores), max(nacional)) * 1.35)


def panel_metricas(ax, r, n_sub, nac_esc, nac_internet):
    """Panel de texto con las metricas clave del perfil."""
    ax.axis("off")
    items = [
        ("PARTICIPACION", None),
        ("Promedio 2009-2024", f"{r['promedio']:.1f}%"),
        ("Brecha presidencial", f"{r['brecha_pres']:+.1f} pts"),
        ("Tendencia", f"{r['tendencia']:+.2f} pts/elec."),
        ("Judicial 2025", f"{r['P_PJ2025']:.1f}%"),
        ("COMPOSICION", None),
        ("Mujeres", f"{r['MUJER']:.0f}%"),
        ("Menores de 40 anos", f"{r['MENOR_40']:.0f}%"),
        ("Seccion rural o mixta", f"{r['RURAL_MIXTA']:.0f}%"),
        ("CONTEXTO DE LA SECCION", None),
        ("Escolaridad (grados)", f"{r['escolaridad']:.1f} (nac. {nac_esc:.1f})"),
        ("Con educacion posbasica", f"{r['pct_posbasica']:.0f}%"),
        ("Viviendas con internet", f"{r['pct_internet']:.0f}% (nac. {nac_internet:.0f}%)"),
        ("MODELO", None),
        ("Asignacion clara (p >= 0.8)", f"{r['CLARA']:.0f}%"),
        ("Subperfiles", f"{n_sub}"),
    ]
    y = 0.98
    for etiqueta, valor in items:
        if valor is None:
            ax.text(0.02, y, etiqueta, transform=ax.transAxes, fontsize=8,
                    fontweight="bold", color="#999")
            y -= 0.055
        else:
            ax.text(0.06, y, etiqueta, transform=ax.transAxes, fontsize=10, color="#555")
            ax.text(0.98, y, valor, transform=ax.transAxes, fontsize=11, fontweight="bold",
                    ha="right", color="#222")
            y -= 0.06


def tabla_subperfiles(ax, p, res_sub, ent_sub, color):
    """Tabla con los subperfiles del perfil p."""
    ax.axis("off")
    subs = res_sub.loc[p]
    filas = []
    for s, rs in subs.iterrows():
        top = ent_sub.loc[ent_sub["subperfil"] == s, "entidad"].head(2).tolist()
        filas.append([
            s, f"{rs['personas'] / subs['personas'].sum() * 100:.0f}%",
            f"{rs['promedio']:.1f}", f"{rs['brecha_pres']:+.1f}", f"{rs['tendencia']:+.1f}",
            f"{rs['MUJER']:.0f}%", rs["edad_dominante"], f"{rs['escolaridad']:.1f}",
            ", ".join(top),
        ])
    tabla = ax.table(
        cellText=filas,
        colLabels=["Subperfil", "% perfil", "Prom.", "Brecha", "Tend.", "Mujeres",
                    "Edad dom.", "Escolaridad", "Entidades sobrerrepresentadas"],
        colWidths=[0.08, 0.08, 0.07, 0.07, 0.07, 0.08, 0.09, 0.09, 0.32],
        loc="upper center", cellLoc="center",
    )
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(9)
    tabla.scale(1, 1.7)
    for (i, _), celda in tabla.get_celld().items():
        celda.set_edgecolor("#ddd")
        if i == 0:
            celda.set_facecolor(color)
            celda.set_text_props(color="white", fontweight="bold")
    ax.set_title("Subperfiles", fontsize=11)


def generar_fichas(celdas, res_perfil, res_sub, tray_perfil, nac_tray,
                   nac_edad, nac_reg, nac_esc_tramo, nac_esc, nac_internet,
                   ent_perfil, ent_sub, gmun, gdf_edo, descriptores, K):
    """Genera una ficha PNG por perfil y las agrupa en un PDF."""
    with PdfPages(DIR_FICHAS / "fichas_perfiles.pdf") as pdf:
        for p in range(K):
            r = res_perfil.loc[p]
            color = COLORES_PERFIL[p]
            dp = celdas[celdas["perfil"] == p]
            n_sub = res_sub.loc[p].shape[0]

            fig = plt.figure(figsize=(16, 20), facecolor="white")
            gs = fig.add_gridspec(4, 3, height_ratios=[1, 1, 1.1, 0.7], hspace=0.32, wspace=0.32,
                                  top=0.92, bottom=0.02, left=0.09, right=0.97)
            fig.suptitle(f"Perfil {p}: {NOMBRES[p]}", fontsize=18, fontweight="bold",
                         color=color, y=0.985)
            fig.text(0.5, 0.958, descriptores[p], ha="center", fontsize=12, style="italic", color="#333")
            fig.text(0.5, 0.94,
                     f"{r['personas']:,.0f} personas ({r['pct_pob']:.1f}% de la lista nominal analizada)"
                     f"   |   edad dominante {r['edad_dominante']}   |   {r['MUJER']:.0f}% mujeres"
                     f"   |   {r['escolaridad']:.1f} grados de escolaridad",
                     ha="center", fontsize=11, color="#555")

            # Trayectoria
            ax = fig.add_subplot(gs[0, :2])
            tray = tray_perfil.loc[p].to_numpy()
            ax.plot(ANOS, nac_tray, "s--", color="#aaa", linewidth=1.5, label="Nacional")
            ax.plot(ANOS, tray, "o-", color=color, linewidth=2.8, markersize=8, label=f"Perfil {p}")
            ax.fill_between(ANOS, tray, nac_tray, color=color, alpha=0.08)
            for a, v in zip(ANOS, tray):
                ax.annotate(f"{v:.1f}", (a, v), textcoords="offset points", xytext=(0, 9),
                            ha="center", fontsize=9, fontweight="bold")
            ax.set_xticks(ANOS)
            ax.set_ylabel("% participacion")
            ax.set_ylim(max(0, min(tray.min(), min(nac_tray)) - 8),
                         min(100, max(tray.max(), max(nac_tray)) + 8))
            ax.set_title("Trayectoria 2009-2024", fontsize=11)
            ax.grid(axis="y", alpha=0.3)
            ax.legend(loc="lower right", fontsize=9)

            # Metricas
            panel_metricas(fig.add_subplot(gs[0, 2]), r, n_sub, nac_esc, nac_internet)

            # Edad
            edad = dp.groupby("GRUPO_EDAD")["peso"].sum().reindex(ETIQUETAS_EDAD, fill_value=0)
            edad = edad / dp["peso"].sum() * 100
            barras_vs_nacional(fig.add_subplot(gs[1, 0]), ETIQUETAS_EDAD,
                               edad.to_numpy(), nac_edad.to_numpy(), color, "Edad (gris = nacional)")

            # Region
            reg = dp.groupby("REGION")["peso"].sum().reindex(REGIONES_ORDEN, fill_value=0)
            reg = reg / dp["peso"].sum() * 100
            barras_vs_nacional(fig.add_subplot(gs[1, 1]), REGIONES_ORDEN,
                               reg.to_numpy(), nac_reg.to_numpy(), color, "Region (gris = nacional)")

            # Escolaridad
            esc = dp.groupby("tramo_esc")["peso"].sum().reindex(TRAMOS_ESC, fill_value=0)
            esc = esc / esc.sum() * 100
            barras_vs_nacional(fig.add_subplot(gs[1, 2]),
                               [f"{t} grados" for t in TRAMOS_ESC], esc.to_numpy(),
                               nac_esc_tramo.to_numpy(), color,
                               "Escolaridad de la seccion (gris = nacional)")

            # Mapa de presencia
            ax = fig.add_subplot(gs[2, 1:])
            col = f"pct_{p}"
            cmap = LinearSegmentedColormap.from_list(f"p{p}", ["#f4f4f4", color])
            gmun.plot(ax=ax, color=COLOR_SIN_DATOS, linewidth=0)
            gmun[gmun["suficiente"]].plot(ax=ax, column=col, cmap=cmap, vmin=0,
                                          vmax=float(np.nanpercentile(gmun[col], 98)), linewidth=0)
            gdf_edo.boundary.plot(ax=ax, color="white", linewidth=0.3)
            ax.set_axis_off()
            ax.set_title("Presencia por municipio (% de su poblacion)", fontsize=11)

            # Entidades sobrerrepresentadas
            ax = fig.add_subplot(gs[2, 0])
            top = ent_perfil[ent_perfil["perfil"] == p].head(8)
            yp = np.arange(len(top))
            ax.barh(yp, top["índice"], color=color, alpha=0.85, height=0.6)
            ax.axvline(100, color="#555", linestyle="--", linewidth=1)
            for i, v in enumerate(top["índice"]):
                ax.text(v + 3, i, f"{v:.0f}", va="center", fontsize=9)
            ax.set_yticks(yp, top["entidad"].replace({"Ciudad de Mexico": "CDMX"}))
            ax.invert_yaxis()
            ax.set_xlim(0, top["índice"].max() * 1.2)
            ax.set_title("Entidades sobrerrepresentadas (100 = nacional)", fontsize=11)

            # Tabla de subperfiles
            tabla_subperfiles(fig.add_subplot(gs[3, :]), p, res_sub, ent_sub, color)

            fig.savefig(DIR_FICHAS / f"ficha_perfil_{p}.png", dpi=DPI_FICHA)
            pdf.savefig(fig)
            plt.close(fig)
            print(f"  ficha_perfil_{p}.png")

    print("  fichas_perfiles.pdf")


# ===================================================================
# Mapa interactivo (HTML con folium)
# ===================================================================

def barras_html(r, K):
    """Barras de composicion por perfil para popups del mapa."""
    html = '<table style="width:100%;border-collapse:collapse;margin-top:4px;">'
    for p in range(K):
        v = r.get(f"pct_{p}", 0) or 0
        c = COLORES_PERFIL[p]
        html += (
            f'<tr><td style="font-size:10px;width:24px;"><b style="color:{c};">P{p}</b></td>'
            f'<td><div style="background:{c};height:9px;width:{max(1, int(v * 1.4))}px;'
            f'border-radius:2px;"></div></td>'
            f'<td style="font-size:10px;width:34px;text-align:right;">{v:.0f}%</td></tr>'
        )
    return html + "</table>"


def popup_municipio(r, K):
    """Popup HTML para capa municipal."""
    if not r["suficiente"]:
        return (f'<div style="font-family:Arial;font-size:12px;"><b>{r["NOMGEO"]}</b><br>'
                f'<span style="color:#999;">Sin datos suficientes</span></div>')
    s = r["subperfil_dom"]
    return (
        f'<div style="font-family:Arial;font-size:12px;width:230px;">'
        f'<b style="font-size:13px;">{r["NOMGEO"]}</b><br>'
        f'<span style="color:#666;">{EDONOM[r["EDOCVE"]]}</span><br>'
        f'{r["personas"]:,.0f} personas | participacion media {r["promedio"]:.1f}%<br>'
        f'Escolaridad media {r["escolaridad"]:.1f} grados | '
        f'{r["pct_internet"]:.0f}% viviendas con internet<br>'
        f'{barras_html(r, K)}'
        f'<div style="margin-top:4px;font-size:11px;">Subperfil dominante: <b>{s}</b> '
        f'({r["pct_subperfil_dom"]:.0f}%)</div></div>'
    )


def popup_entidad(r, K):
    """Popup HTML para capa estatal."""
    return (
        f'<div style="font-family:Arial;font-size:12px;width:230px;">'
        f'<b style="font-size:13px;">{EDONOM[r["EDOCVE"]]}</b><br>'
        f'{r["personas"]:,.0f} personas | participacion media {r["promedio"]:.1f}%<br>'
        f'Escolaridad media {r["escolaridad"]:.1f} grados | '
        f'{r["pct_internet"]:.0f}% viviendas con internet<br>'
        f'{barras_html(r, K)}</div>'
    )


def _svg_trayectoria(tray, nac_t, color, ancho=270, alto=48):
    """SVG inline de la trayectoria para el panel del mapa."""
    vmin = min(min(tray), min(nac_t)) - 3
    vmaxt = max(max(tray), max(nac_t)) + 3
    rng = vmaxt - vmin or 1

    def pts(vals):
        return " ".join(
            f"{i/(len(vals)-1)*(ancho-16)+8:.1f},{alto-(v-vmin)/rng*(alto-10)-5:.1f}"
            for i, v in enumerate(vals)
        )

    svg = (
        f'<svg width="{ancho}" height="{alto+14}" style="display:block;">'
        f'<polyline points="{pts(nac_t)}" fill="none" stroke="#ccc" '
        f'stroke-width="1.5" stroke-dasharray="4,3"/>'
        f'<polyline points="{pts(tray)}" fill="none" stroke="{color}" stroke-width="2.5"/>'
    )
    for i, v in enumerate(tray):
        x = i / (len(tray) - 1) * (ancho - 16) + 8
        y = alto - (v - vmin) / rng * (alto - 10) - 5
        svg += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="{color}"/>'
    for i, a in enumerate(ANOS):
        x = i / (len(ANOS) - 1) * (ancho - 16) + 8
        svg += f'<text x="{x:.0f}" y="{alto+11}" text-anchor="middle" font-size="7" fill="#aaa">{a}</text>'
    svg += "</svg>"
    return svg


def _svg_barras(etiquetas, vals, nac, color, ancho=270, ml=58):
    """SVG inline de barras horizontales comparativas."""
    h = 14
    mr = 40
    wb = ancho - ml - mr
    alto = len(etiquetas) * h + 2
    vmax = max(max(vals), max(nac), 0.1) * 1.15
    svg = f'<svg width="{ancho}" height="{alto}" style="display:block;">'
    for i, (et, v, n) in enumerate(zip(etiquetas, vals, nac)):
        y = i * h
        svg += (
            f'<rect x="{ml}" y="{y}" width="{n/vmax*wb:.1f}" height="{h-2}" fill="#e0e0e0" rx="2"/>'
            f'<rect x="{ml}" y="{y+2}" width="{v/vmax*wb:.1f}" height="{h-6}" fill="{color}" '
            f'opacity="0.8" rx="2"/>'
            f'<text x="{ml-3}" y="{y+h//2+1}" text-anchor="end" font-size="8" fill="#666">{et}</text>'
            f'<text x="{ml+wb+3}" y="{y+h//2+1}" font-size="8" fill="#444">{v:.1f}%</text>'
        )
    svg += "</svg>"
    return svg


def _svg_genero(pct_m, color, ancho=270):
    """SVG inline de la barra de genero."""
    pct_h = 100 - pct_m
    wm = pct_m / 100 * ancho
    svg = (
        f'<svg width="{ancho}" height="20" style="display:block;">'
        f'<rect x="0" y="0" width="{ancho}" height="16" fill="#7caed4" rx="4"/>'
        f'<rect x="0" y="0" width="{wm:.1f}" height="16" fill="{color}" rx="4"/>'
    )
    if pct_m > 12:
        svg += (f'<text x="{wm/2:.0f}" y="12" text-anchor="middle" font-size="9" '
                f'fill="white" font-weight="bold">Mujeres {pct_m:.0f}%</text>')
    if pct_h > 12:
        svg += (f'<text x="{(wm+ancho)/2:.0f}" y="12" text-anchor="middle" font-size="9" '
                f'fill="white" font-weight="bold">Hombres {pct_h:.0f}%</text>')
    svg += "</svg>"
    return svg


def panel_html(res_perfil, tray_perfil, nac_tray, descriptores,
               dist_edad, dist_region, dist_esc, nac_edad, nac_reg, nac_esc_tramo, K):
    """Panel HTML desplegable con los 6 perfiles para el mapa interactivo."""
    css = (
        '<style>'
        '.pp details summary::-webkit-details-marker{display:none}'
        '.pp details summary::marker{content:"";display:none}'
        '.pp details summary{list-style:none}'
        '.pp details[open] .fl{transform:rotate(180deg)}'
        '.pp .fl{transition:transform .2s;display:inline-block}'
        '.pp::-webkit-scrollbar{width:5px}'
        '.pp::-webkit-scrollbar-thumb{background:#ccc;border-radius:3px}'
        '</style>'
    )
    html = (
        css
        + '<div class="pp" style="position:fixed;bottom:20px;left:10px;z-index:1000;'
        'background:white;border-radius:10px;box-shadow:0 2px 12px rgba(0,0,0,.25);'
        'font-family:Arial,sans-serif;font-size:11px;max-height:78vh;width:340px;'
        'overflow-y:auto;scrollbar-width:thin;">'
        '<div style="position:sticky;top:0;background:white;padding:10px 14px 8px;'
        'font-weight:bold;font-size:13px;border-bottom:1px solid #eee;'
        'border-radius:10px 10px 0 0;z-index:1;">Perfiles de participacion</div>'
        '<div style="padding:6px 10px 10px;">'
    )
    nac_e = nac_edad
    nac_r = nac_reg
    nac_es = nac_esc_tramo

    for p, r in res_perfil.iterrows():
        c = COLORES_PERFIL[p]
        tray = tray_perfil.loc[p].values.tolist()

        html += (
            f'<details style="margin-bottom:5px;border-left:4px solid {c};'
            f'border-radius:0 6px 6px 0;background:#fafafa;">'
            f'<summary style="cursor:pointer;padding:7px 10px;display:flex;'
            f'align-items:center;gap:8px;">'
            f'<span style="flex:1;">'
            f'<b style="color:{c};font-size:12px;">P{p}</b> '
            f'<b style="font-size:11px;">{NOMBRES[p]}</b><br>'
            f'<span style="color:#777;font-size:10px;">'
            f'{r["personas"]:,.0f} ({r["pct_pob"]:.1f}%) &middot; '
            f'Prom. {r["promedio"]:.1f}%</span></span>'
            f'<span class="fl" style="color:#aaa;font-size:10px;">&#9660;</span>'
            f'</summary>'
            f'<div style="padding:6px 10px 10px;background:white;'
            f'border-top:1px solid #f0f0f0;font-size:10px;">'
            f'<div style="color:#555;font-style:italic;margin-bottom:6px;'
            f'line-height:1.3;">{descriptores[p]}</div>'
        )

        # Metricas compactas
        html += (
            '<div style="display:flex;gap:4px;margin-bottom:8px;">'
            f'<div style="flex:1;background:#f5f5f5;border-radius:5px;padding:5px 4px;text-align:center;">'
            f'<div style="font-size:7px;color:#999;text-transform:uppercase;">Promedio</div>'
            f'<div style="font-size:14px;font-weight:bold;color:{c};">{r["promedio"]:.1f}%</div></div>'
            f'<div style="flex:1;background:#f5f5f5;border-radius:5px;padding:5px 4px;text-align:center;">'
            f'<div style="font-size:7px;color:#999;text-transform:uppercase;">Brecha</div>'
            f'<div style="font-size:14px;font-weight:bold;color:{c};">{r["brecha_pres"]:+.1f}</div></div>'
            f'<div style="flex:1;background:#f5f5f5;border-radius:5px;padding:5px 4px;text-align:center;">'
            f'<div style="font-size:7px;color:#999;text-transform:uppercase;">Tendencia</div>'
            f'<div style="font-size:14px;font-weight:bold;color:{c};">{r["tendencia"]:+.1f}</div></div>'
            '</div>'
        )

        # Graficos SVG inline
        html += (
            f'<div style="margin-bottom:8px;"><div style="font-size:9px;color:#999;margin-bottom:2px;">'
            f'Trayectoria 2009-2024 <span style="color:#ccc;">gris = nacional</span></div>'
            f'{_svg_trayectoria(tray, nac_tray, c)}</div>'
            f'<div style="margin-bottom:8px;"><div style="font-size:9px;color:#999;margin-bottom:2px;">'
            f'Genero</div>{_svg_genero(r["MUJER"], c)}</div>'
            f'<div style="margin-bottom:8px;"><div style="font-size:9px;color:#999;margin-bottom:2px;">'
            f'Edad <span style="color:#ccc;">gris = nacional</span></div>'
            f'{_svg_barras(ETIQUETAS_EDAD, dist_edad[p], nac_e, c, ml=45)}</div>'
            f'<div style="margin-bottom:8px;"><div style="font-size:9px;color:#999;margin-bottom:2px;">'
            f'Region <span style="color:#ccc;">gris = nacional</span></div>'
            f'{_svg_barras(REGIONES_ORDEN, dist_region[p], nac_r, c, ml=72)}</div>'
            f'<div style="margin-bottom:8px;"><div style="font-size:9px;color:#999;margin-bottom:2px;">'
            f'Escolaridad <span style="color:#ccc;">gris = nacional</span></div>'
            f'{_svg_barras([f"{t} gr." for t in TRAMOS_ESC], dist_esc[p], nac_es, c, ml=50)}'
            f'<div style="margin-top:3px;color:#666;">{r["escolaridad"]:.1f} grados prom. &middot; '
            f'{r["pct_posbasica"]:.0f}% posbasica &middot; {r["pct_internet"]:.0f}% internet</div></div>'
        )

        html += (
            f'<div style="color:#777;font-size:9px;border-top:1px solid #f0f0f0;'
            f'padding-top:4px;">Edad dom. {r["edad_dominante"]} &middot; '
            f'{r["RURAL_MIXTA"]:.0f}% rural/mixta &middot; {r["MENOR_40"]:.0f}% menor de 40 &middot; '
            f'Claridad {r["CLARA"]:.0f}%</div>'
            '</div></details>'
        )

    html += (
        f'<div style="margin-top:6px;padding:2px 0;">'
        f'<span style="display:inline-block;width:10px;height:10px;'
        f'background:{COLOR_SIN_DATOS};border-radius:2px;margin-right:6px;'
        f'vertical-align:middle;"></span>'
        f'<span style="color:#999;">Sin datos suficientes</span></div>'
        '</div></div>'
    )
    return html


def generar_mapa_interactivo(gmun, gedo, celdas, res_perfil, tray_perfil, nac_tray,
                             descriptores, nac_edad, nac_reg, nac_esc_tramo, K):
    """Genera el mapa HTML interactivo con folium."""
    # Distribuciones por perfil para el panel
    w_total = celdas["peso"].sum()
    dist_edad, dist_region, dist_esc = {}, {}, {}
    for p in range(K):
        dp = celdas[celdas["perfil"] == p]
        wp = dp["peso"].sum()
        dist_edad[p] = (dp.groupby("GRUPO_EDAD")["peso"].sum()
                        .reindex(ETIQUETAS_EDAD, fill_value=0) / wp * 100).tolist()
        dist_region[p] = (dp.groupby("REGION")["peso"].sum()
                          .reindex(REGIONES_ORDEN, fill_value=0) / wp * 100).tolist()
        con = dp[dp["escolaridad"].notna()]
        wc = con["peso"].sum() or 1
        dist_esc[p] = (con.groupby("tramo_esc")["peso"].sum()
                       .reindex(TRAMOS_ESC, fill_value=0) / wc * 100).tolist()

    # Mapa base con tiles Stadia Maps (funcionan desde localhost sin API key)
    m = folium.Map(location=[23.6, -102.5], zoom_start=5, tiles=None)
    folium.TileLayer(
        tiles="https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png",
        attr=(
            "&copy; <a href='https://stadiamaps.com/'>Stadia Maps</a> "
            "&copy; <a href='https://openmaptiles.org/'>OpenMapTiles</a> "
            "&copy; <a href='https://www.openstreetmap.org/copyright'>OSM</a>"
        ),
        name="Mapa base",
    ).add_to(m)

    # Capa municipal
    fg_mun = folium.FeatureGroup(name="Municipios", show=True)
    for _, r in gmun.iterrows():
        if r["suficiente"]:
            estilo = {
                "fillColor": COLORES_PERFIL[int(r["perfil_dom"])],
                "color": "#666", "weight": 0.3,
                "fillOpacity": 0.25 + 0.6 * r["pct_dom"] / 100,
            }
        else:
            estilo = {"fillColor": COLOR_SIN_DATOS, "color": "#aaa", "weight": 0.3, "fillOpacity": 0.3}
        folium.GeoJson(
            r.geometry.__geo_interface__,
            style_function=lambda x, e=estilo: e,
            tooltip=r["NOMGEO"],
            popup=folium.Popup(popup_municipio(r, K), max_width=260),
        ).add_to(fg_mun)
    fg_mun.add_to(m)

    # Capa estatal
    fg_edo = folium.FeatureGroup(name="Entidades", show=False)
    for _, r in gedo.iterrows():
        estilo = {
            "fillColor": COLORES_PERFIL[int(r["perfil_dom"])],
            "color": "#333", "weight": 1.5, "fillOpacity": 0.45,
        }
        folium.GeoJson(
            r.geometry.__geo_interface__,
            style_function=lambda x, e=estilo: e,
            tooltip=EDONOM[r["EDOCVE"]],
            popup=folium.Popup(popup_entidad(r, K), max_width=260),
        ).add_to(fg_edo)
    fg_edo.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    # Panel de perfiles
    html_panel = panel_html(
        res_perfil, tray_perfil, nac_tray, descriptores,
        dist_edad, dist_region, dist_esc,
        nac_edad.values.tolist(), nac_reg.values.tolist(), nac_esc_tramo.values.tolist(), K,
    )
    m.get_root().html.add_child(folium.Element(html_panel))

    ruta = DIR_FICHAS / "mapa_clases_latentes.html"
    m.save(str(ruta))
    print(f"  mapa_clases_latentes.html ({ruta.stat().st_size / 1024**2:.1f} MB)")


# ===================================================================
# Orquestador
# ===================================================================

def main():
    DIR_FICHAS.mkdir(exist_ok=True)

    # Cargar datos
    celdas, K = cargar_datos()
    w_total = celdas["peso"].sum()

    # Resumenes ponderados
    res_perfil = resumen(celdas, ["perfil"])
    res_sub = resumen(celdas, ["perfil", "subperfil"])
    tray_perfil = pd.DataFrame({e: media_ponderada(celdas, e, ["perfil"]) for e in ELECCIONES})

    # Referencias nacionales
    nac_tray = [np.average(celdas[e], weights=celdas["peso"]) for e in ELECCIONES]
    nac_edad = celdas.groupby("GRUPO_EDAD")["peso"].sum()[ETIQUETAS_EDAD] / w_total * 100
    nac_reg = celdas.groupby("REGION")["peso"].sum()[REGIONES_ORDEN] / w_total * 100
    con_esc = celdas[celdas["escolaridad"].notna()]
    nac_esc_tramo = con_esc.groupby("tramo_esc")["peso"].sum()[TRAMOS_ESC] / con_esc["peso"].sum() * 100
    nac_esc = np.average(con_esc["escolaridad"], weights=con_esc["peso"])
    con_int = celdas[celdas["pct_internet"].notna()]
    nac_internet = np.average(con_int["pct_internet"], weights=con_int["peso"])

    # Sobrerrepresentacion
    ent_perfil = sobrerrepresentacion(celdas, "perfil", "entidad", MIN_PERSONAS_ENTIDAD)
    ent_sub = sobrerrepresentacion(celdas, "subperfil", "entidad", MIN_PERSONAS_ENTIDAD)

    # Descriptores automaticos
    descriptores = generar_descriptores(celdas, res_perfil, K)
    for p in NOMBRES:
        print(f"  P{p}: {NOMBRES[p]}  ({descriptores[p]})")

    # Geometrias
    print("\nCargando geometrias...")
    gdf_mun = pyogrio.read_dataframe(DIR_GEO / "mun22gw.shp", encoding="latin-1")
    gdf_mun["EDOCVE"] = gdf_mun["CVE_ENT"].astype(int)
    gdf_mun["geometry"] = gdf_mun.geometry.simplify(TOL_MUNICIPIO, preserve_topology=True)

    gdf_edo = gdf_mun.dissolve(by="EDOCVE").reset_index()[["EDOCVE", "NOM_ENT", "geometry"]]
    gdf_edo["geometry"] = gdf_edo.geometry.simplify(TOL_ESTADO, preserve_topology=True)

    # Cruce municipal por nombre
    print("\nCruce municipal:")
    cruce = cruzar_municipios(celdas, gdf_mun)

    # Perfil dominante por municipio
    claves = cruce[["EDOCVE", "MPIOCVE", "CVEGEO"]].drop_duplicates(["EDOCVE", "MPIOCVE"])
    celdas = celdas.merge(claves, on=["EDOCVE", "MPIOCVE"], how="left")
    geo_celdas = celdas.dropna(subset=["CVEGEO"])

    dist_mun = geo_celdas.groupby(["CVEGEO", "perfil"])["peso"].sum().unstack(fill_value=0)
    personas_mun = dist_mun.sum(axis=1)
    pct_mun = dist_mun.div(personas_mun, axis=0) * 100
    sub_dom = (
        geo_celdas.groupby(["CVEGEO", "subperfil"])["peso"].sum().reset_index()
        .sort_values("peso").drop_duplicates("CVEGEO", keep="last").set_index("CVEGEO")
    )

    mun = pd.DataFrame({
        "personas": personas_mun,
        "promedio": media_ponderada(geo_celdas, "promedio", ["CVEGEO"]),
        "escolaridad": media_ponderada(geo_celdas, "escolaridad", ["CVEGEO"]),
        "pct_internet": media_ponderada(geo_celdas, "pct_internet", ["CVEGEO"]),
        "perfil_dom": pct_mun.idxmax(axis=1),
        "pct_dom": pct_mun.max(axis=1),
        "subperfil_dom": sub_dom["subperfil"],
        "pct_subperfil_dom": sub_dom["peso"] / personas_mun * 100,
    })
    mun["suficiente"] = mun["personas"] >= MIN_PERSONAS_MPIO
    mun = mun.join(pct_mun.add_prefix("pct_"))

    gmun = gdf_mun.merge(mun, left_on="CVEGEO", right_index=True, how="left")
    gmun["suficiente"] = gmun["suficiente"].eq(True)

    # Datos estatales
    dist_edo = celdas.groupby(["EDOCVE", "perfil"])["peso"].sum().unstack(fill_value=0)
    edo = pd.DataFrame({
        "personas": dist_edo.sum(axis=1),
        "promedio": media_ponderada(celdas, "promedio", ["EDOCVE"]),
        "escolaridad": media_ponderada(celdas, "escolaridad", ["EDOCVE"]),
        "pct_internet": media_ponderada(celdas, "pct_internet", ["EDOCVE"]),
        "perfil_dom": dist_edo.idxmax(axis=1),
    }).join((dist_edo.div(dist_edo.sum(axis=1), axis=0) * 100).add_prefix("pct_"))
    gedo = gdf_edo.merge(edo, left_on="EDOCVE", right_index=True, how="left")

    print(f"\n  Municipios con datos suficientes: {gmun['suficiente'].sum():,} de {len(gmun):,}")

    # Generar visualizaciones
    print("\nGenerando visualizaciones...")
    generar_vista_general(res_perfil, tray_perfil, nac_tray, K)
    generar_mapa_estatico(gmun, gdf_edo, K)
    generar_fichas(
        celdas, res_perfil, res_sub, tray_perfil, nac_tray,
        nac_edad, nac_reg, nac_esc_tramo, nac_esc, nac_internet,
        ent_perfil, ent_sub, gmun, gdf_edo, descriptores, K,
    )
    generar_mapa_interactivo(
        gmun, gedo, celdas, res_perfil, tray_perfil, nac_tray,
        descriptores, nac_edad, nac_reg, nac_esc_tramo, K,
    )

    # Exportar tablas CSV
    print("\nExportando tablas...")
    tabla_mun = gmun.drop(columns="geometry").loc[
        :, ["CVEGEO", "EDOCVE", "NOMGEO", "personas", "promedio", "escolaridad",
            "pct_internet", "perfil_dom", "pct_dom", "subperfil_dom",
            "pct_subperfil_dom", "suficiente"] + [f"pct_{p}" for p in range(K)]
    ]
    salidas = {
        "fichas_resumen_perfiles.csv": res_perfil.assign(
            nombre=pd.Series(NOMBRES), descriptor=pd.Series(descriptores)
        ).round(2),
        "fichas_municipios.csv": tabla_mun.round(2),
        "fichas_cruce_municipios.csv": cruce.drop(columns="nom"),
    }
    for nombre, df in salidas.items():
        df.to_csv(DIR_FICHAS / nombre, index=nombre == "fichas_resumen_perfiles.csv")
        print(f"  {nombre}")

    print("\nVisualizacion completa.")


if __name__ == "__main__":
    main()
