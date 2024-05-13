# IMPORTS
import duckdb
import pandas as pd
import streamlit as st


# QUERY
# Build the query 
query_write = """
    INSERT INTO {table_name} ({columns})
    VALUES {values};
"""


# MAIN FUNCTIONS
def read_df_from_db(con, query_read):
    """Summary: read data from database

    Args:
        con (duckdb object): duckdb-sqlite connection
        query_read (string): query used to read data

    Returns:
        df (dataframe): data readed
    """
    df = con.execute(query_read).df()
    return df


def write_df_to_db(con, df, table_name, query_write):
    """Summary: write data to database

    Args:
        con (duckdb object): duckdb-sqlite connection
        df (dataframe): dataframe to write in the database
        table_name (string): name of the table in which the data will be written
        query_write (string): query used to write data
    """
    # Format dates in the DataFrame
    #df = format_dates_in_df(df)
    
    # Get the column names of the DataFrame columns
    columns = ','.join(df.columns)
    
    # Iterate over each row of the DataFrame and insert it into the database.
    for index, row in df.iterrows():
        # Extract values from a row
        values = tuple(row)
        # Build the writing query
        query = query_write.format(table_name=table_name, columns=columns, values=values)
        con.execute(query)

