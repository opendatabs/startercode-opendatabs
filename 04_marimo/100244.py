# 100244 — marimo starter (Polars)
# Run:  marimo run 04_marimo/100244.py   (or: marimo edit ...)

import os
import io
import requests
import polars as pl
import marimo as mo
import matplotlib.pyplot as plt

app = mo.app()

# --- CONFIG / LINKS -----------------------------------------------------------
PROVIDER = "Statistisches Amt des Kantons Basel-Stadt - Fachstelle OGD"
IDENTIFIER = "100244"
TITLE = "Gefahrenstufen für Hochwasser"
DESCRIPTION = "<p style='margin-bottom: 11px; font-size: 1.1em; line-height: 1.5; color: rgb(69, 69, 69); font-family: 'Frutiger Neue Regular', Arial, sans-serif;'><span style='font-family: 'Frutiger Neue Bold', Arial, sans-serif; font-size: 15.4px;'>Entsprechend den Bestimmungen der Alarmierungsverordnung verwendet das BAFU für die Warnung vor Hochwasser eine fünfstufige Gefahrenskala. Die Gefahrenstufen geben Auskunft über die Intensität des Ereignisses, die möglichen Auswirkungen und Verhaltensempfehlungen.</span><br></p><p style='margin-bottom: 11px; font-size: 1.1em; line-height: 1.5; color: rgb(69, 69, 69); font-family: 'Frutiger Neue Regular', Arial, sans-serif;'>Die Schwellenwerte, die die Gefahrenstufen abgrenzen, werden ausgehend vom vorhandenen Wissen über das Verhalten des jeweiligen Fliessgewässers festgelegt (Pegel, ab dem das Gewässer über die Ufer tritt, ab dem erste Schäden eintreten usw.). Diese Schwellenwerte entsprechen in etwa der Jährlichkeit von Hochwasserereignissen, also einer Wiederkehrperiode von durchschnittlich 2, 10, 30 oder 100 Jahren.</p><ul style='line-height: 1.5; margin: 1.5em 0px 0px; padding: 0px 0px 0px 0.4em; list-style-type: square; color: rgb(69, 69, 69); font-family: 'Frutiger Neue Regular', Arial, sans-serif;'><li style='font-size: 1.1em; line-height: 1.5; margin-left: 0.8em;'>Die <span style='font-family: 'Frutiger Neue Bold', Arial, sans-serif;'>Gefahrenstufe 1 </span>entspricht ungefähr einer Abflussmenge, die unter dem Wert liegt, der im Durchschnitt einmal in 2 Jahren erreicht wird.</li><li style='font-size: 1.1em; line-height: 1.5; margin-left: 0.8em;'>Die <span style='font-family: 'Frutiger Neue Bold', Arial, sans-serif;'>Gefahrenstufe 2 </span>entspricht ungefähr einer Abflussmenge, die durchschnittlich einmal innerhalb von 2 bis 10 Jahren auftritt.</li><li style='font-size: 1.1em; line-height: 1.5; margin-left: 0.8em;'>Die <span style='font-family: 'Frutiger Neue Bold', Arial, sans-serif;'>Gefahrenstufe 3 </span>entspricht ungefähr einer Abflussmenge, die im Durchschnitt einmal innerhalb von 10 bis 30 Jahren auftritt.</li><li style='font-size: 1.1em; line-height: 1.5; margin-left: 0.8em;'>Die <span style='font-family: 'Frutiger Neue Bold', Arial, sans-serif;'>Gefahrenstufe 4 </span>entspricht ungefähr einer Abflussmenge, die im Durchschnitt einmal innerhalb von 30 bis 100 Jahren auftritt.</li><li style='font-size: 1.1em; line-height: 1.5; margin-left: 0.8em;'>Die <span style='font-family: 'Frutiger Neue Bold', Arial, sans-serif;'>Gefahrenstufe 5 </span>entspricht ungefähr einer Abflussmenge, die im Durchschnitt höchstens einmal in 100 Jahren auftritt.</li></ul><p style='font-size: 1.1em; line-height: 1.5; margin-left: 0.8em;'><br></p><p style='line-height: 1.5; margin-left: 0.8em;'><span style='font-size: 15.4px;'>Für weitere Informationen siehe </span><a href='https://www.hydrodaten.admin.ch/de/die-5-gefahrenstufen-fuer-hochwasser' target='_blank'>https://www.hydrodaten.admin.ch/de/die-5-gefahrenstufen-fuer-hochwasser</a><span style='font-size: 15.4px;'> </span><br></p>"
CONTACT = "Fachstelle für OGD Basel-Stadt | opendata@bs.ch"
DATASHOP_MD_LINK = """[Direct data shop link for dataset](https://data.bs.ch/explore/dataset/100244)"""

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
    mo.md("## Metadata\n- **Dataset_identifier** `100244`
- **Title** `Gefahrenstufen für Hochwasser`
- **Description** `<p style='margin-bottom: 11px; font-size: 1.1em; line-height: 1.5; color: rgb(69, 69, 69); font-family: 'Frutiger Neue Regular', Arial, sans-serif;'><span style='font-family: 'Frutiger Neue Bold', Arial, sans-serif; font-size: 15.4px;'>Entsprechend den Bestimmungen der Alarmierungsverordnung verwendet das BAFU für die Warnung vor Hochwasser eine fünfstufige Gefahrenskala. Die Gefahrenstufen geben Auskunft über die Intensität des Ereignisses, die möglichen Auswirkungen und Verhaltensempfehlungen.</span><br></p><p style='margin-bottom: 11px; font-size: 1.1em; line-height: 1.5; color: rgb(69, 69, 69); font-family: 'Frutiger Neue Regular', Arial, sans-serif;'>Die Schwellenwerte, die die Gefahrenstufen abgrenzen, werden ausgehend vom vorhandenen Wissen über das Verhalten des jeweiligen Fliessgewässers festgelegt (Pegel, ab dem das Gewässer über die Ufer tritt, ab dem erste Schäden eintreten usw.). Diese Schwellenwerte entsprechen in etwa der Jährlichkeit von Hochwasserereignissen, also einer Wiederkehrperiode von durchschnittlich 2, 10, 30 oder 100 Jahren.</p><ul style='line-height: 1.5; margin: 1.5em 0px 0px; padding: 0px 0px 0px 0.4em; list-style-type: square; color: rgb(69, 69, 69); font-family: 'Frutiger Neue Regular', Arial, sans-serif;'><li style='font-size: 1.1em; line-height: 1.5; margin-left: 0.8em;'>Die <span style='font-family: 'Frutiger Neue Bold', Arial, sans-serif;'>Gefahrenstufe 1 </span>entspricht ungefähr einer Abflussmenge, die unter dem Wert liegt, der im Durchschnitt einmal in 2 Jahren erreicht wird.</li><li style='font-size: 1.1em; line-height: 1.5; margin-left: 0.8em;'>Die <span style='font-family: 'Frutiger Neue Bold', Arial, sans-serif;'>Gefahrenstufe 2 </span>entspricht ungefähr einer Abflussmenge, die durchschnittlich einmal innerhalb von 2 bis 10 Jahren auftritt.</li><li style='font-size: 1.1em; line-height: 1.5; margin-left: 0.8em;'>Die <span style='font-family: 'Frutiger Neue Bold', Arial, sans-serif;'>Gefahrenstufe 3 </span>entspricht ungefähr einer Abflussmenge, die im Durchschnitt einmal innerhalb von 10 bis 30 Jahren auftritt.</li><li style='font-size: 1.1em; line-height: 1.5; margin-left: 0.8em;'>Die <span style='font-family: 'Frutiger Neue Bold', Arial, sans-serif;'>Gefahrenstufe 4 </span>entspricht ungefähr einer Abflussmenge, die im Durchschnitt einmal innerhalb von 30 bis 100 Jahren auftritt.</li><li style='font-size: 1.1em; line-height: 1.5; margin-left: 0.8em;'>Die <span style='font-family: 'Frutiger Neue Bold', Arial, sans-serif;'>Gefahrenstufe 5 </span>entspricht ungefähr einer Abflussmenge, die im Durchschnitt höchstens einmal in 100 Jahren auftritt.</li></ul><p style='font-size: 1.1em; line-height: 1.5; margin-left: 0.8em;'><br></p><p style='line-height: 1.5; margin-left: 0.8em;'><span style='font-size: 15.4px;'>Für weitere Informationen siehe </span><a href='https://www.hydrodaten.admin.ch/de/die-5-gefahrenstufen-fuer-hochwasser' target='_blank'>https://www.hydrodaten.admin.ch/de/die-5-gefahrenstufen-fuer-hochwasser</a><span style='font-size: 15.4px;'> </span><br></p>`
- **Contact_name** `Open Data Basel-Stadt`
- **Issued** `2023-01-25`
- **Modified** `2022-12-16T12:54:26+00:00`
- **Rights** `NonCommercialAllowed-CommercialAllowed-ReferenceNotRequired`
- **Temporal_coverage_start_date** `None`
- **Temporal_coverage_end_date** `None`
- **Themes** `['Raum und Umwelt']`
- **Keywords** `['Rhein', 'Birs', 'Wiese', 'Pegel', 'Wasserstand', 'Abflussmenge', 'Strömung', 'Wasser']`
- **Publisher** `Bundesamt für Umwelt BAFU`
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
    df = get_dataset('https://data.bs.ch/explore/dataset/100244/download')
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
