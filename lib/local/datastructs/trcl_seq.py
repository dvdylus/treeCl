#!/usr/bin/env python

from ...remote.datastructs.seq import Seq, concatenate

class TrClSeq(Seq):

    """ A version of the SequenceRecord class with some extra functionality for
    working with tree inference packages, notably TreeCollection """

    def __init__(
        self,
        infile=None,
        file_format='fasta',
        name=None,
        datatype=None,
        headers=[],
        sequences=[],
        dv=[],
        tree=None,
        ):

        self.TCfiles = {}
        self.dv = dv
        if tree and isinstance(tree, Tree):
            self.tree = tree

        self.tmpdir = tmpdir

        super(TrClSeq, self).__init__(
            infile,
            file_format,
            name,
            datatype,
            headers,
            sequences,
            )

    def __add__(self, other):
        """ Allows Records to be added together, concatenating sequences """

        self_set = set(self.headers)
        other_set = set(other.headers)
        if not self.datatype == other.datatype:
            print 'Trying to add sequences of different datatypes'
            return self
        union = self_set | other_set
        intersection = self_set & other_set
        only_in_self = self_set - other_set
        only_in_other = other_set - self_set

        d = {}
        for k in union:
            if k in intersection:
                d[k] = self.mapping[k] + other.mapping[k]
            elif k in only_in_self:
                d[k] = self.mapping[k] + 'N' * other.seqlength
            elif k in only_in_other:
                d[k] = 'N' * self.seqlength + other.mapping[k]
        dvsum = self.dv + other.dv
        return_object = TCSeqRec(headers=d.keys(), sequences=d.values(),
                                 datatype=self.datatype).sort_by_name(in_place=False)
        return_object.dv = dvsum
        return return_object

    def bionj(self):
        """ Uses phyml (via treeCl.externals.tree_builders.Phyml) to build a
        bioNJ tree for the current record """

        p = Phyml(self)
        self.tree = p.run('nj')

    def dv_matrix(self):
        """ Uses darwin (via treeCl.externals.DVWrapper) to calculate pairwise
        distances and variances"""

        dv = DVWrapper(self)
        self.dv.append(dv.run())

    def phyml(self):
        """ Uses phyml (via treeCl.externals.tree_builders.Phyml) to build a
        full ML tree for the current record """

        p = Phyml(self)
        self.tree = p.run('ml')

    def tree_collection(self):
        """ Uses TreeCollection (via
        treeCl.externals.tree_builders.TreeCollection) to build a least squares
        tree for the current record """

        if self.dv <= []:
            self.get_dv_matrix()
        tc = TreeCollection(self)
        self.tree = tc.run()

    def _pivot(self, lst):
        new_lst = zip(*lst)
        return [''.join(x) for x in new_lst]

    def sanitise(self):
        self.sort_by_name()
        l = []
        for h in self.headers:
            if '/' in h:
                h = h[:h.index('/')]
            while h.startswith(' '):
                h = h[1:]
            h = h.replace(' ', '_')
            l.append(h)
        self.headers = l
        self.sequences = [seq.upper() for seq in self.sequences]
        self._update()

    def shuffle(self):
        """ Modifies in-place """

        columns = self._pivot(self.sequences)
        shf(columns)
        self.sequences = self._pivot(columns)
        self._update()

    def sort_by_length(self, in_place=True):
        """ Sorts sequences by descending order of length Uses zip as its own
        inverse [ zip(*zip(A,B)) == (A,B) ] Gaps and 'N' characters are not
        counted """

        (h, s) = zip(*sorted(zip(self.headers, self.sequences),
                     key=lambda item: len(item[1].replace('-', '').replace('N',
                     '')), reverse=True))
        if in_place:
            self.headers = h
            self.sequences = s
        else:
            return TCSeqRec(name=self.name, headers=h, sequences=s,
                            datatype=self.datatype)

    def sort_by_name(self, in_place=True):
        """ Sorts sequences by name, treating numbers as integers (i.e. sorting
        like this: 1, 2, 3, 10, 20 not 1, 10, 2, 20, 3). If in_place = False the
        sorting doesn't mutate the underlying object, and the output is returned
        If in_place = True the sorting mutates the self object """

        items = self.mapping.items()
        if items == []:
            return self
        sort_key = lambda item: tuple((int(num) if num else alpha) for (num,
                                      alpha) in re.findall(r'(\d+)|(\D+)',
                                      item[0]))
        items = sorted(items, key=sort_key)
        (h, s) = zip(*items)
        if in_place:
            self.headers = h
            self.sequences = s
            return self
        else:
            return TCSeqRec(name=self.name, headers=h, sequences=s,
                            datatype=self.datatype)

    def split_by_lengths(self, lengths, names=None):
        assert sum(lengths) == self.seqlength
        columns = self._pivot(self.sequences)
        newcols = []
        for l in lengths:
            newcols.append(columns[:l])
            columns = columns[l:]
        newrecs = []
        for col in newcols:
            newseqs = self._pivot(col)
            newrec = TCSeqRec(headers=self.headers, sequences=newseqs,
                              datatype=self.datatype)
            newrecs.append(newrec)
        if names:
            for (i, newrec) in enumerate(newrecs):
                newrec.name = names[i]
        else:
            for (i, newrec) in enumerate(newrecs):
                newrec.name = 'record_{0}'.format(i + 1)
        return newrecs
