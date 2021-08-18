"""Defines and loads the program configuration."""

import getopt
import os
import sys
from datetime import datetime

import SIM
from Files.BlocFile import BlocFile
from Files.CropFile import CropFile
from Files.DataFile import OutputFormats
from Files.InitialFile import InitialFile
from Files.PrintOutFile import PrintOutFile
from Files.SimControlFile import SimControlFile
from Files.SoilFile import SoilFile
from Files.SoilPropFile import SoilPropFile
from Files.TillageFile import TillageFile

DefaultConfigPath: str = "default.cfg"


class Configuration:
    """Configuration class"""
    __slots__ = ("Version", "INPUTDIR", "OUTDIR", "OUTPUT_FORMAT", "BLOCFILE", "TILLFILE",
                 "PRTFILE", "CNTRFILE", "CROPFILE", "SOILFILE", "INITFILE", "SOILPROPFILE", "WEA_DIR",
                 "ZONES", "ZONES_DIR", "LEGACY", "PRINT_ALL_SOILS", "SINGLE_RUN")

    def __init__(self):
        # Initialize default values.
        self.Version = "9.0"
        self.LEGACY = False
        self.SINGLE_RUN = False
        self.PRINT_ALL_SOILS = False

        self.INPUTDIR: str = "."
        self.OUTDIR: str = "./Results"
        self.OUTPUT_FORMAT: OutputFormats = OutputFormats.COHYST

        # INPUT FILES
        # Filenames must have a proper casing in order to be found
        # on Mac and Linux since UNIX filesystems are case-sensitive.

        self.BLOCFILE: str = "CSModel/BLOCK.DAT"
        self.TILLFILE: str = "CSModel/tillage.dat"
        self.PRTFILE: str = "CSModel/PRFILE"
        self.CNTRFILE: str = "CSModel/WSiteInfo_2020.txt"
        self.CROPFILE: str = "Cropping2020.csv"
        self.SOILFILE: str = "CSModel/Soil/NE_allsoil.csv"
        self.INITFILE: str = "CSModel/INITIAL.dat"
        self.SOILPROPFILE: str = "CSModel/Soil/NESoils.dat"

        self.WEA_DIR: str = "CSModel/Wea"
        self.ZONES: list = [1, 2, 3]
        self.ZONES_DIR: str = "CSModel/Sim/98/"

        print(f"Cropsim v{self.Version}")
        try:
            args, _ = getopt.getopt(sys.argv[1:], "hi:o:f:", ["help", "cfg="])
        except getopt.GetoptError:
            self.PrintUsage()

        # if there's a "default.cfg" file present in the working directory, load it as defaults
        if os.path.isfile(DefaultConfigPath):
            self.__read_config_file__(DefaultConfigPath)

        for arg, value in args:
            if arg in ("-h", "--help"):
                self.PrintUsage()
            elif arg in "-i":
                self.___parseConfigSetting("INPUTDIR", value)
            elif arg in "-o":
                self.___parseConfigSetting("OUTDIR", value)
            elif arg in "-f":
                self.___parseConfigSetting("OUTPUT_FORMAT", value)
            elif arg == "--cfg":
                self.__read_config_file__(value)

        self.checkOutputPath()

        self.__readGlobalData__()

    def __setitem__(self, key, item):
        setattr(self, key, item)

    def __read_config_file__(self, config_file):
        """Reads the specified configuration file."""
        config_file = os.path.normpath(config_file)
        print("Reading Config File: " + config_file)
        if not os.path.isfile(config_file):
            print("The specified configuration file was not found at:")
            print(config_file)
            sys.exit()

        file = open(config_file, "r")
        for line in file.readlines():
            line = line.strip()
            if len(line) > 0 and line[0].isalpha():
                try:
                    idx = line.index("=")
                    self.___parseConfigSetting(line[:idx].strip(), line[idx + 1:].strip())
                except ValueError:
                    pass

        file.close()

    def ___parseConfigSetting(self, name: str, value: str):
        print(f"Parsing {name} configuration setting: {value}")

        if name in self.__slots__:
            if name.endswith("FILE") or name.endswith("DIR"):
                self[name] = os.path.normpath(value)
            else:
                if name == "ZONES":
                    self.ZONES = list(map(int, value.split(",")))
                elif name == "OUTPUT_FORMAT":
                    try:
                        self.OUTPUT_FORMAT = OutputFormats(int(value))
                    except ValueError:
                        print("Invalid Output Format specified: " + value)
                        self.PrintUsage()
                else:
                    self[name] = int(value) == 1

    def getSiteFilename(self, site: str, year: int):
        """Returns the path to the corresponding .WEA file for the given site and year."""
        return os.path.join(self.INPUTDIR,
                            os.path.normpath(self.WEA_DIR), f"{site}{year}.WEA")

    def getZonePath(self, zoneIndex: int):
        """Returns the path to the climatic zone specified by it's 1-based index."""
        return os.path.join(self.INPUTDIR, os.path.normpath(f"{self.ZONES_DIR}{zoneIndex}"))

    def openCropFile(self, zoneIndex: int):
        """Opens the CROPFILE corresponding to the climatic zone specified by it's 1-based index."""
        return CropFile(os.path.join(self.getZonePath(zoneIndex), os.path.normpath(self.CROPFILE)))

    def __readGlobalData__(self):
        """Reads global data for the simulation."""

        # SIM.InitialData = InitialFile(os.path.join(self.INPUTDIR, \
        # os.path.normpath(self.INITFILE)))
        SIM.InitialData = InitialFile()
        # Read BlocFile
        SIM.BLOC = BlocFile(os.path.join(self.INPUTDIR, os.path.normpath(self.BLOCFILE)))
        # Read Tillage File
        SIM.Tillages = TillageFile(os.path.join(self.INPUTDIR, os.path.normpath(self.TILLFILE)))
        # Read PrintOut File
        SIM.PrintOut = PrintOutFile(os.path.join(self.INPUTDIR, os.path.normpath(self.PRTFILE)))
        # Load soils for site data.
        SIM.Sites = SoilFile(os.path.join(self.INPUTDIR, os.path.normpath(self.SOILFILE))).Data
        # Read soil properties file
        SIM.SoilProps = SoilPropFile(os.path.join(self.INPUTDIR,
                                                  os.path.normpath(self.SOILPROPFILE))).SoilTypes
        # Read Simulation Control file
        SIM.Simulations = SimControlFile(os.path.join(self.INPUTDIR, os.path.normpath(self.CNTRFILE))).Rows

        print("Global Data read.")

    def checkOutputPath(self):
        """Creates a timestamped output folder."""
        now = datetime.now()
        self.OUTDIR = os.path.normpath(os.path.join(self.OUTDIR,
                                                    (f"{now.year}{now.month:0>2}{now.day:0>2} "
                                                     f"{now.hour:0>2}{now.minute:0>2}{now.second:0>2}")))
        os.makedirs(self.OUTDIR, exist_ok=True)

    def PrintUsage(self):
        """Prints information about the accepted command-line parameters."""
        print(f"Cropsim v{self.Version}")
        print("Usage:")
        print("CropSim.py -i <input_path> -o <output_path> -f <output_format> --cfg <config_file>")
        sys.exit()
