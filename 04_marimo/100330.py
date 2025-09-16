# 100330 — marimo starter (Polars)
# Run:  marimo run 04_marimo/100330.py   (or: marimo edit ...)

# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "marimo>=0.8.0",
#   "polars>=1.5.0",
#   "pandas>=2.0.0",
#   "matplotlib>=3.8.0",
#   "requests>=2.31.0"
# ]
# ///

import os
import io
import requests
import polars as pl
import pandas as pd
import marimo as mo
import matplotlib.pyplot as plt

app = mo.App()

PROVIDER = """Statistisches Amt des Kantons Basel-Stadt - Fachstelle OGD"""
IDENTIFIER = """100330"""
TITLE = """Handelsregister: Firmen mit Rechtsform und Standort"""
DESCRIPTION = """<p>Dieser Datensatz umfasst die Firmen des Kantons Basel-Stadt, die im Handelsregister des Zefix (Zentraler Firmenindex) registriert sind. Das Zefix bildet das öffentlich zugängliche Angebot des Eidgenössischen Amtes für das Handelsregister (EHRA). Es stellt die Daten des Zentralregisters über verschiedene Zugänge wie die Zefix Webapplikation (<a href='https://www.zefix.admin.ch/' target='_blank'>https://www.zefix.admin.ch/</a>), die Zefix REST API (<a href='https://www.zefix.admin.ch/ZefixPublicREST/swagger-ui/index.html' target='_blank'>https://www.zefix.admin.ch/ZefixPublicREST/swagger-ui/index.html</a>), die Zefix Mobile App (<a href='https://www.zefixapp.ch' target='_blank'>https://www.zefixapp.ch</a>/) und als Linked Data in LINDAS (<a href='https://lindas.admin.ch/' target='_blank'>https://lindas.admin.ch/</a>, was hier verwendet wurde) über das Internet zur Verfügung. Über Zefix können die Daten sämtlicher im Handelsregister eingetragener Rechtseinheiten sowie die täglichen Handelsregisterpublikationen im SHAB (Schweizerischen Handelsamtsblatt, <a href='https://www.shab.ch/' target='_blank'>https://www.shab.ch/</a>) abgerufen werden. Der hier angebotene Datensatz beinhaltet tagesaktuelle Kerndaten der aktiven, im Handelsregister eingetragenen Rechtseinheiten, wie Firma/Name, Sitz und Domiziladresse.</p><p>LINDAS (Linked Data Service) fungiert in diesem Kontext als Plattform für die Vernetzung und den Zugriff auf diverse Datenquellen in der Schweiz, einschliesslich der Daten aus dem Zefix. Zur Gewinnung spezifischer Informationen über die im Kanton Basel-Stadt registrierten Unternehmen wird eine SPARQL-Abfrage verwendet. SPARQL, eine Abfragesprache für Daten im RDF-Format, ermöglicht den Zugriff auf detaillierte Datensätze über die Firmen aus dem LINDAS-Netzwerk. Die SPARQL-Abfrage kann unter einem bereitgestellten Link (<a href='https://s.zazuko.com/2WjT8iZ' target='_blank'>https://s.zazuko.com/2WjT8iZ</a>) aufgerufen werden. Die Abfrage wurde mithilfe der vorhandenen SPARQL-Abfrage von opendata.swiss (<a href='https://opendata.swiss/de/dataset/zefix-zentraler-firmenindex' target='_blank'>https://opendata.swiss/de/dataset/zefix-zentraler-firmenindex</a>) zum Zefix erweitert: <a href='https://github.com/opendatabs/data-processing/blob/master/zefix_handelsregister/etl.py' target='_blank'>https://github.com/opendatabs/data-processing/blob/master/zefix_handelsregister/etl.py</a></p><p>Diese Zefix-Daten und die der anderen Kantone werden von Open Data Basel-Stadt täglich aktualisiert und können unter folgendem HTTPS-Link heruntergeladen werden: <br><i>https://data-bs.ch/stata/zefix_handelsregister/all_cantons/companies_[Kantonskürzel].csv<br></i>Im Beispiel von Basel-Landschaft lautet der Link:<br><a href='https://data-bs.ch/stata/zefix_handelsregister/all_cantons/companies_BL.csv' target='_blank'>https://data-bs.ch/stata/zefix_handelsregister/all_cantons/companies_BL.csv </a><br></p><p>Der Datensatz enthält neben den Grundinformationen der Firmen auch erweiterte Spalten wie die Koordinaten der Unternehmen, die mithilfe der Betriebsadresse und von Nominatim (<a href='https://nominatim.org/' target='_blank'>https://nominatim.org/</a>) berechnet wurden. Nominatim ist ein Open-Source-Tool zur Geokodierung, das heisst, es wandelt Standortdaten wie Adressen oder Ortsnamen in geografische Koordinaten (Längen- und Breitengrade) um und umgekehrt.</p>"""
CONTACT = """Fachstelle für OGD Basel-Stadt | opendata@bs.ch"""
DATASHOP_MD_LINK = """[Direct data shop link for dataset](https://data.bs.ch/explore/dataset/100330)"""

