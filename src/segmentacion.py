"""
Segmentacion - Clases latentes y subperfiles anidados.

Etapa 1 (LCA): Analisis de Clases Latentes sobre terciles ponderados de
    participacion por eleccion. Modelo de mezcla de categoricas con EM propio,
    seleccion por BIC en el rango k=4-6. Resultado: 6 clases con ARI 0.98.

Etapa 2 (Subperfiles): KMeans ponderado dentro de cada clase latente sobre
    promedio, brecha presidencial y tendencia. El numero de subperfiles por
    clase es el mayor que resulta estable en bootstrap. Resultado: 27 subperfiles.

Entrada: DATA/PREPROCESSED/ (parquets de preprocesamiento.py)
Salida:  DATA/PREPROCESSED/
    celdas_clases_latentes.parquet   657,497 celdas con clase y probabilidad
    lca_seleccion_k.csv              Metricas por numero de clases (BIC, AIC, entropia)
    lca_clases.csv                   Resumen ponderado de las clases elegidas
    celdas_subperfiles.parquet       657,497 celdas con perfil y subperfil
    subperfiles_resumen.csv          Resumen ponderado de los 27 subperfiles
    subperfiles_microtargeting.csv   Subperfiles con entidades y personas-tipo sobrerrepresentadas
    subperfiles_entidades.csv        Indice de sobrerrepresentacion por entidad
    subperfiles_personas_tipo.csv    Indice de sobrerrepresentacion por sexo x edad
    subperfiles_municipios.csv       Subperfil dominante por municipio

Uso:
    uv run python src/segmentacion.py

Autores: Angel David Durazo Bartolini y Jehu Jonathan Ramirez Ramirez
"""

import gc
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import logsumexp
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
DIR_PREPROCESSED = ROOT / "DATA" / "PREPROCESSED"

# ---------------------------------------------------------------------------
# Parametros comunes
# ---------------------------------------------------------------------------

ELECCIONES = ["P2009", "P2012", "P2015", "P2018", "P2021", "P2024"]
CORTES_EDAD = [17, 24, 29, 39, 49, 59, 69, 79, 200]
ETIQUETAS_EDAD = ["18-24", "25-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80+"]
LLAVES = ["EDOCVE", "SECCION", "SEXO", "GRUPO_EDAD"]
BASE = ["promedio", "brecha_pres", "tendencia"]

RANDOM_STATE = 42
N_EVAL = 10_000

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

# ---------------------------------------------------------------------------
# Parametros LCA
# ---------------------------------------------------------------------------

# Cada eleccion se convierte en terciles ponderados (baja, media, alta)
# para eliminar el efecto comun presidencial/intermedia y quedarse con la
# posicion relativa de cada celda frente al resto del pais
N_CATEGORIAS = 3
ETIQUETAS_CAT = ["baja", "media", "alta"]

K_RANGO = range(2, 9)
K_VALIDO = range(4, 7)      # la convocatoria pide 4-6 perfiles
MIN_PCT_CLASE = 5.0          # clase minima como % de personas
UMBRAL_CLARA = 0.8           # probabilidad minima para asignacion clara

N_INIT = 20                  # inicializaciones aleatorias del EM
MAX_ITER = 1000
TOL = 1e-8
N_BOOT_LCA = 5

# ---------------------------------------------------------------------------
# Parametros subperfiles
# ---------------------------------------------------------------------------

K_SUB_RANGO = range(2, 6)
MIN_PCT_SUB = 2.0            # subperfil minimo como % de poblacion total
ARI_ESTABLE = 0.8            # umbral de estabilidad bootstrap
N_SIL = 5_000
N_BOOT_SUB = 3
MIN_PERSONAS_ENTIDAD = 20_000
MIN_PERSONAS_TIPO = 20_000
MIN_PERSONAS_MPIO = 1_000


# ===================================================================
# Funciones auxiliares compartidas
# ===================================================================

