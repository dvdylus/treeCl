"""
Data structures to hold model parameters and attributes such as alignment file paths
"""
import json
import sys

class BaseParameters(object):
    __slots__ = []

    @property
    def dict(self):
        return dict((item.lstrip('_'), getattr(self, item)) for item in self.__slots__)

    def write(self, fileobj=sys.stdout):
        json.dump(self.dict, fileobj)


class PartitionParameters(BaseParameters):
    __slots__ = ['_alpha', '_distances', '_frequencies', '_name', '_rates', '_variances']

    def __init__(self):
        self._alpha = None
        self._distances = None
        self._frequencies = None
        self._name = None
        self._rates = None
        self._variances = None

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        self._alpha = value

    @property
    def distances(self):
        return self._distances

    @distances.setter
    def distances(self, value):
        self._distances = value

    @property
    def frequencies(self):
        return self._frequencies

    @frequencies.setter
    def frequencies(self, value):
        self._frequencies = value

    @property
    def name(self):
        return self._frequencies

    @name.setter
    def name(self, value):
        self._frequencies = value

    @property
    def rates(self):
        return self._rates

    @rates.setter
    def rates(self, value):
        self._rates = value

    @property
    def variances(self):
        return self._variances

    @variances.setter
    def variances(self, value):
        self._variances = value


class Parameters(BaseParameters):
    __slots__ = ['_filename', '_likelihood', '_ml_tree', '_ms_tree', '_nj_tree', '_partitions', '_sse']

    def __init__(self):
        self._filename = None
        self._likelihood = None
        self._ml_tree = None
        self._ms_tree = None
        self._nj_tree = None
        self._partitions = []
        self._sse = None

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value

    @property
    def likelihood(self):
        return self._likelihood

    @likelihood.setter
    def likelihood(self, value):
        self._likelihood = value

    @property
    def sse(self):
        return self._sse

    @sse.setter
    def sse(self, value):
        self._sse = value

    @property
    def ml_tree(self):
        return self._ml_tree

    @ml_tree.setter
    def ml_tree(self, value):
        self._ml_tree = value

    @property
    def nj_tree(self):
        return self._nj_tree

    @nj_tree.setter
    def nj_tree(self, value):
        self._nj_tree = value

    @property
    def ms_tree(self):
        return self._ms_tree

    @ms_tree.setter
    def ms_tree(self, value):
        self._ms_tree = value

    @property
    def partitions(self):
        if len(self._partitions) == 1:
            return self._partitions[0]
        else:
            return self._partitions

    @partitions.setter
    def partitions(self, value):
        self._partitions = value

    @property
    def dict(self):
        d = dict((item.lstrip('_'), getattr(self, item)) for item in self.__slots__)
        if d['partitions'] is not None:
            d['partitions'] = {i: subpar.dict for (i, subpar) in enumerate(d['partitions'])}
        return d
