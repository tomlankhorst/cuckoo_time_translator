#!/usr/bin/python

from __future__ import print_function

import os
import numpy as np
import matplotlib

import matplotlib.pyplot as plt

from tools import *


def show(block=True):
    plt.show(block)


def save(fig, legend, fileName, fileFormat='pdf', overwrite=False):
    fullFileName = fileName + '.' + fileFormat if fileFormat and not fileName.endswith(fileFormat) else fileName
    if not overwrite and os.path.exists(fullFileName):
        warn("Output file %s exists already! Not overwriting!" % fullFileName)
        return

    print("Writing plot to " + fullFileName)
    extra = ()
    if legend:
        extra = (legend,)

    fig.savefig(fullFileName, bbox_inches='tight', format=fileFormat, dpi=150)


def plotMultiDelays(x, delays, xLabel, labels=None, title=None, markersize=1.5,
                    fileName=None, overwrite=None, colors=None, block=False,
                    show=False, xOffset=None):
    if not colors:
        defaultColors = ['r', 'g', 'b']
        colors = list(reversed(defaultColors[:len(delays)]))

    yLabel = "offset [msec]"

    import matplotlib.gridspec as gridspec

    v = 1.5
    figsize=(16/v, 8/v)

    breakX = False

    def plotMyDelays(ax):
        xA = np.array(x, dtype=float)
        xA = xA + (-min(xA[~np.isnan(xA)]) if xOffset is None else xOffset)
        if labels:
            for i, (d, l) in enumerate(zip(delays, labels)):
                assert(len(xA) == len(d))
                ax.plot(xA, np.asarray(d) * 1000, linestyle='-', marker='.', markersize=markersize, label=l, color=colors[i])
        else:
            for i, d in enumerate(delays):
                assert(len(xA) == len(d))
                ax.plot(xA, np.asarray(d) * 1000, linestyle='-', marker='.', markersize=markersize, color=colors[i])

    fig, ax = plt.subplots(1, 1, figsize=figsize)
    plotMyDelays(ax)
    ax.set_xlabel(xLabel)
    ax.set_ylabel(yLabel)

    if title:
        ax.set_title(title)

    legend = None
    if labels:
        legend = ax.legend(loc='upper right', shadow=False)

    if fileName:
        save(fig, legend, fileName, fileFormat=None, overwrite=overwrite)

    if show:
      show(block)
    return fig
