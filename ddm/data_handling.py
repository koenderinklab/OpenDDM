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

def readLIF(filename):
    """
    
    """
    lifSeq = pims.Bioformats('data/21-03-31_ddm.lif', read_mode = 'jpype')
    xscale = lifSeq.metadata.PixelsPhysicalSizeX(0)
    tscale = lifSeq.metadata.PlaneDeltaT(0,1)
    lifXCoords = np.arange(0., lifSeq.shape[1]*xscale, xscale)
    lifYCoords = np.arange(0., lifSeq.shape[2]*xscale, xscale)
    lifTCoords = np.arange(0., lifSeq.shape[0]*tscale, tscale)
    ds = da.from_array(lifSeq)
    sequence = xarray.DataArray(data = ds, dims = ["T", "Y", "X"], 
                                coords = (lifTCoords, lifYCoords, lifXCoords), 
                                attrs = dict(xyScale = xscale, tScale = tscale))
    return sequence