# bar_chart() — Compare categories or groups.
# line_chart() — Show trends over time.
# scatter_plot() — Show relationships between two numeric variables.
# histogram() — Show the distribution of numeric data.
# box_plot() — Visualize spread and outliers.
# density_plot() — Show the smooth distribution shape.
# count_plot() — Show counts of categorical values.
# joint_plot() — Show relationship plus distributions.
# correlation_heatmap() — Visualize correlations between numeric columns.
# pair_plot() — Visualize relationships among multiple numeric columns.




import matplotlib
matplotlib.use("Agg")          # draw to files, never open a window
import matplotlib.pyplot as plt
import pandas as pd 
import seaborn as sns
from tools.dataset_management import DatasetManager
import os, time
from pathlib import Path
import os, time

CHART_DIR = Path.home() / "GLACIER_charts"

class Visualisation:



    def __init__(self,dataset_manager):
        self.dataset_manager = dataset_manager
        print("\nVisualisation Initialized. ")

        

    def _save_chart(self, name):

        CHART_DIR.mkdir(exist_ok=True)
        path = CHART_DIR / f"{name}_{int(time.time())}.png"
        plt.tight_layout()
        plt.savefig(path, dpi=150)
        plt.close("all")
        os.startfile(path)          # opens in your image viewer without blocking
        return str(path)


    def bar_chart(self,x,y):
        df = self.dataset_manager.dataframe

        if df is None:
            print("No Active Dataset.")
            return False

        if x not in df.columns:
            print(f"Column '{x}' not found.")
            return False

        if y not in df.columns:
            print(f"Column '{y}' not found.")
            return False

        # bar chart
        plt.bar(df[x],df[y])

        # Labels
        plt.xlabel(x)
        plt.ylabel(y)

        # title
        plt.title(f"{y} by {x} (Bar Chart)")

        # display
        self._save_chart("bar_chart")


    def line_chart(self, x, y):

        df = self.dataset_manager.dataframe

        if df is None:
            print("No Active Dataset.")
            return False

        if x not in df.columns:
            print(f"Column '{x}' not found.")
            return False

        if y not in df.columns:
            print(f"Column '{y}' not found.")
            return False

        # Create a line chart using X and Y columns
        plt.plot(df[x], df[y])

        # Add labels to the axes
        plt.xlabel(x)
        plt.ylabel(y)

        # Add a title
        plt.title(f"{y} vs {x} (Line chart)")

        # Display the chart
        self._save_chart("line_chart")

    def scatter_plot(self, x, y):

        df = self.dataset_manager.dataframe

        if df is None:
            print("No Active Dataset.")
            return False

        if x not in df.columns:
            print(f"Column '{x}' not found.")
            return False

        if y not in df.columns:
            print(f"Column '{y}' not found.")
            return False

        # Create a scatter plot to show the relationship between X and Y
        plt.scatter(df[x], df[y])

        # Add labels to the axes
        plt.xlabel(x)
        plt.ylabel(y)

        # Add a title
        plt.title(f"{y} vs {x} (Scatter Plot)")

        # Display the chart
        self._save_chart("scatter_plot")


    def histogram(self, column):

        df = self.dataset_manager.dataframe

        if df is None:
            print("No Active Dataset.")
            return False

        if column not in df.columns:
            print(f"Column '{column}' not found.")
            return False

        # Create a histogram to show the distribution of the column
        plt.hist(df[column].dropna())

        # Label the X-axis
        plt.xlabel(column)

        # Label the Y-axis as frequency
        plt.ylabel("Frequency")

        # title
        plt.title(f"Distribution of {column} (Histogram)")

        # Display  
        self._save_chart("histogram")


    def box_plot(self, column):

        df = self.dataset_manager.dataframe

        if df is None:
            print("No Active Dataset.")
            return False

        if column not in df.columns:
            print(f"Column '{column}' not found.")
            return False

        # box plot 
        plt.boxplot(df[column].dropna())

        # Add a label to the Y-axis
        plt.ylabel(column)

        # Add a title
        plt.title(f"Box Plot of {column}")

        # Display
        self._save_chart("box_plot")


    def density_plot(self, column):

        df = self.dataset_manager.dataframe

        if df is None:
            print("No Active Dataset.")
            return False

        if column not in df.columns:
            print(f"Column '{column}' not found.")
            return False

        # Seaborn creates the smooth density curve for the selected column
        sns.kdeplot(data=df, x=column)            # KDE = Kernel Density Estimation

        # Add a title
        plt.title(f"Density Plot of {column}")

        # Display
        self._save_chart("density_plot")


    def count_plot(self, column):

        df = self.dataset_manager.dataframe

        if df is None:
            print("No Active Dataset.")
            return False

        if column not in df.columns:
            print(f"Column '{column}' not found.")
            return False

        # Seaborn counts how many times each category appears
        sns.countplot(data=df, x=column)         # count plot = plot the count/frequency of values. False → 35,000, True → 6,713


        # Add a title
        plt.title(f"Count of {column} (Count Plot)")

        # Display
        self._save_chart("count_plot")


    def joint_plot(self, x, y):

        df = self.dataset_manager.dataframe

        if df is None:
            print("No Active Dataset.")
            return False

        if x not in df.columns:
            print(f"Column '{x}' not found.")
            return False

        if y not in df.columns:
            print(f"Column '{y}' not found.")
            return False
        
        # Seaborn creates a relationship plot with distributions
        sns.jointplot(data=df, x=x, y=y)

        # title
        plt.title("Joint plot")
        # Display the chart
        self._save_chart("joint_plot")


    def pair_plot(self):

        df = self.dataset_manager.dataframe

        if df is None:
            print("No Active Dataset.")
            return False

        # Select only numeric columns for pairwise relationship analysis
        numeric_df = df.select_dtypes(include="number")

        # Seaborn automatically creates plots for every pair of columns
        sns.pairplot(numeric_df)

        # Display the charts
        self._save_chart("pair_plot")






# ============================================================
# VISUALIZATION TESTS
# ============================================================



if __name__ =="__main__":
    manager = DatasetManager()
    manager.load_dataset(r"C:\Main\GLACIER\data\Cleaned data\amazon_sales_data_cleaned.csv")
    Visualizer = Visualisation(manager)
    # 1. BAR CHART
    # Compare Rating values with Number_of_reviews
    Visualizer.bar_chart(
        "Rating",
        "Number_of_reviews"
    )


# # 2. LINE CHART
# # Show how Number_of_reviews changes across Rating values
# Visualizer.line_chart(
#     "Rating",
#     "Number_of_reviews"
# )


# # 3. SCATTER PLOT
# # Show the relationship between Rating and Number_of_reviews
# Visualizer.scatter_plot(
#     "Rating",
#     "Number_of_reviews"
# )


# # 4. HISTOGRAM
# # Show the distribution of Rating
# Visualizer.histogram(
#     "Rating"
# )


# # 5. BOX PLOT
# # Show spread and possible outliers in Number_of_reviews
# Visualizer.box_plot(
#     "Number_of_reviews"
# )


# # 6. DENSITY PLOT
# # Show the smooth distribution of Rating
# Visualizer.density_plot(
#     "Rating"
# )


# # 7. COUNT PLOT
# # Count how many products belong to each best-seller category
# Visualizer.count_plot(
#     "is_best_seller"
# )


# # 8. JOINT PLOT
# # Show Rating and Number_of_reviews together
# # plus their individual distributions
# Visualizer.joint_plot(
#     "Rating",
#     "Number_of_reviews"
# )


# # 9. PAIR PLOT
# # Show relationships/distributions among multiple numeric columns
# Visualizer.pair_plot()
























