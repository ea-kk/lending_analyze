
import os, re
from os.path import join, basename, isfile, isdir
from collections import defaultdict, Counter
from datetime import date
from operator import itemgetter
from decimal import Decimal

from fileutil.text_file import load_tsv, save_tsv
from fileutil.csv_rw import save_csv
from fileutil.pdf_table import pdf_all_tables

###### cashflow ######

re_cid = re.compile('\\(cid:\\d*\\)|\n')
re_num = re.compile('(\\d+)_')

def trans(tables):
	head = []
	rows = []
	#print(tables)
	for table in tables:
		if table[0][0] in ('订单流水号',):
			head = [cell.split("（")[0] for cell in table[0]]
			for r in table[1:]:
				row = [re_cid.sub("", cell).strip() for cell in r]
				#print(row)
				if len([c for c in row if c=='']) > len(row)/2:
					if rows:
						#print(rows)
						rows[-1][head[0]] += row[0]
				else:
					rows.append(dict(zip(head,row)))
	#print(rows)
	return rows, head

def get_pdf_files(pdf_dir):
	files = []
	tmp = []
	for file_ in sorted(os.listdir(pdf_dir)):
		item = join(pdf_dir, file_)
		if isdir(item):
			files.extend(get_pdf_files(item))
		elif file_.lower().endswith(".pdf"):
			tmp.append(item)
	tmp.sort(key=lambda f:int(re_num.search(basename(f)).group(1)))
	#print(tmp)
	files.extend(tmp)
	return files

def get_table(tsv_file, pdf_dir, pswd):
	data_l = []
	head = []
	if isfile(tsv_file):
		data_l, head = load_tsv(tsv_file)
	pdf_recf = join("data/%s_record.txt" % basename(pdf_dir))
	pdf_recd = set()
	if isfile(pdf_recf):
		rl, _ = load_tsv(pdf_recf, False)
		pdf_recd = {r[0] for r in rl}
	files = [fp for fp in get_pdf_files(pdf_dir) if fp not in pdf_recd]
	if not files:
		return [dict(zip(head, row)) for row in data_l]
	rows = []
	for pdf_file in files:
		print(pdf_file)
		pdf_recd.add(pdf_file)
		tables = pdf_all_tables(pdf_file, pswd)
		r, h = trans(tables)
		if not head:
			head = h
		else:
			for t in h:
				if t not in head:
					head.append(t)
		rows.extend(r)
	data_l = [[row.get(t,"") for t in head] for row in rows] + data_l
	save_tsv(tsv_file, data_l, head)
	save_tsv(pdf_recf, [[f] for f in pdf_recd])
	return [dict(zip(head, row)) for row in data_l]

###### contract ######

re_bra = re.compile('（.*）|\\(.*\\)|自动|\n|：|:')

def get_contract(tsv_con, con_dir):
	if isfile(tsv_con):
		data_l, head = load_tsv(tsv_con)
		return [dict(zip(head, row)) for row in data_l]
	head = []
	rows = []
	for file_ in sorted(os.listdir(con_dir)):
		if not file_.lower().endswith(".pdf"):
			continue
		print(file_)
		cont_l = []
		con_file = join(con_dir, file_)
		tables = pdf_all_tables(con_file)
		for table in tables:
			if table and table[0][0] in ('产品名称',):
				for r in table:
					row = [re_bra.sub("", cell).strip() for cell in r]
					cont_l.extend([row[i:i+2] for i in range(0,len(row),2)])
		row = {}
		for k, v in cont_l:
			if k not in head:
				head.append(k)
			row[k] = v
		rows.append(row)
	data_l = [[row.get(t,"") for t in head] for row in rows]
	save_tsv(tsv_con, data_l, head)
	return rows

def get_lending(tsv_con, con_dir):
	rows = get_contract(tsv_con, con_dir)
	lend_d = {}
	for row in rows:
		dt = row["出借期开始日"]
		lt = int(row["锁定期限"].strip("天"))
		mt = Decimal(row["加入金额"].strip("元"))
		if dt not in lend_d:
			lend_d[dt] = [0, []]
		lend_d[dt][0] += mt * lt / 365
		lend_d[dt][1].append("%d(%d)"%(mt,lt))
	for dt in lend_d:
		lend_d[dt][0] = round(lend_d[dt][0], 2)
		lend_d[dt][1] = " ".join(lend_d[dt][1])
	return lend_d

###### main ######

