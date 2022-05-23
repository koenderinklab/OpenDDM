def readND2(filename):
    """
    
    """
    sequence = nd2.imread(filename, xarray = True, dask = True)
    frameT = sequence.metadata['experiment'][0].parameters.periodDiff.avg #this is the time per frame in ms
    scale = sequence.X[1] #this is the microns per pixel
    sequence['T'] = np.arange(len(sequence['T']))*frameT
    sequence.attrs = {'xyScale': float(scale),
                      'tScale': frameT}
    return(sequence)