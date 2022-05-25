# Open DDM 

A Python package to analyse an image sequence and measure diffusion properties through Fourier techniques

## Installation for developers

```
git clone git@github.com:koenderinklab/ddmPilotCode.git ddm
cd ddm
conda env create -f environment.yml
conda activate ddm_env
pip install -e .
``` 

## Data processing workflow

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart TB

    id1(Microscope) .-> Data
    Data

    Data -->|".nd2 | .lif | .tiff"| Import(Import data)
    Import -->|"xarray (delayed)"| Fourier(Fourier analysis)
    Data --> Track(pyTrack)

    Fourier -->|np.ndarray| Fit(Fitting)
    Fit -->|np.ndarray| Plot(Plotting)
    
    Fourier -->|np.ndarray| Export(Export data)
    Fit -->|np.ndarray| Export
    Plot -->|mpl.fig| Export

    Export -->|"pickle | .csv | .png"| R(Results)    
    Track --> R    


    subgraph Personal Computer
    Import
    Fourier
    Fit
    Plot
    Export
    Track
    end
```
