# ict1008_python_project <!-- omit in toc -->

## Table of Contents <!-- omit in toc -->
- [Setting Up](#setting-up)
  - [Installing OSMnx](#installing-osmnx)
  - [Installing Required Dependencies](#installing-required-dependencies)
- [Project Details](#project-details)
- [Milestones](#milestones)
- [Collaborators](#collaborators)

## Setting Up
### Installing OSMnx
1. [Install](https://www.anaconda.com/distribution/) Anaconda for Python 3.7.
2. Set up a new virtual environment i.e DSAProjectVE, try not to touch root virtual environment. Once Virtual Environment is set up, do the following:

    1. Click on your new virutal environment, and click on the play Button.
    2. Click on "Open Terminal".
    3. To install this OSMnx with conda run one of the following:
        - conda install -c conda-forge osmnx
        - conda install -c conda-forge/label/gcc7 osmnx
        - conda install -c conda-forge/label/cf201901 osmnx
    4. Open up your Python IDE.
    5. Set your interpreter to your Conda Environment virtual environment.
    6. You are all set!

**If the following steps above doesnt work, you can do the following:**

1. Open up the project in your IDE.
2. There should be 4 wheel (.whl) files when your clone this project.
3. Ensure your terminal directory is where the 4 whell files are located at.
4. Using pip install, install them in the following way:
    - pip install GDAL-3.0.3-cp37-cp37m-win_amd64.whl
    - pip install Shapely-1.6.4.post2-cp37-cp37m-win_amd64.whl
    - pip install Rtree-0.9.3-cp37-cp37m-win_amd64.whl
    - pip install Fiona-1.8.13-cp37-cp37m-win_amd64.whl
    - pip install osmnx
5. You should be all set!

### Installing Required Dependencies
In your pycharm terminal tab:
- pip install overpy
- pip install Flask
- pip install heapq
- pip install folium

## Project Details
Implementing and plotting network
- [X] **Walking**
- [X] **Bus**
- [X] **MRT**

## Milestones
- [X] Planning
- [X] Execute own parts
- [X] Implementation
- [ ] Integration
- [ ] Debugging
- [ ] Code Cleanup (Remove unnecessary shit)

## Collaborators
1. **Darrell Er** | [@derjr96](https://github.com/derjr96) | A* Algorithm & Walking
2. **Alwyn Sim** | [@xiaoShiroNeko](https://github.com/xiaoShiroNeko) | Bus
3. **Yong Quan** | [@ongyongquan](https://github.com/ongyongquan) | MRT
4. **Yee Yong Jian** | [@thedomilicious](https://github.com/thedomilicious) | GUI
5. **Reynard Lim** | [@L2eynard](https://github.com/L2eynard) | GUI
6. **Syaifulnizar** | [@syaifulnizarrr](https://github.com/syaifulnizarrr) | GUI