def guardar_parquet(df, salida):
    """Escribe a un temporal y renombra: una corrida interrumpida no deja un parquet a medias."""
    tmp = salida.with_suffix(".parquet.tmp")
    df.to_parquet(tmp, index=False)
    tmp.replace(salida)


def media_ponderada(df, col, por):
    """Promedio ponderado por peso, agrupado por las columnas en `por`."""
    grupos = [df[c] for c in por]
    wx = (df[col] * df["peso"]).groupby(grupos).sum()
    return wx / df["peso"].where(df[col].notna()).groupby(grupos).sum()


def dominante(df, por, col):
    """Categoria con mayor peso dentro de cada grupo."""
    t = df.groupby(por + [col])["peso"].sum()
    return t.groupby(level=por).idxmax().map(lambda x: x[-1])


def cargar_celdas_con_peso():
    """Carga las celdas del historial con peso = SV + NV de 2024.

    Las celdas sin PJ 2025 se conservan (Campeche no tiene datos judiciales).
    """
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

    celdas["MUJER"] = (celdas["SEXO"] == 1).astype(float)
    celdas["RURAL_MIXTA"] = (celdas["TIPOSEC"].astype(str) != "U").astype(float)
    return celdas


# ===================================================================
# Etapa 1: Clases latentes (LCA)
# ===================================================================

def terciles_ponderados(x, w, n=N_CATEGORIAS):
    """Asigna cada valor a un tercil ponderado (0, 1 o 2).

    Los cortes se calculan por interpolacion sobre la distribucion acumulada
    ponderada, de modo que cada tercil concentra ~1/3 de las personas.
    """
    orden = np.argsort(x)
    acum = np.cumsum(w[orden]) / w.sum()
    cortes = np.interp(np.arange(1, n) / n, acum, x[orden])
    return np.searchsorted(cortes, x, side="right")


def ajustar_lca(K, f, onehot, J, C, seed):
    """Ajusta un modelo de clases latentes con EM.

    El modelo asume independencia local: dentro de cada clase, los indicadores
    son independientes. Cada indicador j tiene una distribucion categorica
    theta_kj sobre C categorias.
    """
    rng = np.random.default_rng(seed)
    pi = np.full(K, 1 / K)
    theta = rng.dirichlet(np.ones(C), size=(K, J))
    ll_prev = -np.inf
    for _ in range(MAX_ITER):
        # E-step: probabilidad posterior de cada clase dado el patron
        log_p = np.log(pi) + onehot @ np.log(theta).reshape(K, J * C).T
        ll_fila = logsumexp(log_p, axis=1)
        resp = np.exp(log_p - ll_fila[:, None])
        ll = (f * ll_fila).sum()
        if ll - ll_prev < TOL * abs(ll):
            break
        ll_prev = ll
        # M-step: actualizar proporciones y distribuciones
        rw = resp * f[:, None]
        pi = rw.sum(axis=0) / rw.sum()
        theta = (rw.T @ onehot).reshape(K, J, C) + 1e-10
        theta /= theta.sum(axis=2, keepdims=True)
    return {"pi": pi, "theta": theta, "ll": ll, "resp": resp}


def mejor_lca(K, f, onehot, J, C, seed=RANDOM_STATE, n_init=N_INIT):
    """Ajusta el LCA con multiples inicializaciones y devuelve el mejor."""
    return max(
        (ajustar_lca(K, f, onehot, J, C, seed + s) for s in range(n_init)),
        key=lambda m: m["ll"],
    )


def entropia_relativa(resp, f):
    """Entropia de clasificacion relativa (0 = maxima ambiguedad, 1 = perfecta)."""
    h = -(f[:, None] * resp * np.log(np.clip(resp, 1e-300, None))).sum()
    return 1 - h / (f.sum() * np.log(resp.shape[1]))


