Environment
    1. python application to process json, built using Visual Studio Code
    2. Installed local copy of postgres on windows
    3. pgAdmin used for querying scripts

Specifications
    1. Processing json files
        a. great_jones_app.py main script
        b. great_jones_db.py is imported into main script
            1. parses json dict to create a metadata dictionary comprising of structure {table: {{column: column_type}, .. }, ..}
            2. generate_tables
                1. for each key (table):value (columns) pair, creates an executable "create table" statement if new table is found
                2. for each key (table):value (columns) pair, creates an executable "alter table" statement if new column is found 
            3. load_json_data to tables. 
                1. DOES NOT handle timestamp types (needs improvement) -- will need is-instance checks
                2. DOES NOT update records to table (needs improvement)
    2. Analytical queries
        a. analytic_queries.sql 
            1. Creates temp tables with distinct, ideally we would need a logical/physical DW with it's own ETL/ELT pipeline
            2. uses the temp tables to do joins
