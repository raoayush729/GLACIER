# GLACIER should know which dataset we're currently working with so you don't have to repeatedly provide the path.
# Phase 3 connects the phase 1 and 2.


#                          THE FLOW -
# FileAccess
# → "Where is the file?"

# DatasetManager
# → "Which dataset are we working with?(csv,json,excel)"

# PythonExecutor
# → "Run Python on it."

# Pandas
# → "Turn the file into a DataFrame."



# from library_or_package import class_or_function
from pathlib import Path
import pandas as pd
from tools.Python_executioner import PythonExecutionor


class DatasetManager:
    
    def __init__(self,executor=None):                   # This is the state GLACIER needs to remember.
        self.original_file=None           # The original dataset selected by the user
        self.current_file=None            # The file currently being worked on
        self.file_type=None               # .csv / .xlsx / .json etc.
        self.dataframe=None               # The DataFrame currently in memory
        self.cleaned_file=None            # Path to the cleaned dataset later
        self.last_operation=None          # What GLACIER did most recently 
        self.executor=executor
        # Callback used to publish dataset viewer requests to Brain.
        self.dataset_viewer_callback = None

        print("\nDataset Manager Initialized")   # Initially everything is None because no dataset has been loaded yet
        

    def load_dataset(self, file_path):

        if not self.dataframe is None:
            return "there a already a dataset loaded first drop that dataset then only the new dataset can be loaded"

        if not file_path:
            print("No dataset name or path provided.")
            return False

        file_path = Path(str(file_path).strip())

        # Case 1: The user provided an existing file path
        if file_path.is_file():
            pass

        else:
            # Case 2: Search the Desktop for the requested dataset
            desktop = Path.home() / "OneDrive" / "Desktop"

            if not desktop.is_dir():
                print("Desktop folder not found.")
                return False

            # First, search for an exact filename match.
            exact_matches = []

            for item in desktop.rglob("*"):      # if the requested filename is dirty_cafe_sales.csv, it searches for that exact filename first instead of immediately comparing individual words.
                if (
                    item.is_file()
                    and item.suffix.lower() in [".csv", ".xlsx", ".xls", ".json"]
                    and item.name.lower() == file_path.name.lower()
                ):
                    exact_matches.append(item)


            if len(exact_matches) == 1:
                file_path = exact_matches[0]

            elif len(exact_matches) > 1:
                return (
                    f"Multiple files have the exact filename "
                    f"'{file_path.name}'. Please specify the folder."
                )

            else:
                # If no exact match exists, search using all keywords.
                search_name = file_path.stem.lower().replace("_", " ").replace("-", " ")
                words = search_name.split()
                keywords = []

                for word in words:
                    if word not in ["dataset", "data", "file"]:
                        keywords.append(word)

                if not keywords:
                    print("Invalid dataset name.")
                    return False

                matches = []

                for item in desktop.rglob("*"):
                    if (
                        item.is_file()
                        and item.suffix.lower() in [".csv", ".xlsx", ".xls", ".json"]
                    ):
                        item_name = item.stem.lower().replace("_", " ").replace("-", " ")

                        all_keywords_match = True

                        for word in keywords:
                            if word not in item_name:
                                all_keywords_match = False
                                break

                        if all_keywords_match:
                            matches.append(item)

                if len(matches) == 0:
                    print("No matching dataset found on the Desktop.")
                    return False

                elif len(matches) > 1:
                    file_names = ""

                    for item in matches:
                        file_names += item.name + ", "

                    return (
                        f"There are multiple files matching your request: "
                        f"{file_names.rstrip(', ')}. Which one do you want to load?"
                    )

                else:
                    file_path = matches[0]


        # Step 1: Validate the file
        if not file_path.is_file():
            print("Invalid dataset file.")
            return False

        file_type = file_path.suffix.lower()

        if file_type not in [".csv", ".xlsx", ".xls", ".json"]:
            print("Unsupported file format.")
            return False

        # Step 2: Prepare the loading code
        file_path_str = str(file_path)

        if file_type == ".csv":
            code = (
                "import pandas as pd\n"
                f"df = pd.read_csv({file_path_str!r})"   # !r is to convert that string to r string because there will be a path to the file, to avoide escape sequence
            )

        elif file_type in [".xlsx", ".xls"]:
            code = (
                "import pandas as pd\n"
                f"df = pd.read_excel({file_path_str!r})"  # !r is to convert that string to r string because there will be a path to the file, to avoide escape sequence
            )

        elif file_type == ".json":
            code = (
                "import pandas as pd\n"
                f"df = pd.read_json({file_path_str!r})"  # !r is to convert that string to r string because there will be a path to the file, to avoide escape sequence
            )

        # Step 3: Execute the loading code
        result = self.executor.execute(code)

        if not result.get("success"):
            print(f"Dataset loading error: {result.get('error', 'Unknown error')}")
            return False

        # Step 4: Verify the DataFrame exists
        dataframe = self.executor.namespace.get("df")

        if not isinstance(dataframe, pd.DataFrame):
            print("Dataset loading failed: DataFrame was not created.")
            return False

        # Step 5: Update DatasetManager's state
        self.original_file = file_path
        self.current_file = file_path
        self.file_type = file_type
        self.dataframe = dataframe
        self.last_operation = "Dataset Loaded"

        # Step 6: Report the result
        print(f"Dataset Loaded: {file_path.name}")
        print(f"Shape: {self.dataframe.shape}")

        return {
            "success": True,
            "file_path": str(self.current_file),
            "file_name": self.current_file.name,
            "shape": self.dataframe.shape
            }


    def show_active_dataset(self):

        # Step 1: Check whether a dataset is loaded.
        if self.current_file is None or self.dataframe is None:
            return {
                "success": False,
                "message": "No active dataset is loaded."
            }

        # Step 2: Prepare the dataset metadata.
        dataframe = self.dataframe

        dataset_info = {
            "type": "dataset_viewer",
            "success": True,
            "file_name": self.current_file.name,
            "file_path": str(self.current_file),
            "file_type": self.file_type,
            "row_count": len(dataframe),
            "column_count": len(dataframe.columns),
            "last_operation": self.last_operation,
            "columns": [str(column) for column in dataframe.columns]
        }

        # Step 3: Publish the viewer request to Brain.
        if self.dataset_viewer_callback is None:
            return {
                "success": False,
                "message": "Dataset viewer callback is not configured."
            }

        self.dataset_viewer_callback.dataset_viewer_output = dataset_info

        # Step 4: Return a concise result to GLACIER.
        return {
            "success": True,
            "message": (
                f"Dataset viewer requested for '{self.current_file.name}'. "
                f"The dataset contains {len(dataframe):,} rows and "
                f"{len(dataframe.columns)} columns."
            )
        }


    def drop_dataset(self):
    # Check whether a dataset is currently loaded.
        if self.dataframe is None:
            return {
                "success": False,
                "message": "No active dataset is currently loaded."
            }

        # Remove the active dataset from memory.
        self.dataframe = None

        return {
            "success": True,
            "message": "The active dataset has been removed successfully."
        }



    
