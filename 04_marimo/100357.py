# 100357 — marimo starter (Polars)
# Run:  marimo run 04_marimo/100357.py   (or: marimo edit ...)

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
IDENTIFIER = """100357"""
TITLE = """Baumkronenbedeckung"""
DESCRIPTION = """<p>Dieser Datensatz zeigt die gesamte durch Bäume beschattete Fläche (Baumkronenbedeckung) im Kanton Basel-Stadt in verschiedenen Jahren. Der Kanton Basel-Stadt erhebt durch Laserabtastung der Oberfläche (LiDAR) Daten zur Baumkronenbedeckung (durch Bäume beschattete Fläche) über die gesamte Kantonsfläche. Die von LiDAR abgeleitete Baumkronenbedeckung und Kennzahlen wurden für 2012, 2021 und 2024 berechnet. Die Nachführung wird in Zukunft alle drei Jahre stattfinden (2027 und 2030), so dass die Entwicklung der Baumkronendeckung in Basel genau verfolgt werden kann.</p><p>Die Stadtgärtnerei stellt der interessierten Öffentlichkeit dieses digitale Wissen zur Verfügung: <a href='https://www.bs.ch/bvd/stadtgaertnerei/unsere-abteilungen/gruenflaechenunterhalt/staedtischer-baumbestand#baumkronenbedeckung' target='_blank'>Stadtgärtnerei des Kantons Basel-Stadt - Baumkronenbedeckung (https://www.bs.ch/bvd/stadtgaertnerei/unsere-abteilungen/gruenflaechenunterhalt/staedtischer-baumbestand#baumkronenbedeckung)</a>
</p><p>

Man kann die LiDAR-Daten im PNG- und PGW-Format in der Tabellenansicht herunterladen. Eine PGW-Datei ist eine Weltdatei, die Georeferenzierungsdaten für ein zugehöriges Bild im PNG-Format enthält, um dessen genaue Positionierung auf einer Karte zu ermöglichen.</p><p>Hier finden Sie die URLs zu den ZIP-Dateien, die beide Dateien enthalten:<br> 
<a href='https://data-bs.ch/stata/stadtgaertnerei/Baumkronenbedeckung_2012.zip' target='_blank'>https://data-bs.ch/stata/stadtgaertnerei/Baumkronenbedeckung_2012.zip</a><br><a href='https://data-bs.ch/stata/stadtgaertnerei/Baumkronenbedeckung_2021.zip' target='_blank'>https://data-bs.ch/stata/stadtgaertnerei/Baumkronenbedeckung_2021.zip</a><a href='https://data-bs.ch/stata/stadtgaertnerei/Baumkronenbedeckung_2021.zip' target='_blank'></a><br><a href='https://data-bs.ch/stata/stadtgaertnerei/Baumkronenbedeckung_2024.zip' target='_blank'>https://data-bs.ch/stata/stadtgaertnerei/Baumkronenbedeckung_2024.zip</a></p><p>Weiter kann man die LiDAR-Daten im TIF-Format in der Tabellenansicht herunterladen. Dieses Dateiformat bündelt alle Informationen in einer Datei.</p><p>Hier finden Sie die URLs zu der ZIP-Datei, die die TIF-Dateien aller Jahre enthält:<br><a href='https://data-bs.ch/stata/stadtgaertnerei/Baumkronenbedeckung_TIF.zip' target='_blank'>https://data-bs.ch/stata/stadtgaertnerei/Baumkronenbedeckung_TIF.zip</a></p><p>Auf der Website des Tiefbauamts können Sie die Daten mit dem GeoViewer betrachten: <a href='https://tiefbauamt-bs.ch/geoviewer/lidar' target='_blank'>https://tiefbauamt-bs.ch/geoviewer/lidar</a></p><p>Detailinformationen zur LiDAR-Technologie finden Sie hier: <a href='https://www.swisstopo.admin.ch/de/lidar-daten-swisstopo' target='_blank'>https://www.swisstopo.admin.ch/de/lidar-daten-swisstopo</a> </p>"""
CONTACT = """Fachstelle für OGD Basel-Stadt | opendata@bs.ch"""
DATASHOP_MD_LINK = """[Direct data shop link for dataset](https://data.bs.ch/explore/dataset/100357)"""

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
- **Dataset_identifier** `100357`
- **Title** `Baumkronenbedeckung`
- **Description** `<p>Dieser Datensatz zeigt die gesamte durch Bäume beschattete Fläche (Baumkronenbedeckung) im Kanton Basel-Stadt in verschiedenen Jahren. Der Kanton Basel-Stadt erhebt durch Laserabtastung der Oberfläche (LiDAR) Daten zur Baumkronenbedeckung (durch Bäume beschattete Fläche) über die gesamte Kantonsfläche. Die von LiDAR abgeleitete Baumkronenbedeckung und Kennzahlen wurden für 2012, 2021 und 2024 berechnet. Die Nachführung wird in Zukunft alle drei Jahre stattfinden (2027 und 2030), so dass die Entwicklung der Baumkronendeckung in Basel genau verfolgt werden kann.</p><p>Die Stadtgärtnerei stellt der interessierten Öffentlichkeit dieses digitale Wissen zur Verfügung: <a href="https://www.bs.ch/bvd/stadtgaertnerei/unsere-abteilungen/gruenflaechenunterhalt/staedtischer-baumbestand#baumkronenbedeckung" target="_blank">Stadtgärtnerei des Kantons Basel-Stadt - Baumkronenbedeckung (https://www.bs.ch/bvd/stadtgaertnerei/unsere-abteilungen/gruenflaechenunterhalt/staedtischer-baumbestand#baumkronenbedeckung)</a>
</p><p>

Man kann die LiDAR-Daten im PNG- und PGW-Format in der Tabellenansicht herunterladen. Eine PGW-Datei ist eine Weltdatei, die Georeferenzierungsdaten für ein zugehöriges Bild im PNG-Format enthält, um dessen genaue Positionierung auf einer Karte zu ermöglichen.</p><p>Hier finden Sie die URLs zu den ZIP-Dateien, die beide Dateien enthalten:<br> 
<a href="https://data-bs.ch/stata/stadtgaertnerei/Baumkronenbedeckung_2012.zip" target="_blank">https://data-bs.ch/stata/stadtgaertnerei/Baumkronenbedeckung_2012.zip</a><br><a href="https://data-bs.ch/stata/stadtgaertnerei/Baumkronenbedeckung_2021.zip" target="_blank">https://data-bs.ch/stata/stadtgaertnerei/Baumkronenbedeckung_2021.zip</a><a href="https://data-bs.ch/stata/stadtgaertnerei/Baumkronenbedeckung_2021.zip" target="_blank"></a><br><a href="https://data-bs.ch/stata/stadtgaertnerei/Baumkronenbedeckung_2024.zip" target="_blank">https://data-bs.ch/stata/stadtgaertnerei/Baumkronenbedeckung_2024.zip</a></p><p>Weiter kann man die LiDAR-Daten im TIF-Format in der Tabellenansicht herunterladen. Dieses Dateiformat bündelt alle Informationen in einer Datei.</p><p>Hier finden Sie die URLs zu der ZIP-Datei, die die TIF-Dateien aller Jahre enthält:<br><a href="https://data-bs.ch/stata/stadtgaertnerei/Baumkronenbedeckung_TIF.zip" target="_blank">https://data-bs.ch/stata/stadtgaertnerei/Baumkronenbedeckung_TIF.zip</a></p><p>Auf der Website des Tiefbauamts können Sie die Daten mit dem GeoViewer betrachten: <a href="https://tiefbauamt-bs.ch/geoviewer/lidar" target="_blank">https://tiefbauamt-bs.ch/geoviewer/lidar</a></p><p>Detailinformationen zur LiDAR-Technologie finden Sie hier: <a href="https://www.swisstopo.admin.ch/de/lidar-daten-swisstopo" target="_blank">https://www.swisstopo.admin.ch/de/lidar-daten-swisstopo</a> </p>`
- **Contact_name** `Open Data Basel-Stadt`
- **Issued** `2024-03-23`
- **Modified** `2025-09-10T14:24:30+00:00`
- **Rights** `NonCommercialAllowed-CommercialAllowed-ReferenceRequired`
- **Temporal_coverage_start_date** `2012-12-30T23:00:00+00:00`
- **Temporal_coverage_end_date** `None`
- **Themes** `['Raum und Umwelt', 'Geographie']`
- **Keywords** `['Baum', 'Baumbestand', 'Baumkrone', 'Kronenbedeckung', 'Vegetation', 'LiDAR']`
- **Publisher** `Stadtgärtnerei`
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
    df = get_dataset('https://data.bs.ch/explore/dataset/100357/download?format=csv&timezone=Europe%2FZurich')
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
