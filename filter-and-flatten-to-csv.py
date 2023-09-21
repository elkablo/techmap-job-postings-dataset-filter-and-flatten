#!/usr/bin/env python

import pandas as pd
import json
from tqdm import tqdm
import csv

tags_to_save = {'CATEGORIES', 'SKILLS', 'INDUSTRIES', 'REQUIREMENTS'}

def filter_tags(d):
	if 'orgTags' not in d or d['orgTags'] is None:
		return {tag.lower(): {} for tag in tags_to_save}
	r = {}
	for tag in tags_to_save:
		if tag in d['orgTags']:
			r[tag.lower()] = [ v for v in d['orgTags'][tag] if v is not None and len(v.strip()) > 0 ]
		else:
			r[tag.lower()] = []
	return r

def filter_address(d):
	if 'orgAddress' not in d or d['orgAddress'] is None:
		return {}
	#for k, v in d['orgAddress'].items():
	#	if isinstance(v, dict):
	#		print(d['orgAddress'])
	return {k: v for k, v in d['orgAddress'].items() if k not in ('level', 'addressLine', 'geoPoint', 'source') and len(v.strip()) > 0}

def parse_salary(s):
	s = s.lower().replace('(', '').replace(')', '').replace('per per', 'a') \
		.replace('/ per', 'a').replace('per', 'a').replace('  ', ' ').replace('a hour', 'an hour') \
		.replace('par mois', 'a month').replace('/ year', 'a year') \
		.replace('a annum, inc benefits', 'a year').replace('a annum', 'a year').replace(' a year, ote', 'a year')
	periods = {
		' a day': 'day',
		' a year': 'year',
		' an hour': 'hour',
		' a week': 'week',
		' a month': 'month',
	}
	salary_period = None
	for suffix, period in periods.items():
		if s[-len(suffix):] == suffix:
			salary_period = period
			s = s[:-len(suffix)]
			break
	if salary_period is None:
		#print(s)
		return (None, None, None, None)

	if s[-4:] in (' eur', ' gbp', ' usd'):
		currency = s[-3:].upper()
		s = s[:-4].strip()
		if '-' in s:
			min, max = tuple(map(lambda x: x.strip().replace(',', ''), s.split('-')))
			return min, max, currency, salary_period
		else:
			return s, s, currency, salary_period

	if '-' in s:
		s = s.replace('euro', 'EUR').replace('pound', 'GBP').replace('usd dollar', 'USD').replace('aud dollar', 'AUD').replace('dollar', 'USD')
		min, max = tuple(map(lambda x: x.strip(), s.split('-')))
		if min[:4] in ('EUR ', 'GBP ', 'USD ', 'AUD '):
			currency = min[:3]
			min = min[4:].replace(',', '')
			max = max[4:].replace(',', '')
		else:
			raise

		return min, max, currency, salary_period

	s = s.replace('euro', 'EUR').replace('pound', 'GBP').replace('usd dollar', 'USD').replace('aud dollar', 'AUD').replace('dollar', 'USD')
	if s[:4] in ('EUR ', 'GBP ', 'USD ', 'AUD '):
		currency = s[:3]
		min = max = s[4:].replace(',', '')
		return min, max, currency, salary_period
	else:
		return None, None, s.upper(), salary_period

