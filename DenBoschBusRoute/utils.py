def get_traffic_combos(df, frac):
    df = df.sample(frac=frac)

    combos = []
    for index, row in df.iterrows():
        r = list(row[df.columns])
        if (r.count('#') > 1):
            combo = [int(ind) for ind in row.index if row[ind] == '#']
            if combo not in combos:
                combos.append(combo)

    return combos


def calculate_yellow_light(speed_limit):
    """
    based on https://onlinepubs.trb.org/onlinepubs/nchrp/docs/NCHRP03-95_FR.pdf

    :param speed_limit: speed limit in 0.02 m/s
    :return: yellow light timing in s
    """

    # deceleration rate in ft/s**2
    a = 10

    # approach grade in ft/ft
    g = 0

    # driver perception reaction time in seconds
    t = 1

    # 85th percentile speed of verhicles approaching the intersection in mph
    v = 11.369 + (speed_limit * 0.02 * 3.6 / 1.609344 * 0.8846)

    Y = t + (1.47 * v) / (2 * a + 64.4 * g)

    return Y


def calculate_red_clearance_interval(speed_limit, width):
    """
    based on https://onlinepubs.trb.org/onlinepubs/nchrp/docs/NCHRP03-95_FR.pdf

    :param speed_limit: speed limit in 0.02 m/s
    :param width: highest intersection crossing distance in meters
    :return: red clearence duration in seconds
    """
    # 85th percentile speed of verhicles approaching the intersection in mph
    v = 11.369 + (speed_limit * 0.02 * 3.6 / 1.609344 * 0.8846)

    # distance to cross the intersection in ft
    W = 3.28084 * width

    # car length in ft
    L = 20

    R = (W + L) / (1.47 * v)

    return R
