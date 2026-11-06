# GLACIER should first inspect the dataset and understand what is wrong.
# So Phase 4 starts with a Data Inspection / Cleaning Analysis method.



# prompts - 
# Level 1 — Basic Cleaning
# 1. Clean this dataset.
# 2. Clean this dataset and remove duplicate records.
# 3. Find and handle all missing values in this dataset.
# 4. Check this dataset for duplicate rows and remove them.
# 5. Fix inconsistent formatting in the dataset.
# 6. Clean the column names and make them consistent.
# 7. Check whether any columns have incorrect data types and fix them.
# 8. Find empty strings and whitespace-only values and handle them appropriately.

# Level 2 — Data Quality and Validation
# 9. Check this dataset for data quality issues.
# 10. Find columns with missing values and tell me how many values are missing in each.
# 11. Identify duplicate records and show me how many duplicates exist before removing them.
# 12. Check whether this dataset contains invalid or inconsistent values.
# 13. Find suspicious values that might indicate data-entry errors.
# 14. Check whether numerical columns contain unexpected values that need cleaning.
# 15. Inspect the dataset for problems that could affect statistical analysis.

# Level 3 — Realistic Business Requests
# 16. This dataset is messy. Make it ready for analysis.
# 17. Prepare this sales dataset for a business performance report.
# 18. Clean the dataset without unnecessarily deleting rows or losing useful information.
# 19. I'm planning to perform a statistical test on this dataset. Check its quality and fix any cleaning issues that could affect the results.
# 20. Get this dataset ready for analysis. Check for missing values, duplicates, inconsistent data, and incorrect data types, then save the cleaned version.


from tools.dataset_management import DatasetManager
import pandas as pd
from pathlib import Path

class DataCleaning:

    def __init__(self,dataset_manager):
        self.dataset_manager=dataset_manager
        print("\nData Cleaning Initialized.")

    def inspect_dataset(self):
        df=self.dataset_manager.dataframe                     

        if df is None:
            print("No active Dataset.")
            return None

        inspection={
            "rows": df.shape[0],
            "columns": df.shape[1],
            "column_names": list(df.columns),
            "data_types": df.dtypes.to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "duplicate_rows": df.duplicated().sum()
        }
        return inspection




# 1. Missing Values
# Functions responsible for identifying, analyzing, and handling missing data.

# -methods of handling missing values:

# --delete rows/columns:-
#   this method can be applied when equal to or more than 50% of the data is missing eg- 1 row 8 columns and 4 out 8 colum values are missing then we can remove the whole row 

# --Imputations:- filling missing values
#   mean/median/mode - Numerical columns
#   mode/unknown - catagorical column and numeric columns on which mathematical operation cannot be performed like Phone_no.
#   forward fill / backward fill - date_time_columns, total_sales_per_day columns, some numerical columns
#   predictive imputation using LLM model 

# limitation of this pandas cleaning - 
# df = df.drop(index=5) If row 5 contained an important customer record, pandas doesn't automatically provide an Excel-style undo history for that operation.


    def analyze_missing_values(self):
        df = self.dataset_manager.dataframe                         # "Give me the DataFrame that GLACIER is currently working with."
        if df is None:
            print("No Active Dataset. ")
            return None
        
        missing_count = df.isnull().sum()                           # counts the missing values 

        missing_percentage = (missing_count / len(df)) * 100

        missing_report = {}
        for column in df.columns:                                    # to check every column of the dataset and give it to "for column" one by one
            missing_report[column] = {                               # creating a nested dictionary.
                "missing_count": int(missing_count[column]),
                "missing_percentage":round(missing_percentage[column],2)      # = round(missing_percentage["Title"], round to 2 decimals. Eg - 10.234234 = 10.23)
            }
        return missing_report

    def decide_missing_value_strategy(self):

        df=self.dataset_manager.dataframe                  # "Give me the DataFrame that GLACIER is currently working with."
        if df is None:
            print("No Active dataset")
            return None

        missing_count=df.isnull().sum()            # Counts missing values in every column.
        total_rows = len(df)
        strategy_report={}                      # Creates an empty dictionary for our cleaning decisions.

        for column in df.columns:
            count = missing_count[column]                # "Go to the Series missing_count and give me the value whose label is Rating.".

            percentage= (count/total_rows)*100                # Calculates the percentage of missing values in the current column.

            if count == 0:
                strategy = "No action"                  # There are no missing values, so nothing needs to be done.

            elif percentage<5:
                strategy = "Consider filling or dropping affected rows"               # Small amount of missing data; this may be manageable at row level.

            elif percentage < 40:
                strategy= "Investigate column before cleaning"                # A larger amount of missing data requires understanding the column first.

            else:
                strategy = "Consider Column - specific handling"               # Very high missing percentage; blindly deleting rows could destroy too much data.


            strategy_report[column] = {
                "missing_count" : int(count),
                "missing_percentage" : round(percentage,2),
                "strategy": strategy
            }                                                                # Stores the missing-value information and our initial recommended strategy.
        return strategy_report

    def prepare_missing_value_analysis(self):
        df = self.dataset_manager.dataframe
        if df is None:
            print("No active Dataset.")
            return None

        missing_count=df.isnull().sum()

        column_with_missing = {}

        for column in df.columns:
            count=int(missing_count[column])

            if count>0:
                column_with_missing[column] = count

        return column_with_missing




                    # inspect only columns that contain missing values.
    
    def inspect_missing_value_columns(self):
        df=self.dataset_manager.dataframe
        if df is None:
            print("no active dataset")
            return None

        missing_count = df.isnull().sum()

        for column in df.columns:

            if missing_count[column] > 0:    # Only inspect columns that actually contain missing values.

                print(f"\n===== {column} =====")

                print("Missing values:", int(missing_count[column]))    # Shows how many values are missing.
                

                print("Sample non-missing values:")

                print(df[column].dropna().head(20).to_list())

        return True
    
    


