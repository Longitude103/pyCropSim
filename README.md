# pyCropSim
A python implementation of the Nebraska CropSim model at version 8

## Install and Use
To use this application, download a zip of the application onto your computer and use an archive tool to decompress the files. We recommend using a venv environment for the application but it can be used with your global python install. This has been tested using python 3.6+ venv on Windows 10, macOS 10.15 and Ubuntu Linux 19.10.  

### VENV
For venv please refer to the following documentation [here](https://docs.python.org/3/library/venv.html) to create an environment and active it within your console.

### Packages
Use the requirements file to ensure that all of the packages are either installed in venv or your global python library with `pip install -r requirements.txt`

### Bugs
Please report bugs in the issues section of the repository for consideration and fixes. Please make a pull request for your updates.

## CropSim Background
CropSim is a soil water balance model to aid in the prediction of evapotranspiration, deep percolation, and runoff that occurs from a range of cropped and naturally vegetated systems. The model originally was a Fortran based program that reads numerous input files containing information on climate, tillage practices, soils, and farming practices and outputs soils water balance information for various time periods.

### Input Files:
There can be thousands of input files used by pyCropSim for the input of various data parts that are required. The four major classifications for them are:

- Climate Files
- Tillage Files
- Soil Inputs
- Program Control Inputs

#### Climate Inputs
The Climate station inputs that are used for the pyCropSim for data for each weather station. They are the 4 letter abbreviation followed by the four digit year to designate each file. The station format is ssssyyyy.WEA such as AGAT1953.WEA to provide the climate information for the AGATE 3 E station during 1953.

#### Tillage Input Files
The tillage information is from a Tillage.DAT file that contains the tillage practices that can be simulated. The order and which files are not included in this file.

#### Soil Input Files
There are two basic Soil input files that are used. The first is the ______soils.DAT file that is a table of the soil properties of all the potential soil types.

The second file is the ____soilxnws.DAT file that lists the specific soils that will be simulated for each climate station. 

#### Program Control Files
There were originally three files that are used for the control the program execution. Those three files are:

- Wsiteinfo.DAT
- Block.DAT
- Initial.DAT

We consolidated several of those files into a more friendly format in the default.cfg file that is used to set several of the variables for the input / output file paths and the other variables that are used to control the application.

# CropSim Output Files

CropSim xxxx_MON.txt output file used in WWUMM has the following format:

Station, year, soil, crop, Tillage, Irrigation Type

| Station | Year | Soil | Crop No | Tillage | Irr |
| ------- | ---- | ---- | ------- | ---- | --- |
| SDN6 | 2009 | 622 | 8 | 1 | 1 |

This is at station Sydney in year 2009 for soil 622 for crop 8 (corn) Tillage = 1, irrigation = Dryland

## Soils
Soils were greatly simplified, Soils in CropSim are:

| Soil | Class No |
| :--- | -------: |
| Sandy Soil | 412 |
| Table Lands Soils | 622 |
| Valley Soils | 722 |

Soil 412 is mostly in the NE part of the model in the sand hills and areas along the river, there are small amounts just north of the upper most canals. Soil 622 is mostly the table lands and and the northern part of the model. Soil 722 looks like the majority of the farmlands.

Soils: Identified By A 3 Digit Code That Represents The Available Water Holding Capacity (In Quarter Of Inch/Foot), Hydrologic Group (1=a,...4=d), And Depth To Groundwater Indicator (1<6ft, 2>6ft)

## Crop Numbers
CropSim results crop number conversion:

| Crop | CropSim Result |
| ----- | ------------: |
| Corn | 8 |
| SugarBeets | 5 |
| EdibleBeans | 2 |
| Alfalfa | 10 |
| WinterWheat | 7 |
| Potatoes | 4 |
| Milo | 6 |
| Sunflower | 9 |
| SoyBeans | 3 |
| SmallGrain | 1 |
| Fallow | 15 |
| Past | 12 |

## Tillage
| Tillage | Int Value |
| :------ | --------: |
| Fallow  | 0 |
| Convent | 1 |
| Conserv | 2 |
| Continuous | 3 |

## Irrigation Types
Irrigation is split among types, however it appears WWUMM is only using 1 and 3.

| Irrigation Number | Type |
| ----------------- | :--- |
| 1 | Dryland |
| 2 | Fixed Irrig. Dates |
| 3 | Pivot - Sprinkler |
| 4 | Furrow Irrigation |
| 5 | Other |

## Monthly Data
Following the first set of columns that detail the above information are 12 sets of monthly information that provide the following (in this order):
- ET month (in)
- EFF Precip (in)
- NIR (in)
- DP (in)
- RO (in)
- Precip (in)