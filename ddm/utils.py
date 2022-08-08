import multiprocessing
from urllib.error import HTTPError

import pims


def print_cpu_count():
    ncpus = multiprocessing.cpu_count()
    print(f"We have {ncpus} cores to work on!")


def verify_bioformats_jar():
    """Check presence of .jar file for pims.bioformats and download verison 6.5 if missing

    """
    # Catch problem with jar library
    try:
        pims.bioformats._find_jar()
    except HTTPError:
        pims.bioformats.download_jar(version="6.5")