# 2. Analysing
# funtions responsible for reporting the problem(not taking any action)

#   for finding duplicates
    def analyze_duplicates(self):
        df = self.dataset_manager.dataframe          # Gets the currently active DataFrame from DatasetManager.

        if df is None:
            print('No active dataset ')              # There is no DataFrame available to analyze.
            return None

        duplicate_count = df.duplicated().sum()      # df.duplicated() checks each row and marks it true if it is a duplicate.
#                                                    # .sum() counts the True values, giving us the total number of duplicate rows.
        duplicate_percentage=(duplicate_count / len(df)) * 100

        duplicate_report= {                         # Createing a dictionary containing the duplicate count and percentage.
            "duplicate_count" : int(duplicate_count),
            "duplicate_percentage" : round(duplicate_percentage,2)
        }

        return duplicate_report              # Sends the report back to whoever called this function.

#   for finding the datatypes of columns
    def analyze_datatypes(self):
        df=self.dataset_manager.dataframe          # "Give me the DataFrame that GLACIER is currently working with."
        if df is None:
            print("No active Dataset")
            return None
        datatype_report = {}         # Creating an empty dictionary where we will store information
        for column in df.columns:
            datatype_report[column] = {
                "datatype" : str(df[column].dtype),                   # and number of missing values for the current column.
                "unique_values" : int(df[column].nunique()),          # Stores the data type, number of unique values,
                "missing_values" : int(df[column].isnull().sum())
            }
        return datatype_report        # Sends the complete report back to whoever called the function.

#   for analyzing the numeric column to perform mathematical operations
    def analyze_numeric_columns(self):
        df=self.dataset_manager.dataframe
        if df is None:
            print("No Active Dataset")
            return None
        numeric_report = {}           # Creates an empty dictionary where we will store the analysis.

        for column in df.columns:

            converted = pd.to_numeric(df[column],errors="coerce")           # Tries to convert the column's values into numbers.   
#                                                                              # Values that cannot be converted are changed to NaN instead of causing an error.
            total_numeric_values= converted.notna().sum()                            # Counts how many values successfully became numbers.
            total_values= df[column].notna().sum()                             # Counts how many non-missing values the original column contains.
#                                                                              # .notna() Returns True for values that are not missing.

            if total_values >0:
                numeric_percentage= (total_numeric_values/total_values) *100         # Calculates what percentage of the non-missing values are numeric.

            else:
                numeric_percentage = 0

            numeric_report[column]= {
                "numeric_values": int(total_numeric_values),
                "non_missing_values": int(total_values),
                "numeric_percentage": round(numeric_percentage,2)
            }                                                                  # Stores the numeric conversion results for the current column.

        return numeric_report

