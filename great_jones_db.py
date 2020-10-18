import psycopg2 as pgql
import datetime

#function for data type parser, doesn't handle all (e.g. timestamp), None is later varchar
def type_parser(v):
    data_type = ""

    if type(v) == str:
        data_type = "varchar"
    elif type(v) == int:
        data_type = "int"
    elif type(v) == "float":
        data_type = "float"
    elif type(v) == bool:
        data_type = "bool"
    else:
        data_type = "None"
    
    return data_type

#refer to metadata.txt, creates a dictionary with {tableA: {{colA: type}, {colB: type}, etc.}, etc.}
def table_metadata_dict (js, table_name = 'main', table_dict = {'main':{}}):

    for k, v in js.items():
        if type(v) == dict:
            table_metadata_dict(v, k, table_dict)
        else:
            if type(v) == list:
                if k not in table_dict:
                    table_dict[k] = {}

                for item in v:
                    if type(item) == dict:
                        for item_k, item_v in item.items():
                            if item_k not in table_dict[k]:
                                table_dict[k][item_k] = type_parser(item_v)
                            else:
                                if type_parser(item_v) != "None":
                                    table_dict[k][item_k] = type_parser(item_v)                          

            else:
                if table_name not in table_dict:
                    table_dict[table_name] = {k:type_parser(v)}
                else:
                    if k not in table_dict[table_name]:
                        table_dict[table_name][k] = type_parser(v)
                    else:
                        if type_parser(v) != "None":
                            table_dict[table_name][k] = type_parser(v)

    return table_dict

#checks if table/column exists in great_jones_db
def check_exists_db (table_name, column_name = ""):
    conn = pgql.connect(
        dbname = "great_jones_db",
        user = "postgres",
        host = "localhost",
        password = "7394",
        connect_timeout = 30
    )

    sql_string = ""
    if column_name == "":
        #for subsequent loads if new table arrives
        sql_string = "select table_name from information_schema.tables where table_name = '{0}';".format(table_name)
    else:
        #for subsequent loads if new column arrives
        #performance opportunity here, perhaps better to load a dictionary at the very beginning instead of querying db like this
        sql_string = "select table_name from information_schema.columns where table_name = '{0}' and column_name = '{1}';".format(table_name, column_name)

    cur = conn.cursor()
    cur.execute(sql_string)

    if bool(cur.rowcount):
        return True
    else:
        return False

#simple execute DDL/DML against db
def modify_table (table_sql):
    conn = pgql.connect(
        dbname = "great_jones_db",
        user = "postgres",
        host = "localhost",
        password = "7394",
        connect_timeout = 30
    )

    cur = conn.cursor()
    cur.execute(table_sql)
    conn.commit()

#get data type of column, opportunity to improve -- doesn't have to be this way
#perhaps load once to dict, instead of querying like this
def get_db_data_type (table_name, column_name):
    conn = pgql.connect(
        dbname = "great_jones_db",
        user = "postgres",
        host = "localhost",
        password = "7394",
        connect_timeout = 30
    )

    cur = conn.cursor()
    cur.execute("select data_type from information_schema.columns where table_name = '{0}' and column_name = '{1}'".format(table_name, column_name))

    row = cur.fetchone()[0]

    return row

#creates tables if not exists, alters tables if new columns found
def generate_tables(metadata):
    for tbl, tblc in metadata.items():
        sql_string = ""
        if not check_exists_db(tbl):
            sql_string = "create table {0} (".format(tbl)
            for col_name, col_type in tblc.items():
                #print (col_name, col_type)
                if col_type in ("varchar","None"):
                    col_type = "varchar(255)"
                
                sql_string += col_name + " " + col_type + ","

            sql_string = sql_string[:-1] + ");"

            modify_table(sql_string)

        else:
            for col, col_type in tblc.items():
                if col_type in ("varchar","None"):
                    col_type = "varchar(255)"
                if not check_exists_db(tbl, col):
                    modify_table("alter table {0} add {1} {2};".format(tbl, col, col_type))


# recursive function to load json file, doesn't handle updates yet
def load_json_data(js, table_name = 'main'):

    sql_insert_string = "insert into {0} (".format(table_name)
    sql_values_string = "values ("
    sql_string = ""

    for k, v in js.items():
        if type(v) == dict:
            #if value is dictionary, recurse through, load to respective table
            load_json_data(v, k)
        else:
            #if value is not a list, load to current table
            if type(v) != list:
                sql_insert_string += k + ","
                value = ""
                if v == None:
                    value = "null"
                else:
                    #data_type = get_db_data_type(table_name, k)
                    data_type = type_parser(v)

                    if data_type == "varchar":#"character varying":
                        value = "'" + str(v) + "'"
                    else:
                        value = str(v)

                sql_values_string += value + ","
            else:
                #if value is not a list, iterate through items and load to respective table
                for item in v:
                    if type(item) == dict:
                        l_insert_string = "insert into {0} (".format(k)
                        l_value_string = "values ("
                        for item_k, item_v in item.items():
                            l_insert_string += item_k + ","
                            value = ""
                            if item_v == None:
                                value = "null"
                            else:
                                data_type = type_parser(item_v)#get_db_data_type(k, item_k)

                                if data_type == "varchar": #"character varying":
                                    value = "'" + str(item_v) + "'"
                                else:
                                    value = str(item_v)

                            l_value_string += value + ","
                        
                        l_string = l_insert_string[:-1] + ") " + l_value_string[:-1] + ");"
                        #print(l_string)
                        modify_table(l_string)
    
    
    sql_string = sql_insert_string[:-1] + ") " + sql_values_string[:-1] + ");"

    #print (sql_string)
    #execute inserts to db
    modify_table(sql_string)