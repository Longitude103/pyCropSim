"""Module implementing CALDAY and DAYOFYR subroutines"""

IDAYS = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)

def CALDAY(JDAY: int):
    """Returns a tuple with IMON and IDAY being the month and day for the specified Julian Day."""
    if JDAY == 0:
        return (0, 0)
    if JDAY > 366:
        return (13, 0)
    IMON = 0, 0
    for J in range(12):
        IMON = J
        if JDAY <= IDAYS[J]:
            break
        IMON += 1
    return (IMON, JDAY - IDAYS[IMON -1])

# This function assummes IMON is in the [1,12] range
# The IMON value must not be changed when passed to this function
def DAYOFYR(IMON: int, IDAY: int) -> int:
    """Computes the Julian Day for the month and day specified and returns it as integer."""

    # IMON is the 1-based index for the month, so 1 for January and 12 for December.
    # In the Fortran code JDYPLT, JDYSTR and JDYEND receive the result.
    if IMON == 0:
        return 0
    if IMON > 12:
        # TODO: Check if this could happen in the code and decide to handle the error if required.
        return -1
    return IDAY+IDAYS[IMON-1]