#   takes the first 20 available values and converts them into a python list for easy reading.
    def inspect_problematic_values(self):
        
        # building a function that tries to determine:
        # "Does this string column contain values that could reasonably be numeric?"

        df = self.dataset_manager.dataframe                  # "Give me the DataFrame that GLACIER is currently working with."
        if df is None:
            print("No Active Data")
            return None

        for column in df.columns:
            print(f"\n===== {column} =====")

            print(df[column].dropna().head(20).to_list())  # Removes missing values temporarily,
#                                                          # takes the first 20 available values,
#                                                          # and converts them into a Python list for easy reading.
        return True




# 3. ACTION on Cleaning 
# These function will actually perform action to clean the dataset.

    def handle_missing_values(self, column, action="drop"):
        df = self.dataset_manager.dataframe
        if df is None:
            print("No active Dataset.")
            return False 

        if column not in df.columns:                          # Checks whether the requested column exists
            print(f"Column '{column}' not found.")
            return False

        missing_before= df[column].isnull().sum()                # Counts how many missing values this column has before cleaning

        if action == "drop": 
            df = df.dropna(subset=[column])                # Removes rows where this particular column contains a missing value

        elif action == "fill":
            fill_value = "Unknown"            # Value that will replace missing values
            df[column] = df[column].fillna(fill_value)                 # Replaces every missing value with the selected value


        else:

            print("Invalid missing_value Action")
            return False                              # Only "drop" and "fill" are currently supported

        missing_after = df[column].isnull().sum()             # Counts missing values again after cleaning
        
        self.dataset_manager.dataframe = df                # Updates DatasetManager's active DataFrame
    
        self.dataset_manager.last_operation = (f"MISSING VALUE HANDLED '{column}'")         # Records the operation
        print(f"Column: {column}")
        print(f"Missing Before: {missing_before}")
        print(f"Missing After: {missing_after}")
        return True
    
# this function is to clean the numeric columns except columns like primary_key or phone_numbers or 6k 600k.
    def clean_numeric_column(self,column):
        df = self.dataset_manager.dataframe
        if df is None:
            print("No active Dataset.")
            return False

        if column not in df.columns:                       # Checks whether the requested column actually exists.
            print(f"Column '{column}' not found.")
            return False

        original=df[column].copy()            # Makes a copy of the column before cleaning.    # We keep it so we can compare before vs after.

        cleaned = df[column].astype(str).str.replace(",", "")

        converted = cleaned.str.extract(r"(\d+(?:\.\d+)?)")[0] #--------------------------------EXPLANATION - astype(str) means:  Convert the data into a specified data type.
#                                                                             #--------------------------------   .str.extract() means: Find a pattern inside strings and extract the matching part.
        converted = pd.to_numeric(converted,errors="coerce")



        df[column] = converted                     # Replaces the original column with the converted numeric values.

        self.dataset_manager.dataframe = df              # Updates the active DataFrame inside DatasetManager.

        self.dataset_manager.last_operation = f"Cleaned numeric column: {column}"          # Records what GLACIER just did.
        return True

# This function is for numeric columns with values like (6k,600+,600.0 etc) converts them to simple float like (6k = 6000, 600+ = 600)
    def clean_abbreviated_numbers(self, column):
        df = self.dataset_manager.dataframe
        if df is None:
            print("No active Dataset.")
            return False
        if column not in df.columns:
            print(f"Column '{column}' not found.")
            return False

        cleaned = df[column].astype(str).str.upper()
        converted =[]
        for value in cleaned:
            if pd.isna(value):
                converted.append(float("nan"))
                continue

            if "K+" in value:
                number = value.split("K+")[0].strip()
                numfloat =float(number)*1000
                converted.append(numfloat)

            else:
                numother = value.split("+")[0].strip()
                converted.append(pd.to_numeric(numother,errors="coerce"))

        df[column]= converted
        self.dataset_manager.dataframe = df
        self.dataset_manager.last_operation = (f"Cleaned abbreviated numbers: {column}")
        return True

