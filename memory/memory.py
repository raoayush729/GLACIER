
# ---------------------------------------------------------
# PHASE 8 — GLACIER MEMORY MANAGER
# This file is also a tool file just like data_cleaning , statistics.py, visualization.py
# but these tools will be called on some voice commands like 
# my name is ayush
# glacier uses Ollama with qwen 
# im a data analyst student 
# something that should be stored in a memory for glacier to remember always 
# ---------------------------------------------------------


# Step 1
# Temporary conversation memory
#         ↓
# Python list

# Step 2
# Persistent important memories
#         ↓
# Simple JSON

# Step 3
# Persistent scalable memory
#         ↓
# SQLite

# Step 4
# Memory retrieval
#         ↓
# Find only relevant memories

# Step 5
# Agent decides
#         ↓
# "Should I save this?"
# "Should I retrieve something?"




# Types of memory to store 

# USER
# → Who is the user?

# PREFERENCE
# → How should GLACIER behave?

# PROJECT
# → What belongs to a particular project?

# TASK
# → What are we doing right now?

# SESSION
# → What was just discussed?

# HISTORY
# → What happened in the past?

# ENVIRONMENT
# → What does GLACIER know about the laptop?

# WORKFLOW
# → How should a job be performed?


# flow
# GLACIER starts
#       ↓
# MemoryManager object created
#       ↓
# create/find memory folder
#       ↓
# load old memory.json
#       ↓
# store old memories in self.memories
#       ↓
# Now GLACIER can add new memories
#       ↓
# add_memory()
#       ↓
# save_memory()
#       ↓
# memory.json gets updated


import json
from pathlib import Path
from datetime import datetime
import uuid


class MemoryManager:

    def __init__(self, memory_file=r"C:\Main\GLACIER\memory\memory.json"):
        # Store the location of the memory file.
        self.memory_file = Path(memory_file)

        # Create the memory folder if it does not already exist.
        self.memory_file.parent.mkdir(parents=True,exist_ok=True)         # mkdir() is a path method that creates a directory/folder.
#                                                                         # parents=True means: If parent folders (memory\) are missing, create them too.
#                                                                         # exist_ok=True Means: If the folder already exists, don't give an error. continue


        # crate empty list to temporarily Store all loaded memories in this list.
        self.memories=[]

        # Load previously saved memories when MemoryManager starts.
        self.load_memory()

        print("\nMemory Manager Initialized.")
        print(f"Memory file: {self.memory_file}")


    def load_memory(self):         # basically converting memory.json - Python memory(self.memories)

        # Check whether the memory file already exists.  Right now = this if block is somewhat redundant.
        #                                                but as a defensive design = useful.
        if not self.memory_file.exists():
            self.memories=[]      # if No memory file  → self.memories must be []
            return True       # Tell the caller of this function that its true that file does not exist.

        # Open the memory file in read mode.
        with open(self.memory_file,"r",encoding="utf-8") as file:    # as file this variable represents the opened file.
            self.memories = json.load(file)           # load() A json function that reads JSON data from an open file and converts it into Python data.
#                                                     # so here the file opened with open() func is getting stored inside self.memories

    def add_memory(self, content):

        # Step 1: Create the memory record.
        memory = {
            "content": content
        }

        # Step 2: Add the memory to the temporary memory list.
        self.memories.append(memory)

        # Step 3: Return the created memory.
        return memory
    

    def save_memory(self):      # basically converting  Python memory → memory.json    

        # load_memory()
        # → file → Python

        # save_memory()
        # → Python → file

        # Open the memory file in write mode.
        with open(self.memory_file,"w",encoding="utf-8") as file:

            # Convert Python data into JSON and save it.
            json.dump(               # dump() A json function that converts Python data into JSON and writes it to an open file.
                self.memories,        # what to store
                file,                 # inside where to store
                indent=4,           # indent=4 means use four spaces for indentation when formatting the JSON.
                ensure_ascii=False  # This is useful for preserving normal Unicode characters. like ₹, é, 中文
            )
        return True   # Tell the caller of this function that saving completed successfully.


    def get_memories(self):       # give us the memories currently loaded in Python
        # Return all stored memories.
        return self.memories


    def delete_memory(self, memory_id):
    
        # Go through every memory currently loaded in Python.
        for memory in self.memories:

            # Check whether this memory has the ID we want to delete.
            if memory["id"] == memory_id:

                # Remove this memory from the Python memory list.
                self.memories.remove(memory)

                # Save the updated memory list to memory.json.
                self.save_memory()

                # Tell the caller that deletion was successful.
                return True

        # If the loop finishes without finding the ID,
        # the requested memory does not exist.
        return False


# ---------------------------------------------------TESTS

# RUN 1 (saving 1st memory which will be my name )
if __name__ == "__main__":

    memory_manager = MemoryManager()

    memory_manager.add_memory(
        content="My name is Ayush.",
        memory_type="personal",
        scope="user",
        importance="high",
        lifetime="long_term"
    )

    memory_manager.save_memory()

    print("\nMemory saved successfully.")

    print("\nCurrent memories:")
    print(memory_manager.memories)


# RUN 2 (getting the memories that we saved checks if it actually got saved and retriavable or not)
# if __name__ == "__main__":

#     # Create the MemoryManager.
#     # __init__() will automatically call load_memory().
#     memory_manager = MemoryManager()

#     # Get the memories that were loaded from memory.json.
#     memories = memory_manager.get_memories()

#     print("\nMemories loaded after restarting GLACIER:")

#     print(memories)


# RUN 3 (removing the save_memory from add_memory because both should be called saparately as a function)
# if __name__ == "__main__":

#     # Create the MemoryManager.
#     memory_manager = MemoryManager()

#     # Add a new memory to the Python memory list.
#     result = memory_manager.add_memory(
#         content="GLACIER is my personal AI assistant.",
#         memory_type="project",
#         scope="glacier",
#         importance="high",
#         lifetime="long_term"
#     )

#     print("\nMemory added:", result)

#     # Show the current Python memory list.
#     print("\nCurrent memories:")
#     print(memory_manager.get_memories())

#     # Save the current memories to memory.json.
#     save_result = memory_manager.save_memory()

#     print("\nMemory saved:", save_result)


# RUN 3 (to delete any perticular memory with id number)
# if __name__ == "__main__":

#     # Create the MemoryManager.
#     memory_manager = MemoryManager()

#     print("\nMemories before deletion:")
#     print(memory_manager.get_memories())

#     # Delete memory with ID 2.
#     result = memory_manager.delete_memory()

#     print("\nMemory deleted:", result)

#     print("\nMemories after deletion:")
#     print(memory_manager.get_memories())