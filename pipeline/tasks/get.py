from pathlib import Path
import requests
import logging

def metadata(product):
    """
    Get latest metadata table from CORD-19
    """
    logger = logging.getLogger(__name__)
    logger.info("Downloading CORD-19 metadata.csv")

    data = requests.get('https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/latest/metadata.csv')

    Path(str(product['metadata'])).parent.mkdir(exist_ok=True, parents=True)

    with open(str(product['metadata']), 'wb') as f:
        f.write(data.content)

    logger.info("Donwloading changelog")
    r = requests.get('https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/latest/changelog')

    
    with open(str(product['changelog']), 'wb') as f:
        f.write(r.content)
    
