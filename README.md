# ict1008_python_project <!-- omit in toc -->

## Table of Contents <!-- omit in toc -->
- [Setting Up](#setting-up)
  - [Manual Installation](#manual-installation)
    - [Installing OSMnx](#installing-osmnx)
    - [Installing Required Dependencies](#installing-required-dependencies)
- [Project Details](#project-details)
- [Milestones](#milestones)
- [Collaborators](#collaborators)

## Project Title


## Getting Started

### Installing Environment

    Recommended to create environment from environment.yml, if this does not work, you would have to do it manually

#### Creating an environment from an environment.yml file

1. [Install](https://www.anaconda.com/distribution/) Anaconda for Python 3.7. (Ensure you have Anaconda first)

2. Use the terminal or an Anaconda Prompt for the following steps:

* Create the environment from the environment.yml file:

  1.      conda env create -f environment.yml

  The first line of the yml file sets the new environment's name. For details see Creating an environment file manually.

  2. Activate the new environment: conda activate myenv

  3. Verify that the new environment was installed correctly:

          conda env list
      
      You can also use conda info --envs.

### Manual Installation

#### Installing OSMnx

1. [Install](https://www.anaconda.com/distribution/) Anaconda for Python 3.7.
2. Set up a new virtual environment i.e DSAProjectVE, try not to touch root virtual environment. Once Virtual Environment is set up, do the following:

    1. Click on your new virutal environment, and click on the play Button.
    2. Click on "Open Terminal".
    3. To install this OSMnx with conda run one of the following:
        -     conda install -c conda-forge osmnx
        -     conda install -c conda-forge/label/gcc7 osmnx
        -     conda install -c conda-forge/label/cf201901 osmnx
    4. Open up your Python IDE.
    5. Set your interpreter to your Conda Environment virtual environment.
    6. You are all set!

**If the following steps above doesnt work, you can do the following:**

1. Open up the project in your IDE.
2. There should be 4 wheel (.whl) files when your clone this project.
3. Ensure your terminal directory is where the 4 whell files are located at.
4. Using pip install, install them in the following way:
    -     pip install GDAL-3.0.3-cp37-cp37m-win_amd64.whl
    -     pip install Shapely-1.6.4.post2-cp37-cp37m-win_amd64.whl
    -     pip install Rtree-0.9.3-cp37-cp37m-win_amd64.whl
    -     pip install Fiona-1.8.13-cp37-cp37m-win_amd64.whl
    -     pip install osmnx
5. You should be all set!

#### Installing Required Dependencies

In your pycharm terminal tab:
*     pip install overpy
*     pip install Flask
*     pip install heapq
*     pip install folium

## Built With

* [Python 3.7](https://docs.python.org/3.7/) - Language used
* [Flask](https://flask.palletsprojects.com/en/1.1.x/) - The web framework used
* [Geopy](https://geopy.readthedocs.io/en/stable/) - Used for geocoding and reverse geocoding
* [Folium](https://python-visualization.github.io/folium/) - Used for rendering of map
* [Osmnx](https://osmnx.readthedocs.io/en/stable/) - Graph creation

## Project Details

Implementing and plotting network
* [X] **Walking**
* [X] **Walk + Bus**
* [X] **Walk + LRT**
* [ ] **Walk + LRT + Bus**

## Milestones

* [X] Planning
* [X] Execute own parts
* [X] Implementation
* [ ] Integration
* [ ] Debugging
* [ ] Code Cleanup (Remove unnecessary shit)

## Collaborators with Contributions

1. **Darrell Er** | [@derjr96](https://github.com/derjr96) | Dijkstra and A* Algorithm, MRT + Walk & Walk
2. **Alwyn Sim** | [@xiaoShiroNeko](https://github.com/xiaoShiroNeko) | Bus + Walk
3. **Yong Quan** | [@ongyongquan](https://github.com/ongyongquan) | GUI
4. **Yee Yong Jian** | [@thedomilicious](https://github.com/thedomilicious) | GUI
5. **Reynard Lim** | [@L2eynard](https://github.com/L2eynard) | GUI, Video & Poster
6. **Syaifulnizar** | [@syaifulnizarrr](https://github.com/syaifulnizarrr) | GUI
