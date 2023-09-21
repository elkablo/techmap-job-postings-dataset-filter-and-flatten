#!/usr/bin/env python

# This script takes the reconds from JSON files
#   techmap-jobs-export-2020-10_ie.json
#   techmap-jobs-export-2021-10_ie.json
#   techmap-jobs-export-2022-10_ie.json
# removes the 'html' and 'text' field from each record, and prints the records
# in JSON format.
#
# The 'html' and 'text' field contain data we are not interested in, so dropping
# them makes further transformations a little bit faster.
#
# Example usage:
#   ./purge-unused.py >techmap-jobs-export-all.json

import json

def purge_job_postings(path):
	for line in open(path, 'r'):
		data = json.loads(line)

		if 'text' in data:
			del data['text']
		if 'html' in data:
			del data['html']

		print(json.dumps(data, separators=(',', ':')))

purge_job_postings('techmap-jobs-export-2020-10_ie.json')
purge_job_postings('techmap-jobs-export-2021-10_ie.json')
purge_job_postings('techmap-jobs-export-2022-10_ie.json')
