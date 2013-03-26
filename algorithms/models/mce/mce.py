# encoding: utf-8


# TODO: make abstract class for all models/managers
# to prevent code coping of common methods (for example _predict method)

import numpy as np

from molusce.algorithms.dataprovider import Raster, ProviderError

class MCEError(Exception):
    '''Base class for exceptions in this module.'''
    def __init__(self, msg):
        self.msg = msg


class MCE(object):

    randomConsistencyIndex = {
        2:  0,
        3:  0.58,
        4:  0.90,
        5:  1.12,
        6:  1.24,
        7:  1.32,
        8:  1.41,
        9:  1.45,
        10: 1.49,
        11: 1.51,
        12: 1.48,
        13: 1.56,
        14: 1.57,
        15: 1.59,
        16: 1.60,
        17: 1.61,
        18: 1.62,
        19: 1.63,
        20: 1.63,
        21: 1.64,
        22: 1.65,
        23: 1.65,
        24: 1.66,
        25: 1.66,
        26: 1.67,
        27: 1.67,
        28: 1.67,
        29: 1.68,
        30: 1.68,
        31: 1.68,
        32: 1.69,
        33: 1.69,
        34: 1.69,
        35: 1.69,
        36: 1.70,
        37: 1.70,
        38: 1.70,
        39: 1.70
    }
    def __init__(self, factors, wMatr, areaAnalyst, initStateNum, finalStateNum):
        '''
        Multicriteria evaluation based on Saaty method. It defines transition probability of two classes (initStateNum, finalStateNum).
        @param factors          List of the factor rasters used for prediction.
        @param wMatr            List of lists -- NxN comparison matrix.
        @param areaAnalyst      AreaAnalyst that contains map of the changes, encodes and decodes class numbers.
        @param initStateNum     Number of initial state (the state before transition).
        @param finalStateNum    Number of final state (the state after transition).
        '''

        self.factors = factors
        self.analyst = areaAnalyst
        self.changeMap   = areaAnalyst.getChangeMap()

        self.dim = 0
        for f in factors:
            self.dim = self.dim + f.getBandsCount()

        if self.dim != len(wMatr):
            raise MCEError('Matrix size is different from the number of variables!')

        # Check if the matrix is valid
        for i in xrange(self.dim):
            if len(wMatr[i]) != self.dim:
                raise MCEError('The weight matrix is not NxN!')
        EPSILON = 0.000001      # A small number
        for i in xrange(self.dim):
            for j in xrange(i+1, self.dim):
                if abs(wMatr[i][j] * wMatr[j][i] - 1) > EPSILON:
                    raise MCEError('w[i,j] * w[j,i] not equal 1 !')

        self.wMatr = np.array(wMatr)

        self.weights = None     # Weigths of the factors, calculated using wMatr
        self.consistency =None  # Consistency ratio of the comparison matrix.

        self.prediction = None
        self.confidence = None


    def getConsistency(self):
        if self.consistency == None:
            self.setWeights()
        return self.consistency

    def getConfidence(self):
        return self.confidence

    def getPrediction(self, state, factors=None):
        '''
        Most of the models use factors for prediction, but WoE takes list of factors only once (during the initialization).
        '''
        self._predict(state)
        return self.prediction

    def getWeights(self):
        if self.weights == None:
            self.setWeights()
        return self.weights

    def _predict(self, state):
        pass

    def setWeights(self):
        '''
        Calculate the weigths and consistency ratio.
        '''
        # Weights
        w, v = np.linalg.eig(self.wMatr)
        maxW = np.max(w)
        maxInd = list(w).index(maxW)    # Index of the biggest eigenvalue
        maxW = maxW.real
        v = v[:,maxInd]       # The eigen vector
        self.weights = [x.real for x in v]  # Maxtix v can be complex
        self.weights = self.weights/sum(self.weights)

        # Consistency ratio
        if self.dim > 2:
            ci = (maxW - self.dim)/(self.dim - 1)
            try:
                ri = self.randomConsistencyIndex[self.dim]
                self.consistency = ci/ri
            except KeyError:
                self.consistency = -1
        else:
            self.consistency = 0






