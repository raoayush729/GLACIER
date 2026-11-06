# in this file i am creating a ladder of function -
# 1 function will be passed to another then that to another and so on




import pandas as pd 
import mysql.connector     # mysql.connector is a Python library that allows Python code to establish a connection to a MySQL server and communicate with it.
from tools.dataset_management import DatasetManager
from sqlalchemy import create_engine    # create_engine function from SQLAlchemy library. Its job is to create a SQLAlchemy Engine.
from sqlalchemy.engine import URL   # This imports the URL class from SQLAlchemy's engine module.  Its job is to help you construct a properly formatted database connection URL.

# A database URL contains information such as:
# - Which database driver to use.
# - The database username.
# - The password.
# - The server's address.
# - The database name.
# You could construct a URL manually as a string, but using URL.create() is generally safer and more convenient, especially when passwords contain special characters.


# - Pandas — holds your dataset in a DataFrame and prepares it for export.
# - SQLAlchemy — manages the database connection interface and provides the engine pandas can use.
# - MySQL Connector/Python — the driver that communicates with your MySQL server.



# sqlalchemy is the name of a Python library.
# When you install SQLAlchemy, you gain access to tools that help your Python application communicate with databases.
class ExportManager:

    def __init__(self,dataset_manager):
        self.dataset_manager = dataset_manager
        print("\nExport Manager Initialised")


    def export_csv(self,file_path):
        df = self.dataset_manager.dataframe

        if df is None:
            print("No Active Dataset")
            return False

        df.to_csv(file_path,index=False)   #         # Save the DataFrame as a CSV file.         index=False → prevents Pandas from adding the DataFrame's row index as an extra CSV column.
        print(f"Dataset exported to csv {file_path}")
        return True

    def export_excel(self,file_path):
        df = self.dataset_manager.dataframe
        if df is None:
            print("No active dataset")
            return False

        df.to_excel(file_path,index=False)         #         # Save the DataFrame as an Excel file.
        print(f"Dataset exported to Excel: {file_path}")
        return True



# ===============================================================================================================================
#                                              Chain of SQL
# ===============================================================================================================================

    def connect_to_mysql(self, Host, User, Password, Database=None, Port=None):
        # Step 1: Prepare the MySQL connection settings.
        connection_settings = {
            "host": Host,
            "user": User,
            "password": Password,
            "database": Database
        }

        # Step 2: Include the port only if the user provided one.
        if Port is not None:
            connection_settings["port"] = int(Port)

        # Step 3: Connect Python to the MySQL server.
        connection = mysql.connector.connect(**connection_settings)

        # Step 4: Return the connection for further operations.
        return connection

    def create_cursor(self,connection):
        # Create a cursor used to send SQL commands to MySQL.
        cursor = connection.cursor()     # ◆ connection.cursor() — creates a cursor object that allows Python to execute SQL statements on the connected MySQL server.
        return cursor

    def create_database(self,cursor,connection,database_name):

        # Create the database if it does not already exist.
        query = f"CREATE DATABASE IF NOT EXISTS {database_name}"

        try:

            #send the create database command to sql
            cursor.execute(query)
            print(f"Database {database_name} created succesfully")

            return True
        except mysql.connector.Error as error:

           # Handle errors raised by MySQL.
            print(f"Error creating database: {error}")
            return False

    def execute_query(self,cursor,query):
        # Send the SQL query to MySQL.
        cursor.execute(query)          # cursor.execute(query) — sends a SQL statement to MySQL for execution.

        print(f"SQL query execute succesfully : {query}")
        return True     

    def commit_changes(self,connection):   # Save the changes
        # permanantly save the changes done by execute query 
        connection.commit()

        print("Changes committed succesfully")
        return True

    def close_connection(self, connection):
        # Close the connection between Python and MySQL.
        connection.close()

        print("MySQL connection closed.")

        return True 



