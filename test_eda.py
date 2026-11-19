
"""Small-data tests for the Seattle and Chicago permit EDA."""

import pandas as pd
import eda_analysis


def test_filter_seattle():
    """Keep only new Seattle building permits in 2021-2024."""
    data = pd.DataFrame({
        'permitnum': ['A', 'B', 'C', 'D'],
        'issueddate': [
            '2021-01-01', '2024-12-31', '2023-05-10', '2025-01-01'
        ],
        'permittypemapped': ['Building'] * 4,
        'permittypedesc': ['New', 'New', 'Addition/Alteration', 'New']
    })
    result = eda_analysis.filter_seattle(data)
    assert len(result) == 2
    assert list(result['permitnum']) == ['A', 'B']


def test_filter_chicago():
    """Keep only new Chicago construction permits in 2021-2024."""
    data = pd.DataFrame({
        'id': ['A', 'B', 'C', 'D'],
        'issue_date': [
            '2021-01-01', '2024-12-31', '2023-05-10', '2025-01-01'
        ],
        'permit_type': [
            'PERMIT - NEW CONSTRUCTION',
            'PERMIT - NEW CONSTRUCTION',
            'PERMIT - SIGNS',
            'PERMIT - NEW CONSTRUCTION'
        ]
    })
    result = eda_analysis.filter_chicago(data)
    assert len(result) == 2
    assert list(result['id']) == ['A', 'B']


def test_missing_summary():
    """Count missing values and calculate missing percentages."""
    data = pd.DataFrame({
        'applieddate': ['2021-01-01', None, '2021-03-01', '2021-04-01'],
        'issueddate': ['2021-01-02', '2021-02-02', None, '2021-04-02']
    })
    counts, percentages = eda_analysis.missing_summary(data)
    assert counts['applieddate'] == 1
    assert counts['issueddate'] == 1
    assert percentages['applieddate'] == 25
    assert percentages['issueddate'] == 25


def test_valid_dates():
    """Remove rows without a requested application date."""
    data = pd.DataFrame({
        'id': ['A', 'B', 'C'],
        'applieddate': ['2021-01-01', None, '2021-03-01']
    })
    result = eda_analysis.valid_dates(data, 'applieddate')
    assert len(result) == 2
    assert list(result['id']) == ['A', 'C']


def test_yearly_count():
    """Count the number of permits in each year."""
    data = pd.DataFrame({
        'issueddate': [
            '2021-01-01', '2021-05-10', '2022-03-01',
            '2022-06-15', '2022-09-20'
        ]
    })
    result = eda_analysis.yearly_count(data, 'issueddate')
    assert result[2021] == 2
    assert result[2022] == 3


def test_monthly_count():
    """Count by year and month without mixing different years."""
    data = pd.DataFrame({
        'issueddate': [
            '2021-01-01', '2021-01-20', '2021-02-01', '2022-01-01'
        ]
    })
    result = eda_analysis.monthly_count(data, 'issueddate')
    assert result[(2021, 1)] == 2
    assert result[(2021, 2)] == 1
    assert result[(2022, 1)] == 1
    assert len(result) == 3


def test_processing_days():
    """Keep valid, nonnegative durations and exclude invalid dates."""
