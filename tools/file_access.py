from pathlib import Path  # - Main module for files and folders 
import os # - operating system interaction
import platform # - Identify the operating system 


# creating home directory
home= Path.home()
print(f"home: {home}")


# creating paths for common folder
desktop= home/"Desktop"
download=home/"Downloads"
documents=home/"documents"


# Creating for all directories 
class FileAccess:

    def check_path(self, path):

        directory = Path(path)

        if directory.exists():
            return("Path exists")

        else:
            return("Path does not exist")


    def identify_path(self,path):
        item = Path(path)
        if not item.exists():
            return('path does not exist')
        elif item.is_file():
            return("This is a file")
        elif item.is_dir():
            return('this is a directory')


    def list_items(self, path):
        directory = Path(path)

        # Check whether the provided path is a directory.
        if not directory.is_dir():
            return {
                "success": False,
                "message": "The provided path is not a directory.",
                "path": str(directory),
                "items": []
            }

        # Store the directory contents.
        items = []

        for item in directory.iterdir():
            if item.is_file():
                items.append({
                    "name": item.name,
                    "type": "file",
                    "path": str(item)
                })

            elif item.is_dir():
                items.append({
                    "name": item.name,
                    "type": "directory",
                    "path": str(item)
                })

        # Return the results directly to Glacier.
        return {
            "success": True,
            "path": str(directory),
            "items": items,
            "total_items": len(items)
        }


    def get_file_type(self, file_path):

        item = Path(file_path)

        if item.is_file():
            return item.suffix.lower()

        else:
            return("This is not a valid file")


    def search_file(self,directory_path,file_name):

        if str(directory_path).lower().strip() in ["desktop", "my desktop"]:
            directory_path = self.get_location("desktop")

            print("RESOLVED DESKTOP PATH:", repr(directory_path))
            print("DIRECTORY EXISTS:", Path(directory_path).is_dir() if directory_path else False)
            if directory_path is None:
                print("Desktop location could not be found.")
                return None
            
        directory = Path(directory_path)

        supported_files=[".csv", ".xlsx", ".xls", ".json"]

        if directory.is_dir():

            matches=[]

            keywords = Path(file_name).stem.lower().split()

            for item in directory.rglob("*"):  

                try:
                    if item.is_file():

                        file_type=item.suffix.lower()

                        requested_name = Path(file_name).stem.lower()
                        keywords = requested_name.replace("_", " ").split()

                        item_name = item.stem.lower().replace("_", " ")

                        if file_type in supported_files:
                            for word in keywords:
                                if word in item_name:
                                    matches.append(item)
                                    break
                                
                except PermissionError:
                    continue

            if len(matches) == 0:
                print('File Not Found')

            elif len(matches) == 1:
                print(f"File Found: {matches[0]}")
                return matches[0]

            else:
                print(f"Sir, we have {len(matches)} files matching '{file_name}', which one should I take?")
                for m in matches:
                    print(f" - {m.name}")
                return matches        
                 
        else:
            print('Invalid Directory')


    def get_location(self, location_name):

        if not isinstance(location_name, str):
            print("Location name must be a string.")
            return False
        
        locations = {
            "desktop": Path.home() / "OneDrive" / "Desktop",
            "downloads": Path.home() / "Downloads",
            "documents": Path.home() / "Documents",
            "pictures": Path.home() / "Pictures",
            "videos": Path.home() / "Videos",
        }

        location = location_name.lower()

        if location in locations:

            path = locations[location]

            if path.is_dir():
                return path

            else:
                return(f"{location_name} folder does not exist.")

        else:

            return("Location not recognized.")


    def get_path(self, path):

        item = Path(path)

        if item.exists():

            return item

        else:

            print(f"Path does not exist: {path}")
            return None


    def get_file_info(self, file_path):

        item = Path(file_path)

        if item.is_file():

            return {
                "name": item.name,
                "path": item,
                "type": item.suffix.lower(),
                "location": item.parent
            }

        else:

            print("Invalid file")
            return None










# --------------------------------------TESTS
# file_access = FileAccess()


# # 1. Common location
# desktop = file_access.get_location("desktop")
# print(desktop)


# # 2. Arbitrary path
# custom_path = file_access.get_path(r"C:\Main")
# print(custom_path)


# # 3. Search for a file
# sales_file = file_access.search_file("desktop","sales")
# print(sales_file)




# sales_file = file_access.search_file(desktop, "sales")
# print(sales_file)


# -------------------------------------------------ALL FUNCTIONS CALLING 

# file_access.check_path(r"C:\Users\ayush")
# file_access.identify_path(r"C:\Users\ayush")
# file_access.list_items(r"C:\Users\ayush")
# filetype=file_access.get_file_type(r"C:\Main\passwords.txt")
# print(filetype)
# file_access.search_file(r"C:\Main",'sales')
# desktop = file_access.get_location("Documents")
# print(desktop)
# getpath=file_access.get_path(r"C:\Drivers\Bluetooth")
# print(getpath)
# info = file_access.get_file_info(
#     r"C:\Main\DA projects\Amazon Sales Data\Data\amazon_sales_data_uncleaned.csv")
# print(info)











