# 100302 — marimo starter (Polars)
# Run:  marimo run 04_marimo/100302.py   (or: marimo edit ...)

import os
import io
import requests
import polars as pl
import marimo as mo
import matplotlib.pyplot as plt

app = mo.app()

# --- CONFIG / LINKS -----------------------------------------------------------
PROVIDER = "Statistisches Amt des Kantons Basel-Stadt - Fachstelle OGD"
IDENTIFIER = "100302"
TITLE = "Abwassermonitoring: Influenza und RSV"
DESCRIPTION = "<p><b>Figur<br></b><span>Der Datensatz zeigt den 7-Tage-Median der RNA-Kopien des angegebenen Virus jeweils pro Tag und 100‘000 Personen im Abwasser der Abwasserreinigungs-Anlage (ARA) Basel sowie den 7-Tage-Median der entsprechenden Fallzahlen. Der Datensatz wird i.d.R. jeweils dienstags mit den Daten bis vorangegangenem Sonntag aktualisiert. In einzelnen Wochen kann es zu Verschiebungen kommen.</span></p><p><span style='font-weight: bolder;'>Messung<br></span>Die ProRheno AG (Betreiber der ARA Basel) entnimmt jeweils eine 24h-Probe des Rohabwassers, welche durch das Kantonale Laboratorium Basel-Stadt (KL BS) auf RNA der angegebenen Viren untersucht wird. Die Messmethodik wurde dabei seit Beginn des Monitorings nicht verändert: siehe Publikation <a href='https://smw.ch/index.php/smw/article/view/3226' target='_blank'>https://smw.ch/index.php/smw/article/view/3226</a>. Die Plausibilität der Werte wird laufend anhand interner Qualitätsparameter überprüft. Das Untersuchungsgebiet umfasst das Einzugsgebiet der ARA Basel, welches sich hauptsächlich aus dem Kanton Basel-Stadt sowie den Gemeinden Allschwil, Binningen, Birsfelden, Bottmingen, Oberwil und Schönenbuch (alle Kanton Baselland) zusammensetzt. Bis Ende Juni 2023 wurden die Messwerte des KL BS auch auf dem Abwasser-Dashboard des BAG <a href='https://www.covid19.admin.ch/de/epidemiologic/waste-water?wasteWaterFacility=270101' target='_blank'>Covid-⁠19 Schweiz | Coronavirus | Dashboard (https://www.covid19.admin.ch/de/epidemiologic/waste-water?wasteWaterFacility=270101)</a> dargestellt. Ab Juli 2023 werden auf dieser Seite die Messwerte der EAWAG <a href='https://www.eawag.ch/de/abteilung/sww/projekte/sars-cov2-im-abwasser/' target='_blank'>SARS-CoV2 im Abwasser - Eawag</a> (<a href='https://www.eawag.ch/de/abteilung/sww/projekte/sars-cov2-im-abwasser/' target='_blank'>https://www.eawag.ch/de/abteilung/sww/projekte/sars-cov2-im-abwasser/</a>) publiziert, welche ebenfalls das Rohabwasser der ARA Basel untersucht. Die vom KL BS und der EAWAG verwendeten Untersuchungsmethoden sind sehr ähnlich aber nicht identisch.</p><p><span style='font-size:11.0pt;font-family:'Arial',sans-serif;
mso-fareast-font-family:Calibri;mso-fareast-theme-font:minor-latin;mso-ansi-language:
DE-CH;mso-fareast-language:EN-US;mso-bidi-language:AR-SA'>In den Zeiträumen
29.4. bis 1.8.2022 (ausser 1.6.2022 und 5.6.2022) und 30.5.2023 bis 3.9.2023
wurden keine Abwasserproben auf Influenza und RSV untersucht.</span><br></p><p><b>Fallzahlen <br></b>Die Fallzahlen entsprechen der Anzahl der bestätigten und dem Kanton gemeldeten Fälle der dargestellten Infektionen im Einzugsgebiet der ARA Basel.<br></p><p><b>Interpretation der Kurven<br></b><span'>Beim Monitoring von Viren im Abwasser geht es in erster Linie darum, Trends zu erkennen (insbesondere natürlich die Zunahme eines zirkulierenden Virus). Es ist nicht möglich, daraus eine bestimmte Fallzahl oder den Schweregrad einer Infektion abzuleiten. Ein Vergleich des Kurvenausschlags (Höhe der Peaks) zu verschiedenen Zeitpunkten ist kaum möglich, da z.B. unterschiedliche Virusvarianten zu unterschiedlichen Virusmengen pro Fall führen. Unterschiedliche Virusvarianten können auch die Symptomatik beeinflussen, so dass z.B. Infektionen bei Menschen spurlos verlaufen, aber dennoch Viren ins Abwasser abgegeben werden.</span'></p>

<div class='html_button btn-left'>
    <a class='btn customButton large' href='https://data.bs.ch/pages/abwassermonitoring-dashboard/'>Hier gehts zum Dashboard</a>
