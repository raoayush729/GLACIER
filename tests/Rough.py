import pandas as pd
import statistics as st
from pathlib import Path
import matplotlib.pyplot as plt

# df=pd.read_csv(r"C:\Main\GLACIER\data\amazon_sales_data_uncleaned.csv")


# m=df.isnull().sum()
# print(m)
# print(df.columns)
# print(len(df))
# print(df["Rating"].nunique())
# print(df["Rating"])
# print(df.dtypes)
# print(df["is_best_seller"].mode())

df = pd.read_csv(r"C:\Main\GLACIER\data\Uncleaned data\amazon_sales_data_uncleaned.csv")
# print(df.dtypes)
# df2 = pd.read_csv(r"C:\Main\GLACIER\data\amazon_sales_data_uncleaned.csv")
# print(df2.dtypes)

x = "Rating"
y = "Number_of_reviews"
plt.bar(df[x],df[y])

# Labels
plt.xlabel(x)
plt.ylabel(y)


plt.show()

# ------------Types of memory for glacier to remember 
# Conversation:
# "What is the average rating?"
# → probably temporary

# Fact:
# "My name is Ayush."
# → persistent

# Preference:
# "Explain technical concepts slowly."
# → persistent

# Project context:
# "GLACIER uses qwen3..."
# → persistent/project memory

# Temporary task:
# "Analyze this CSV."
# → probably temporary

#                  CHATGPT
#                     │
#         ┌───────────┴───────────┐
#         ↓                       ↓
#    Chat history          Saved memories
#         │                       │
#    full conversations      selected facts
#         │                       │
#         └───────────┬───────────┘
#                     ↓
#              Relevant context
#                     ↓
#                    GPT


# There are actually three separate operations:

# 1. STORE
#    ↓
#    Data is written to disk.

# 2. RETRIEVE
#    ↓
#    We search storage for something relevant.

# 3. SEND TO MODEL
#    ↓
#    Only the retrieved information becomes part of the model's current input.



# unpacking of a dicitonary using ** operators
# def abc(a,b="rao"):
#     print(a+b)

# x={"a":"ayush"}

# method = abc(**x)   # this one





# a="            my name is ayush             j"
# print(a.strip())  
# print (a)  
# print(a.upper())




# for prompt, expect in test_cases:
#     print((prompt))
#     print((expect))





# a = {"success":False}

# if a["success"]:
#     print("hello")




# a = {2,34,3445,56,676,868,87,56,4,46,36,3,7}
# print (type(a))

# a = "Hello My name is ayush"

# print(a.split())



file_path = "dirty cafe dataset.csv"
a = Path(file_path)
print(a.stem.lower())










# but why do we need to save the history ? in self.messages ? i mean in the terminal it behaves just like a chat of claude gpt or gemini so i want the same thing here if we are not running the file again and again instead we are making a loop then the flow should be simple we shouldnt have to save the history by ourselves and self.messages is totally useless cuz all it does is pass the previous convo to next one as a prompt so its the same thing if chat becomes big the time qwen will take more to evaluate the prompt 

# so that isnt an option 

# the flow needs to be like this 



# user request: load the dataset

# now look here


# # ------------------------------------------------------TESTS
# # manager = DatasetManager()
# # manager.load_dataset(r"C:\Main\GLACIER\data\Cleaned data\amazon_sales_data_cleaned.csv")
# # manager.load_into_executor()
# # statistics = Statistics(manager)






# # # ---------------------------------------Statistics inspection
# # # print("\n -------------------Statistical inspection-------------------")
# # # statistical_report = statistics.inspect_statistical_data()

# # # print("\n STATISTICAL REPORT")



# this was when we were testing statistics see how we loaded the dataset then performed all the tests using that same statistics variable thats the flow i want for our glacier continuity 



# load_dataset is called 1 time only and stored into a variable then all the other tools are gonna use that so we might need to change alot in the 









# import inspect

# def analyze_missing_values(self):
#     return "Missing values analyzed"

# signature = inspect.signature(analyze_missing_values)

# print(signature)



# def loaddata(self,file_path):
#     return "Missing values analyzed"

# signature = inspect.signature(loaddata)

# print(signature)



# import sys

# print("Complete argument list:", sys.argv)

# print("Program name:", sys.argv[0])

# if len(sys.argv) > 1:
#     print("First argument:", sys.argv[1])

# if len(sys.argv) > 2:
#     print("Second argument:", sys.argv[2])


# l = [1023,3423,"ayush","load the dataset", 348342,23454,654,7865,234]
# while True:
#     a = input("enter anything: ")
#     l.append(a)
#     if len(l) > 10:
#         l.pop(4)
#     print(l)