# makeing clean_boolean_column universal for all kind of dataset in the world and let the function receive the meaning/mapping from outside.(Ollama)
    def clean_boolean_column(self, column, true_values, false_values):  
        df = self.dataset_manager.dataframe
        if df is None:
            print("No active Dataset.")
            return False
        if column not in df.columns:
            print(f"Column '{column}' not found.")
            return False


        cleaned = df[column].astype(str).str.strip().str.lower()
        converted = []

        for value in cleaned:

            if value in true_values:
                converted.append(True)

            elif value in false_values:
                converted.append(False)

            else:
                converted.append(None)

        df[column] = converted
        self.dataset_manager.dataframe = df
        self.dataset_manager.last_operation = (
            f"Cleaned boolean column: {column}"
        )

        return True


    def remove_duplicates(self):
        df = self.dataset_manager.dataframe
        if df is None:
            print("No active Dataset.")
            return False

        rows_before = len(df)       # Stores the number of rows before duplicate removal

        duplicate_count = df.duplicated().sum()       # Finds duplicate rows and counts how many there are

        df = df.drop_duplicates()
        rows_after = len(df)                 # Stores the number of rows remaining after cleaning.

        self.dataset_manager.dataframe = df           # Sends the cleaned DataFrame back into DatasetManager

        self.dataset_manager.last_operation = "Duplicates Removed"       # Records the latest cleaning operation

        print("\nDUPLICATE CLEANING")
        print(f"Rows Before: {rows_before}")
        print(f"Duplicates Found: {duplicate_count}")
        print(f"Rows After: {rows_after}")
        
        return True


    def clean_text_column(self, column):

        df = self.dataset_manager.dataframe        # Gets the current DataFrame from DatasetManager
        if df is None:
            print("No active Dataset.")
            return False
        if column not in df.columns:
            print(f"Column '{column}' not found.")        # Checks whether the requested column exists
            return False

        df[column] = df[column].astype(str).str.strip()  # Converts values to strings and removes unnecessary spaces from the beginning and end of each value.

        self.dataset_manager.dataframe = df             
        self.dataset_manager.last_operation = f"Text cleaned: {column}"
        print(f"Text cleaning completed: {column}")
        return True


    def convert_to_numeric(self, column):
        df = self.dataset_manager.dataframe
        if df is None:
            print("No active Dataset.")
            return False
        if column not in df.columns:
            print(f"Column '{column}' not found.")
            return False    # Checks whether the requested column exists

        df[column] = pd.to_numeric(df[column], errors="coerce")

        self.dataset_manager.dataframe = df     # Updates DatasetManager with the modified DataFrame
    
        self.dataset_manager.last_operation = f"Converted to numeric: {column}"

        
        print(f"Column converted to numeric: {column}")
        print(f"Data type: {df[column].dtype}")

        return True


    def validate_cleaning(self):

        df = self.dataset_manager.dataframe
        if df is None:
            print("No active Dataset.")
            return False
        print("\n===== CLEANING VALIDATION =====")

        print("\nDATASET SHAPE")
        print(df.shape)

        print("\nMISSING VALUES")
        print(df.isnull().sum())

        print("\nDUPLICATE ROWS")
        print(df.duplicated().sum())

        print("\nDATA TYPES")
        print(df.dtypes)

        return True




# 4. Final reporting and saving
# these functions will either show the final result of the actions performed on the dataset or it will save the cleaned dataset to csv

    def final_cleaning_report(self):
        df = self.dataset_manager.dataframe
        if df is None:
            print("No active Dataset.")
            return False

        total_rows = len(df)
        total_columns = len(df.columns)
        missing_values = df.isnull().sum()
        duplicate_rows = df.duplicated().sum()
        print("\nFINAL CLEANING REPORT")
        print(f"Rows: {total_rows}")
        print(f"Columns: {total_columns}")
        print(f"Duplicate Rows: {duplicate_rows}")

        print("\nMISSING VALUES")
        print(missing_values)

        print("\nDATA TYPES")
        print(df.dtypes.to_dict())
        return True


    def save_cleaned_dataset(self,file_path):
            df =  self.dataset_manager.dataframe
            if df is None:
                print("No active Dataset.")
                return False
            df.to_csv(file_path,index=False)      # index=False prevents Pandas from adding the DataFrame index as an extra column.
            print(f"Cleaned dataset saved to: {file_path}")    # file_path tells Pandas where and under what name to save it.
            return True 























# -----------------------------------------------------TESTS

# manager=DatasetManager()
# manager.load_dataset(r"C:\Main\GLACIER\data\amazon_sales_data_uncleaned.csv")
# manager.load_into_executor()
# cleaner=DataCleaning(manager)           # Python passes the manager object into:     def __init__(self, dataset_manager):



# # ----------------------------------------missing value test

# # missing_report= cleaner.analyze_missing_values()

# # print('\n MISSING VALUE REPORT')

# # for column, info in missing_report.items():           # .items() gives each dictionary key + its value together.

