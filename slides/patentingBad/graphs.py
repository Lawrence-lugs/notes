#%%

# Save as innovation_dashboard.py or run in a Jupyter/Colab cell
import io
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

sns.set(style="whitegrid", context="talk")
plt.rcParams["figure.dpi"] = 150

# ----- CONFIG -----
countries = {
    "United States": "USA",
    "South Korea": "KOR",
    "Singapore": "SGP",
    "Japan": "JPN",
    "China": "CHN",
}
start_year = 1990
end_year = 2021

# Our World in Data grapher CSV endpoints (derived from World Bank / WDI)
owid_urls = {
    "patents": "https://ourworldindata.org/grapher/annual-patent-applications.csv",
    "publications": "https://ourworldindata.org/grapher/scientific-and-technical-journal-articles.csv",
    # research spending as % GDP (OurWorldInData uses UNESCO/World Bank data)
    "rd_gdp": "https://ourworldindata.org/grapher/research-spending-gdp.csv"
}

# Policy years - fill in (these are placeholders / examples).
# Replace or extend with the exact policy years you want to mark.
policy_years = {
    "United States": [1980],   # Bayh-Dole Act (1980) - canonical example
    # Suggested placeholders — please verify exact act/dates for each country:
    "South Korea": [2001],     # candidate: major S&T / technology transfer reforms ~2000s (placeholder)
    "Singapore": [2000],       # candidate: IP/regulatory reforms / innovation agencies growth (placeholder)
    "Japan": [1999],           # candidate: late-1990s IP / tech reforms (placeholder)
    "China": [1984],           # Patent Law (first enacted 1984, implemented 1985) - verify
}

# --------------------

def download_csv(url):
    print(f"Downloading {url} ...")
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return pd.read_csv(io.StringIO(r.text))

# Fetch data
patent_df = download_csv(owid_urls["patents"])
pub_df = download_csv(owid_urls["publications"])
rd_df = download_csv(owid_urls["rd_gdp"])

# Select countries and filter years
def filter_owid(df, countries_iso, value_col=None):
    # OWID format: "country","year","<indicator code>"
    # The CSV often contains one value column with the indicator name as header.
    # We'll identify the numeric column (not country/year)
    numeric_cols = [c for c in df.columns if c not in ["country", "Year", "year", "Country"]]
    data_col = numeric_cols[-1]  # usually last
    df_sel = df[df['Entity'].isin(countries_iso)] if 'Entity' in df.columns else df[df['country'].isin(countries_iso)]
    # normalize column names
    if 'Year' in df_sel.columns:
        df_sel = df_sel.rename(columns={'Year':'year'})
    if 'Entity' in df_sel.columns:
        df_sel = df_sel.rename(columns={'Entity':'country'})
    df_sel = df_sel[['country','year',data_col]].rename(columns={data_col:'value'})
    df_sel['year'] = df_sel['year'].astype(int)
    df_sel = df_sel[(df_sel['year'] >= start_year) & (df_sel['year'] <= end_year)]
    return df_sel

# OWID CSVs sometimes use 'Entity', sometimes 'country'
def prepare_owid_dataset(df, name):
    # handle both possible column names
    if 'Entity' in df.columns:
        df = df.rename(columns={'Entity':'country'})
    if 'Year' in df.columns:
        df = df.rename(columns={'Year':'year'})
    # the value column is the one that's not 'country' or 'year'
    value_cols = [c for c in df.columns if c not in ('country','year')]
    if len(value_cols) != 1:
        # keep last column as value
        value_col = value_cols[-1]
    else:
        value_col = value_cols[0]
    df = df[['country','year',value_col]].rename(columns={value_col:'value'})
    df['year'] = df['year'].astype(int)
    df = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
    return df

patent_prepared = prepare_owid_dataset(patent_df, 'patents')
pub_prepared = prepare_owid_dataset(pub_df, 'publications')
rd_prepared = prepare_owid_dataset(rd_df, 'rd_gdp')

# The OWID "country" names may differ from our display names; build mapping
iso_to_name = {v: k for k, v in countries.items()}
# OWID uses full country names (e.g., "United States", "Korea, Rep.") - let's map by ISO where possible:
# We'll normalize by matching ISO codes via a small lookup (requests to restcountries could be added),
# but simplest: filter by display names in our countries dict:
target_country_names = list(countries.keys())

def keep_targets(df):
    # reduce to our list of display country names (best-effort)
    df = df[df['country'].isin(target_country_names)]
    return df

pat = keep_targets(patent_prepared)
pub = keep_targets(pub_prepared)
rd = keep_targets(rd_prepared)

# Merge into a tidy DataFrame
pat['indicator'] = 'patent_applications'
pub['indicator'] = 'publications'
rd['indicator'] = 'rd_gdp_pct'

combined = pd.concat([pat, pub, rd], ignore_index=True)

# pivot for plotting convenience
# we'll keep as long format for seaborn but ensure numeric values
combined['value'] = pd.to_numeric(combined['value'], errors='coerce')

# If any country missing data for some indicator, NaNs will occur; that's ok.
# Prepare country-order for facet grid
country_order = list(countries.keys())

# Plotting
g = sns.FacetGrid(combined, row='country', hue='indicator', sharey=False,
                  aspect=3, height=2.5, row_order=country_order,
                  palette={'patent_applications':'tab:green','publications':'tab:blue','rd_gdp_pct':'tab:red'})

def plot_line(data, color, label, **kwargs):
    sns.lineplot(data=data, x='year', y='value', hue='indicator', legend=False, **kwargs)

g.map_dataframe(sns.lineplot, 'year', 'value')
g.add_legend(title='Indicator', labels=['Patents','Publications','R&D % GDP'])

# Add vertical lines for policy years
for ax, country in zip(g.axes.flatten(), country_order):
    years = policy_years.get(country, [])
    ylim = ax.get_ylim()
    for y in years:
        ax.axvline(x=y, color='gray', linestyle='--', linewidth=1.2)
        ax.text(y + 0.2, ylim[1]*0.9, 'Policy: {}'.format(y), rotation=90, va='top', fontsize=8, color='gray')

# Beautify labels
for ax in g.axes.flatten():
    ax.set_xlabel('Year')
    ax.set_ylabel('')
g.set_titles(row_template='{row_name}')
plt.subplots_adjust(hspace=0.6)
plt.suptitle('Patents, Publications, and R&D (% GDP) — 1990–2021', y=1.02, fontsize=16)
plt.tight_layout()
plt.savefig('innovation_timeseries_by_country.png', bbox_inches='tight')
print("Saved figure to innovation_timeseries_by_country.png")
plt.show()
