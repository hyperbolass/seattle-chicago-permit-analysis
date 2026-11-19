import pandas as pd
import matplotlib.pyplot as plt


def filter_seattle(data):
    """Keep Seattle new-building permits issued from 2021 through 2024."""
    seattle_filter = (
        (data['issueddate'] >= '2021-01-01') &
        (data['issueddate'] < '2025-01-01') &
        (data['permittypemapped'] == 'Building') &
        (data['permittypedesc'] == 'New')
    )
    return data.loc[seattle_filter]


def filter_chicago(data):
    """Keep Chicago new-construction permits issued in 2021-2024."""
    chicago_filter = (
        (data['issue_date'] >= '2021-01-01') &
        (data['issue_date'] < '2025-01-01') &
        (data['permit_type'] == 'PERMIT - NEW CONSTRUCTION')
    )
    return data.loc[chicago_filter]


def missing_summary(data):
    """Return the missing-value count and percentage for each column."""
    missing = data.isnull()
    missing_count = missing.sum()
    missing_rate = missing.mean()
    missing_percent = missing_rate * 100
    return missing_count, missing_percent


def valid_dates(data, date_column):
    """Keep rows where the specified application date is not missing."""
    valid_mask = data[date_column].notnull()
    return data.loc[valid_mask]


def yearly_count(data, date_column):
    """Return the number of permits issued in each year."""
    data = data.copy()
    dates = pd.to_datetime(data[date_column])
    data['year'] = dates.dt.year
    grouped = data.groupby('year')
    counts = grouped.size()
    return counts


def monthly_count(data, date_column):
    """Return the number of permits issued in each month."""
    data = data.copy()
    dates = pd.to_datetime(data[date_column])
    data['year'] = dates.dt.year
    data['month'] = dates.dt.month
    grouped = data.groupby(['year', 'month'])
    counts = grouped.size()
    return counts


def plot_monthly_counts(seattle_monthly, chicago_monthly):
    """Plot monthly permit counts for Seattle and Chicago."""
    months = range(1, 49)
    plt.figure()
    plt.plot(months, seattle_monthly, label='Seattle')
    plt.plot(months, chicago_monthly, label='Chicago')
    plt.title('Monthly New Construction Permits (2021-2024)')
    plt.xlabel('Month (Jan 2021 = 1)')
    plt.ylabel('Number of Permits')
    plt.legend()
    plt.savefig('monthly_permits.png')
    plt.close()


def merge_population(yearly_counts, population, city):
    """Merge annual permit counts with city population."""
    yearly_table = pd.DataFrame({
        'year': yearly_counts.index,
        'permits': yearly_counts.values,
        'city': city
    })
    merged = yearly_table.merge(population, on='city')
    merged['per_100k'] = (
        merged['permits'] / merged['population'] * 100000
    )
    return merged


def plot_per_100k(seattle_merged, chicago_merged):
    """Plot annual permits per 100,000 residents using merged data."""
    plt.figure()
    plt.plot(
        seattle_merged['year'], seattle_merged['per_100k'],
        label='Seattle'
    )
    plt.plot(
        chicago_merged['year'], chicago_merged['per_100k'],
        label='Chicago'
    )
    plt.title('New Construction Permits per 100,000 Residents')
    plt.xlabel('Year')
    plt.xticks([2021, 2022, 2023, 2024])
    plt.ylabel('Permits per 100,000 Residents')
    plt.legend()
    plt.savefig('permits_per_100k.png')
    plt.close()


def processing_days(data, applied_column, issued_column):
    """Calculate valid application-to-issue durations in days."""
    data = data.copy()
    applied = pd.to_datetime(data[applied_column], errors='coerce')
    issued = pd.to_datetime(data[issued_column], errors='coerce')
    difference = issued - applied
    data['processing_days'] = difference.dt.days
    valid = (
        data['processing_days'].notnull() &
        (data['processing_days'] >= 0)
    )
    return data.loc[valid]


def plot_processing_time(data, city, filename):
    """Plot the distribution of processing days."""
    plt.figure()
    plt.hist(data['processing_days'], bins=30)
    plt.title(city + ' Processing Time Distribution')
    plt.xlabel('Processing Time (Days)')
    plt.ylabel('Number of Permits')
    plt.savefig(filename)
    plt.close()


def trim_outliers(data):
    """Remove processing times above the 99th percentile."""
    threshold = data['processing_days'].quantile(0.99)
    trimmed = data.loc[data['processing_days'] <= threshold]
    return trimmed