# #     print(                                             # Python puts the key into 'column' and the value into 'info'.
# #         f"{column}: "                                  # {column} inserts the current column name into the string.
# #         f"{info["missing_count"]} missing"             # open info dictionary and the give the value whose key is "missing_count"
# #         f"({info['missing_percentage']}%)"             # open info dictionary and the give the value whose key is "missing_percentage"
# #     )



# # ------------------------------------duplicate value test

# # duplicate_report=cleaner.analyze_duplicates()
# # print('\nDuplicate Values.')
# # print(f"Duplicated Rows: {duplicate_report["duplicate_count"]}, {duplicate_report["duplicate_percentage"]}%")



# #---------------------------------------Dtype test

# # datatype_report=cleaner.analyze_datatypes()
# # print("\nData type report.\n")

# # for column, info in datatype_report.items():        # .items() gives the column name and its information dictionary.
# #     print(
# #         f"{column}: "
# #         f"\ntype= {info["datatype"]}, "
# #         f"unique= {info['unique_values']}, "
# #         f"missing= {info['missing_values']}\n"
# #     )





# # ------------------------------------------------Strategy report test

# # strategy_report = cleaner.decide_missing_value_strategy()
# # print("\nMissing Value Cleaning Strategy")

# # for column, info in strategy_report.items():
# #     print(
# #         f"{column}: "
# #         f"{info['missing_count']} missing"
# #         f"({info['missing_percentage']}%) - "
# #         f"{info["strategy"]}"
# #     )
# # ---------------------------------------------- inspect_problematci_value test(needs to be run with decide_missing_values_Strategy to make sense)
# # print("\nProblematic values ")
# # cleaner.inspect_problematic_values()



# # ------------------------------------------------REmove Duplicates test

# # duplicate_report = cleaner.remove_duplicates()
# # print('\nDuplicate Cleaning Report')
# # print(f"Rows Before: {duplicate_report['rows_before']}")
# # print(f"Rows after: {duplicate_report['rows_after']}")
# # print(f"Duplicates Removed: {duplicate_report['duplicates_removed']}")


# # -----------------------------------------------------prepare_missing_value_analysis test

# # missing_columns = cleaner.prepare_missing_value_analysis()
# # print("\nColumns with Missing values\n")

# # for column,count in missing_columns.items():
# #     print(f"{column}: {count} Missing values")


# # ---------------------------------------------------inspect_missing_value_columns

# # print("\nMISSING VALUE COLUMN INSPECTION")

# # cleaner.inspect_missing_value_columns()





# #----------------------------------------------------clean_numeric_column
# # print("\nBEFORE NUMBER CLEANING")
# # print(cleaner.dataset_manager.dataframe["Number_of_reviews"].head(10).tolist())

# # cleaner.clean_numeric_column("Number_of_reviews")

# # print("\nAFTER NUMBER CLEANING")
# # print(cleaner.dataset_manager.dataframe["Number_of_reviews"].head(10).tolist())
# # print("\nDATA TYPE")
# # print(cleaner.dataset_manager.dataframe["Number_of_reviews"].dtype)




# # -------------------------------------------------------clean_abbreviated_numbers
# # print("\nBEFORE ABBREVIATED NUMBER CLEANING")
# # print(cleaner.dataset_manager.dataframe["bought_in_last_month"].head(10).tolist())

# # cleaner.clean_abbreviated_numbers("bought_in_last_month")

# # print("\nAFTER ABBREVIATED NUMBER CLEANING")
# # print(cleaner.dataset_manager.dataframe["bought_in_last_month"].head(10).tolist())

# # print("\nDATA TYPE")
# # print(cleaner.dataset_manager.dataframe["bought_in_last_month"].dtype)



# # --------------------------------------------------------Clean_bolean_value
# # print("\nBOOLEAN CLEANING TEST")

# # # is_best_seller
# # cleaner.clean_boolean_column(
# #     "is_best_seller",
# #     ["best seller"],
# #     ["no badge"]
# # )

# # # is_sponsored
# # cleaner.clean_boolean_column(
# #     "is_sponsored",
# #     ["sponsored"],
# #     ["organic"]
# # )

# # # is_couponed
# # cleaner.clean_boolean_column(
# #     "is_couponed",
# #     ["save 15%  with coupon", "save 50%  with coupon"],
# #     ["no coupon"]
# # )

# # print("\nAFTER BOOLEAN CLEANING")

