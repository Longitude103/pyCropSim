"""Implements arithmetic function as Fortran does."""

import math

eInPython3: float = 2.7182818284590450907955982984276488
eInFortran: float = 2.7182818284590452353602874713526625
#====================================^
#                   2.7182818284590450907955982984276488

EXP2InPython3 = 7.3890560989306504069418224389664829
EXP2InFortran = 7.3890560989306504069418224389664829
#===================================================

# From mathq.h
#===================================================
#define M_Eq                2.7182818284590452353602874713526625Q  /* e */
#define M_LOG2Eq        1.4426950408889634073599246810018921Q  /* log_2 e */
#define M_LOG10Eq        0.4342944819032518276511289189166051Q  /* log_10 e */
#define M_LN2q                0.6931471805599453094172321214581766Q  /* log_e 2 */
#define M_LN10q                2.3025850929940456840179914546843642Q  /* log_e 10 */
#define M_PIq                3.1415926535897932384626433832795029Q  /* pi */
#define M_PI_2q                1.5707963267948966192313216916397514Q  /* pi/2 */
#define M_PI_4q                0.7853981633974483096156608458198757Q  /* pi/4 */
#define M_1_PIq                0.3183098861837906715377675267450287Q  /* 1/pi */
#define M_2_PIq                0.6366197723675813430755350534900574Q  /* 2/pi */
#define M_2_SQRTPIq        1.1283791670955125738961589031215452Q  /* 2/sqrt(pi) */
#define M_SQRT2q        1.4142135623730950488016887242096981Q  /* sqrt(2) */
#define M_SQRT1_2q        0.7071067811865475244008443621048490Q  /* 1/sqrt(2) */


def AMOD(A: float, P: float) -> float:
    """Computes the remainder of the division of A by P."""
    return A - (INT(A / P) * P)


def INT(A: float) -> int:
    """Convert to integer type"""

    # Fortran has a different way to cast a float to an integer.
    if A == 0.0: return 0
    return int(math.floor(A) if A > 0.0 else math.ceil(A))
