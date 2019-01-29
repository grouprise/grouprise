import randomcolor


def get_random_color():
    return randomcolor.RandomColor().generate(luminosity='dark')[0]
