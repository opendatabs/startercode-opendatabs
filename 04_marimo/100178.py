# 100178 — marimo starter (Polars)
# Run:  marimo run 04_marimo/100178.py   (or: marimo edit ...)

import os
import io
import requests
import polars as pl
import marimo as mo
import matplotlib.pyplot as plt

app = mo.app()

# --- CONFIG / LINKS -----------------------------------------------------------
PROVIDER = "Statistisches Amt des Kantons Basel-Stadt - Fachstelle OGD"
IDENTIFIER = "100178"
TITLE = "Smarte Strasse: Luftqualität Vergleichsmessungen"
DESCRIPTION = "<p>Das <a href='https://www.baselland.ch/politik-und-behorden/direktionen/bau-und-umweltschutzdirektion/lufthygiene' target='_blank'>Lufthygieneamt beider Basel</a> (LHA) testet im Projekt «Smarte Strasse» kosteneffiziente Mikrosensoren auf ihre Genauigkeit und Zuverlässigkeit. Der installierte Sensor vom Typ «Nubo» der Firma Sensirion AG ist in der Lage, die Konzentration verschiedener Schadstoffe in der Luft in Echtzeit zu ermitteln. Gemessen werden die Gehalte der Gase Stickstoffdioxid (NO2) und Ozon (O3), sowie die feinere Fraktion des Feinstaubs «PM2.5». Dieser Datensatz enthält die Daten von drei «Nubo»- Sensoren, welche an den permanenten Messstationen des LHA am St. Johanns-Platz, an der Feldbergstrasse und auf der Autobahn A2 in der Hard installiert und gegen die Referenzmessgeräte des LHA verglichen werden.</p><p>Genaue Standorte dieser Sensoren: </p><ul><li>Feldbergstrasse: 2611747 / 1268491, <a href='https://map.geo.admin.ch/?X=268491&amp;Y=611747&amp;zoom=9&amp;lang=de&amp;topic=ech&amp;bgLayer=ch.swisstopo.pixelkarte-farbe&amp;crosshair=bowl&amp;layers=ch.swisstopo.zeitreihen,ch.bfs.gebaeude_wohnungs_register,ch.bav.haltestellen-oev,ch.swisstopo.swisstlm3d-wanderwege,ch.astra.wanderland-sperrungen_umleitungen&amp;layers_opacity=1,1,1,0.8,0.8&amp;layers_visibility=false,false,false,false,false&amp;layers_timestamp=18641231,,,,' target='_blank'>Kartenansicht</a></li><li>St. Johanns-Platz: 2610790 / 1268370, <a href='https://map.geo.admin.ch/?X=268370&amp;Y=610790&amp;zoom=9&amp;lang=de&amp;topic=ech&amp;bgLayer=ch.swisstopo.pixelkarte-farbe&amp;crosshair=bowl&amp;layers=ch.swisstopo.zeitreihen,ch.bfs.gebaeude_wohnungs_register,ch.bav.haltestellen-oev,ch.swisstopo.swisstlm3d-wanderwege,ch.astra.wanderland-sperrungen_umleitungen&amp;layers_opacity=1,1,1,0.8,0.8&amp;layers_visibility=false,false,false,false,false&amp;layers_timestamp=18641231,,,,' target='_blank'>Kartenansicht</a></li><li>A2 Hard: 2615839 / 1265282, <a href='https://map.geo.admin.ch/?X=265282&amp;Y=615839&amp;zoom=9&amp;lang=de&amp;topic=ech&amp;bgLayer=ch.swisstopo.pixelkarte-farbe&amp;crosshair=bowl&amp;layers=ch.swisstopo.zeitreihen,ch.bfs.gebaeude_wohnungs_register,ch.bav.haltestellen-oev,ch.swisstopo.swisstlm3d-wanderwege,ch.astra.wanderland-sperrungen_umleitungen&amp;layers_opacity=1,1,1,0.8,0.8&amp;layers_visibility=false,false,false,false,false&amp;layers_timestamp=18641231,,,,' target='_blank'>Kartenansicht</a></li></ul><p>Weitere Informationen zur Luftqualität in der Region Basel sind auf <a href='https://www.luftqualitaet.ch' target='_blank'>www.luftqualitaet.ch</a>
 verfügbar. Hintergrundinformationen zu Ozon und Feinstaub auf den Webseiten <a href='https://ozon-info.ch/' target='_blank'>www.ozon-info.ch</a> und <a href='https://feinstaub.ch/' target='_blank'>www.feinstaub.ch</a>. Angaben zu den gesundheitlichen Auswirkungen der Luftverschmutzung auf der Webseite <a href='https://www.swisstph.ch/de/projects/ludok/healtheffects/' target='_blank'>https://www.swisstph.ch/de/projects/ludok/healtheffects/</a>.</p><p class=''>Weitere Informationen und Daten rund um das Projekt «Smarte Strasse» finden Sie unter den folgenden Links:</p><ul><li>Die Luftqualitäts-Daten der Sensoren an der smarten Strasse finden Sie hier: <a href='https://data.bs.ch/explore/dataset/100093/' target='_blank'>https://data.bs.ch/explore/dataset/100093/</a> </li><li>Die Maximalwerte (O3) und Mittelwerte (NO2, PM 2.5) des Vortages sind zudem unter folgendem Datensatz zu finden: <a href='https://data.bs.ch/explore/dataset/100174/' target='_blank'>https://data.bs.ch/explore/dataset/100174/</a></li><li>Weitere Informationen zum Projekt «Smarte Strasse»: <a href='https://www.bs.ch/medienmitteilungen/pd/2022-pilotprojekt-smarte-strasse-neue-technologien-im-test-fuer-die-stadt-von-morgen' target='_blank'>https://www.bs.ch/medienmitteilungen/pd/2022-pilotprojekt-smarte-strasse-neue-technologien-im-test-fuer-die-stadt-von-morgen</a> </li><li>Genaue Standorte aller Sensoren: <a href='https://data.bs.ch/explore/dataset/100114/' target='_blank'>https://data.bs.ch/explore/dataset/100114/</a> </li><li>Weitere Datensätze rund um das Thema «Smarte Strasse»: <a href='https://data.bs.ch/explore/?refine.tags=smarte+strasse' target='_blank'>https://data.bs.ch/explore/?refine.tags=smarte+strasse</a> </li></ul><p><b>Hinweis: <br>Die Luft-Sensoren an der Gundeldingerstrasse wurden am 29.6.23 abmontiert. Seit Anfang/Mitte Juni wurden keine Daten mehr erhoben.</b><br></p>"
