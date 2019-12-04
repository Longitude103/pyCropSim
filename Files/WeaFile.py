"""WEA File module."""

from io import TextIOWrapper

from HelperIO import ReadNextWord
from HelperIO import ReadNextInteger
from HelperIO import  ReadNextFloat

from Data.WeatherStation import WeatherStation
from Data.WeatherDailyData import WeatherDailyData


class WeaFile:
    """Class for reading a .WEA file."""
    __file: TextIOWrapper = None

    StationData: WeatherStation = None

    def __init__(self, filename):
        print("Reading WEA file at: " + filename)
        file = open(filename, "rt+")
        self.__file = file

        # Read Weather Station data.
        location = file.readline().strip()

        IMSTR = ReadNextInteger(file)
        IDSTR = ReadNextInteger(file)
        NDAYS = ReadNextInteger(file)

        ReadNextWord(file)
        LAT = ReadNextFloat(file)
        ReadNextWord(file)
        LONG = ReadNextFloat(file)
        ReadNextWord(file)
        ELEV = ReadNextFloat(file)

        self.StationData = WeatherStation(location, IMSTR, IDSTR, NDAYS, LAT, LONG, ELEV)

        file.readline()

    def ReadNextDayData(self):
        """Reads the next weather daily data in the file"""
        values = self.__file.readline().strip().split(",")
        return WeatherDailyData(
            int(values[0].strip()),
            float(values[1].strip()),
            float(values[2].strip()),
            float(values[3].strip()),
            float(values[4].strip()),
            float(values[5].strip()))

    def close(self):
        """Close the opened file."""
        self.__file.close()

    def readAllAndClose(self):
        """Test method not actually used."""
        for _ in range(self.StationData.NDAYS):
            self.ReadNextDayData()
        self.close()
