# 100006 — marimo starter (Polars)
# Run:  marimo run 04_marimo/100006.py   (or: marimo edit ...)

import os
import io
import requests
import polars as pl
import marimo as mo
import matplotlib.pyplot as plt

app = mo.app()

# --- CONFIG / LINKS -----------------------------------------------------------
PROVIDER = "Statistisches Amt des Kantons Basel-Stadt - Fachstelle OGD"
IDENTIFIER = "100006"
TITLE = "Verkehrszähldaten motorisierter Individualverkehr"
DESCRIPTION = "<p>Resultate der Messungen der Dauerzählstellen und Kurzzeitzählstellen für den Motorisierten Individualverkehr. </p><p>Aus Kostengründen sind nur die Werte des aktuellen Jahres und der letzten zwei Jahre als Tabelle / Visualisierung sichtbar bzw. via API abgreifbar. </p><p>Die Zählstellen, die zwischen allen Fahrzeugklassen unterscheiden können, ab dem Jahr 2014 können hier heruntergeladen werden: </p><ul><li><a href='https://data-bs.ch/mobilitaet/converted_MIV_Class_10_1.csv'>Leicht aufbereiteter Datensatz: https://data-bs.ch/mobilitaet/converted_MIV_Class_10_1.csv</a> </li><li><a href='https://data-bs.ch/mobilitaet/MIV_Class_10_1.csv'>Rohdaten: https://data-bs.ch/mobilitaet/MIV_Class_10_1.csv</a></li></ul><p>Die vollständigen Daten der Zählstellen, die mit FLIR (Forward Looking Infrared) messen und zwischen sechs Fahrzeugklassen unterscheiden können, können hier heruntergeladen werden:</p><ul><li><a href='https://data-bs.ch/mobilitaet/converted_FLIR_KtBS_MIV6.csv'>Leicht aufbereiteter Datensatz: https://data-bs.ch/mobilitaet/converted_FLIR_KtBS_MIV6.csv</a></li><li><a href='https://data-bs.ch/mobilitaet/FLIR_KtBS_MIV6.csv'>Rohdaten: https://data-bs.ch/mobilitaet/FLIR_KtBS_MIV6.csv</a></li></ul><p>Für die Lichtsignalanlagen (LSA) können die vollständigen Daten hier heruntergeladen werden:</p><ul><li><a href='https://data-bs.ch/mobilitaet/converted_MIV_LSA_Count.csv'>Leicht aufbereiteter Datensatz: https://data-bs.ch/mobilitaet/converted_MIV_LSA_Count.csv</a></li><li><a href='https://data-bs.ch/mobilitaet/MIV_LSA_Count.csv'>Rohdaten: https://data-bs.ch/mobilitaet/MIV_LSA_Count.csv</a></li></ul><p>Die Daten einzelner Jahre ab dem Jahr 2014 können unter der URL mit dem Muster https://data-bs.ch/mobilitaet/[JAHR]_MIV_Class_10_1.csv heruntergeladen werden, also zum Beispiel für das Jahr 2020 hier: https://data-bs.ch/mobilitaet/2020_MIV_Class_10_1.csv.<br>Für FLIR-Zähldaten muss folgendes Muster verwendet werden: https://data-bs.ch/mobilitaet/[JAHR]_FLIR_KtBS_MIV6.csv. <br>Für LSA-Zähldaten muss folgendes Muster verwendet werden: https://data-bs.ch/mobilitaet/[JAHR]_MIV_LSA.csv.</p><p>Die Zählstellen sind auf MET eingestellt (Spalten TimeFrom und TimeTo), d.h. die Zeitumstellung wird wie in Mitteleuropa ausgeführt. Bei der Umstellung von Winter- auf Sommerzeit fehlt die Stunde der Umstellung, dieser Tag hat dann 23 Stunden. Bei der Umstellung von Sommer- auf Winterzeit ist eine Stunde zu viel enthalten (der Tag hat dann 25 Stunden), die Stunde der Umstellung ist dann doppelt, aber mit unterschiedlichen Verkehrsdaten (da die gleiche Stunde zweimal durchlaufen wird).</p>"
CONTACT = "Fachstelle für OGD Basel-Stadt | opendata@bs.ch"
DATASHOP_MD_LINK = """[Direct data shop link for dataset](https://data.bs.ch/explore/dataset/100006)"""

# --- HELPERS ------------------------------------------------------------------
def _ensure_data_dir():
    data_path = os.path.join(os.getcwd(), "..", "data")
    os.makedirs(data_path, exist_ok=True)
    return data_path