def resumen_lca(celdas, por):
    """Resumen ponderado de clases o subperfiles."""
    personas = celdas.groupby(por)["peso"].sum()
    out = pd.DataFrame({"personas": personas, "pct_pob": personas / celdas["peso"].sum() * 100})
    cols = ["promedio", "brecha_pres", "tendencia", "P_PJ2025",
            "MUJER", "RURAL_MIXTA", "asignacion_clara"]
    for col in cols:
        if col in celdas.columns:
            out[col] = media_ponderada(celdas, col, por)
    for col in ["MUJER", "RURAL_MIXTA", "asignacion_clara"]:
        if col in out.columns:
            out[col] *= 100
    out["edad_dominante"] = dominante(celdas, por, "GRUPO_EDAD")
    out["region_dominante"] = dominante(celdas, por, "REGION")
    return out.round(1)


def etapa_lca(celdas):
    """Ejecuta el analisis de clases latentes y guarda resultados."""
    print("=== Etapa 1: Clases latentes (LCA) ===")

    salida = DIR_PREPROCESSED / "celdas_clases_latentes.parquet"
    if salida.exists():
        n = pd.read_parquet(salida, columns=["EDOCVE"]).shape[0]
        print(f"  Ya existe: {salida.name} ({n:,} filas)")
        return

    w = celdas["peso"].to_numpy(dtype=float)
    n_celdas = len(celdas)
    J = len(ELECCIONES)
    C = N_CATEGORIAS

    # Terciles ponderados por eleccion
    cat = np.column_stack([
        terciles_ponderados(celdas[c].to_numpy(dtype=float), w)
        for c in ELECCIONES
    ])

    # Colapsar a patrones unicos con su peso normalizado
    patrones, inv = np.unique(cat, axis=0, return_inverse=True)
    inv = inv.ravel()
    w_pat = np.bincount(inv, weights=w)
    f_pat = w_pat / w_pat.sum() * n_celdas

    onehot = np.zeros((len(patrones), J * C))
    onehot[np.arange(len(patrones))[:, None], np.arange(J) * C + patrones] = 1
    print(f"  Patrones observados: {len(patrones):,} de {C ** J:,} posibles")

    # Ajustar modelos para k = 2 a 8
    modelos, filas = {}, []
    for K in K_RANGO:
        print(f"  Ajustando k={K}...", end=" ", flush=True)
        m = mejor_lca(K, f_pat, onehot, J, C)
        modelos[K] = m
        n_par = (K - 1) + K * J * (C - 1)
        bic = -2 * m["ll"] + n_par * np.log(n_celdas)
        ent = entropia_relativa(m["resp"], f_pat)
        filas.append({
            "K": K, "loglik": m["ll"], "n_parametros": n_par,
            "BIC": bic, "AIC": -2 * m["ll"] + 2 * n_par,
            "entropia": ent, "pct_min": m["pi"].min() * 100,
        })
        print(f"BIC={bic:.0f}  entropia={ent:.3f}  min_clase={m['pi'].min()*100:.1f}%")

    df_k = pd.DataFrame(filas)
    df_k["mejora_BIC_pct"] = -df_k["BIC"].diff() / df_k["BIC"].shift().abs() * 100

    # Elegir k: menor BIC en 4-6 con clase minima >= 5%
    cand = df_k[df_k["K"].isin(K_VALIDO) & (df_k["pct_min"] >= MIN_PCT_CLASE)]
    if len(cand) == 0:
        cand = df_k[df_k["K"].isin(K_VALIDO)]
    K_ELEGIDO = int(cand.loc[cand["BIC"].idxmin(), "K"])
    print(f"\n  K elegido: {K_ELEGIDO}")

    # Ordenar clases por participacion relativa esperada (0 = menor)
    m = modelos[K_ELEGIDO]
    orden = np.argsort((m["theta"] * np.arange(C)).sum(axis=2).mean(axis=1))
    pi, theta, resp = m["pi"][orden], m["theta"][orden], m["resp"][:, orden]

    # Asignar clase a cada celda
    clase_pat = resp.argmax(axis=1)
    celdas["clase"] = clase_pat[inv]
    celdas["prob_clase"] = resp.max(axis=1)[inv]
    celdas["asignacion_clara"] = (celdas["prob_clase"] >= UMBRAL_CLARA).astype(float)

    clara = np.average(celdas["asignacion_clara"], weights=w) * 100
    print(f"  Asignacion clara (prob >= {UMBRAL_CLARA}): {clara:.1f}%")

    # Bootstrap de estabilidad
    idx_eval = np.random.default_rng(RANDOM_STATE).choice(
        n_celdas, size=N_EVAL, replace=False, p=w / w.sum()
    )
    aris = []
    for b in range(N_BOOT_LCA):
        w_b = w * np.random.default_rng(1000 + b).poisson(1.0, size=len(w))
        f_b = np.bincount(inv, weights=w_b, minlength=len(patrones))
        f_b = f_b / f_b.sum() * n_celdas
        m_b = mejor_lca(K_ELEGIDO, f_b, onehot, J, C, seed=1000 + b * N_INIT, n_init=10)
        clase_b = m_b["resp"].argmax(axis=1)[inv]
        aris.append(adjusted_rand_score(celdas["clase"].to_numpy()[idx_eval], clase_b[idx_eval]))
    print(f"  Estabilidad: ARI medio {np.mean(aris):.3f}, minimo {np.min(aris):.3f}")

    # Resumen de las clases
    clases = resumen_lca(celdas, ["clase"])
    for j, c in enumerate(ELECCIONES):
        clases[f"p_alta_{c}"] = pd.Series(theta[:, j, C - 1], index=range(K_ELEGIDO)).round(3)

    # Guardar: el parquet al final, porque su existencia indica que la etapa termino
    df_k.to_csv(DIR_PREPROCESSED / "lca_seleccion_k.csv", index=False)
    clases.to_csv(DIR_PREPROCESSED / "lca_clases.csv")
    guardar_parquet(celdas[LLAVES + ["peso", "clase", "prob_clase"]], salida)
    print(f"  Guardado: {salida.name}, lca_seleccion_k.csv, lca_clases.csv")


