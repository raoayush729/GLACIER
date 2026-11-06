
# PHASE 2
# Objective

# Build a Python execution system that allows GLACIER to execute Python operations,
# maintain a persistent Python environment, capture output/errors, and return useful results.


# FileAccess
#     ↓
# Find sales.csv
#     ↓
# PythonExecutor
#     ↓
# pandas.read_csv()
#     ↓
# DataFrame
#     ↓
# return result

import io 
from contextlib import redirect_stdout
import pandas as pd

class PythonExecutionor:
    def __init__(self,dataset_manager):

        print('\nPython Executionor Initialized. ')

        # Reference to the existing DatasetManager.
        self.dataset_manager = dataset_manager

        # Persistent Python execution environment.
        self.namespace={
            "pd":pd
        }

    def execute(self, code):
        output = io.StringIO()            # io.stringIO() Creates an in-memory text stream that can store text like a file. (making output into storage that can store a file)

        try:
            # Get the currently active DataFrame.
            dataframe = self.dataset_manager.dataframe

            # Make the active DataFrame available to generated code.
            if dataframe is not None:
                self.namespace['df'] = dataframe

            # Try evaluating an expression first.
            try:
                result = eval(code, self.namespace)      # Runs a perticular piece of code that gives a result/value like df.shape()

                # Synchronize the resulting DataFrame.
                updated_dataframe = self.namespace.get("df")

                if isinstance(updated_dataframe, pd.DataFrame):
                    self.dataset_manager.dataframe = updated_dataframe

                return {
                    'success': True,
                    "Type": "expression",
                    'output': result,
                    "error": None
                }

            except SyntaxError:

                # Execute statements and capture print() output.
                with redirect_stdout(output):     # redirect_stdout() Temporarily redirects print() output from the terminal to another destination. (redirecting the code output into this storage(output))

                    exec(code, self.namespace)     # exec(code, namespace) "run this code in the environment represented by this namespace"

                # Synchronize the resulting DataFrame.
                updated_dataframe = self.namespace.get("df")

                if isinstance(updated_dataframe, pd.DataFrame):
                    self.dataset_manager.dataframe = updated_dataframe

                result = output.getvalue()        # Getvalue() Returns the text currently stored inside a StringIO object. (getting the text out from the output)

                return {
                    "success": True,
                    "Type": "stdout",
                    "output": result,
                    "error": None
                }

        except Exception as error:
            print(f"Python Execution error : {error}")
            return {
                "success": False,
                'Type': None,
                'output': None,
                'error': str(error)
            }


# ----------------------------------------------------------TESTS

# executor=PythonExecutionor()
# a=executor.execute("import pandas as pd\n\ndata_path = r'C:\\Users\\ayush\\OneDrive\\Desktop\\amazon_sales_data_cleaned.csv'\n\n# Load the dataset into a DataFrame\ndf = pd.read_csv(data_path)\n\n# Retrieve and display the top 10 rows\ntop_10_rows = df.head(10)\n\n# Output the result\nprint(top_10_rows)")
# print(a)
# result = executor.execute("""
# print("Hello from GLACIER")
# print("Python Executor is working")
# print("Output captured successfully")
# """)

# print("GLACIER received:")
# print(result)


# ----------------------------------------testing the exec() funtion 
# result0 = executor.execute("""
# import numpy as np
# import pandas as pd
# data=[10,20,30,40,50]
# df=pd.DataFrame(data)
# print(df)
# print("mean:",df.mean())
# """)
# print(result['output'])



# -----------------------testing to read and load the dataset from directory 
# result1=executor.execute(r"""
# import pandas as pd

# df = pd.read_csv(r"C:\Main\GLACIER\data\amazon_sales_data_uncleaned.csv")
# """)
# print('load result: ')
# print(result1['output'])

# print('----------------------------------------------------')

# --------------------Testing to give top 5 rows of the dataset after loading the data 
# result2=executor.execute("""
# df.head()
# """)
# print("dataset top 5: ")
# print(result2['output'])

# print('----------------------------------------------------')



# --------------------------------testing the differnece of exec and eval funtions
# result3= executor.execute("df.shape")
# print(f"SHAPE: {result3['output']}")

# print('----------------------------------------------------')


# result4 = executor.execute("df.isnull().sum()")
# print(f"NULL VALUES: {result4['output']}")
# print('----------------------------------------------------')




