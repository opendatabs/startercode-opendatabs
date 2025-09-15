# 100162 — marimo starter (Polars)
# Run:  marimo run 04_marimo/100162.py   (or: marimo edit ...)

import os
import io
import requests
import polars as pl
import marimo as mo
import matplotlib.pyplot as plt

app = mo.app()

# --- CONFIG / LINKS -----------------------------------------------------------
PROVIDER = "Statistisches Amt des Kantons Basel-Stadt - Fachstelle OGD"
IDENTIFIER = "100162"
TITLE = "Coronavirus (COVID-19): Geimpfte Personen mit Wohnsitz in Basel-Stadt"
DESCRIPTION = "<p>Dieser Datensatz zeigt die SARS-CoV-2-Impfungen, welche an Personen mit Wohnsitz im Kanton Basel-Stadt verabreicht wurden nach Impfstatus. Unterschieden wird dabei auf oberster Ebene in teilweise geimpfte Personen, vollständig geimpfte Personen und Personen mit Auffrischimpfung. Die Definitionen dieser Einteilung finden Sie in den Spaltenbeschreibungen resp. im Datensatzschema. </p><p>Die Datenbasis bildet der Vaccination Monitoring Data Lake (VMDL) des BAG. Der Datensatz wird stündlich aktualisiert. </p><p>Anmerkung: Die geimpften Personen wohnen im Kanton Basel-Stadt, müssen aber nicht zwingend auch im Kanton Basel-Stadt geimpft worden sein. Aus diesem Grund unterscheiden sich die hier publizierten Zahlen auch von jenen im <a href='https://data.bs.ch/explore/dataset/100111/' target='_blank'>Datensatz mit den im Kanton Basel-Stadt verabreichten Impfungen</a>.</p><p>Methodische Hinweise:<br>Als vollständig geimpft gelten folgende Personen:</p><ul><li>Mindestens zwei Dosen einer Mehrdosisimpfung</li><li>Eine Dosis einer Einmaldosisimpfung</li><li>Genesene (positiver PCR-Test) und mindestens eine Dosis einer Einmal- oder einer Mehrdosisimpfung</li></ul><p>Als teilweise geimpft gelten folgende Personen:</p><ul><li>Erste Dosis einer Mehrdosisimpfung</li></ul><p>Als mit mindestens einer Dosis geimpft gelten folgende Personen:</p><ul><li>Mindestens eine Dosis einer Einmal- oder einer Mehrfachdosisimpfung</li></ul><p>Als Impfung aufgefrischt gelten folgende Personen:</p><ul><li>Mindestens dritte Dosis einer Mehrfachdosisimpfung nach abgeschlossener Grundimmunisierung durch Mehrdosisimpfung</li><li>Genesene (positiver PCR-Test) mit zweiter Dosis einer Mehrdosisimpfung</li><li>Erste Dosis einer Mehrdosisimpfung nach abgeschlossener Grundimmunisierung durch eine Einmaldosisimpfung</li></ul><p>Der Code für die Berechnung der verschiedenen Impftypen kann unter diesem Link eingesehen werden: <a href='https://github.com/opendatabs/data-processing/blob/master/bag_coronavirus/src/etl_vmdl_impftyp.py' target='_blank'>https://github.com/opendatabs/data-processing/blob/master/bag_coronavirus/src/etl_vmdl_impftyp.py</a><a href='https://github.com/opendatabs/data-processing/blob/master/bag_coronavirus/src/etl_vmdl_impftyp.py' target='_blank'></a></p><p>Die Meldepflicht der COVID-Impfungen via VMDL Plattform des Bundes wurde per 1. Juli 2023 aufgehoben. Nach diesem Datum wurden Impfungen deshalb nicht mehr systematisch erfasst. Der vorliegende Datensatz zeigt deshalb Impfungen nur bis 1. Juli 2023.<br></p>"
CONTACT = "Fachstelle für OGD Basel-Stadt | opendata@bs.ch"
DATASHOP_MD_LINK = """[Direct data shop link for dataset](https://data.bs.ch/explore/dataset/100162)"""

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
    mo.md("## Metadata\n- **Dataset_identifier** `100162`
- **Title** `Coronavirus (COVID-19): Geimpfte Personen mit Wohnsitz in Basel-Stadt`
- **Description** `<p>Dieser Datensatz zeigt die SARS-CoV-2-Impfungen, welche an Personen mit Wohnsitz im Kanton Basel-Stadt verabreicht wurden nach Impfstatus. Unterschieden wird dabei auf oberster Ebene in teilweise geimpfte Personen, vollständig geimpfte Personen und Personen mit Auffrischimpfung. Die Definitionen dieser Einteilung finden Sie in den Spaltenbeschreibungen resp. im Datensatzschema. </p><p>Die Datenbasis bildet der Vaccination Monitoring Data Lake (VMDL) des BAG. Der Datensatz wird stündlich aktualisiert. </p><p>Anmerkung: Die geimpften Personen wohnen im Kanton Basel-Stadt, müssen aber nicht zwingend auch im Kanton Basel-Stadt geimpft worden sein. Aus diesem Grund unterscheiden sich die hier publizierten Zahlen auch von jenen im <a href='https://data.bs.ch/explore/dataset/100111/' target='_blank'>Datensatz mit den im Kanton Basel-Stadt verabreichten Impfungen</a>.</p><p>Methodische Hinweise:<br>Als vollständig geimpft gelten folgende Personen:</p><ul><li>Mindestens zwei Dosen einer Mehrdosisimpfung</li><li>Eine Dosis einer Einmaldosisimpfung</li><li>Genesene (positiver PCR-Test) und mindestens eine Dosis einer Einmal- oder einer Mehrdosisimpfung</li></ul><p>Als teilweise geimpft gelten folgende Personen:</p><ul><li>Erste Dosis einer Mehrdosisimpfung</li></ul><p>Als mit mindestens einer Dosis geimpft gelten folgende Personen:</p><ul><li>Mindestens eine Dosis einer Einmal- oder einer Mehrfachdosisimpfung</li></ul><p>Als Impfung aufgefrischt gelten folgende Personen:</p><ul><li>Mindestens dritte Dosis einer Mehrfachdosisimpfung nach abgeschlossener Grundimmunisierung durch Mehrdosisimpfung</li><li>Genesene (positiver PCR-Test) mit zweiter Dosis einer Mehrdosisimpfung</li><li>Erste Dosis einer Mehrdosisimpfung nach abgeschlossener Grundimmunisierung durch eine Einmaldosisimpfung</li></ul><p>Der Code für die Berechnung der verschiedenen Impftypen kann unter diesem Link eingesehen werden: <a href='https://github.com/opendatabs/data-processing/blob/master/bag_coronavirus/src/etl_vmdl_impftyp.py' target='_blank'>https://github.com/opendatabs/data-processing/blob/master/bag_coronavirus/src/etl_vmdl_impftyp.py</a><a href='https://github.com/opendatabs/data-processing/blob/master/bag_coronavirus/src/etl_vmdl_impftyp.py' target='_blank'></a></p><p>Die Meldepflicht der COVID-Impfungen via VMDL Plattform des Bundes wurde per 1. Juli 2023 aufgehoben. Nach diesem Datum wurden Impfungen deshalb nicht mehr systematisch erfasst. Der vorliegende Datensatz zeigt deshalb Impfungen nur bis 1. Juli 2023.<br></p>`
- **Contact_name** `Open Data Basel-Stadt`
- **Issued** `2021-11-30`
- **Modified** `2024-01-04T08:34:36+00:00`
- **Rights** `NonCommercialAllowed-CommercialAllowed-ReferenceRequired`
- **Temporal_coverage_start_date** `2020-12-27T23:00:00+00:00`
- **Temporal_coverage_end_date** `2023-06-30T22:00:00+00:00`
- **Themes** `['Gesundheit']`
- **Keywords** `['SARS-CoV-2', 'Corona', 'Coronavirus', 'COVID-19', 'impfen', 'Impfung', 'Impftermin', 'Impfzentrum', 'Spital']`
- **Publisher** `Medizinische Dienste`
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
    df = get_dataset('https://data.bs.ch/explore/dataset/100162/download')
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
