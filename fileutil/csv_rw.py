from __future__ import print_function, unicode_literals

import csv
from fileutil import open

def yield_csv(file_, head_exist=False):
    f = open(file_, "r")
    reader = csv.reader(f)
    for row in reader:
        yield row
    f.close()

def load_csv(file_, head_exist=True):
    f = open(file_, 'r', encoding='gbk')
    reader = csv.reader(f)
    data_l = [row for row in reader]
    f.close()
    fields = data_l.pop(0) if head_exist else []
    return data_l, fields

def save_csv(file_, data_l, fields=[]):
    o = open(file_, 'w', encoding='gbk')
    writer = csv.writer(o)
    if fields:
        writer.writerow(fields)
    writer.writerows(data_l)
    o.close()
