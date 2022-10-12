# Project: FUNCATE / Frel
# author: filipe.lopes@funcate.org.br
# date: 11/10/2022
# Description: conecta a banco de dados do postgres através do console do QGis


import psycopg2

def db_writer(vals):

    # Connect to an existing database
    conn = psycopg2.connect(dbname='ta_qgis_python', user='postgres', password='postgres', host='localhost', port='5432')

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a command: this creates a new table
    # cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")

    # Pass data to fill a query placeholders and let Psycopg perform
    # the correct conversion (no more SQL injections!)


    cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)",(vals))


    # Query the database and obtain data as Python objects
    cur.execute("SELECT * FROM test;")
    cur.fetchone()


    # Make the changes to the database persistent
    conn.commit()


    # Close communication with the database
    cur.close()
    conn.close()


data_to_insert = (24,'teste')


db_writer(data_to_insert)