# ---------------------------------------------------------------------------------------------------------------------------
# Mastermind of SQL 
    def create_database(self, Host, User, Password, Database_name):

        # Check whether all required inputs were provided.
        if not Host or not User or not Password or not Database_name:
            return "Please provide the host, username, password, and database name."

        connection = None
        cursor = None

        try:
            # Connect to the MySQL server without selecting a database.
            connection = self.connect_to_mysql(
                Host=Host,
                User=User,
                Password=Password,
                Database=None
            )

            # Create a cursor using our existing method.
            cursor = self.create_cursor(connection=connection)

            # Validate the database name before using it as an SQL identifier.
            if not Database_name.replace("_", "").isalnum():     # isalnum() method returns True if a string is non-empty and contains only alphanumeric characters (letters and numbers). Otherwise, it returns False.
                return "Invalid database name. Use only letters, numbers, and underscores."

            # Create the database only if it does not already exist.
            query = f"CREATE DATABASE IF NOT EXISTS `{Database_name}`"

            # Execute the SQL query using our existing helper method.
            self.execute_query(cursor, query)

            # Save the changes.
            self.commit_changes(connection)

            # Return a success message.
            return {
                "success": True,
                "message": f"Database '{Database_name}' is ready."
            }

        except mysql.connector.Error as error:

            # Handle MySQL errors.
            return {
                "success": False,
                "error": str(error)
            }

        finally:
            # Close the cursor if it was created.
            if cursor is not None:
                cursor.close()

            # Close the connection if it was established.
            if connection is not None:
                self.close_connection(connection)

    def Export_to_SQL(self,Host=None,User=None,Password=None,Database_name=None,Table_name=None):
    
            #  Check whether all required connection details were provided.
            if not Host or not User or not Password or not Database_name or not Table_name:
                return (
                    "Please provide these 4 inputs to connect to MySQL: "
                    "Username, password, host, database name and table_name."
                )
    
            # Get the active DataFrame.
            df = self.dataset_manager.dataframe
            if df is None:
                return "No Active dataset. Please load a dataset before exporting."
    
            engine = None
    
            try:
                # Create a SQLAlchemy engine for MySQL.
                connection_url = URL.create(              # Builds a URL object from the connection details.
                    drivername="mysql+mysqlconnector",    # mysql → use SQLAlchemy's MySQL dialect. mysqlconnector → use MySQL Connector/Python as the DBAPI driver.
                    username=User,
                    host=Host,
                    password=Password,
                    database=Database_name  
                )       # the URL created will be like this : mysql+mysqlconnector://analyst:my_password@localhost/company_db
    
                engine = create_engine(connection_url)   # The Engine is an object created by that library, and the Engine manages access to actual database connections. using sqlAlchemys Engine to let pandas communicate with MySQL.
    #                                                       The URL : mysql+mysqlconnector://analyst:my_password@localhost/company_db
        
                # Verify that the connection works.
                with engine.connect():   # calling create_engine() generally does not immediately connect to MySQL. It creates the Engine, which can establish connections when they're needed.
                    pass      # this condition is the one that gonna create errors like access denied and unknown database 
    
    
                # Export the DataFrame into the SQL table. Pandas provides the DataFrame.to_sql() method to write DataFrame data into a SQL database table.
                df.to_sql(                              # In my case, SQLAlchemy provides the database interface that pandas uses to communicate with MySQL.
                    name = Table_name,
                    con= engine,                        # con means connection or connectable. It specifies which database interface pandas should use to perform the operation.  Pandas supports SQLAlchemy Engines and Connections for this workflow, as well as certain supported SQLite connections. The exact supported options depend on the pandas version and database backend.
                    if_exists="fail",                   # This controls what happens if the destination table already exists. "fail" means Raise an error if the table already exists.
                    index=False                         # the python indexing starts from 0 so The index is pandas' row-label mechanism. It isn't necessarily a meaningful dataset column.
                )
    
                return (
                        f"Successfully exported {len(df)} rows and "
                        f"{len(df.columns)} columns to the MySQL table "
                        f"'{Table_name}' in database '{Database_name}'."
                    )
    
    
    
    
            # Suppose GLACIER tries to connect using an incorrect password.
            # MySQL may reject the login and send an error to the driver.
            # The driver reports the failure through Python's exception mechanism. SQLAlchemy may wrap the underlying driver error in a SQLAlchemy exception.
    
            except Exception as error:
    
                # Identify common connection errors.
                error_message = str(error).lower()     # 
                if "access denied" in error_message:
                    return (
                        "MySQL authentication failed. The username or password "
                        "may be incorrect, or the user may lack permission."
                    )
    
                elif "unknown database" in error_message:
                    return (
                        f"Database '{Database_name}' does not exist. "
                        "Please provide an existing database name."
                    )
    
                elif "can't connect" in error_message or "connection refused" in error_message:
                    return (
                        f"Could not connect to MySQL host '{Host}'. "
                        "Please check the host and ensure the MySQL server is running."
                    )
    
                elif "already exists" in error_message:
                    return (
                        f"Table '{Table_name}' already exists in database "
                        f"'{Database_name}'. Please choose another table name."
                    )
    
            # Return an informative message for any other error.
                return f"SQL export failed: {error}"
    
            finally:
                # Release the database resources.
                if engine is not None:
                    engine.dispose()
    
    def SQL_Quaries(self, Host, User,Password, quary, Database= None):

        # Check whether the generated SQL query is valid.
        if not isinstance(quary,str) or not quary.strip():
            print("Invalid or empty SQL quary.")
            return False

        # Establish a connection to the MySQL server
        connection = None
        cursor = None

        try:
            connection = self.connect_to_mysql(
            Host=Host,
            User=User,
            Password=Password,
            Database=Database
        )

            # Create a cursor using our existing method.
            cursor = self.create_cursor(connection=connection)

            # Select the requested database before executing the user's query.
            if Database:
                database_query = f"USE `{Database}`"
                self.execute_query(cursor=cursor, query=database_query)

            # execute the quary
            self.execute_query(cursor=cursor,query=quary)

            # Check whether the query returns data.
            if cursor.with_rows:
                rows = cursor.fetchall()
                columns = [column[0] for column in cursor.description]

                # Prepare the actual SQL results for the Action Output window.
                sql_result = {
                    "type": "sql_result",
                    "success": True,
                    "columns": columns,
                    "rows": rows,
                    "row_count": len(rows)
                }

                # Send the results to Brain's Action Output storage.
                self.action_output_callback.action_output = sql_result

      
                # Return a concise status instead of sending all SQL rows to Qwen.
                return {
                    "success": True,
                    "message": (
                        f"SQL query executed successfully. "
                        f"{len(rows)} rows and {len(columns)} columns returned. "
                        "The actual results are available in the SQL Action Output window."
                    )
                }


            # Save changes for queries such as INSERT or UPDATE.
            self.commit_changes(connection)


            # Return the execution status.
            return {
                "success": True,
                "message": "SQL query executed successfully.",
                "affected_rows": cursor.rowcount
            }


        except mysql.connector.Error as error:

            # Handle errors reported by MySQL.
            print(f"MySQL error: {error}")

            return {
                "success": False,
                "error": str(error)
            }

        finally:
            # Close the cursor if it was created.
            if cursor is not None:
                cursor.close()

            # Close the connection if it was established.
            if connection is not None:
                self.close_connection(connection)                

   