def _ensure_data_dir():
    data_path = os.path.join(os.getcwd(), "..", "data")
    os.makedirs(data_path, exist_ok=True)
    return data_path

def get_dataset(url: str) -> pl.DataFrame:
    _ensure_data_dir()
    csv_path = os.path.join("..", "data", f"{IDENTIFIER}.csv")

    try:
        r = requests.get(
            url,
            params={"format": "csv", "timezone": "Europe%2FZurich"},
            timeout=60,
        )
        r.raise_for_status()
        with open(csv_path, "wb") as f:
            f.write(r.content)
        content = io.BytesIO(r.content)
    except Exception:
        content = csv_path if os.path.exists(csv_path) else None

    if content is None:
        raise RuntimeError("Could not download or locate dataset locally.")

    for sep in (";", ",", "\t"):
        try:
            df = pl.read_csv(
                content,
                separator=sep,
                ignore_errors=True,
                infer_schema_length=2000,
            )
            if df.width > 1:
                return df
        except Exception:
            if hasattr(content, "seek"):
                content.seek(0)

    return pl.read_csv(content, ignore_errors=True, infer_schema_length=2000)

def drop_all_null_columns(df: pl.DataFrame) -> pl.DataFrame:
    if df.height == 0:
        return df
    null_counts_row = df.null_count().row(0)
    cols_keep = [c for c, n in zip(df.columns, null_counts_row) if n < df.height]
    return df.select(cols_keep)

@app.cell
def _():
    mo.md(
        f"""## Open Government Data, provided by **{PROVIDER}**
*Autogenerated Python (marimo) starter for dataset* **`{IDENTIFIER}`**"""
    )
    return

@app.cell
def _():
    mo.md(
        f"""## Dataset
# **{TITLE}**"""
    )
    return

@app.cell
def _():
    mo.md(
        """## Data set links

""" + DATASHOP_MD_LINK
    )
    return

