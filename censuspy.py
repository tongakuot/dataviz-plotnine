# Importing south sudan census dataset
url = 'https://raw.githubusercontent.com/tongakuot/python_tutorials/main/00_data/ss_2008_census_data_raw.csv'

# Write a function for cleaning and transforming South Sudan census data
def tweak_census(df, grouping_cols, condition):
    """
    Cleans and transforms South Sudan census data.

    This function processes a DataFrame containing South Sudan census data by:
    - Selecting relevant columns
    - Renaming and recategorizing age groups
    - Filtering rows based on a given condition
    - Handling null values
    - Renaming columns for clarity
    - Adding a new column to categorize regions
    - Grouping data by specified columns
    - Aggregating population counts
    - Sorting the results in descending order of total population

    Parameters:
    df (pl.DataFrame): The input DataFrame containing South Sudan census data.
    grouping_cols (list): A list of column names to group by.
    condition (pl.Expr): A condition to filter the DataFrame.

    Returns:
    pl.DataFrame: A transformed DataFrame with aggregated population counts, grouped by specified columns, and sorted by total population.
    """
    import polars as pl
    import polars.selectors as cs
    
    age_mappings = {'0 to 4':'0-14', 
                '5 to 9':'0-14', 
                '10 to 14':'0-14', 
                '15 to 19':'15-24', 
                '20 to 24':'15-24', 
                '25 to 29':'25-34', 
                '30 to 34':'25-34', 
                '35 to 39':'35-44', 
                '40 to 44':'35-44',
                '45 to 49':'45-54', 
                '50 to 54':'45-54',
                '55 to 59':'55-64',
                '60 to 64':'55-64',
                '65+':'65 and above'
               }
 
    return (
        df
        .select(cs.ends_with('Name'), '2008')
        .with_columns(
            gender=pl.col('Variable Name').str.replace_many(['Population, ', ' (Number)'], ''),
            category=pl.col('Age Name').replace(age_mappings)
        )
        .select(pl.col('*').exclude(['Variable Name', 'Age Name']))
        .filter(condition)
        .drop_nulls()
        .rename({'Region Name': 'state', '2008': 'population'})
        .with_columns(former_region=pl.when(pl.col('state').is_in(['Upper Nile', 'Unity', 'Jonglei']))
                                    .then(pl.lit('Greater Upper Nile'))
                                    .when(pl.col('state').str.ends_with('Equatoria'))
                                    .then(pl.lit('Greater Equatoria'))
                                    .when(pl.col('state').str.contains('Ghazal'))
                                    .then(pl.lit('Greater Bahr el Ghazal'))
                                    .otherwise(pl.lit('Greater Bahr el Ghazal'))
        )
        .group_by(grouping_cols)
        .agg(total=pl.col('population').sum())
        .sort('total', descending=True)
    )   
    
    
# Summarization function
def summarize_census(df, cols):
    """
    Summarizes the South Sudan 2008 census data by grouping and aggregating the specified columns.
    This function groups the input DataFrame by the specified columns, calculates the sum of the 'total' column 
    for each group, sorts the groups in descending order based on the summed totals, and adds a new column 'labels' 
    that represents the total in millions, rounded to two decimal places.
    Parameters:
    df (pl.DataFrame): The input DataFrame containing the census data.
    cols (list): A list of column names by which to group the data.
    Returns:
    pl.DataFrame: A DataFrame with the grouped and aggregated data, sorted in descending order by 'total', 
                  and a new 'labels' column with the totals in millions.
    """
    import polars as pl
    return (
        df
        .group_by(cols)
        .agg(total=pl.col('total').sum())
        .sort('total', descending=True)
        .with_columns(labels=(pl.col('total') / 1_000_000).round(2))
    )
