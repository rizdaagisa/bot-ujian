import sys, subprocess, os
from io import StringIO
import pandas as pd
from meza import io
VERBOSE = True
path = os.path.dirname(__file__)
# path = path.replace("\\","/")
# print("/KD021216.MDB")
def mdb_to_pandas():
    subprocess.call(["mdb-schema", "KD021216.MDB", "mysql"])
    # Get the list of table names with "mdb-tables"
    table_names = subprocess.Popen(["mdb-tables", "-1", database_path],
                                   stdout=subprocess.PIPE).communicate()[0]
    tables = table_names.splitlines()
    sys.stdout.flush()
    # Dump each table as a stringio using "mdb-export",
    out_tables = {}
    for rtable in tables:
        table = rtable.decode()
        if VERBOSE: print('running table:',table)
        if table != '':
            if VERBOSE: print("Dumping " + table)
            contents = subprocess.Popen(["mdb-export", database_path, table],
                                        stdout=subprocess.PIPE).communicate()[0]
            temp_io = StringIO(contents.decode())
            print(table, temp_io)
            out_tables[table] = pd.read_csv(temp_io)
    return out_tables

records = io.read('KD021216.MDB') # only file path, no file objects
print(next(records))