from pathlib import Path
import requests
import pandas as pd

def metadata(product):
    """
    Get latest metadata table from CORD-19
    """
    df = pd.read_csv('https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/latest/metadata.csv', 
                        dtype={
                'cord_uid' : str,
                'sha' : str,
                'source_x' : str,
                'title' : str,
                'doi' : str,
                'pmcid' : str,
                'pubmed_id' : str,
                'license' : str,
                'abstract' : str,
                'publish_time' : str,
                'authors' : str,
                'journal' : str,
                'mag_id' : str,
                'who_covidence_id' : str,
                'arxiv_id' : str,
                'pdf_json_files' : str,
                'pmc_json_files' : str,
                'url' : str,
                's2_id' : str
                       })

    r = requests.get('https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/latest/changelog')

    Path(str(product['metadata'])).parent.mkdir(exist_ok=True, parents=True)

    df.to_parquet(str(product['metadata']))
    
    with open(str(product['changelog']), 'wb') as f:
        f.write(r.content)
    
