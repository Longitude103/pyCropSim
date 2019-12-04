"""PrintOut file module"""

from aenum import IntEnum

from HelperIO import ReadNextSequenceAsInteger

class PrintOutFlags(IntEnum):
    """PrintOut Flags"""
    NoDetails = 0
    AnnualSummary = 1
    AnnualAndDailySummaries = 2
    AnnualDailyMonthlySummaries = 3
    AllAndInputSummary = 4

class PrintOutFile:
    """PrintOut configuration file data."""
    __slots__ = ("INPRIN", "IPFLAG", "IPSOIL", "JPRSTR", "JPRSTP", "NPRSITE", "PRSITE")

    def __init__(self, filename):
        print("Reading PRTFILE file at: " + filename)
        file = open(filename, "r")
        values = ReadNextSequenceAsInteger(file)

        self.IPFLAG = PrintOutFlags(values[0])
        """Printout flags."""
        self.INPRIN = values[1]
        """The frequency of printint in days."""
        self.IPSOIL = values[2]
        """Soil number for printing results."""
        self.JPRSTR = values[3]
        """The first year for printouts."""
        self.JPRSTP = values[4]
        """The last year for printouts."""
        # TONOTE: The code limits the number of sites for printing daily summaries to 8.
        self.NPRSITE = min(8, values[5])
        """The number of sites for printing daily summaries."""
        self.PRSITE = []
        """The sites to print daily results for."""
        for _ in range(self.NPRSITE):
            self.PRSITE.append(file.readline().strip())

        file.close()