# # print(
# #     cleaner.dataset_manager.dataframe[
# #         "is_best_seller"
# #     ].head(20).tolist()
# # )

# # print(
# #     cleaner.dataset_manager.dataframe[
# #         "is_sponsored"
# #     ].head(20).tolist()
# # )

# # print(
# #     cleaner.dataset_manager.dataframe[
# #         "is_couponed"
# #     ].head(20).tolist()
# # )


# # print("\nUNRECOGNIZED VALUES")

# # print(
# #     cleaner.dataset_manager.dataframe[
# #         "is_best_seller"
# #     ].value_counts(dropna=False)
# # )

# # print(
# #     cleaner.dataset_manager.dataframe[
# #         "is_couponed"
# #     ].value_counts(dropna=False)
# # )


# # print("\nDATA TYPES")

# # print(
# #     cleaner.dataset_manager.dataframe[
# #         ["is_best_seller", "is_sponsored", "is_couponed"]
# #     ].dtypes
# # )






# #------------------------------------------Handle missing values test
# # cleaner.handle_missing_values("Rating",'drop')
# # print(manager.dataframe["Rating"].isnull().sum())
# # print(manager.dataframe.shape)




# # #------------------------------------------remove_duplicates test
# print("\nBEFORE DUPLICATE CLEANING")
# print(f"Shape: {manager.dataframe.shape}")

# cleaner.remove_duplicates()

# print("\nAFTER DUPLICATE CLEANING")
# print(f"Shape: {manager.dataframe.shape}")




# # -------------------------------------------------clean_text_column
# # print("\nBEFORE TEXT CLEANING")
# # print(manager.dataframe["Title"].head(10).tolist())

# # cleaner.clean_text_column("Title")

# # print("\nAFTER TEXT CLEANING")
# # print(manager.dataframe["Title"].head(10).tolist())


# #---------------------------------------------convert_to_numeric test 
# # cleaner.convert_to_numeric("Rating")



# #-----------------------------------------------Validate_cleaning test
# # print("\nFINAL CLEANING VALIDATION")

# # cleaner.validate_cleaning()




# #------------------------------------------Final cleaning report test 
# # cleaner.final_cleaning_report()


























# # ====================================================================PHASE 4 FINAL TEST==========================================================================

# manager = DatasetManager()
# manager.load_dataset(r"C:\Main\GLACIER\data\amazon_sales_data_uncleaned.csv")
# manager.load_into_executor()

# cleaner = DataCleaning(manager)

# print("\n========== PHASE 4 FINAL TEST ==========")

# # Remove duplicate rows
# cleaner.remove_duplicates()


# # ================= NUMERIC COLUMNS =================

# cleaner.clean_numeric_column("Rating")
# cleaner.clean_numeric_column("Number_of_reviews")

# cleaner.clean_numeric_column("Current/discounted_price")
# cleaner.clean_numeric_column("Price_on_variant")
# cleaner.clean_numeric_column("Listed_price")


# # ================= ABBREVIATED NUMBERS =================

# cleaner.clean_abbreviated_numbers("bought_in_last_month")


# # ================= BOOLEAN COLUMNS =================

# cleaner.clean_boolean_column(
#     "is_best_seller",
#     ["true", "yes", "y", "1", "best seller"],
#     ["false", "no", "0", "no badge"]
# )

# cleaner.clean_boolean_column(
#     "is_sponsored",
#     ["true", "yes", "y", "1", "sponsored"],
#     ["false", "no", "0", "organic"]
# )

# cleaner.clean_boolean_column(
#     "is_couponed",
#     ["true", "yes", "y", "1", "save 15%  with coupon", "save 50%  with coupon"],
#     ["false", "no", "0", "no coupon"]
# )


# # ================= TEXT COLUMNS =================

# cleaner.clean_text_column("Title")
# cleaner.clean_text_column("buy_box_availability")
# cleaner.clean_text_column("delivery_details")
# cleaner.clean_text_column("sustainability_badges")
# cleaner.clean_text_column("image_url")
# cleaner.clean_text_column("product_url")


# # ================= FINAL VALIDATION =================

# print("\n========== FINAL VALIDATION ==========")

# cleaner.validate_cleaning()



# # ================== SAVE DATASET ====================
# print("\n --------------SAVING CLeaned Dataset----------------------")
# manager.save_cleaned_dataset(r"C:\Main\GLACIER\data\Cleaned data\amazon_sales_data_cleaned.csv")
