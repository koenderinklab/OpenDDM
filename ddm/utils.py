import multiprocessing

def print_cpu_count():
    ncpus = multiprocessing.cpu_count()
    print(f"We have {ncpus} cores to work on!")