# ===================================================================
# Etapa 2: Subperfiles anidados
# ===================================================================

def sobrerrepresentacion(df, dim, min_personas, top=3):
    """Indice de sobrerrepresentacion de cada subperfil en cada categoria.

    indice = (% de la categoria en el subperfil) / (% nacional del subperfil) x 100.
    100 = igual al promedio nacional; 200 = el doble de lo esperado.
    """
    t = df.groupby(["subperfil", dim])["peso"].sum().rename("personas").reset_index()
    t["pct_en_categoria"] = t["personas"] / t.groupby(dim)["personas"].transform("sum") * 100
    pct_nacional = df.groupby("subperfil")["peso"].sum() / df["peso"].sum() * 100
    t["indice"] = t["pct_en_categoria"] / t["subperfil"].map(pct_nacional) * 100
    t = t[t["personas"] >= min_personas]
    return t.sort_values("indice", ascending=False).groupby("subperfil").head(top).sort_values(
        ["subperfil", "indice"], ascending=[True, False]
    )


def resumen_subperfiles(celdas, por):
    """Resumen ponderado por subperfil."""
    personas = celdas.groupby(por)["peso"].sum()
    out = pd.DataFrame({"personas": personas, "pct_pob": personas / celdas["peso"].sum() * 100})
    for col in ["promedio", "brecha_pres", "tendencia", "desviacion", "P_PJ2025", "MUJER", "RURAL_MIXTA"]:
        if col in celdas.columns:
            out[col] = media_ponderada(celdas, col, por)
    out[["MUJER", "RURAL_MIXTA"]] *= 100
    out["edad_dominante"] = dominante(celdas, por, "GRUPO_EDAD")
    out["region_dominante"] = dominante(celdas, por, "REGION")
    return out.round(1)


