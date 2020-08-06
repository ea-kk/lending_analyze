from __future__ import print_function, unicode_literals

from fileutil import open

def yield_tsv(file_, head_exist=False):
    f = open(file_, "r")
    fields = f.readline().strip("\n").split("\t") if head_exist else []
    for line in f:
        yield line.strip("\n").split("\t")
    f.close()
    if head_exist:
        print(fields)

def load_tsv(file_, head_exist=True):
    f = open(file_, "r")
    fields = f.readline().strip("\n").split("\t") if head_exist else []
    data_l = [line.strip("\n").split("\t") for line in f]
    f.close()
    return data_l, fields

def save_tsv(file_, data_l, fields=[]):
    o = open(file_, "w")
    if fields:
        print("\t".join(fields), file=o)
    for data in data_l:
        print("\t".join(data), file=o)
    o.close()