# -----------------------------------------------------TESTS

# manager=DatasetManager()
# manager.load_dataset(
#     r"C:\Main\GLACIER\data\amazon_sales_data_uncleaned.csv"
# )

# manager.load_into_executor()
# manager.executor.execute("df = df.drop_duplicates()")

# manager.sync_dataframe()

# manager.show_active_dataset()






# ---------------------------------------------FINAL TEST OF DatasetManager

# manager = DatasetManager()

# # 1 select the dataset 

# selected=manager.load_dataset(r"C:\Main\GLACIER\data\amazon_sales_data_uncleaned.csv")

# if selected:
     
#     # 2 actually load the dataset through python executioner 
#     loaded= manager.load_into_executor()

#     if loaded:
#         print("\n--- ACTIVE DATASET ---")
#         manager.show_active_dataset()


#         # 3 perform a python operation through the executor 
#         result = manager.executor.execute(
#             "df=df.drop_duplicates()"
#         )

#         if result['success']:

#             # 4 synchronized the changed DataFrame 
#             manager.sync_dataframe()

#             print("\n--- AFTER CLEANING OPERATION ---")
#             manager.show_active_dataset()


#         else:
#             print(f"python execution failed: {result['error']}")

#     else:
#         print('failed to load the data')

# else:
#     print("failed to select the data")\






#------------------------------------------Table Generation
# Test show_active_dataset()

# if __name__ == "__main__":
#     manager = DatasetManager()

#     manager.load_dataset("amazon_sales_data_cleaned.csv")

#     result = manager.show_active_dataset()
#     print("\nTEST RESULT:")
#     print(result)

#     app = QApplication.instance()

#     if app is not None:
#         app.exec()

# python -m tools.dataset_management