def etapa_subperfiles(celdas):
    """Ejecuta la subdivision en subperfiles y guarda resultados."""
    print("\n=== Etapa 2: Subperfiles anidados ===")

    salida = DIR_PREPROCESSED / "celdas_subperfiles.parquet"
    if salida.exists():
        n = pd.read_parquet(salida, columns=["EDOCVE"]).shape[0]
        print(f"  Ya existe: {salida.name} ({n:,} filas)")
        return

    # Cargar clases latentes
    lca = pd.read_parquet(
        DIR_PREPROCESSED / "celdas_clases_latentes.parquet",
        columns=LLAVES + ["clase", "prob_clase"],
    )
    n0 = len(celdas)
    celdas = celdas.merge(lca.rename(columns={"clase": "perfil_origen"}), on=LLAVES, how="inner")
    print(f"  Celdas sin clase latente (excluidas): {n0 - len(celdas):,}")
    del lca

    # Renumerar perfiles por promedio de participacion (0 = menor)
    w = celdas["peso"].to_numpy(dtype=float)
    orden = media_ponderada(celdas, "promedio", ["perfil_origen"]).sort_values().index
    celdas["perfil"] = celdas["perfil_origen"].map(
        {old: new for new, old in enumerate(orden)}
    ).astype(int)
    celdas = celdas.drop(columns="perfil_origen")
    K_PERFILES = celdas["perfil"].nunique()
    perfil = celdas["perfil"].to_numpy()

    celdas["persona_tipo"] = (
        celdas["SEXO"].map({0: "Hombre", 1: "Mujer"}) + " " + celdas["GRUPO_EDAD"]
    )

    # Estandarizar el espacio de subdivision
    Z = StandardScaler().fit(
        celdas[BASE].to_numpy(dtype=float), sample_weight=w
    ).transform(celdas[BASE].to_numpy(dtype=float))

    # Muestra para evaluacion de estabilidad
    idx_eval = np.random.default_rng(RANDOM_STATE).choice(
        len(celdas), size=N_EVAL, replace=False, p=w / w.sum()
    )

    # Buscar k optimo por perfil
    filas, modelos_sub = [], {}
    for p in range(K_PERFILES):
        mask = perfil == p
        idx_s = np.flatnonzero(mask)
        idx_s = np.random.default_rng(RANDOM_STATE + p).choice(
            idx_s, size=min(N_SIL, len(idx_s)), replace=False, p=w[idx_s] / w[idx_s].sum()
        )
        for k in K_SUB_RANGO:
            km = KMeans(k, n_init=10, random_state=RANDOM_STATE).fit(Z[mask], sample_weight=w[mask])
            modelos_sub[(p, k)] = km
            lab_s = km.predict(Z[idx_s])
            aris = []
            for b in range(N_BOOT_SUB):
                w_b = w[mask] * np.random.default_rng(1000 + b).poisson(1.0, size=mask.sum())
                km_b = KMeans(k, n_init=3, random_state=1000 + b).fit(Z[mask], sample_weight=w_b)
                aris.append(adjusted_rand_score(lab_s, km_b.predict(Z[idx_s])))
            tam = np.bincount(km.labels_, weights=w[mask], minlength=k) / w.sum() * 100
            filas.append({
                "perfil": p, "k": k,
                "silhouette": silhouette_score(Z[idx_s], lab_s),
                "pct_min_total": tam.min(),
                "ari_boot": np.mean(aris),
            })

    seleccion = pd.DataFrame(filas)

    # Elegir: mayor k estable con subperfil minimo >= 2% de la poblacion
    K_SUB = {}
    for p, d in seleccion.groupby("perfil"):
        ok = d[(d["ari_boot"] >= ARI_ESTABLE) & (d["pct_min_total"] >= MIN_PCT_SUB)]
        K_SUB[p] = int(ok["k"].max()) if len(ok) else int(d.loc[d["silhouette"].idxmax(), "k"])
    print(f"  Subperfiles por perfil: {K_SUB}  (total {sum(K_SUB.values())})")

    # Asignar subperfiles, numerados por promedio dentro de cada perfil
    sub_k = np.full(len(celdas), -1)
    for p, k in K_SUB.items():
        sub_k[perfil == p] = modelos_sub[(p, k)].labels_
    celdas["sub_k"] = sub_k

    prom = (
        media_ponderada(celdas, "promedio", ["perfil", "sub_k"])
        .rename("prom").reset_index().sort_values("prom")
    )
    prom["subperfil"] = (
        prom["perfil"].astype(str) + "." + (prom.groupby("perfil").cumcount() + 1).astype(str)
    )
    celdas = celdas.merge(prom[["perfil", "sub_k", "subperfil"]], on=["perfil", "sub_k"], how="left")

    # Resumen y microtargeting
    tabla_sub = resumen_subperfiles(celdas, ["perfil", "subperfil"])

    ent = sobrerrepresentacion(
        celdas.assign(entidad=celdas["EDOCVE"].map(EDONOM)),
        "entidad", MIN_PERSONAS_ENTIDAD,
    )
    tipo = sobrerrepresentacion(celdas, "persona_tipo", MIN_PERSONAS_TIPO)

    def como_texto(t, etiqueta):
        txt = t[etiqueta] + " (" + t["indice"].round(0).astype(int).astype(str) + ")"
        return txt.groupby(t["subperfil"]).agg(", ".join)

    micro = tabla_sub[["pct_pob", "promedio", "brecha_pres", "tendencia"]].reset_index()
    micro["entidades"] = micro["subperfil"].map(como_texto(ent, "entidad"))
    micro["personas_tipo"] = micro["subperfil"].map(como_texto(tipo, "persona_tipo"))

    # Municipios: subperfil dominante
    llave_mpio = ["EDOCVE", "MPIOCVE"]
    mpio = celdas.groupby(llave_mpio + ["MPIONOM", "subperfil"])["peso"].sum().reset_index()
    mpio["personas_mpio"] = mpio.groupby(llave_mpio)["peso"].transform("sum")
    mpio["pct_sub"] = mpio["peso"] / mpio["personas_mpio"] * 100
    municipios = mpio.loc[mpio.groupby(llave_mpio)["peso"].idxmax()]
    municipios = municipios[municipios["personas_mpio"] >= MIN_PERSONAS_MPIO].copy()
    municipios["entidad"] = municipios["EDOCVE"].map(EDONOM)
    municipios = municipios.rename(columns={"peso": "personas_sub"})

    # Guardar: el parquet al final, porque su existencia indica que la etapa termino
    tabla_sub.to_csv(DIR_PREPROCESSED / "subperfiles_resumen.csv")
    micro.to_csv(DIR_PREPROCESSED / "subperfiles_microtargeting.csv", index=False)
    ent.to_csv(DIR_PREPROCESSED / "subperfiles_entidades.csv", index=False)
    tipo.to_csv(DIR_PREPROCESSED / "subperfiles_personas_tipo.csv", index=False)
    municipios.to_csv(DIR_PREPROCESSED / "subperfiles_municipios.csv", index=False)
    guardar_parquet(celdas[LLAVES + ["peso", "perfil", "subperfil"]], salida)

    print(f"  Municipios con datos suficientes: {len(municipios):,}")
    print("  Guardados: celdas_subperfiles.parquet + 5 CSVs de resumen")


# ===================================================================
# Orquestador
# ===================================================================

def main():
    print("Cargando celdas con peso...\n")
    celdas = cargar_celdas_con_peso()
    print(f"Celdas: {len(celdas):,}  personas: {celdas['peso'].sum():,.0f}\n")

    etapa_lca(celdas)
    gc.collect()

    # Recargar para la segunda etapa (la primera modifica celdas)
    celdas = cargar_celdas_con_peso()
    etapa_subperfiles(celdas)

    print("\nSegmentacion completa.")


if __name__ == "__main__":
    main()