def get_dataset(url: str) -> pl.DataFrame:
    """Download CSV once (to ../data) and read with Polars.
    Tries common delimiters (;, ',', '\\t')."""
    _ensure_data_dir()
    csv_path = os.path.join("..", "data", f"{IDENTIFIER}.csv")

    # Download (idempotent)
    try:
        r = requests.get(url, params={"format": "csv", "timezone": "Europe%2FZurich"}, timeout=60)
        r.raise_for_status()
        with open(csv_path, "wb") as f:
            f.write(r.content)
        content = io.BytesIO(r.content)
    except Exception:
        # Fallback to local file if present
        content = csv_path if os.path.exists(csv_path) else None

    if content is None:
        raise RuntimeError("Could not download or locate dataset locally.")

    # Try delimiters
    for sep in (";", ",", "\t"):
        try:
            df = pl.read_csv(content, separator=sep, ignore_errors=True, infer_schema_length=2000)
            if df.width > 1:  # likely correct delimiter
                return df
        except Exception:
            content.seek(0) if hasattr(content, "seek") else None

    # Last attempt: let Polars auto-detect
    return pl.read_csv(content, ignore_errors=True, infer_schema_length=2000)

def drop_all_null_columns(df: pl.DataFrame) -> pl.DataFrame:
    if df.height == 0:
        return df
    null_counts_row = df.null_count().row(0)
    cols_keep = [c for c, n in zip(df.columns, null_counts_row) if n < df.height]
    return df.select(cols_keep)

# --- UI CELLS -----------------------------------------------------------------
@app.cell
def _():
    mo.md(f"""
## Open Government Data, provided by **{PROVIDER}**  
*Autogenerated Python (marimo) starter for dataset* **`{IDENTIFIER}`**
""")
    return

@app.cell
def _():
    mo.md(f"## Dataset\n# **{TITLE}**")
    return

@app.cell
def _():
    mo.md("""## Data set links

""" + DATASHOP_MD_LINK)
    return

