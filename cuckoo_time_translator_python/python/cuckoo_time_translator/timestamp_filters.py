from __future__ import print_function

import numpy as np
import math
import sys

import cuckoo_time_translator as ctt
from cuckoo_time_translator import LocalTime, RemoteTime

class TimestampFilter:
  def __init__(self, owt, batch = False, switchTime = None):
    if switchTime:
      self.owt = ctt.SwitchingOwt(switchTime, owt)
    else:
      self.owt = owt
    self.batch = batch
    self.switchTime = switchTime
    
    self._paramNames = { "batch" : False, "switchTime" : None }
    
    self.name = self.__class__.__name__

  def _addParamNames(self, extra_names):
    return self._paramNames.update(extra_names)

  def getConfigString(self, showDefaults = False):
    return "%s(%s)" %  (self.name, ", ".join([ "%s=%s"% (name, getattr(self, name)) for name, default in self._paramNames.items() if showDefaults or default != getattr(self, name)]))

  def __str__(self):
    return self.getConfigString(False)

  def apply(self, hwTimes, receiveTimes):
    self.owt.reset()
    assert(len(hwTimes) > 2)
    assert(len(hwTimes) == len(receiveTimes))
    correctedhwTimes = []

    timeScale = (receiveTimes[-1] - receiveTimes[0]) / (hwTimes[-1] - hwTimes[0])

    for ht, rt in zip(hwTimes, receiveTimes):
      correctedhwTimes.append(float(self.owt.updateAndTranslateToLocalTimestamp(RemoteTime(ht * timeScale) , LocalTime(rt))))

    if self.batch:
        correctedhwTimes = []
        for ht, rt in zip(hwTimes, receiveTimes):
            correctedhwTimes.append(float(self.owt.translateToLocalTimestamp(RemoteTime(ht * timeScale))))

    return correctedhwTimes

  def getConfigAndStateString(self):
    return self.owt.getNameAndConfigString() + ": "+ self.owt.getStateString()

class ConvexHullFilter (TimestampFilter):
  def __init__(self, *args, **kwargs):
    TimestampFilter.__init__(self, ctt.ConvexHullOwt(), *args, **kwargs)

class KalmanFilter(TimestampFilter):
  def __init__(self, outlierThreshold = None, sigmaSkew = None, *args, **kwargs):
    k = ctt.KalmanOwt()
    c = k.getConfig()
    
    extra_params = { "outlierThreshold" : c.outlierThreshold, "sigmaSkew" : c.sigmaSkew }

    if outlierThreshold:
      c.outlierThreshold = outlierThreshold
    if sigmaSkew:
      c.sigmaSkew = sigmaSkew

    self.outlierThreshold = c.outlierThreshold
    self.sigmaSkew = c.sigmaSkew

    k.setConfig(c)
    TimestampFilter.__init__(self, k, *args, **kwargs)
    
    self._addParamNames(extra_params)