def yearly_validity_summary(data, date_column):
    """Summarize processing times and zero-day records by year."""
    data = data.copy()

    dates = pd.to_datetime(data[date_column])
    data['year'] = dates.dt.year
    data['is_zero'] = data['processing_days'] == 0

    grouped = data.groupby('year')

    summary = pd.DataFrame({
        'count': grouped['processing_days'].count(),
        'median_days': grouped['processing_days'].median(),
        'zero_day_count': grouped['is_zero'].sum()
    })

    summary['zero_day_percent'] = (
        summary['zero_day_count'] / summary['count'] * 100
    )

    return summary


def main():
    """Read the CSV files, analyze permits, and save results."""
    seattle = pd.read_csv('seattle_permits.csv')
    chicago = pd.read_csv('chicago_permits.csv', dtype={'id': str})
    population = pd.read_csv('population_acs2024.csv')

    seattle_new = filter_seattle(seattle)
    chicago_new = filter_chicago(chicago)

    seattle_missing_count, seattle_missing_percent = missing_summary(
        seattle_new
    )
    chicago_missing_count, chicago_missing_percent = missing_summary(
        chicago_new
    )
    pd.DataFrame({
        'missing_count': seattle_missing_count,
        'missing_percent': seattle_missing_percent
    }).to_csv('seattle_missing_summary.csv')
    pd.DataFrame({
        'missing_count': chicago_missing_count,
        'missing_percent': chicago_missing_percent
    }).to_csv('chicago_missing_summary.csv')

    # Count issued permits by year and by month.
    seattle_yearly = yearly_count(seattle_new, 'issueddate')
    chicago_yearly = yearly_count(chicago_new, 'issue_date')
    seattle_monthly = monthly_count(seattle_new, 'issueddate')
    chicago_monthly = monthly_count(chicago_new, 'issue_date')
    plot_monthly_counts(seattle_monthly, chicago_monthly)

    seattle_merged = merge_population(
        seattle_yearly, population, 'Seattle'
    )
    chicago_merged = merge_population(
        chicago_yearly, population, 'Chicago'
    )
    plot_per_100k(seattle_merged, chicago_merged)
    seattle_merged.to_csv('seattle_yearly_summary.csv', index=False)
    chicago_merged.to_csv('chicago_yearly_summary.csv', index=False)

    seattle_valid = valid_dates(seattle_new, 'applieddate')
    chicago_valid = valid_dates(chicago_new, 'application_start_date')
    seattle_processed = processing_days(
        seattle_valid, 'applieddate', 'issueddate')
    chicago_processed = processing_days(
        chicago_valid, 'application_start_date', 'issue_date'
    )
    seattle_validity = yearly_validity_summary(
        seattle_processed, 'issueddate'
    )
    chicago_validity = yearly_validity_summary(
        chicago_processed, 'issue_date'
    )
    seattle_validity.to_csv('seattle_validity.csv')
    chicago_validity.to_csv('chicago_validity.csv')

    # Compare Chicago medians with and without zero-day records.
    chicago_positive = chicago_processed.loc[
        chicago_processed['processing_days'] > 0
    ]
    chicago_positive_summary = yearly_validity_summary(
        chicago_positive, 'issue_date'
    )
    chicago_comparison = pd.DataFrame({
        'original_median': chicago_validity['median_days'],
        'positive_median': chicago_positive_summary['median_days'],
        'zero_day_percent': chicago_validity['zero_day_percent']
    })
    print(chicago_comparison)
    chicago_comparison.to_csv('chicago_comparison.csv')
    seattle_summary = seattle_processed['processing_days'].describe()
    chicago_summary = chicago_processed['processing_days'].describe()
    seattle_summary.to_csv('seattle_processing_summary.csv')
    chicago_summary.to_csv('chicago_processing_summary.csv')
    plot_processing_time(
        seattle_processed, 'Seattle', 'seattle_processing.png'
    )
    plot_processing_time(
        chicago_processed, 'Chicago', 'chicago_processing.png'
    )

    seattle_trimmed = trim_outliers(seattle_processed)
    chicago_trimmed = trim_outliers(chicago_processed)
    seattle_trimmed['processing_days'].describe().to_csv(
        'seattle_trimmed_summary.csv'
    )
    chicago_trimmed['processing_days'].describe().to_csv(
        'chicago_trimmed_summary.csv'
    )
    plot_processing_time(
        seattle_trimmed, 'Seattle Trimmed', 'seattle_trimmed.png'
    )
    plot_processing_time(
        chicago_trimmed, 'Chicago Trimmed', 'chicago_trimmed.png'
    )


if __name__ == '__main__':
    main()