@app.cell
def _():
    mo.md(
        """## Metadata
- **Dataset_identifier** `100330`
- **Title** `Handelsregister: Firmen mit Rechtsform und Standort`
- **Description** `<p>Dieser Datensatz umfasst die Firmen des Kantons Basel-Stadt, die im Handelsregister des Zefix (Zentraler Firmenindex) registriert sind. Das Zefix bildet das öffentlich zugängliche Angebot des Eidgenössischen Amtes für das Handelsregister (EHRA). Es stellt die Daten des Zentralregisters über verschiedene Zugänge wie die Zefix Webapplikation (<a href="https://www.zefix.admin.ch/" target="_blank">https://www.zefix.admin.ch/</a>), die Zefix REST API (<a href="https://www.zefix.admin.ch/ZefixPublicREST/swagger-ui/index.html" target="_blank">https://www.zefix.admin.ch/ZefixPublicREST/swagger-ui/index.html</a>), die Zefix Mobile App (<a href="https://www.zefixapp.ch" target="_blank">https://www.zefixapp.ch</a>/) und als Linked Data in LINDAS (<a href="https://lindas.admin.ch/" target="_blank">https://lindas.admin.ch/</a>, was hier verwendet wurde) über das Internet zur Verfügung. Über Zefix können die Daten sämtlicher im Handelsregister eingetragener Rechtseinheiten sowie die täglichen Handelsregisterpublikationen im SHAB (Schweizerischen Handelsamtsblatt, <a href="https://www.shab.ch/" target="_blank">https://www.shab.ch/</a>) abgerufen werden. Der hier angebotene Datensatz beinhaltet tagesaktuelle Kerndaten der aktiven, im Handelsregister eingetragenen Rechtseinheiten, wie Firma/Name, Sitz und Domiziladresse.</p><p>LINDAS (Linked Data Service) fungiert in diesem Kontext als Plattform für die Vernetzung und den Zugriff auf diverse Datenquellen in der Schweiz, einschliesslich der Daten aus dem Zefix. Zur Gewinnung spezifischer Informationen über die im Kanton Basel-Stadt registrierten Unternehmen wird eine SPARQL-Abfrage verwendet. SPARQL, eine Abfragesprache für Daten im RDF-Format, ermöglicht den Zugriff auf detaillierte Datensätze über die Firmen aus dem LINDAS-Netzwerk. Die SPARQL-Abfrage kann unter einem bereitgestellten Link (<a href="https://s.zazuko.com/2WjT8iZ" target="_blank">https://s.zazuko.com/2WjT8iZ</a>) aufgerufen werden. Die Abfrage wurde mithilfe der vorhandenen SPARQL-Abfrage von opendata.swiss (<a href="https://opendata.swiss/de/dataset/zefix-zentraler-firmenindex" target="_blank">https://opendata.swiss/de/dataset/zefix-zentraler-firmenindex</a>) zum Zefix erweitert: <a href="https://github.com/opendatabs/data-processing/blob/master/zefix_handelsregister/etl.py" target="_blank">https://github.com/opendatabs/data-processing/blob/master/zefix_handelsregister/etl.py</a></p><p>Diese Zefix-Daten und die der anderen Kantone werden von Open Data Basel-Stadt täglich aktualisiert und können unter folgendem HTTPS-Link heruntergeladen werden: <br><i>https://data-bs.ch/stata/zefix_handelsregister/all_cantons/companies_[Kantonskürzel].csv<br></i>Im Beispiel von Basel-Landschaft lautet der Link:<br><a href="https://data-bs.ch/stata/zefix_handelsregister/all_cantons/companies_BL.csv" target="_blank">https://data-bs.ch/stata/zefix_handelsregister/all_cantons/companies_BL.csv </a><br></p><p>Der Datensatz enthält neben den Grundinformationen der Firmen auch erweiterte Spalten wie die Koordinaten der Unternehmen, die mithilfe der Betriebsadresse und von Nominatim (<a href="https://nominatim.org/" target="_blank">https://nominatim.org/</a>) berechnet wurden. Nominatim ist ein Open-Source-Tool zur Geokodierung, das heisst, es wandelt Standortdaten wie Adressen oder Ortsnamen in geografische Koordinaten (Längen- und Breitengrade) um und umgekehrt.</p>`
- **Contact_name** `Open Data Basel-Stadt`
- **Issued** `2024-01-18`
- **Modified** `2025-09-12T00:11:51+00:00`
- **Rights** `NonCommercialAllowed-CommercialAllowed-ReferenceNotRequired`
- **Temporal_coverage_start_date** `None`
- **Temporal_coverage_end_date** `None`
- **Themes** `['Industrie, Dienstleistungen', 'Volkswirtschaft']`
- **Keywords** `['Handelsregister', 'Zefix', 'Unternehmen', 'Betrieb', 'Betriebe', 'Aktiengesellschaft', 'Einzelunternehmen', 'Genossenschaft', 'GMBH', 'Kollektivgesellschaft', 'Stiftung', 'Verein']`
- **Publisher** `Open Data Basel-Stadt`
- **Reference** `None`
"""
    )
    return

@app.cell
def _():
    mo.md(
        """## Imports and helper functions
Using Polars for speed and memory efficiency."""
    )
    return

@app.cell
def _():
    pass

@app.cell
def _():
    mo.md(
        """## Load data
The dataset is read into a Polars DataFrame."""
    )
    return

@app.cell
def _():
    df = get_dataset('https://data.bs.ch/explore/dataset/100330/download?format=csv&timezone=Europe%2FZurich')
    df = drop_all_null_columns(df)
    mo.md(
        f"Loaded **{df.height:,}** rows × **{df.width:,}** columns after dropping all-null columns."
    )
    df
    return df

@app.cell
def _(df):
    mo.md("## Quick profile")
    duplicates = int(df.is_duplicated().sum()) if df.height else 0
    schema = "\n".join([f"- `{k}`: {v}" for k, v in df.schema.items()])
    try:
        size_mb = f"{(df.estimated_size() or 0)/1_048_576:,.2f} MB"
    except Exception:
        size_mb = "n/a"
    mo.md(
        f"""- Approx. memory size: **{size_mb}**  
- Exact duplicates (row-wise): **{duplicates:,}**  
- Schema:
{schema}"""
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
        plt.tight_layout()
        plt.show()
    return

@app.cell
def _(df):
    mo.md("### Histograms (numeric)")
    num_cols = [c for c, t in df.schema.items() if pl.datatypes.is_numeric(t)]
    if not num_cols:
        mo.md("_No numeric data to plot._")
    else:
        for c in num_cols[:24]:
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
    mo.md(f"""**Questions about the data?** {CONTACT}""")
    return

if __name__ == "__main__":
    app.run()
