import great_jones_db, json

# function to read json file
def js_r(filename):
   with open(filename) as f_in:
       return(json.load(f_in))


#read json to dict
my_data = js_r("sample.json")

#create db tables based on my_data dict
great_jones_db.generate_tables(great_jones_db.table_metadata_dict(my_data))

#load tables
great_jones_db.load_json_data(my_data)