def parse_job_postings(path):
	#f = pd.read_json(path, lines=True)

	N = 91902

	position_types = {}

	companies = {}
	job_postings = []
	sources = set()

	pbar = tqdm(total=N, desc='Processing')
	for line in open(path, 'r'):
		d = json.loads(line)
		pbar.update(1)

		job_posting_id = d['_id']['$oid']
		name = d['name'].replace('&amp;', '&')
		date_created = int(d['dateCreated']['$date']['$numberLong'])

		address = filter_address(d)
		if 'countryCode' in address:
			cc = address['countryCode']
			if cc in ('gb', 'ma', 'us', 'id', 'ca'):
				continue
			del address['countryCode']
		if 'country' in address and address['country'] not in ('Ireland', 'Irland', 'Irlande', 'global.country.IE', 'Ierland',
			'ie', ' IL', ' Irlande', 'IE', ' Ireland'):
			continue
		if 'country' in address:
			del address['country']

		salary = None, None, None, None
		if 'salary' in d and d['salary'] is not None:
			if 'text' not in d['salary']:
				pass
			else:
				s = d['salary']['text'].strip()
				if s in ('null', '(EUR per HOUR)', '(EUR per YEAR)', '(EUR per DAY)', '(per)', '(GBP per YEAR)', '(EUR per)',
					 '(EUR per UNKNOWN)', 'remunDescription', '(GBP per)', '(GBP per DAY)', '(UNKNOWN per)', '(USD per)',
					 'Salary negotiable', 'Competitive salary', '(per UNKNOWN)'):
					pass
				else:
					salary = parse_salary(s)

		source = d["source"]
		sources.add(source)

		i = len(job_postings)
		job_posting = {
			'job_posting_id': i + 1,
			'name': name,
			'date_created': date_created,
			'salary_min': salary[0],
			'salary_max': salary[1],
			'salary_currency': salary[2],
			'salary_period': salary[3],
			'source': source,
			'city': address.get('city'),
			'post_code': address.get('post_code')
		} | filter_tags(d)
		job_postings.append(job_posting)

		company_source = d['orgCompany']['source']
		company_name = d['orgCompany']['name'].strip()
		if 'idInSource' in d['orgCompany'] and d['orgCompany']['idInSource'] is not None and len(d['orgCompany']['idInSource'].strip()) > 0:
			company_id = d['orgCompany']['idInSource'].strip()
		else:
			company_id = company_name
		company_name = company_name.replace('&amp;', '&')

		if company_source in companies:
			if company_id in companies[company_source]:
				companies[company_source][company_id]['job_postings'].append(i)
			else:
				companies[company_source][company_id] = {
					'name': company_name,
					'job_postings': [i]
				}
		else:
			companies[company_source] = {
				company_id: {
					'name': company_name,
					'job_postings': [i]
				}
			}

	if False:
		print(f'#job_postings = {len(job_postings)}')
		print(f'#companies = {len(companies)}')
		for company_source in companies:
			print(f'# companies[{company_source}] = {len(companies[company_source])}')
			for company_id in companies[company_source]:
				l = len(companies[company_source][company_id]['job_postings'])
				if l > 5:
					print(f'# companies[{company_source}][{company_id}][job_postings] = {l}')

	all_company_names = {}
	for csrc in companies:
		for company in companies[csrc].values():
			n = company['name']
			if n in all_company_names:
				all_company_names[n] += 1
			else:
				all_company_names[n] = 1

	i = 1
	csvfile = open('companies.csv', 'w', newline='')
	writer = csv.DictWriter(csvfile, fieldnames=['company_id', 'name'])
	writer.writeheader()
	pbar = tqdm(total=len(all_company_names), desc='Writing companies')
	for company_name, cnt in all_company_names.items():
		writer.writerow({'company_id': i, 'name': company_name})
		for csrc in companies:
			for cid, company in companies[csrc].items():
				if company['name'] == company_name:
					for job in company['job_postings']:
						job_postings[job]['company_id'] = i
		pbar.update(1)
		i += 1
	del writer
	csvfile.close()

	csvfile = open('job_postings.csv', 'w', newline='')
	fieldnames = ['job_posting_id', 'name', 'company_id', 'date_created', 'salary_min',
		      'salary_max', 'salary_currency', 'salary_period', 'city', 'post_code', 'source']
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()
	pbar = tqdm(total=len(job_postings), desc='Writing job postings')
	for job in job_postings:
		writer.writerow({k: v for k, v in job.items() if k in fieldnames})
		pbar.update(1)
	del writer
	csvfile.close()

	T = {
		'categories': 'category',
		'skills': 'skill',
		'requirements': 'requirement',
		'industries': 'industry'
	}
	for table, name in T.items():
		csvfile = open(f'{table}.csv', 'w', newline='')
		writer = csv.DictWriter(csvfile, fieldnames=['job_posting_id', name])
		writer.writeheader()
		pbar = tqdm(total=len(job_postings), desc=f'Writing {table}')
		for job in job_postings:
			jid = job['job_posting_id']
			for value in job[table]:
				writer.writerow({'job_posting_id': jid, name: value})
		del writer
		csvfile.close()

	#for k, v in position_types.items():
	#	if len(v) > 5:
	#		v = set(list(v)[:5])
	#	print(f'{k}: {v}')

parse_job_postings('techmap-jobs-export-all.json')
