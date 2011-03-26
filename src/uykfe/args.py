
from argparse import ArgumentError, ArgumentParser


def non_zero_int(value):
    try:
        nzi = int(value)
        if nzi < 0:
            raise ArgumentError('{0} is negative.'.format(value))
        else:
            return nzi
    except:
        raise ArgumentError('{0} is not an integer.'.format(value))


def build_weighted_parser(description):
    parser = ArgumentParser(description=description)
    parser.add_argument('-a', '--artist', help='starting artist')
    parser.add_argument('-t', '--track', help='starting track')
    parser.add_argument('-d', '--depth', default=0, type=non_zero_int, help='depth for delayed weighting')
    parser.add_argument('-x', '--localexp', default=1, type=int, help='exponent for local weight')
    parser.add_argument('-y', '--depthexp', default=1, type=int, help='exponent for depth weight')
    parser.add_argument('-c', '--config', default='.uykferc', help='config file')
    return parser
