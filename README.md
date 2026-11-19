# seattle-chicago-permit-analysis
An analysis of building permit issuance and processing times in Seattle and Chicago (2021–2024).
## Project Overview

This project compares new-construction permit issuance and processing times in Seattle and Chicago from 2021 to 2024.

## Research Objectives

- Compare annual and monthly new-construction permit issuance trends.
- Compare permit issuance rates per 100,000 residents.
- Explore differences in application-to-issuance processing times.
- Examine how outliers and zero-day records affect the results.

## Datasets

The project uses Seattle and Chicago building permit data and 2024 ACS population estimates. Dataset sources are documented in `data/sources.csv`.

## Project Files

- `eda_analysis.py`: Data cleaning, analysis, and visualizations.
- `test_eda.py`: Tests for analysis functions.
- `data/`: Input datasets and source information.
- `figures/`: EDA visualizations.

## Running the Project

The project requires Python, pandas, and matplotlib.

Run the analysis:

```bash
python3 eda_analysis.py
```

Run the tests:

```bash
python3 test_eda.py
```

Check code quality:

```bash
python3 -m flake8 eda_analysis.py test_eda.py
```

## Limitations

Processing-time definitions may differ between Seattle and Chicago. In addition, Chicago contains many zero-day processing records, which affect the interpretation of annual median processing times.
