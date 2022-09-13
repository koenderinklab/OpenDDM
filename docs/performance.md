# Performance OpenDDM

OpenDDM uses two performance optimization strategies, delayed computation with Dask, and GPU support with CuPy. Processing data on your system will require some tweaking in order to balance the performance and memory usage.

[Dask](https://www.dask.org/) enables processing datasets that are larger than the available RAM. Dask organizes the loading and processing of these datasets through [Chunks](https://docs.dask.org/en/stable/array-chunks.html). Increasing the chunk size will generally increase the performance, but also increase the memory usage. 

For a system with 8GB of RAM, we recommend a chunk of ~5 frames. This depends on the size and bitdepth of the images.

Additionally, we recommend optimizing the range of lag times being calculated at a single time through calling `dmm.processing.dmm`. Splitting the range of lag times will reduce the memory usage. The example below shows a method to split the calculation of 50 lag times into sets of 5:

```python
import numpy as np
tau_range = np.arange(1,50)
tau_step = 5
tau_split = np.array_split(tau_range, np.round(len(tau_range)/tau_step))

# Call ddm through loop
for taus in tau_split:
    ddmMatrix = ddm(data, taus)
    # ...
```



## Benchmarking

**Dataset**
Simulated dataset with 1000 frames of 512x512, totalling 512 MB.

**CPU**
_Intel i7-8665U @ 1.9GHz (TU Delft laptop)_
- Chunk size = (5,512,512)
- Calling dask.compute on entire tau range
- Hyperthreading enabled (2 threads per core)
- Boost enabled @ 3GHz (not stable during calculation)

Result: Calculating `ddm` for taus=np.arange(1,100) takes **~270 seconds**

**GPU**
_Nvidia Geforce GTX 1070 with 8GB of dedicated GPU memory_

Benchmark 1:
- Chunk size = (50,512,512)
- Calling dask.compute on every tau separately

Result: Calculating `ddm` for taus=np.arange(1,100) takes **~40 seconds**
Uses ~1.5Gb of GPU memory

Benchmark 2:
- Chunk size = (50,512,512)
- Calling dask.compute on entire tau range

Result: Calculating `ddm` for taus=np.arange(1,100) takes **~15 seconds**
Uses ~4.5Gb of GPU memory


## References
- https://blog.dask.org/2019/01/03/dask-array-gpus-first-steps
- https://stackoverflow.com/questions/56776385/how-to-create-a-dask-array-from-cupy-array
- https://medium.com/rapids-ai/reading-larger-than-memory-csvs-with-rapids-and-dask-e6e27dfa6c0f