</div>"
CONTACT = "Fachstelle für OGD Basel-Stadt | opendata@bs.ch"
DATASHOP_MD_LINK = """[Direct data shop link for dataset](https://data.bs.ch/explore/dataset/100302)"""

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
    mo.md("## Metadata\n- **Dataset_identifier** `100302`
- **Title** `Abwassermonitoring: Influenza und RSV`
- **Description** `<p><b>Figur<br></b><span>Der Datensatz zeigt den 7-Tage-Median der RNA-Kopien des angegebenen Virus jeweils pro Tag und 100‘000 Personen im Abwasser der Abwasserreinigungs-Anlage (ARA) Basel sowie den 7-Tage-Median der entsprechenden Fallzahlen. Der Datensatz wird i.d.R. jeweils dienstags mit den Daten bis vorangegangenem Sonntag aktualisiert. In einzelnen Wochen kann es zu Verschiebungen kommen.</span></p><p><span style='font-weight: bolder;'>Messung<br></span>Die ProRheno AG (Betreiber der ARA Basel) entnimmt jeweils eine 24h-Probe des Rohabwassers, welche durch das Kantonale Laboratorium Basel-Stadt (KL BS) auf RNA der angegebenen Viren untersucht wird. Die Messmethodik wurde dabei seit Beginn des Monitorings nicht verändert: siehe Publikation <a href='https://smw.ch/index.php/smw/article/view/3226' target='_blank'>https://smw.ch/index.php/smw/article/view/3226</a>. Die Plausibilität der Werte wird laufend anhand interner Qualitätsparameter überprüft. Das Untersuchungsgebiet umfasst das Einzugsgebiet der ARA Basel, welches sich hauptsächlich aus dem Kanton Basel-Stadt sowie den Gemeinden Allschwil, Binningen, Birsfelden, Bottmingen, Oberwil und Schönenbuch (alle Kanton Baselland) zusammensetzt. Bis Ende Juni 2023 wurden die Messwerte des KL BS auch auf dem Abwasser-Dashboard des BAG <a href='https://www.covid19.admin.ch/de/epidemiologic/waste-water?wasteWaterFacility=270101' target='_blank'>Covid-⁠19 Schweiz | Coronavirus | Dashboard (https://www.covid19.admin.ch/de/epidemiologic/waste-water?wasteWaterFacility=270101)</a> dargestellt. Ab Juli 2023 werden auf dieser Seite die Messwerte der EAWAG <a href='https://www.eawag.ch/de/abteilung/sww/projekte/sars-cov2-im-abwasser/' target='_blank'>SARS-CoV2 im Abwasser - Eawag</a> (<a href='https://www.eawag.ch/de/abteilung/sww/projekte/sars-cov2-im-abwasser/' target='_blank'>https://www.eawag.ch/de/abteilung/sww/projekte/sars-cov2-im-abwasser/</a>) publiziert, welche ebenfalls das Rohabwasser der ARA Basel untersucht. Die vom KL BS und der EAWAG verwendeten Untersuchungsmethoden sind sehr ähnlich aber nicht identisch.</p><p><span style='font-size:11.0pt;font-family:'Arial',sans-serif;
mso-fareast-font-family:Calibri;mso-fareast-theme-font:minor-latin;mso-ansi-language:
DE-CH;mso-fareast-language:EN-US;mso-bidi-language:AR-SA'>In den Zeiträumen
29.4. bis 1.8.2022 (ausser 1.6.2022 und 5.6.2022) und 30.5.2023 bis 3.9.2023
wurden keine Abwasserproben auf Influenza und RSV untersucht.</span><br></p><p><b>Fallzahlen <br></b>Die Fallzahlen entsprechen der Anzahl der bestätigten und dem Kanton gemeldeten Fälle der dargestellten Infektionen im Einzugsgebiet der ARA Basel.<br></p><p><b>Interpretation der Kurven<br></b><span'>Beim Monitoring von Viren im Abwasser geht es in erster Linie darum, Trends zu erkennen (insbesondere natürlich die Zunahme eines zirkulierenden Virus). Es ist nicht möglich, daraus eine bestimmte Fallzahl oder den Schweregrad einer Infektion abzuleiten. Ein Vergleich des Kurvenausschlags (Höhe der Peaks) zu verschiedenen Zeitpunkten ist kaum möglich, da z.B. unterschiedliche Virusvarianten zu unterschiedlichen Virusmengen pro Fall führen. Unterschiedliche Virusvarianten können auch die Symptomatik beeinflussen, so dass z.B. Infektionen bei Menschen spurlos verlaufen, aber dennoch Viren ins Abwasser abgegeben werden.</span'></p>

<div class='html_button btn-left'>
    <a class='btn customButton large' href='https://data.bs.ch/pages/abwassermonitoring-dashboard/'>Hier gehts zum Dashboard</a>
</div>`
- **Contact_name** `Open Data Basel-Stadt`
- **Issued** `2023-12-19`
- **Modified** `2025-09-09T07:42:23+00:00`
- **Rights** `NonCommercialAllowed-CommercialAllowed-ReferenceRequired`
- **Temporal_coverage_start_date** `2023-08-13T22:00:00+00:00`
- **Temporal_coverage_end_date** `None`
- **Themes** `['Gesundheit']`
- **Keywords** `['Abwasser', 'Influenza', 'RSV', 'Kanalisation', 'Krankheit', 'Kläranlage', 'Grippe']`
- **Publisher** `Kantonales Laboratorium`
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
    df = get_dataset('https://data.bs.ch/explore/dataset/100302/download')
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
