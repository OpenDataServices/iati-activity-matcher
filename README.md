# Activity Matching demo using CGIAR and BMGF data

To view the output of this repo, see https://docs.google.com/spreadsheets/d/1uOqdLlDJGnIBIB1egFdUBFUMSVMOo77UiS-9FhX5mJ8/edit?usp=sharing

## WARNING: Assumptions

Currently this makes a bunch of assumptions that happen to be true of these specific datasets:
* CGIAR (the recipient) only has 1 transaction per activity
* All values are USD
* Filenames, participating org refs and CRS Channel codes are all hardcoded

## Usage

```
python3 -m venv .ve
source .ve/bin/activate
pip install -r requirements.txt
python match.py
```
