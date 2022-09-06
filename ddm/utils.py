import os
import multiprocessing
from urllib.error import HTTPError
import psutil


import pims


def is_gpu_available():
    try:
        import cupy
    except ImportError:
        return False

    if cupy.cuda.runtime.getDeviceCount() > 0:
        return True
    else:
        return False


def print_cpu_count():
    ncpus = multiprocessing.cpu_count()
    print(f"We have {ncpus} cores to work on!")


def print_available_ram():
    available_ram = psutil.virtual_memory().available / 1024**3
    used_ram = psutil.virtual_memory().used / 1024**3
    percentage = (available_ram / (used_ram + available_ram)) * 100
    print(f"Available ram: {available_ram:.2f} GB ({percentage:.1f}%)")


def print_file_size(file: str):
    file_size = os.stat(file).st_size / 1024**3
    print(f"{file} is {file_size:.2f} GB")


def verify_bioformats_jar():
    """Check presence of .jar file for pims.bioformats and download verison 6.5 if missing"""
    # Catch problem with jar library
    try:
        pims.bioformats._find_jar()
    except HTTPError:
        pims.bioformats.download_jar(version="6.5")
