# IMPORTS
import duckdb
import pandas as pd


# AUXILIARY FUNCTIONS
# create a connection to a file called 'file.db'
con = duckdb.connect("G:/Mi unidad/Silver/lab_db.db")

# QUERY
query_read = """
    SELECT
        --tra.index_id,
        cut.cut,
        col.color,
        cla.clarity,
        tra.price,
        cit.city,
        tra.carat,
        dim.depth,
        dim.table,
        dim.x,
        dim.y,
        dim.z
    FROM diamonds_properties AS pro
    JOIN diamonds_cut AS cut ON pro.cut_id = cut.cut_id
    JOIN diamonds_color AS col ON pro.color_id = col.color_id
    JOIN diamonds_clarity AS cla ON pro.clarity_id = cla.clarity_id
    JOIN diamonds_transactional as tra ON pro.index_id = tra.index_id
    JOIN diamonds_city AS cit ON tra.city_id = cit.city_id
    JOIN diamonds_dimensions AS dim ON pro.index_id = dim.index_id
    """


query_write = """
    --INSERT INTO customers (name, address) VALUES (%s, %s)
    INSERT INTO temp 
    SELECT nextval('serial'), Name, Age 
    FROM df
    """


# MAIN FUNCTIONS
def read_db(con, query_read):
    df = con.execute(query_read).df()
    return df


def write_db(con, df, query_write):
    con.execute(query_write, df)



# CREATE DATABASE CODE
