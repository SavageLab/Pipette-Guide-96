#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import csv
import numpy as np
import pandas as pd
import sys
import os.path

from operator import itemgetter

backgroundcoloring = 0
letters = 'ABCDEFGH'


def main(values_df, outfile, headerfile):
	"""Main function.

	Args:
		values_df: values to output in HTML as a Pandas DataFrame.
		outfile: output file object.
		headerfile: JS header content file object.
	"""
	# write beginning of header
	outfile.write('<script language="JavaScript">\n<!--\n')

	# Find the order from lowest to highest
	values = []
	for idx, row in values_df.iterrows():
		for v in row.values:
			values.append(v)
	wellorder = [i[0] for i in sorted(enumerate(values), key=lambda x:x[1])]

	# Record order as a variable which javascript will interact with
	outfile.write('var wellorder = [')
	reversewellorder = wellorder[::-1]

	for i in range(0, 95):
		outfile.write(str(reversewellorder[i])+',')
	outfile.write(str(reversewellorder[95])+'];\n')

	# write rest of header by copying from old file
	for line in headerfile:
		outfile.write(line)

	# make top row of table
	outfile.write('<tr valign="top">\n')
	outfile.write('<td class = "td" style="background-color:rgb(255,255,255)" >  </td>\n')
	for c in range(0, 12):
		outfile.write('<td class = "column-label" style="background-color:rgb(255,255,255)" > %s  </td>\n'%(str(c+1)))

	# make rest of table table
	k = 0
	for r in range(0, 8):
		outfile.write('<tr valign="top">\n')
		outfile.write('<td class = "row-label" style="background-color:rgb(255,255,255)" > %s   </td>\n'%(letters[r]))
		for c in range(0, 12):
			value = values[k]
			order = wellorder.index(k)
			if backgroundcoloring==1:
				rawcolor=int(255-(1.3*order))
				color=str(rawcolor)+','+str(rawcolor)+','+str(rawcolor)
			elif value < 0.01:
				color='0,0,0'
			else:
				color='255,255,255'
			if (c==4 or c==8) and r==3:
				outfile.write('<td class = "border-both" style="background-color:rgb(%s);" > <a href="#" onClick="javascript:changeBGC(%s)">%s</a>   </td>\n'%(color,str(k),value))
			elif c==4 or c==8:
				outfile.write('<td class = "border-side" style="background-color:rgb(%s);" > <a href="#" onClick="javascript:changeBGC(%s)">%s</a>   </td>\n'%(color,str(k),value))
			elif r==3:
				outfile.write('<td class = "border-bottom" style="background-color:rgb(%s);" > <a href="#" onClick="javascript:changeBGC(%s)">%s</a>   </td>\n'%(color,str(k),value))
			else:
				outfile.write('<td class = "td" style="background-color:rgb(%s);" > <a href="#" onClick="javascript:changeBGC(%s)">%s</a>   </td>\n'%(color,str(k),value))
			k = k+1
						
	outfile.write('</tr>\n </table>\n</div>\n</body>\n</html>')


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description='Make an HTML file for dilutions.')
	parser.add_argument(
		'--header_file', default='header.html',
		type=argparse.FileType('rU'),
		help='Path to HTML header template file.')
	parser.add_argument(
		'--out_file', default='index.html',
		type=argparse.FileType('w'),
		help='Output HTML template file.')
	parser.add_argument(
		'--amounts_file', default='volumes.csv',
		type=argparse.FileType('rU'),
		help='Path to amounts CSV file.')
	parser.add_argument(
		'--final_conc', default=None, type=float,
		help=(
			'If set, assumes amounts specify concentrations and '
			'outputs volumes needed to achieve final concentrations. '
			'Must also specify --sample_volume if --final_conc is not None.'
			))
	parser.add_argument(
		'--sample_volume', default=None, type=float,
		help='Volume of all samples. Used if amounts are concentrations')
	args = parser.parse_args()

	# TODO(flamholz): fix JS so that highest value is highlighted on
	# start in Chrome.
	# TODO(flamholz): make script calculate dilutions.
	# TODO(flamholz): use a Jinja template to simplify output?
	values_df = pd.read_csv(args.amounts_file, names=np.arange(1, 13))
	main(values_df, args.out_file, args.header_file)