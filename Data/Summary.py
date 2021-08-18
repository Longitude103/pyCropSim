"""Summary module."""

from Files.DataFile import DataRow


class WeeklyData(DataRow):
    """Data stored weekly"""
    __slots__ = ("ET", "ER", "ETR", "IRN", "IRG", "RA")

    # In the Fortran code, these variables have the WK suffix, like ETRWK, ETWK, ...

    def __init__(self):
        self.ET = 0.0
        """Evapotranspiration."""
        self.ER = 0.0
        """ET Reference."""
        self.ETR = 0.0
        self.IRN = 0.0
        """Net irrigation."""
        self.IRG = 0.0
        """Gross irrigation."""
        self.RA = 0.0
        """Rain."""

    def init(self):
        """Reset every value to zero."""
        self.ET = 0.0
        self.ER = 0.0
        self.ETR = 0.0
        self.IRN = 0.0
        self.IRG = 0.0
        self.RA = 0.0

    def add(self, other):
        """Adds the values of the specified weekly data to this one."""
        self.RA += other.RA
        self.ET += other.ET
        self.ER += other.ER
        self.ETR += other.ETR
        self.IRN += other.IRN
        self.IRG += other.IRG

    def toPrecipFile(self):
        """Returns the string representation for the PRECIP.CSV file."""
        return (f"{self.ETR:>7.2f},{self.ET:>7.2f},{self.ER:>7.2f},{self.RA:>7.2f},"
                f"{self.IRN:>7.2f},{self.IRG:>7.2f},")

    def __add__(self, other):
        res = WeeklyData()
        res.RA = self.RA + other.RA
        res.ET = self.ET + other.ET
        res.ER = self.ER + other.ER
        res.ETR = self.ETR + other.ETR
        res.IRN = self.IRN + other.IRN
        return res

    def __sub__(self, other):
        res = WeeklyData()
        res.RA = self.RA - other.RA
        res.ET = self.ET - other.ET
        res.ER = self.ER - other.ER
        res.ETR = self.ETR - other.ETR
        res.IRN = self.IRN - other.IRN
        return res

    def __eq__(self, other):
        if isinstance(other, WeeklyData):
            return self.RA == other.RA and self.ET == other.ET \
                   and self.ER == other.ER and self.ETR == other.ETR and self.IRN == self.IRN
        return super().__eq__(other)


class MonthlyData(WeeklyData):
    """Data stored monthly, it inherits the weekly data too."""
    __slots__ = ("E", "T", "RON", "ROF", "INF", "DRA", "DPL", "NUMIRR")

    def __init__(self):
        super().__init__()

        self.E = 0.0
        """Evaporation."""
        self.T = 0.0
        """Transpiration."""
        self.RON = 0.0
        """Run-On"""
        self.ROF = 0.0
        """Run-Off"""
        self.INF = 0.0
        """Infiltration."""
        self.DRA = 0.0
        """Drainage."""
        self.DPL = 0.0
        """Depletion."""
        self.NUMIRR = 0
        """Number of irrigations."""

    def init(self):
        super().init()

        print("Initializing monthly summary.")

        self.E = 0.0
        self.T = 0.0
        self.ROF = 0.0
        self.RON = 0.0
        self.INF = 0.0
        self.DRA = 0.0
        self.NUMIRR = 0

    def add(self, other):
        """Adds the values of the specified monthly data to this one."""
        super().add(other)

        self.E += other.E
        self.T += other.T
        self.RON += other.RON
        self.ROF += other.ROF
        self.INF += other.INF
        self.DRA += other.DRA
        self.DPL += other.DPL

    def toMonthlyOutput(self, index):
        """Returns the string corresponding to the monthly report."""
        return (f"{' ' * 10}{index:>5}{self.ETR:>6.1f}{self.E:>6.1f}{self.T:>6.1f}{self.ET:>6.1f}"
                f"{self.RA:>6.1f}{self.ER:>6.1f}{self.RON:>6.1f}  {self.IRG:>8.1f}{self.IRN:>8.1f}"
                f"      {self.NUMIRR:>2}{self.INF:>8.1f}{self.DRA:>8.1f}{self.DPL:>8.1f}\n")

    def toTotalOutput(self):
        """Returns the string corresponding to the monthly totals report."""
        return (f"{self.ETR:>6.1f}{self.E:>6.1f}{self.T:>6.1f}{self.ET:>6.1f}{self.RA:>6.1f}"
                f"{self.ER:>6.1f}{self.RON:>6.1f}  {self.IRG:>8.1f}{self.IRN:>8.1f}        "
                f"{self.INF:>8.1f}{self.DRA:>8.1f}{self.DPL:>8.1f}\n")

    @classmethod
    def getTotals(cls, months: list):
        """Computes the totals for the list of months specified."""
        tot = MonthlyData()
        for month in months:
            tot.add(month)
        return tot

    def __add__(self, other):
        res = MonthlyData()
        res.RA = self.RA + other.RA
        res.ET = self.ET + other.ET
        res.ER = self.ER + other.ER
        res.ETR = self.ETR + other.ETR
        res.IRN = self.IRN + other.IRN
        res.E = self.E + other.E
        res.T = self.T + other.T
        res.RON = self.RON + other.RON
        res.ROF = self.INF + other.INF
        res.DRA = self.DRA + other.DRA
        res.DPL = self.DPL + other.DPL
        return res

    def __sub__(self, other):
        res = MonthlyData()
        res.RA = self.RA - other.RA
        res.ET = self.ET - other.ET
        res.ER = self.ER - other.ER
        res.ETR = self.ETR - other.ETR
        res.IRN = self.IRN - other.IRN
        res.E = self.E - other.E
        res.T = self.T - other.T
        res.RON = self.RON - other.RON
        res.ROF = self.INF - other.INF
        res.DRA = self.DRA - other.DRA
        res.DPL = self.DPL - other.DPL
        return res
