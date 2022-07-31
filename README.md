# IATI Activity Matcher

Linking provider and recipient activities in the IATI dataset by matching on title text similarity.

There's a writeup of the work in this repo at https://docs.google.com/document/d/1NiNNhlqU3E0uqEjX8VNmIFNWgJSz50idPx_9QG0Awdo/edit

## WARNING: Assumptions

Currently this makes a bunch of assumptions that happen to be true of certain datasets:
* Only version 2.01 and later data is supported
* There is no currency conversion. Transactions must be in the same currency to be matched by value.
* If there are multiple titles texts, they are concatenated. This means multilingual titles may not match well.

## Installation

```
git clone https://github.com/OpenDataServices/iati-activity-matcher.git
cd iati-activity-matcher
python3 -m venv .ve
source .ve/bin/activate
pip install -r requirements.txt
```

### Example usage


First we fetch the entire IATI dataset, and process it into some intermediate JSON files, see `out/*.json` (this is required to run `match.py`):

```
python extract_participating_org.py
```

This downloads the entire IATI dataset, so needs ~12GB of space, but the download is compressed, so needs (<1GB currently).

We can produce a CSV to summarise this (see `out/linked_orgs.csv`, or [this example](https://docs.google.com/spreadsheets/d/1wKR06_mLipAmeIb8W7Q_uRHHajry0rRPTFF1Qn_muZc/edit#gid=1509188840)):

```
python make_org_csv.py
```

Run `match.py` with a recipient and funder org ref:

```
python match.py --recipient-org-ref XM-DAC-47015 --funder-org-ref DAC-1601
```

The output is in `out/matches.csv`.

Or just specifiy a recipient org to match with all relevant funder orgs:

```
python match.py --recipient-org-ref XM-DAC-47015
```

The output is in `out/matches.csv`.

For an example of this output, see https://docs.google.com/spreadsheets/d/1kc9SttmUR3xo-JNVvOijBoa8qyPP_eh9ughbwm7N6tw/edit#gid=0


### Tests

Run:

```
pip install -r requirements_dev.txt
pytest
```