# build is a generic Pandas → MySQL datatype mapper because the pandas and sql has same different name for same datatype like:
# Pandas                 MySQL

# int64          →       INT
# float64        →       FLOAT/DOUBLE
# object/string  →       VARCHAR/TEXT
# bool           →       BOOLEAN
# datetime       →       DATETIME 

    # The datatype Mapper


#-----------------------------------------TEST

# manager=DatasetManager()
# manager.load_dataset(r"C:\Main\GLACIER\data\Cleaned data\amazon_sales_data_cleaned.csv")
# manager.load_into_executor()
# export_manager=ExportManager(manager)





# #-----------------------------------------------TO show fetch the query the executed inside the database


# # if __name__ == "__main__":       # means: "Only run the code below this line if this Python file is being run directly."
# #     export_manager=ExportManager(None)

# #     # connect python to the local sql server.
# #     connection = export_manager.connect_to_mysql(
# #         Host="localhost",
# #         User="root",
# #         Password=""
# #     )

# #     # Create a cursor for sending SQL commands to MySQL.
# #     cursor = export_manager.create_cursor(connection)

# #     # Send a simple SQL command to verify that the connection works.
# #     result=export_manager.execute_query(cursor, "SELECT 1")

# #     # Read the result returned by the SELECT query.
# #     result = cursor.fetchone()               # cursor.fetchone() — retrieves the next single row returned by a SQL query.
# #     print(f"MySQL returned: {result}")

# #     # Close the cursor after finishing the test.
# #     cursor.close()

# #     # Close the connection to the MySQL Server.
# #     export_manager.close_connection(connection)




# # ----------------------------------------to create a database 
# # if __name__ == "__main__":       # means: "Only run the code below this line if this Python file is being run directly."
# #     export_manager=ExportManager(None)

# #     # connect python to the local sql server.
# #     connection = export_manager.connect_to_mysql(
# #         Host="localhost",
# #         User="root",
# #         Password=""
# #     )
    
# #     # Create a cursor for sending SQL commands to MySQL.
# #     cursor = export_manager.create_cursor(connection)

# #     # create the database 
# #     export_manager.create_database(cursor=cursor,connection=connection,database_name="amazon_database")

# #     # Close the cursor after finishing the test.
# #     cursor.close()

# #     # Close the connection to the MySQL Server.
# #     export_manager.close_connection(connection)


# #--------------------------------------------To create a table

