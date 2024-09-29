# MeshProcess 

## Highlights
1. Generates simplified 2-manifold meshes with convex decomposition *in seconds*.
2. High success rate on messy, in-the-wild mesh data, including datasets like [Objaverse](https://objaverse.allenai.org).
3. Supports parallel processing of multiple meshes on CPUs.
4. Easy to customize the processing tasks.

## Dependences
1. The code is currently only tested on Linux Ubuntu.
2. [ACVD](https://github.com/valette/ACVD).
3. [CoACD](https://github.com/JYChen18/CoACD).

## Installation
1. Clone the third-parties.
```
git submodule update --init --recursive 
```

2. Create and install the python environment using [Conda](https://docs.anaconda.com/miniconda/).
```
conda create -n meshproc python=3.10    
conda activate meshproc
pip install trimesh
pip install hydra-core
pip install lxml
```

3. Build the third-party packages, [ACVD](https://github.com/valette/ACVD/tree/master?tab=readme-ov-file#simple-compilation-howto-under-linux)
and [CoACD](https://github.com/SarahWeiii/CoACD?tab=readme-ov-file#3-compile), according to the official repositories. For ACVD, here is a guidance for installing the [VTK](https://www.vtk.org/) dependence:
```
sudo apt-get update
sudo apt install -y build-essential cmake git unzip qt5-default libqt5opengl5-dev libqt5x11extras5-dev libeigen3-dev libboost-all-dev libglew-dev libglvnd-dev

git clone https://gitlab.kitware.com/vtk/vtk.git
cd vtk
git checkout v9.2.0     
mkdir build
cd build
cmake ..
make
sudo make install
export VTK_DIR=/usr/local/include/vtk-9.2
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
``` 

## Mesh Data Preparing
1. The meshes should be organized similarly as in `example_data`. 

2. The downloading guidance for [objaverse-1.0](https://objaverse.allenai.org/objaverse-1.0/) is in `src/dataset/objaverse/README.md`.

## Running
1. Processing meshes for `example_data`. The logs will be saved to `outputs`.
```
python src/script/process.py data=example task=main
```
2. Get statistic.
```
python src/script/statistic.py data=example task=main
```
3. Remove all processed results and only leave `raw.obj`
```
python src/script/process.py data=example task=clean
```

## TODO

1. Export xml for MuJoCo.
2. Get valid object pose on a table from MuJoCo.
3. GPU-based partial point clouds rendering.
4. (Potential) Reduce part number of the CoACD output.
5. Filtering out similar objects.

## Known issues
1. The output mesh of the OpenVDB for manifold repairing would be a little bit larger (~1%) than the input mesh.
