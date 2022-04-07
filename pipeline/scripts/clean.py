# ---
# Cleaning pipeline for CORD-19 
#
# ---

# %%
import pandas as pd
import numpy as np
from thefuzz import fuzz, process
from pandarallel import pandarallel

pandarallel.initialize(use_memory_fs=False)

# %% tags=["parameters"]
# Parameters
upstream = ['get']
product = None
sample = None
# %%

metadata_path = str(upstream['get']['metadata'])

col_names = pd.read_csv(metadata_path, nrows=0).columns
types_dict = {}
types_dict.update({col:str for col in col_names})

df = pd.read_csv(metadata_path, dtype=types_dict)

if sample:
    df = df.sample(frac=0.01, random_state=777)

print("Original shape is ", str(df.shape))

# %%
# Deduplication

dupl = df.loc[df.duplicated(subset='cord_uid',keep=False)].copy()
ndupl = df.loc[~df.duplicated(subset='cord_uid',keep=False)].copy()
print("There are ", str(dupl.shape[0]), " papers")

# %%
#Pairs of cord_uid and copy count
dupl_group = dupl['cord_uid'].value_counts().reset_index().rename(columns={'index':'cord_uid', 'cord_uid':'count'}).copy()

# %%
#Include NaN count column in dupl
dupl['nan_count'] = dupl.isnull().sum(axis=1)

# %%
#Create an empty dataframe to fill with deduplicated documents
dupl_aggregated = pd.DataFrame(columns=dupl.columns)

# %%
# Deduplication strategy. 
# Create a list of the docs with that cord_uid
# Copy the row with less NaN values

# If empty:
# Pick the longest abstract available
# Pick the longest title
# Pick the longest author 
# Pick the longest string date
# Pick the path for full text document

# Pick the first entry for each id or source if empty
for doc in dupl_group.cord_uid:
    if doc in dupl_aggregated.cord_uid:
        continue
    temp = dupl[dupl.cord_uid == doc]
    row = temp[temp.nan_count == temp.nan_count.min()].iloc[0].copy(deep=True)

    #row

    #Fields with 'longest' as selection principle
    fields = ['title','abstract','authors','journal','pdf_json_files','pmc_json_files','url','publish_time']

    for field in fields:
        if(not row[field]):
            idx = temp[field].dropna()
            if len(idx) > 0:
                idx = idx.apply(len).idxmax()

                # Get that row
                row[field] = temp.loc[idx, :][field]

    fields = ['sha', 'source_x','doi','pmcid','pubmed_id','license','mag_id','who_covidence_id','arxiv_id','s2_id']

    for field in fields:
        if(not row[field]):
            idx = temp[field].dropna()
            if len(idx) > 0:
                idx = idx.iloc[0][field]

            # Get that row
            row[field] = idx

    #row
    df_row = pd.DataFrame(data=[row.values],columns=row.index) 
    dupl_aggregated = pd.concat([dupl_aggregated,df_row], ignore_index=True)

# %%
# Concat the nonduplicated and the reconciliated dataframe
df = pd.concat([ndupl, dupl_aggregated], ignore_index=True, sort=False)

# %%
# Time selection
# Drop papers published before 2020 Check if it is enough to avoid SARS1 and MERS
df[['publish_time']] = df[['publish_time']].apply(pd.to_datetime)

# %%
# Keep only papers with abstract
df = df[df.abstract.notna()]

# %%
# Load CiteScore data
cs = pd.read_csv('/home/frinve/Code/agave/pipeline/rsc/CiteScoreMay2021.csv', sep=';')

#Change locale to us_US
cs['CiteScore 2020'] = cs['CiteScore 2020'].str.replace(',','.')
cs['CiteScore 2020'] = cs['CiteScore 2020'].apply(float)
cs = cs.drop_duplicates(subset=["Scopus Source ID"])
TITLES = cs.Title.to_list()

# %%


# Expand J or J. to Journal
def expandJournal(title):
    return ' '.join(["Journal" if (token=="J" or token=="J.") else token for token in title.split()])

SUBS = {"j":"journal",
        "j.":"Journal",
        "arch":"archives",
        "arch.":"archives",
        "int":"international",
        "int.":"international",
        "ann":"annals",
        "biol":"biology",
        "biol.":"biology",
        "med":"medicine",
        "med.":"medicine",
        "dis.":"disease",
        "dis":"disease",
        "jpn":"japan",
        "res":"research",
        "rep":"report",
        "eur":"european",
        "exp":"experimental",
        "ther":"therapeutic",
        "manag":"management",
        "phys":"physical",
        "biomol":"biomolecular",
        "struct":"structural",
        "mol":"molecular",
        "sci.":"science",
        "sci":"science",
        "(basel)":"",
        "pract":"practice",
        "(Stuttg.)":"",
        "educ":"education",
        "clin":"clinical",
        "surg":"surgery"
}

SUBS_KEYS = SUBS.keys()

# Expand common NLM Title abbreviations
def expandNLM(title):
    expTitle = []
    for token in title.lower().split():
        if token in SUBS_KEYS:
            token = SUBS[token]
        expTitle.append(token)
    return ' '.join(expTitle)

def getJournal(title):
    if str(title).lower() == "nan":
        return np.nan
    else:
        matched_title = process.extractOne(expandNLM(title), TITLES, scorer=fuzz.token_sort_ratio)
        if matched_title[1] > 72:
            return matched_title[0]
        else:
            return np.nan

# %%
df['CiteScoreJournal'] = df['journal'].parallel_apply(getJournal)

# %%
df.to_parquet(str(product['cleaned_metadata']))
