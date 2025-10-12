# Jupyter Lab

``` bash

ipykernel install --user --name myenv 
ipykernel install --user --name myenv  --display-name myen

/path/to/myenv/bin/python3 -m ipykernel install --user --name sweetheart --display-name sweetheart

jupyter kernelspec list
jupyter kernelspec remove mykernel

jupyter notebook --no-browser --notebook-dir=/path/to/notebooks/dir
jupyterlab --no-browser --notebook-dir=/path/to/notebooks/dir
jupyter notebook password -y
```