CONTACT = "Fachstelle für OGD Basel-Stadt | opendata@bs.ch"
DATASHOP_MD_LINK = """[Direct data shop link for dataset](https://data.bs.ch/explore/dataset/100178)"""

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
    mo.md("## Metadata\n- **Dataset_identifier** `100178`
- **Title** `Smarte Strasse: Luftqualität Vergleichsmessungen`
- **Description** `<p>Das <a href='https://www.baselland.ch/politik-und-behorden/direktionen/bau-und-umweltschutzdirektion/lufthygiene' target='_blank'>Lufthygieneamt beider Basel</a> (LHA) testet im Projekt «Smarte Strasse» kosteneffiziente Mikrosensoren auf ihre Genauigkeit und Zuverlässigkeit. Der installierte Sensor vom Typ «Nubo» der Firma Sensirion AG ist in der Lage, die Konzentration verschiedener Schadstoffe in der Luft in Echtzeit zu ermitteln. Gemessen werden die Gehalte der Gase Stickstoffdioxid (NO2) und Ozon (O3), sowie die feinere Fraktion des Feinstaubs «PM2.5». Dieser Datensatz enthält die Daten von drei «Nubo»- Sensoren, welche an den permanenten Messstationen des LHA am St. Johanns-Platz, an der Feldbergstrasse und auf der Autobahn A2 in der Hard installiert und gegen die Referenzmessgeräte des LHA verglichen werden.</p><p>Genaue Standorte dieser Sensoren: </p><ul><li>Feldbergstrasse: 2611747 / 1268491, <a href='https://map.geo.admin.ch/?X=268491&amp;Y=611747&amp;zoom=9&amp;lang=de&amp;topic=ech&amp;bgLayer=ch.swisstopo.pixelkarte-farbe&amp;crosshair=bowl&amp;layers=ch.swisstopo.zeitreihen,ch.bfs.gebaeude_wohnungs_register,ch.bav.haltestellen-oev,ch.swisstopo.swisstlm3d-wanderwege,ch.astra.wanderland-sperrungen_umleitungen&amp;layers_opacity=1,1,1,0.8,0.8&amp;layers_visibility=false,false,false,false,false&amp;layers_timestamp=18641231,,,,' target='_blank'>Kartenansicht</a></li><li>St. Johanns-Platz: 2610790 / 1268370, <a href='https://map.geo.admin.ch/?X=268370&amp;Y=610790&amp;zoom=9&amp;lang=de&amp;topic=ech&amp;bgLayer=ch.swisstopo.pixelkarte-farbe&amp;crosshair=bowl&amp;layers=ch.swisstopo.zeitreihen,ch.bfs.gebaeude_wohnungs_register,ch.bav.haltestellen-oev,ch.swisstopo.swisstlm3d-wanderwege,ch.astra.wanderland-sperrungen_umleitungen&amp;layers_opacity=1,1,1,0.8,0.8&amp;layers_visibility=false,false,false,false,false&amp;layers_timestamp=18641231,,,,' target='_blank'>Kartenansicht</a></li><li>A2 Hard: 2615839 / 1265282, <a href='https://map.geo.admin.ch/?X=265282&amp;Y=615839&amp;zoom=9&amp;lang=de&amp;topic=ech&amp;bgLayer=ch.swisstopo.pixelkarte-farbe&amp;crosshair=bowl&amp;layers=ch.swisstopo.zeitreihen,ch.bfs.gebaeude_wohnungs_register,ch.bav.haltestellen-oev,ch.swisstopo.swisstlm3d-wanderwege,ch.astra.wanderland-sperrungen_umleitungen&amp;layers_opacity=1,1,1,0.8,0.8&amp;layers_visibility=false,false,false,false,false&amp;layers_timestamp=18641231,,,,' target='_blank'>Kartenansicht</a></li></ul><p>Weitere Informationen zur Luftqualität in der Region Basel sind auf <a href='https://www.luftqualitaet.ch' target='_blank'>www.luftqualitaet.ch</a>
 verfügbar. Hintergrundinformationen zu Ozon und Feinstaub auf den Webseiten <a href='https://ozon-info.ch/' target='_blank'>www.ozon-info.ch</a> und <a href='https://feinstaub.ch/' target='_blank'>www.feinstaub.ch</a>. Angaben zu den gesundheitlichen Auswirkungen der Luftverschmutzung auf der Webseite <a href='https://www.swisstph.ch/de/projects/ludok/healtheffects/' target='_blank'>https://www.swisstph.ch/de/projects/ludok/healtheffects/</a>.</p><p class=''>Weitere Informationen und Daten rund um das Projekt «Smarte Strasse» finden Sie unter den folgenden Links:</p><ul><li>Die Luftqualitäts-Daten der Sensoren an der smarten Strasse finden Sie hier: <a href='https://data.bs.ch/explore/dataset/100093/' target='_blank'>https://data.bs.ch/explore/dataset/100093/</a> </li><li>Die Maximalwerte (O3) und Mittelwerte (NO2, PM 2.5) des Vortages sind zudem unter folgendem Datensatz zu finden: <a href='https://data.bs.ch/explore/dataset/100174/' target='_blank'>https://data.bs.ch/explore/dataset/100174/</a></li><li>Weitere Informationen zum Projekt «Smarte Strasse»: <a href='https://www.bs.ch/medienmitteilungen/pd/2022-pilotprojekt-smarte-strasse-neue-technologien-im-test-fuer-die-stadt-von-morgen' target='_blank'>https://www.bs.ch/medienmitteilungen/pd/2022-pilotprojekt-smarte-strasse-neue-technologien-im-test-fuer-die-stadt-von-morgen</a> </li><li>Genaue Standorte aller Sensoren: <a href='https://data.bs.ch/explore/dataset/100114/' target='_blank'>https://data.bs.ch/explore/dataset/100114/</a> </li><li>Weitere Datensätze rund um das Thema «Smarte Strasse»: <a href='https://data.bs.ch/explore/?refine.tags=smarte+strasse' target='_blank'>https://data.bs.ch/explore/?refine.tags=smarte+strasse</a> </li></ul><p><b>Hinweis: <br>Die Luft-Sensoren an der Gundeldingerstrasse wurden am 29.6.23 abmontiert. Seit Anfang/Mitte Juni wurden keine Daten mehr erhoben.</b><br></p>`
- **Contact_name** `Open Data Basel-Stadt`
- **Issued** `2022-02-17`
- **Modified** `2023-06-29T07:45:18+00:00`
- **Rights** `NonCommercialAllowed-CommercialAllowed-ReferenceRequired`
- **Temporal_coverage_start_date** `2022-02-12T23:00:00+00:00`
- **Temporal_coverage_end_date** `2023-06-28T22:00:00+00:00`
- **Themes** `['Raum und Umwelt']`
- **Keywords** `['Smarte Strasse', 'Luftqualität', 'Feinstaub', 'PM2.5', 'O3', 'NO2']`
- **Publisher** `Lufthygieneamt beider Basel`
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
    df = get_dataset('https://data.bs.ch/explore/dataset/100178/download')
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
