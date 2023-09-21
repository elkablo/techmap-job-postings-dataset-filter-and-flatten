# Techmap Job Postings from Ireland datasets flatten utility

This repository contains code I wrote to filter and flatten the **Techmap Job Postings from Ireland** Kaggle datasets:
* [Job Postings from Ireland (October 2020)](https://www.kaggle.com/datasets/techmap/job-postings-ireland-october-2020)
* [Job Postings from Ireland (October 2021)](https://www.kaggle.com/datasets/techmap/job-postings-ireland-october-2021)
* [Job Postings from Ireland (October 2022)](https://www.kaggle.com/datasets/techmap/job-postings-ireland-october-2022)

## Usage

Download the above mentioned datasets and unpack the files `techmap-jobs-export-2020-10_ie.json`,
`techmap-jobs-export-2021-10_ie.json` and `techmap-jobs-export-2022-10_ie.json` into the directory
containing the Python scripts.

Then purge the `html` and `text` fields from the JSON files and create one file containing all records with
```
./purge-unused.py >techmap-jobs-export-all.json
```

Afterwards generate CSV files that can be imported to SQL:
```
./filter-and-flatten-to-csv.py
```