@app.cell
def _():
    mo.md("## Metadata\n- **Dataset_identifier** `100006`
- **Title** `Verkehrszähldaten motorisierter Individualverkehr`
- **Description** `<p>Resultate der Messungen der Dauerzählstellen und Kurzzeitzählstellen für den Motorisierten Individualverkehr. </p><p>Aus Kostengründen sind nur die Werte des aktuellen Jahres und der letzten zwei Jahre als Tabelle / Visualisierung sichtbar bzw. via API abgreifbar. </p><p>Die Zählstellen, die zwischen allen Fahrzeugklassen unterscheiden können, ab dem Jahr 2014 können hier heruntergeladen werden: </p><ul><li><a href='https://data-bs.ch/mobilitaet/converted_MIV_Class_10_1.csv'>Leicht aufbereiteter Datensatz: https://data-bs.ch/mobilitaet/converted_MIV_Class_10_1.csv</a> </li><li><a href='https://data-bs.ch/mobilitaet/MIV_Class_10_1.csv'>Rohdaten: https://data-bs.ch/mobilitaet/MIV_Class_10_1.csv</a></li></ul><p>Die vollständigen Daten der Zählstellen, die mit FLIR (Forward Looking Infrared) messen und zwischen sechs Fahrzeugklassen unterscheiden können, können hier heruntergeladen werden:</p><ul><li><a href='https://data-bs.ch/mobilitaet/converted_FLIR_KtBS_MIV6.csv'>Leicht aufbereiteter Datensatz: https://data-bs.ch/mobilitaet/converted_FLIR_KtBS_MIV6.csv</a></li><li><a href='https://data-bs.ch/mobilitaet/FLIR_KtBS_MIV6.csv'>Rohdaten: https://data-bs.ch/mobilitaet/FLIR_KtBS_MIV6.csv</a></li></ul><p>Für die Lichtsignalanlagen (LSA) können die vollständigen Daten hier heruntergeladen werden:</p><ul><li><a href='https://data-bs.ch/mobilitaet/converted_MIV_LSA_Count.csv'>Leicht aufbereiteter Datensatz: https://data-bs.ch/mobilitaet/converted_MIV_LSA_Count.csv</a></li><li><a href='https://data-bs.ch/mobilitaet/MIV_LSA_Count.csv'>Rohdaten: https://data-bs.ch/mobilitaet/MIV_LSA_Count.csv</a></li></ul><p>Die Daten einzelner Jahre ab dem Jahr 2014 können unter der URL mit dem Muster https://data-bs.ch/mobilitaet/[JAHR]_MIV_Class_10_1.csv heruntergeladen werden, also zum Beispiel für das Jahr 2020 hier: https://data-bs.ch/mobilitaet/2020_MIV_Class_10_1.csv.<br>Für FLIR-Zähldaten muss folgendes Muster verwendet werden: https://data-bs.ch/mobilitaet/[JAHR]_FLIR_KtBS_MIV6.csv. <br>Für LSA-Zähldaten muss folgendes Muster verwendet werden: https://data-bs.ch/mobilitaet/[JAHR]_MIV_LSA.csv.</p><p>Die Zählstellen sind auf MET eingestellt (Spalten TimeFrom und TimeTo), d.h. die Zeitumstellung wird wie in Mitteleuropa ausgeführt. Bei der Umstellung von Winter- auf Sommerzeit fehlt die Stunde der Umstellung, dieser Tag hat dann 23 Stunden. Bei der Umstellung von Sommer- auf Winterzeit ist eine Stunde zu viel enthalten (der Tag hat dann 25 Stunden), die Stunde der Umstellung ist dann doppelt, aber mit unterschiedlichen Verkehrsdaten (da die gleiche Stunde zweimal durchlaufen wird).</p>`
- **Contact_name** `Open Data Basel-Stadt`
- **Issued** `2019-11-05`
- **Modified** `2025-09-15T07:26:51+00:00`
- **Rights** `NonCommercialAllowed-CommercialAllowed-ReferenceNotRequired`
- **Temporal_coverage_start_date** `2022-12-30T23:00:00+00:00`
- **Temporal_coverage_end_date** `2025-08-05T22:00:00+00:00`
- **Themes** `['Mobilität und Verkehr', 'Tourismus']`
- **Keywords** `['Autos', 'Motorräder', 'Busse', 'Lieferwagen', 'Lastwagen', 'Anhänger', 'Verkehr', 'Verkehrszählung', 'Erhebung']`
- **Publisher** `Amt für Mobilität`
- **Reference** `None`
")
    return

@app.cell
def _():
    mo.md("## Imports and helper functions\nUsing Polars for speed and memory efficiency.")
    return

@app.cell
def _():
    # Intentionally empty: imports are at the top of the file
    pass

@app.cell
def _():
    mo.md("## Load data\nThe dataset is read into a Polars DataFrame.")
    return

@app.cell
def _():
    # Read the dataset
    df = get_dataset('https://data.bs.ch/explore/dataset/100006/download')
    df = drop_all_null_columns(df)
    mo.md(f"Loaded **{df.height:,}** rows × **{df.width:,}** columns after dropping all-null columns.")
    df
    return df

@app.cell
def _(df):
    mo.md("## Quick profile")
    duplicates = int(df.is_duplicated().sum()) if df.height else 0
    schema = "\n".join([f"- `{k}`: {v}" for k, v in df.schema.items()])
    size_mb = f"{(df.estimated_size() or 0)/1_048_576:,.2f} MB"
    mo.md(
        f"""
- Approx. memory size: **{size_mb}**  
- Exact duplicates (row-wise): **{duplicates:,}**  
- Schema:
{schema}
"""
    )
    return

@app.cell
def _(df):
    mo.md("### Head (first 5 rows)")
    df.head(5)
    return

@app.cell
def _(df):
    mo.md("### Describe (numeric columns)")
    try:
        desc = df.describe()
        desc
    except Exception:
        mo.md("_No numeric columns to describe._")
    return

@app.cell
def _(df):
    mo.md("### Missingness overview (first 1,000 rows, up to 40 columns)")
    n = min(1000, df.height)
    c = min(40, df.width)
    if n == 0 or c == 0:
        mo.md("_Dataset empty._")
    else:
        sub = df.select(df.columns[:c]).head(n)
        miss = sub.to_pandas().isna().to_numpy()
        plt.figure()
        plt.imshow(miss, aspect="auto", interpolation="nearest")
        plt.title("Missingness matrix (True=missing)")
        plt.xlabel("columns")
        plt.ylabel("rows")
        plt.show()
    return

@app.cell
def _(df):
    mo.md("### Histograms (numeric)")
    num_cols = [c for c, t in df.schema.items() if pl.datatypes.is_numeric(t)]
    if not num_cols:
        mo.md("_No numeric data to plot._")
    else:
        for c in num_cols[:24]:  # cap to avoid excessive plots
            s = df.select(c).drop_nulls()
            if s.height == 0:
                continue
            plt.figure()
            plt.hist(s.to_series().to_list(), bins=25)
            plt.title(f"Histogram: {c}")
            plt.tight_layout()
            plt.show()
    return

@app.cell
def _():
    mo.md(f"**Questions about the data?** {CONTACT}")
    return

if __name__ == "__main__":
    app.run()