def ana(pdf_dir, pswd, tsv_file, out_file, con_dir, tsv_con):
	stat = defaultdict(Counter)
	rows = get_table(tsv_file, pdf_dir, pswd)
	head = []
	for row in rows:
		dt = row['交易完成时间']
		if not dt:
			continue
		dt = dt.split()[0]
		tp = row['交易类型']
		mt = Decimal(row['交易金额'])
		tn = None
		if tp == "债权转让":
			if mt > 0:
				tp = "债权转让(入账)"
				tn = "债权次数(入账)"
			else:
				tn = "债权次数"
		stat[dt][tp] += mt
		if tp not in head:
			head.append(tp)
		if tn:
			stat[dt][tn] += 1
			if tn not in head:
				head.append(tn)
	zou_idx = head.index("债权次数") + 1
	zin_idx = head.index("债权次数(入账)") + 1
	if zou_idx < zin_idx:
		zin_idx += 1
		insert_seq = [(zou_idx,"债权均值"), (zin_idx,"债权均值(入账)")]
	else:
		zou_idx += 1
		insert_seq = [(zin_idx,"债权均值(入账)"), (zou_idx,"债权均值")]
	stat_table = []
	for dt, ct in sorted(stat.items(), key=itemgetter(0), reverse=True):
		row = [ct.get(tp,'') for tp in head]
		for idx, fname in insert_seq:
			ave = round(row[idx-2] / row[idx-1], 2) if row[idx-1] else ''
			row.insert(idx, ave)
		stat_table.append([dt]+row)
	for idx, fname in insert_seq:
		head.insert(idx, fname)
	lend_d = get_lending(tsv_con, con_dir)
	lend_idx = max(zou_idx, zin_idx) + 1
	head.insert(lend_idx, "出借详情")
	head.insert(lend_idx, "出借年化")
	for row in stat_table:
		nh, dt = lend_d.get(row[0], ['',''])
		row.insert(lend_idx+1, dt)
		row.insert(lend_idx+1, nh)
	save_csv(out_file, stat_table, ['date']+head)

def ana_target(pdf_dir, pswd, tsv_file, out_file, dt_fr, dt_to, sort_i=0):
	tc_tg = {}
	stat = {}
	rows = get_table(tsv_file, pdf_dir, pswd)
	for row in rows:
		dt = row['交易完成时间']
		if not dt:
			continue
		dt = dt.split()[0]
		if dt > dt_to or dt < dt_fr:
			continue
		tp = row['交易类型']
		if tp not in ("债权转让",):
			continue
		mt = Decimal(row['交易金额'])
		tg = row['对方账户名']
		tc = row['对方会员编号']
		tc_tg[tc] = tg
		if tc not in stat:
			stat[tc] = [0, 0, 0, 0]
		if mt > 0:  # 入账
			stat[tc][0] += mt
			stat[tc][1] += 1
		else:
			stat[tc][2] += mt
			stat[tc][3] += 1
	stat_table = []
	for tc, res in sorted(stat.items(), key=lambda kv:abs(kv[1][sort_i]), reverse=True):
		row = res + [res[0]/res[1] if res[1] else '', res[2]/res[3] if res[3] else '']
		row = [c if isinstance(c,str) else round(c,2) for c  in row]
		stat_table.append([tc, tc_tg[tc]] + row)
	save_csv(out_file, stat_table, ["对方会员编号","对方账户名","入账额","入账量","出账额","出账量","平均入账额","平均出账额"])


if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('dir', help="pdf files dir")
	parser.add_argument('-p', '--pw', help="pdf files password")
	parser.add_argument('-t', '--tsv', help='pdf tables detail data file')
	parser.add_argument('-c', '--con', help="contract pdf files dir")
	parser.add_argument('-v', '--ctsv', help="contract pdf tables detail data file")
	parser.add_argument('-o', '--out', help="output file")
	parser.add_argument('--fr', help="date from")
	parser.add_argument('--to', help="date to")
	parser.add_argument('--sort', type=int, default=0, help="sort index")
	parser.add_argument('--target', action='store_true')
	args = parser.parse_args()
	name = basename(args.dir)
	tsvf = args.tsv or join("data/%s_detail.tsv" % name)
	if args.target:
		outf = args.out or join("data/%s_target.csv" % name)
		dt_to = args.to or date.today().isoformat()
		ana_target(args.dir, args.pw, tsvf, outf, args.fr, dt_to, args.sort)
		exit(0)
	outf = args.out or join("data/%s_output.csv" % name)
	tsvc = args.con and args.ctsv or join("data/%s_contract.tsv" % name)
	ana(args.dir, args.pw, tsvf, outf, args.con, tsvc)