# # if __name__ == "__main__":
# #     export_manager = ExportManager(None)

# #     # Connect directly to our Amazon database.
# #     connection = export_manager.connect_to_mysql(
# #         Host="localhost",
# #         User="root",
# #         Password="",
# #         Database="amazon_database"
# #     )

# #     # Create a cursor for executing SQL commands.
# #     cursor = export_manager.create_cursor(connection)

# #     # Create the products table.
# #     export_manager.create_table(
# #         cursor,
# #         connection,
# #         "products"
# #     )

# #     # Close the cursor.
# #     cursor.close()

# #     # Close the MySQL connection.
# #     export_manager.close_connection(connection)



# #--------------------------------------------to check the will any query work with execute_query function like create table insert into table---

# # if __name__ == "__main__":

# #     export_manager = ExportManager(None)

# #     # Connect directly to our database.
# #     connection = export_manager.connect_to_mysql(
# #         Host="localhost",
# #         User="root",
# #         Password="",
# #         Database="amazon_database"
# #     )

# #     # Create a cursor.
# #     cursor = export_manager.create_cursor(connection)

# #     # Create a table using the generic SQL execution function.
# #     export_manager.execute_query(
# #         cursor=cursor,query=
# #         """
# #         CREATE TABLE IF NOT EXISTS test_table (
# #             id INT,
# #             name VARCHAR(100),
# #             salary FLOAT
# #         )
# #         """
# #     )

# #     # Save the CREATE TABLE operation.
# #     export_manager.commit_changes(connection)

# #     # Insert a test row using the SAME execute_query().
# #     export_manager.execute_query(
# #         cursor=cursor,query=
# #         """
# #         INSERT INTO test_table
# #         (id, name, salary)
# #         VALUES (1, 'Ayush', 35000)
# #         """
# #     )

# #     # Save the INSERT operation.
# #     export_manager.commit_changes(connection)

# #     # Read the data using the SAME execute_query().
# #     export_manager.execute_query(
# #         cursor,
# #         "SELECT * FROM test_table"
# #     )

# #     # Fetch the result.
# #     rows = cursor.fetchall()

# #     for row in rows:
# #         print("Database returned:", row)

# #     # Close everything.
# #     cursor.close()
# #     export_manager.close_connection(connection)





# #---------------------------------------------- the pandas to sql data type conversion----------
# # print(export_manager.pandas_to_mysql_type("int64"))
# # print(export_manager.pandas_to_mysql_type("bool"))
# # print(export_manager.pandas_to_mysql_type("float64"))
# # print(export_manager.pandas_to_mysql_type("datetime64[ns]"))
# # print(export_manager.pandas_to_mysql_type("object"))





# #---------------------------------------Automatically create table when needed
# # query = export_manager.generate_create_table_query(table_name="amazon_products")    # this will create a single table containing the whole amazon sales dataset since the dataset only contains 1 table having so many columns                                     
# # print(query)






# #------------------------------------------- Automatically create table and insert data into the table.
# # if __name__ =="__main__":

# #     connection=export_manager.connect_to_mysql(
# #         Host="localhost",
# #         User="root",
# #         Password="",
# #         Database="amazon_database"
# #     )
# #     # create cursor for executing sql commands.
# #     cursor = export_manager.create_cursor(connection=connection)

# #     # automatically generate the create table query.
# #     # from dataframe columns and datatypes.
# #     query = export_manager.generate_create_table_query(table_name="amazon_products")

# #     # execute the generated create table query.
# #     export_manager.execute_query(cursor=cursor,query=query)

# #     # save the create table operation.
# #     export_manager.commit_changes(connection=connection)


# #     #insert the dataframe rows into the amaazon table.
# #     export_manager.insert_dataframe_rows(
# #         cursor=cursor,
# #         table_name="amazon_products"
# #     )

# #     #Permanently save the inserted rows.
# #     export_manager.commit_changes(connection=connection)

# #     #close the cursor.
# #     cursor.close()

# #     #close the mysql connection.
# #     export_manager.close_connection(connection=connection)


# connection=export_manager.connect_to_mysql(
#         Host="localhost",
#         User="root",
#         Password="",
#         Database="amazon_database"
#     )
#     # create cursor for executing sql commands.
# cursor = export_manager.create_cursor(connection=connection)
# # Verify how many rows were inserted into MySQL.
# export_manager.execute_query(
#     cursor=cursor,
#     query="SELECT COUNT(*) FROM amazon_products"
# )

# # Fetch the result returned by MySQL.
# result = cursor.fetchone()

# print("Total rows in MySQL:", result[0])