#!/usr/bin/env python

import sys
import csv

rep = {
	'Monaclinoe Ind': 'Limerick',
	'Market Green Shopping Centre Knockgriffin Midleton': 'Midleton',
	'30 Upper Baggot Street': 'Dublin',
	'17-19 Patrick St': 'Limerick',
	'Church Street': 'Dublin',
	'Gratfton Street': 'Dublin',
	'Kevin Street Upper': 'Dublin',
	'Maldron Hotel Pearse Street': 'Dublin',
	'Main Street': 'Donegal',
	'Main Street, Johnston': 'Donegal',
	'Paul Street, Lavitts Quay': 'Cork',
	'Thomas Street': 'Cavan',
	'Thomas Street, Beckscourt': 'Cavan',
	'Dub 1': 'Dublin',
	'The Old Street': 'Dublin',
	'D22, D24, D12': 'Dublin',
	'd04': 'Dublin',
}

city_county_map = {
	'Terenure': 'Dublin',
	'Willow Court': 'Dublin',
}

csvfile = open('cities.csv', 'r')
r = csv.reader(csvfile)
for row in r:
	if row[2].find('Dublin') >= 0 or row[2] == 'Fingal':
		row[2] = 'Dublin'
	if row[2] == ' Cnoc na Muirleog' or row[2] == ' Cross Roads':
		row[2] = 'Donegal'
	if row[2][-5:] == ' City':
		row[2] = row[2][:-5]
	city_county_map[row[0]] = row[2]

import requests
import urllib.parse
import re

session = requests.Session()
session.headers['User-Agent'] = 'Wget/1.21.3'
session.headers['Accept'] = '*/*'

county_re = re.compile('<place [^>]* display_name="[^"]*, County ([^,]*), [^"]*"[^>]* />')

print('insert into "cities" values')

for line in open('cities', 'r'):
	orig_line = line
	line = line.strip().strip('.,').replace('&amp;', '&').replace('\t', ' ').replace('  ', ' ').replace('  ', ' ').replace('  ', ' ').replace(', Ireland', '').replace(', IE', '').replace(', ARC', '').replace('SHANNON', 'Shannon').replace('ATHLONE', 'Athlone').replace('ATHY', 'Athy').replace('CLANE', 'Clane').replace('RINGASKIDDY', 'Ringaskiddy').replace(' / Hybrid', '').replace(', outer ring road', '')
	if line[-4:] == ', UK' or line in ('Field', 'FIELD', 'IRELAND', 'Ireland (ROI and NI)', 'Head Office/WFH (2 days) and Site based (3 days)', 'Virtual', 'UNAVAILABLE', 'IE', 'WFH', 'WFH or Hybrid', 'Work from home', 'Work From Home', 'Home Office', '-', 'All', '70 applicants', '18 Fairview', 'anywhere in Ireland', 'UNAVAILABLE', 'ERX – Smartply Europe Ltd', 'DEU Karlsruhe', 'BSDP Bristol', 'CHE Eysins - Business Park Terre', '(Ireland West)', 'Ireland', 'ireland', 'Embassy Office Park', 'West of Ireland', 'Warsaw, Poland', 'Republic of Ireland', 'Nationwide Ireland', 'Flexible throughout Ireland', 'Northern Ireland Assembly', 'The Island', 'The Islands', 'Midlands', 'Leinster', 'Leinster - Republic of Ireland', 'Ulster', 'munster', 'Mid-West', 'South-West', 'Little-Island', 'Other', 'Offsite', 'Tel Aviv', 'International Financial Services Centre', 'Eastern Region', 'europe', 'European Union', 'Heidelberg (Germany)', 'Road', 'London', 'Sweden', 'Street', 'Time Square', 'The Mall', 'School Road'):
		continue
	if line in city_county_map:
		matches = [city_county_map[line]]
	elif line in rep:
		matches = [rep[line]]
	else: #line.find(',') == -1:
		matches = []
		for key in city_county_map:
			if line.find(key) >= 0:
				county = city_county_map[key]
				if county not in matches:
					matches.append(county)

	if len(matches) == 0:
		url = 'https://nominatim.openstreetmap.org/search?format=xml&q=' + urllib.parse.quote_plus(line + ', ireland')
		req = session.get(url, timeout=30)
		contents = req.content.decode('utf-8')
		srch = county_re.search(contents)
		county = None
		if srch is not None:
			county = county_re.search(contents)[1]
			matches.append(county)

	if len(matches) == 0:
		print(orig_line, file=sys.stderr)
	elif len(matches) > 1:
		print(orig_line + '\t' + repr(matches), file=sys.stderr)
	else:
		print(f"('{line}', null, '{matches[0]}'),", flush=True)

