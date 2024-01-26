from collections import deque

import numpy as np
import pandas as pd
from scipy.signal import argrelextrema


def getHigherLows(data: np.array, order=5, K=2):
    """
    Finds consecutive higher lows in price pattern.
    Must not be exceeded within the number of periods indicated by the width
    parameter for the value to be confirmed.
    K determines how many consecutive lows need to be higher.
    """
    # Get lows
    low_idx = argrelextrema(data, np.less, order=order)[0]
    lows = data[low_idx]
    # Ensure consecutive lows are higher than previous lows
    extrema = []
    ex_deque = deque(maxlen=K)
    for i, idx in enumerate(low_idx):
        if i == 0:
            ex_deque.append(idx)
            continue
        if lows[i] < lows[i - 1]:
            ex_deque.clear()

        ex_deque.append(idx)
        if len(ex_deque) == K:
            extrema.append(ex_deque.copy())

    return extrema


def getLowerHighs(data: np.array, order=5, K=2):
    """
    Finds consecutive lower highs in price pattern.
    Must not be exceeded within the number of periods indicated by the width
    parameter for the value to be confirmed.
    K determines how many consecutive highs need to be lower.
    """
    # Get highs
    high_idx = argrelextrema(data, np.greater, order=order)[0]
    highs = data[high_idx]
    # Ensure consecutive highs are lower than previous highs
    extrema = []
    ex_deque = deque(maxlen=K)
    for i, idx in enumerate(high_idx):
        if i == 0:
            ex_deque.append(idx)
            continue
        if highs[i] > highs[i - 1]:
            ex_deque.clear()

        ex_deque.append(idx)
        if len(ex_deque) == K:
            extrema.append(ex_deque.copy())

    return extrema


def getHigherHighs(data: np.array, order=5, K=2):
    """
    Finds consecutive higher highs in price pattern.
    Must not be exceeded within the number of periods indicated by the width
    parameter for the value to be confirmed.
    K determines how many consecutive highs need to be higher.
    """
    # Get highs
    high_idx = argrelextrema(data, np.greater, order=5)[0]
    highs = data[high_idx]
    # Ensure consecutive highs are higher than previous highs
    extrema = []
    ex_deque = deque(maxlen=K)
    for i, idx in enumerate(high_idx):
        if i == 0:
            ex_deque.append(idx)
            continue
        if highs[i] < highs[i - 1]:
            ex_deque.clear()

        ex_deque.append(idx)
        if len(ex_deque) == K:
            extrema.append(ex_deque.copy())

    return extrema


def getLowerLows(data: np.array, order=5, K=2):
    """
    Finds consecutive lower lows in price pattern.
    Must not be exceeded within the number of periods indicated by the width
    parameter for the value to be confirmed.
    K determines how many consecutive lows need to be lower.
    """
    # Get lows
    low_idx = argrelextrema(data, np.less, order=order)[0]
    lows = data[low_idx]
    # Ensure consecutive lows are lower than previous lows
    extrema = []
    ex_deque = deque(maxlen=K)
    for i, idx in enumerate(low_idx):
        if i == 0:
            ex_deque.append(idx)
            continue
        if lows[i] > lows[i - 1]:
            ex_deque.clear()

        ex_deque.append(idx)
        if len(ex_deque) == K:
            extrema.append(ex_deque.copy())

    return extrema


def get_tline_output(deq: deque, df: pd.DataFrame):
    tlines = []
    for i in deq:
        pair = []
        for j in i:
            pair.append(df.iloc[j].Date)
        tlines.append(pair)
    return tlines
