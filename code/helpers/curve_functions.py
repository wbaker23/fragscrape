import numpy as np


def linear(x, m, b):
    return m * x + b


def logistic(x, L, k, d):
    return L / (1 + np.exp(-k * (x - d)))


def cubic(x, a, b, c, d):
    return a * pow(x, 3) + b * pow(x, 2) + c * x + d


def exponential(x, a, b, c, d):
    return a * np.exp(b * (x - c)) + d


def logarithmic(x, a, c):
    return a * np.log(x) + c


def rational(x, a, b, c):
    return (a / (b - x)) + c
