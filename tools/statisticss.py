# CLEANED DATA 

# ┌──────────────────────────────┐
# │ 1. STATISTICAL INSPECTION    │
# └──────────────┬───────────────┘

    # Before doing statistics, GLACIER needs to determine:

    # Which columns are numeric
    # Which are categorical
    # Number of observations
    # Missing values
    # Unique values
    # Whether a column is appropriate for a particular analysis


# ┌──────────────────────────────┐
# │ 2. DESCRIPTIVE STATISTICS    │
# └──────────────┬───────────────┘
# This will be our first major section.

# GLACIER should be able to answer:

# "What does this data look like numerically?"

# We'll cover:

# Central tendency

# Mean

# Median

# Mode

# Spread

# Range

# Variance

# Standard deviation

# Position

# Quartiles

# Percentiles

# These are the basic building blocks for understanding a dataset.


# ┌──────────────────────────────┐
# │ 3. DISTRIBUTION ANALYSIS     │
# └──────────────┬───────────────┘
#
# deal with:

# Skewness
# Kurtosis
# Normal distribution
# Understanding distribution shape

# This becomes useful later when deciding which statistical test makes sens


# ┌──────────────────────────────┐
# │ 4. OUTLIER ANALYSIS          │
# └──────────────┬───────────────┘
# Then we'll teach GLACIER to identify unusual observations.

# For example:

# 10
# 12
# 11
# 13
# 12
# 14
# 11
# 500  ← suspicious

# We'll use:

# IQR method
# Q1
# Q3
# IQR = Q3 - Q1

# and determine whether observations fall outside the normal range.

# Z-score method

# We'll also use standard deviation-based detection.

# And importantly, GLACIER shouldn't automatically delete outliers.

# It should identify them and potentially report:

# "These observations are unusual. Investigate before removing."

# That's much more appropriate for a professional analytics system.


# ┌──────────────────────────────┐
# │ 5. RELATIONSHIP ANALYSIS     │
# └──────────────┬───────────────┘
# covering:

# Covariance

# Tells whether two variables tend to move together.

# Correlation

# Tells both the direction and strength of their relationship.

# For example:

# Price ↑

# Sales ↓

# could indicate a negative relationship.

# We'll eventually cover:

# Pearson correlation
# Spearman correlation
# Correlation matrix

# And we'll be careful about the classic rule:

# Correlation ≠ causation.


# ┌──────────────────────────────┐
# │ 6. HYPOTHESIS TESTING        │
# └──────────────┬───────────────┘
# This will be one of the bigger sections because you've already learned some of it.

# We'll revise:

# H₀ → Null Hypothesis
# H₁ → Alternative Hypothesis
# α  → Significance Level
# p-value
# Critical value
# Test statistic

# Then:

# Z-test

# You'll revise:

# Formula
# One-tailed
# Two-tailed
# Critical values
# p-value approach
# Decision
# T-test

# We'll revise:

# One-sample t-test
# Independent two-sample t-test
# Paired t-test
# One-tailed / two-tailed

# You already know the basic concept, so we'll build the actual GLACIER implementation around it.


# 6.1 Other Hypothesis Tests


# Z-test
# T-test

# We'll introduce other important tests gradually.

# ANOVA

# This will be a major one.

# Instead of asking:

# "Are these two means different?"

# ANOVA helps answer:

# "Are the means of multiple groups significantly different?"

# For example:

# Amazon product category

# Electronics → average price
# Home        → average price
# Clothing    → average price
# Books       → average price


# F-statistic, between-group variation, within-group variation, p-value and the conclusion when we reach ANOVA.

# Chi-square test
# Other appropriate tests depending on the type of data/question

# We won't blindly add every statistical test that exists. We'll focus on tests useful for a Data Analyst and eventually useful to GLACIER.


# ┌──────────────────────────────┐
# │ 7. CONFIDENCE INTERVALS      │
# └──────────────┬───────────────┘

# GLACIER should eventually be able to answer things like:

# "What's the 95% confidence interval for the average rating?"

# We'll revisit:

# Point estimate
# Margin of error
# Confidence level
# Lower bound
# Upper bound

# And you'll get the formulas again when we actually implement it.


# ┌──────────────────────────────┐
# │ 8. STATISTICAL DECISION      │
# └──────────────┬───────────────┘
# This is where raw mathematical results become an analyst's conclusion.

# Instead of GLACIER saying:

# p-value = 0.032

# we eventually want:

# Significance level = 5%

# p-value = 0.032

# Since p-value < 0.05:
# Reject H₀.

# Conclusion:
# There is statistically significant evidence
# of a difference between the groups.

# That's much closer to what an actual analyst needs.


# ┌──────────────────────────────┐
# │ 9. STATISTICAL REPORT        │
# └──────────────────────────────┘
# Finally:

# ========== STATISTICAL REPORT ==========

# Dataset: Amazon Sales

# Observations: 41,713

# DESCRIPTIVE STATISTICS
# ...

# DISTRIBUTION
# ...

# OUTLIERS
# ...

# CORRELATIONS
# ...

# HYPOTHESIS TESTS
# ...

# CONFIDENCE INTERVALS
# ...

# CONCLUSIONS
# ...




import pandas as pd
from tools.dataset_management import DatasetManager
import math
from scipy.stats import norm, t, f, chi2_contingency, chi2


# # Temporary dataset used only for testing ANOVA
# anova_df = pd.DataFrame({

#         # 15mg group
#         "15mg": [9, 8, 7, 8, 9, 8, 9],

#         # 30mg group
#         "30mg": [6, 7, 6, 5, 7, 6, 6],

#         # 45mg group
#         "45mg": [3, 4, 2, 3, 4, 3, 3]
#     })

class Statistics:

    def __init__(self, dataset_manager):
        self.dataset_manager = dataset_manager
        print("\nStatistics Initialized.")

    # Inspection of the data
    def inspect_statistical_data(self):
        df = self.dataset_manager.dataframe

        if df is None:
            print("No active Dataset")
            return False

        statistical_report = {}

        for column in df.columns:
            dtype = df[column].dtype
            missing = df[column].isnull().sum()
            unique = df[column].nunique()

            numeric = pd.api.types.is_numeric_dtype(df[column])


            statistical_report[column] = {
                "dtype" : str(dtype),
                "missing" : int(missing),
                "unique" : int(unique),
                "is_numeric" : bool(numeric)
            }
        return statistical_report

    # Descriptive Statistics 
    def calculate_descriptive_stats(self):
        df = self.dataset_manager.dataframe
        if df is None:
            print('No Active dataset')
            return False

        descriptive_report = {}

        for column in df.columns:
            if pd.api.types.is_numeric_dtype(df[column]) and not pd.api.types.is_bool_dtype(df[column]):               # Checks whether the current column contains numeric data AND is not a boolean column because python treats boolean as a numeric value and creates error

                mode_value = df[column].mode()
                if mode_value.empty:        # If theres no mode store None Otherwise take the first mode value and store it in mode
                    mode = None
                else:
                    mode=mode_value.iloc[0]      # mode function does not gives a single value it give index, mode, name, dtype so we need to select 0th index element which will be the mode 
                minimum = df[column].min()
                maximum = df[column].max()

                descriptive_report[column] = {
                    "mean" : df[column].mean(),
                    "median" : df[column].median(),
                    "mode" : mode,
                    "min" : minimum,
                    "max" : maximum,
                    "range" : maximum-minimum,
                    "std" : df[column].std(),
                    "varience" : df[column].var(),
                    "q1":df[column].quantile(0.25),
                    "q2":df[column].quantile(0.50),
                    "q3":df[column].quantile(0.75),
                    "iqr":df[column].quantile(0.75) - df[column].quantile(0.25)
                    }
        return descriptive_report

    # Data Distribution
    def analyze_distribution(self):

        df = self.dataset_manager.dataframe

        if df is None:
            print("No Active Dataset")
            return False

        distribution_report = {}

        for column in df.columns:

            if pd.api.types.is_numeric_dtype(df[column]) and not pd.api.types.is_bool_dtype(df[column]):   # Checks whether the current column contains numeric data AND is not a boolean column because python treats boolean as a numeric value and creates error
                skewness = df[column].skew()
                kurtosis = df[column].kurt()

                distribution_report[column] = {
                    "skewness" : skewness,
                    "kurtosis" : kurtosis         
                }
        return distribution_report

    # Analyze Outliers
    def analyze_outliers(self):

        df = self.dataset_manager.dataframe

        if df is None:
            print("No Active Dataset.")
            return False

        outlier_report = {}

        for column in df.columns:
            if pd.api.types.is_numeric_dtype(df[column]) and not pd.api.types.is_bool_dtype(df[column]):
                q1 = df[column].quantile(0.25)
                q3 = df[column].quantile(0.75)
                iqr = q3 - q1
                lower_boundary = q1-(1.5*iqr)
                upper_boundary = q3+(1.5*iqr)
                below_lower = df[column] < lower_boundary
                above_upper = df[column] > upper_boundary   
                outliers = df[column][below_lower | above_upper]           # | means OR but we cannot use or keyword because A or B expects a true or false but here pandas gives a whole series of true and false and for that we have to use |, | means: OR this condition for each individual row.
                outliers_count= len(outliers)
                total_values = df[column].notna().sum()

                if total_values > 0:
                    outlier_percentage =    (outliers_count/total_values)*100
                else:
                    outlier_percentage = 0

                outlier_report[column] = {
                    "q1" :q1,
                    "q3" : q3,
                    "iqr" : iqr,
                    "lower_boundary": lower_boundary,
                    "upper_boundary": upper_boundary,
                    "outlier_count": outliers_count,
                    "outlier_percentage" : round(outlier_percentage,2)
                }
        return outlier_report

    
    # relationship / corelation
    def analyze_correlation(self,col1,col2):

        df = self.dataset_manager.dataframe

        if df is None:
            print("No Active Dataset.")
            return False

        if col1 not in df.columns:
            print(f"Column '{col1}' not found.")        # checks weather column 1 exist in the df
            return False

        if col2 not in df.columns:
            print(f"Column '{col2}' not found.")        # checks weather column 2 exist in the df
            return False

        if not pd.api.types.is_numeric_dtype(df[col1]):   # checks weather column 1 is numeric 
            print(f"Column '{col1}' is not numeric.")
            return False

        if not pd.api.types.is_numeric_dtype(df[col2]):    # checks weather column 2 is numeric 
            print(f"Column '{col2}' is not numeric.")
            return False

        if pd.api.types.is_bool_dtype(df[col1]):       # checks weather column 1 is bool
            print(f"Column '{col1}' is boolean.")
            return False

        if pd.api.types.is_bool_dtype(df[col2]):      # checks weather column 2 is bool
            print(f"Column '{col2}' is boolean.")
            return False
        
        corelation = round(df[col1].corr(df[col2]),2)        # main function to execute the corelation

        return corelation


    # covariance
    def analyze_covariance(self, col1, col2):

        df = self.dataset_manager.dataframe

        if df is None:
            print("No Active Dataset.")
            return False

        if col1 not in df.columns:
            print(f"Column '{col1}' not found.")
            return False

        if col2 not in df.columns:
            print(f"Column '{col2}' not found.")
            return False

        if not pd.api.types.is_numeric_dtype(df[col1]):
            print(f"Column '{col1}' is not numeric.")
            return False

        if not pd.api.types.is_numeric_dtype(df[col2]):
            print(f"Column '{col2}' is not numeric.")
            return False

        if pd.api.types.is_bool_dtype(df[col1]):     # Checks whether the current column contains numeric data AND is not a boolean column because python treats boolean as a numeric value and creates error
            print(f"Column '{col1}' is boolean.")
            return False

        if pd.api.types.is_bool_dtype(df[col2]):         # Checks whether the current column contains numeric data AND is not a boolean column because python treats boolean as a numeric value and creates error
            print(f"Column '{col2}' is boolean.")
            return False        
        covariance = round(df[col1].cov(df[col2]),2)

        return covariance
    


    # Hypothesis Testing 
    def z_two_tailed_test(self, column, population_mean, significance_level):
        df = self.dataset_manager.dataframe

        if df is None:
            print("No Active Dataset.")
            return False
        if column not in df.columns:
            print(f"Column '{column}' not found.")
            return False
        if not pd.api.types.is_numeric_dtype(df[column]):             # Checks whether the current column contains numeric data AND is not a boolean column because python treats boolean as a numeric value and creates error
            print(f"Column '{column}' is not numeric.")
            return False    
        if pd.api.types.is_bool_dtype(df[column]):                     # Checks whether the current column contains numeric data AND is not a boolean column because python treats boolean as a numeric value and creates error
            print(f"Column '{column}' is boolean.")
            return False

        # Requirements 
        sample_mean = df[column].mean()
        sample_size = df[column].count()
        population_std = df[column].std()                
        if significance_level > 1:
            significance_level = significance_level / 100

        if significance_level <= 0 or significance_level >= 1:
            print("Significance level must be between 0 and 1")
            return False
            
        # z-score
        z_score = round((sample_mean - population_mean) / (population_std / math.sqrt(sample_size)),2)     # "The sample mean is (z_score) standard-error units away from the hypothesized mean."

        # critical value
        critical_value = round((norm.ppf(1 - significance_level/2)),2)    #norm = Normal Distribution , ppf = percent point function


        #Decision
        if z_score < -critical_value or z_score > critical_value:
            decision ="Reject Ho"
        else:
            decision = "fail to reject Ho"

        return f"z_score = {z_score}", f"critical_value = {critical_value}",f"decision = {decision}"



    def z_one_tailed_test(self, column, direction, population_mean, significance_level):
        df = self.dataset_manager.dataframe

        if df is None:
            print("No Active Dataset.")
            return False

        if column not in df.columns:
            print(f"Column '{column}' not found.")
            return False

        if not pd.api.types.is_numeric_dtype(df[column]):
            print(f"Column '{column}' is not numeric.")
            return False

        if pd.api.types.is_bool_dtype(df[column]):
            print(f"Column '{column}' is boolean.")
            return False

        # Convert 5 into 0.05 if the user enters significance level as 5
        if significance_level > 1:
            significance_level = significance_level / 100

        if significance_level <= 0 or significance_level >= 1:
            print("Significance level must be between 0 and 1")
            return False

        direction = direction.lower()    # normalize direction
         
        if direction != "left" and direction != "right":      # terminate the function if direction is anything except left or right
            print("Direction must be 'left' or 'right'.")
            return False

        # Requirements
        sample_mean = df[column].mean()                   
        sample_size = df[column].count()
        population_std = df[column].std(ddof=0)               #  (ddof=0)  bascially tells python not to substract anything from the observation

        # Calculate Z-score
        z_score = (sample_mean - population_mean) / (population_std / math.sqrt(sample_size))
        
        # One-tailed critical value
        critical_value = round(norm.ppf(1 - significance_level),2)


        if direction =="right" and z_score > critical_value:
            decision = "Reject Ho"
            p_value = 1 -norm.cdf(z_score)          # this lines is the formula for finding the p value using the z ditribution table
#                                                   # norm.cdf(z_score) → probability to the left of that Z-score

        elif direction == "right" and z_score <= critical_value:
            decision = "Fail to reject Ho"
            p_value =  1- norm.cdf(z_score)        # if the p value is less than significance level we reject null hypothesis if not we fail to reject null hypothesis

        elif direction == "left" and z_score < -critical_value:
            decision = "Reject Ho"
            p_value = norm.cdf(z_score)           # The CDF(Cumulative Distribution Function) asks:  "How much area under the normal curve is to the LEFT of Z = 2.10?

        elif direction == "left" and z_score >= -critical_value:
            decision = "Fail to Reject Ho"
            p_value = norm.cdf(z_score)


        return(
            f"z_score = {z_score}, "
            f"critical_value = {critical_value}, "
            f"p_value = {p_value}, "
            f"decision = {decision}, "
        )



    def t_two_tailed_test(self,column,population_mean,significance_level):

        df = self.dataset_manager.dataframe
        if df is None:
            print("No active Dataset")
            return False

        if column not in df.columns:
            print(f"Column {column} not found.")
            return False
        
        # Check whether the column contains numeric data
        if not pd.api.types.is_numeric_dtype(df[column]):
            print(f"Column '{column}' is not numeric.")
            return False

        # Reject boolean columns because True False should not be used for this test
        if pd.api.types.is_bool_dtype(df[column]):
            print(f"Column '{column}' is boolean.")
            return False

        # Convert 5 into 0.05 significance level 
        if significance_level > 1:
            significance_level = significance_level / 100

        # Make sure significance level is valid
        if significance_level <= 0 or significance_level >= 1:
            print("Significance level must be between 0 and 1.")
            return False
        
        # requirements
        sample_mean = df[column].mean()
        sample_size = df[column].count()
        sample_std = df[column].std(ddof= 1)      # ddof= 1 Calculate the standard deviation as a "SAMPLE" standard deviation, using n - 1 in the denominator. ddof=1 tells Pandas to use the "SAMPLE" standard deviation formula. otherwise it will take n instead of n-1 in the denominator and critical value will differ to 1 value 
        degree_of_freedom = sample_size -1

        # Calculating T statistic
        t_score = (sample_mean - population_mean) / (sample_std/math.sqrt(sample_size))

        # Calculating critical value for two tailed
        critical_value = t.ppf( 1-significance_level / 2, degree_of_freedom)       #t.ppf refers to the t distribution table it takes 2 parameters( probablity , degree of freedom) just like the formula

        # compare t statistic with crititcal value
        if t_score < -critical_value or t_score > critical_value:
            decision = "Reject Ho"
        else:
            decision = "fail to Reject Ho"

        # return the result
        return(
        f"t_score = {t_score}, "
        f"critical_value = {critical_value}, "
        f"degrees_of_freedom = {degree_of_freedom}, "
        f"decision = {decision}"
        )


    def t_test_one_tailed(self,column,direction,population_mean,significance_level):
        df = self.dataset_manager.dataframe

        if df is None:
            print("No Active Dataset")
            return False
         # Check whether the requested column exists
        if column not in df.columns:
            print(f"Column '{column}' not found.")
            return False

        # Check whether the column contains numeric data
        if not pd.api.types.is_numeric_dtype(df[column]):
            print(f"Column '{column}' is not numeric.")
            return False

        # Reject boolean columns
        if pd.api.types.is_bool_dtype(df[column]):
            print(f"Column '{column}' is boolean.")
            return False\


        # Convert 5 into 0.05 if significance level was entered as 5
        if significance_level > 1:
            significance_level = significance_level / 100

        # Check whether significance level is valid
        if significance_level <= 0 or significance_level >= 1:
            print("Significance level must be between 0 and 1.")
            return False

        direction = direction.lower()

        # Only left and right are accepeted
        if direction != "left" and direction != "right":
            print("Direction must be 'left' or 'right'.")
            return False


        # requirements
        sample_mean=df[column].mean()
        sample_size=df[column].count()
        sample_std=df[column].std(ddof=1)
        degree_of_freedom = sample_size -1

        # Calculate T score
        t_score = (sample_mean - population_mean) / (sample_std/math.sqrt(sample_size))

        # Calculate one-tailed critical T-value
        critical_value = t.ppf(1-significance_level,degree_of_freedom)


        # Right-tailed test
        if direction == "right" and t_score > critical_value:
            decision = "Reject Ho"

        elif direction == "right" and t_score <= critical_value:
            decision = "Fail to Reject Ho"

        if direction == "left" and t_score < -critical_value:
            decision = "Reject Ho"

        elif direction == "left" and t_score >= -critical_value:
            decision = "Fail to Reject Ho"


        # Return the test results
        return (
            f"t_score = {t_score}",
            f"critical_value = {critical_value}",
            f"degrees_of_freedom = {degree_of_freedom}",
            f"decision = {decision}"
        )





    def anova(self,columns,significance_level):

        df = self.dataset_manager.dataframe
        if df is None:
            print("No active Dataset")
            return False

        # Check whether at least two groups were provided
        if len(columns) < 2:
            print("ANOVA requires at least 2 groups.")
            return False

        # Check whether every requested column exists
        for column in columns:
            if column not in df.columns:
                print(f"Column '{column}' not found.")
                return False

        # Check whether every group contains numeric data
        for column in columns:
            if not pd.api.types.is_numeric_dtype(df[column]):
                print(f"Column '{column}' is not numeric.")
                return False

        # Convert 5 into 0.05 if significance level was entered as 5
        if significance_level > 1:
            significance_level = significance_level / 100


        # Check whether significance level is valid
        if significance_level <= 0 or significance_level >= 1:
            print("Significance level must be between 0 and 1.")
            return False

        # find how many levels/groups we have 
        a = len(columns)

        # Find how many observations are in each group
        group_sizes = []
        for column in columns:
            group_sizes.append(df[column].count())

        # ANOVA formula being used here assumes equal observations in each group
        if len(set(group_sizes)) != 1:
            print("All groups must contain the same number of observations.")
            return False

        # Number of observations in each group
        n = group_sizes[0]

        # Total number of observations
        N = a * n

        # Degrees of freedom between groups
        df_between = a - 1

        # Degrees of freedom within groups
        df_within = N - a

        # Find the total of every group separately
        group_totals = []

        for column in columns:
            group_total = df[column].sum()
            group_totals.append(group_total)

        # Find T by adding the totals of all groups
        T = sum(group_totals)

        # Calculate SS Between using formula:
        # SS Between = Σ((Σaᵢ)² / n) - T² / N
        ss_between_first_part = 0

        for group_total in group_totals:
            ss_between_first_part += (group_total ** 2) / n

        ss_between = ss_between_first_part - (T ** 2) / N

        # Find Σyᵢⱼ² by squaring every value in every group and adding them
        sum_of_squared_values = 0
        for column in columns:
            sum_of_squared_values += (df[column] ** 2).sum()

         # Calculate SS Within using your exact formula:
         # SS Within = Σyᵢⱼ² - Σ((Σaᵢ)² / n)
        ss_within = sum_of_squared_values - ss_between_first_part

        # Calculate MS Between
        ms_between = ss_between / df_between

        # Calculate MS Within
        ms_within = ss_within / df_within

        # Calculate F statistic
        f_statistic = ms_between / ms_within

        # Find F critical value from the F-distribution
        # For ANOVA, cumulative probability is 1 - significance level
        f_critical = f.ppf(
            1 - significance_level,
            df_between,
            df_within
        )

        # Compare F statistic with F critical value
        if f_statistic > f_critical:
            decision = "Reject Ho"
        else:
            decision = "Fail to reject Ho"



            # Return all important ANOVA results
        return (
            f"N = {N}",
            f"n = {n}",
            f"a = {a}",
            f"df_between = {df_between}",
            f"df_within = {df_within}",
            f"f_critical = {f_critical}",
            f"ss_between = {ss_between}",
            f"ss_within = {ss_within}",
            f"ms_between = {ms_between}",
            f"ms_within = {ms_within}",
            f"f_statistic = {f_statistic}",
            f"decision = {decision}"
        )


    # 1. H₀ / H₁
    # 2. α
    # 3. df = (rows - 1)(columns - 1)
    # 4. O = observed frequency
    # 5. E = expected frequency
    # 6. Calculate χ² = Σ((O-E)²/E)
    # 7. Find critical value
    # 8. Compare χ² with critical value
    # 9. Decision


    # Chi-square test of independence
    
    def chi_square_test(self, column1, column2, significance_level):

        # Get the active DataFrame
        df = self.dataset_manager.dataframe

        # Check whether a dataset is loaded
        if df is None:
            print("No Active Dataset.")
            return False

        # Check whether the first column exists
        if column1 not in df.columns:
            print(f"Column '{column1}' not found.")
            return False

        # Check whether the second column exists
        if column2 not in df.columns:
            print(f"Column '{column2}' not found.")
            return False

        # Create the observed frequency table from the two categorical columns
        observed = pd.crosstab(df[column1], df[column2])        # pd.crosstab() — a Pandas function used to create a frequency table showing how often combinations of values from two categorical variables occur.


        # Convert 5 into 0.05 if significance level was entered as 5
        if significance_level > 1:
            significance_level = significance_level / 100


        # Check whether significance level is valid
        if significance_level <= 0 or significance_level >= 1:
            print("Significance level must be between 0 and 1.")
            return False

        # Calculate Chi-square statistic, p-value, degrees of freedom and expected frequencies
        chi_square_value, p_value, degrees_of_freedom, expected = chi2_contingency(observed)


        # Calculate the critical Chi-square value
        critical_value= chi2.ppf(1 - significance_level, degrees_of_freedom)  # PPF asks:  "At what Chi-square value does 95% of the distribution lie to the left?"   That's the critical value. it does the same thing as critival_value = (significance level , degree of freedom)


        # Compare Chi-square statistic with critical value
        if chi_square_value> critical_value: 
            decision = "Reject Ho"

        else:
            decision = "Fail to Reject Ho"


        # return the results
        return (
        f"chi_square = {chi_square_value}",
        f"critical_value = {critical_value}",
        f"degrees_of_freedom = {degrees_of_freedom}",
        f"decision = {decision}")



# CONFIDENCE INTERVAL 
# - Confidence interval (CI) — a range of values calculated from sample data that is used to estimate a population parameter.
# - Margin of error — the amount added to and subtracted from the point estimate to form the confidence interval.

    def confidence_interval(self,column,confidence_level= 0.95):
        df = self.dataset_manager.dataframe
        if df is None:
            print("No Active Dataset.")
            return False

        # Check whether the requested column exists
        if column not in df.columns:
            print(f"Column '{column}' not found.")
            return False

        # Check whether the column contains numeric data
        if not pd.api.types.is_numeric_dtype(df[column]):
            print(f"Column '{column}' is not numeric.")
            return False

        # Reject boolean columns
        if pd.api.types.is_bool_dtype(df[column]):
            print(f"Column '{column}' is boolean.")
            return False

        # Convert 95 into 0.95 if confidence level was entered as 95
        if confidence_level > 1:
            confidence_level = confidence_level / 100

        # Check whether confidence level is valid
        if confidence_level <= 0 or confidence_level >= 1:
            print("Confidence level must be between 0 and 1.")
            return False

        # Calculate the sample mean
        sample_mean= df[column].mean()

        # count the number of non-missing observation
        sample_size= df[column].count()

        # calculate sample standerd daviation
        sample_std = (df[column].std(ddof=1))

        # calculate degree of freedom
        degree_of_freedom = sample_size-1

        # calculate alpha from the confidence level
        alpha = 1 - confidence_level


        # calculate critical_value
        critical_value= t.ppf(1-alpha/2,degree_of_freedom)

        # calculate the standerd error
        standerd_error= sample_std/math.sqrt(sample_size)

        # calculate margin of error
        margin_of_error = critical_value * standerd_error

        # Calculate the lower confidence limit
        lower_limit = sample_mean - margin_of_error

        # Calculate the upper confidence limit
        upper_limit = sample_mean + margin_of_error
            
        # Return the confidence interval results
        return (
            f"sample_mean = {sample_mean}",
            f"critical_value = {critical_value}",
            f"degree_of_freedom = {degree_of_freedom}",
            f"margin_of_error = {margin_of_error}",
            f"lower_limit = {lower_limit}",
            f"upper_limit = {upper_limit}")

# FINAL STATISTICAL SUMMERY

        # Final statistical summary
    def statistical_summary(self, column1, column2):

        df = self.dataset_manager.dataframe
        
        if df is None:
            print("No Active Dataset.")
            return False

        # Check whether the first column exists
        if column1 not in df.columns:
            print(f"Column '{column1}' not found.")
            return False

        # Check whether the second column exists
        if column2 not in df.columns:
            print(f"Column '{column2}' not found.")
            return False

        # Calculate descriptive statistics for the first column
        descriptive_result = self.calculate_descriptive_stats()[column1]

        # Calculate distribution information for the first column
        distribution_result = self.analyze_distribution()[column1]

        # Calculate correlation between the two columns
        correlation_result = self.analyze_correlation(column1, column2)

        # Calculate covariance between the two columns
        covariance_result = self.analyze_covariance(column1, column2)

        # Calculate the 95% confidence interval for the first column
        confidence_result = self.confidence_interval(column1, 0.95)

        # Return the important statistical results together
        return {
            "descriptive_statistics": descriptive_result,
            "distribution": distribution_result,
            "correlation": correlation_result,
            "covariance": covariance_result,
            "confidence_interval": confidence_result
        }



# ------------------------------------------------------TESTS
# manager = DatasetManager()
# manager.load_dataset(r"C:\Main\GLACIER\data\Cleaned data\amazon_sales_data_cleaned.csv")
# manager.load_into_executor()
# statistics = Statistics(manager)






# # ---------------------------------------Statistics inspection
# # print("\n -------------------Statistical inspection-------------------")
# # statistical_report = statistics.inspect_statistical_data()

# # print("\n STATISTICAL REPORT")

# # for column, info in statistical_report.items():
# #     print(
# #         f"\n{column} :"
# #         f"dtype = {info["dtype"]}, "
# #         f"missing = {info["missing"]}, "
# #         f"unique = {info['unique']}, "
# #         f"is_numeric = {info['is_numeric']}, "
# #     )






# # --------------------------------------- Descriptive statistics test

# # print("\n============= DESCRIPTIVE STATISTICS TEST ================")

# # descriptive_report = statistics.calculate_descriptive_stats()
# # print("\nDESCRIPTIVE STATISTICS REPORT")

# # for column, info in descriptive_report.items():
# #     print(f'\n {column}: ')
# #     print(
# #         f"Mean     = {info['mean']}\n"
# #         f"Median   = {info['median']}\n"
# #         f"Mode     = {info['mode']}\n"
# #         f"Min      = {info['min']}\n"
# #         f"Max      = {info['max']}\n"
# #         f"Range    = {info['range']}\n"
# #         f"Std      = {info['std']}\n"
# #         f"Variance = {info['varience']}\n"
# #         f"Q1       = {info['q1']}\n"
# #         f"Q2       = {info['q2']}\n"
# #         f"Q3       = {info['q3']}\n"
# #         f"IQR      = {info['iqr']}")


# # print('\n current dataset ')
# # print(manager.dataframe.dtypes)



# # ------------------------------------------Distribution test 
# # print("\n============= DISTRIBUTION ANALYSIS TEST =============")
# # distribution_report = statistics.analyze_distribution()
# # print("\nDistribution Report: ")

# # for column, info in distribution_report.items():
# #     print(
# #         f"\n {column}: "
# #         f"skewness = {info["skewness"]}, "
# #         f"kurtosis = {info["kurtosis"]}"  
# #     )




# # -----------------------------------------------outlier analysis
# # print("\n============= OUTLIER ANALYSIS TEST =============")

# # outlier_report = statistics.analyze_outliers()
# # for column, info in outlier_report.items():
# #     print(f"\n{column}: ")

# #     print(f"Q1 = {info['q1']}")
# #     print(f"Q3 = {info['q3']}")
# #     print(f"IQR = {info['iqr']}")

# #     print(f"Lower Boundary = {info['lower_boundary']}")
# #     print(f"Upper Boundary = {info['upper_boundary']}")

# #     print(f"Outliers = {info['outlier_count']}")
# #     print(f"Outlier Percentage = {info['outlier_percentage']}%")


# # ----------------------------------------------Correlation Test
# # print("\n==================Correlation===================")
# # corelation = statistics.analyze_correlation("Rating","Number_of_reviews")
# # print("\nCorrelation Report: ")
# # print(corelation)


# # # -------------------------------------Covariance test
# # print("\n============= COVARIANCE ANALYSIS TEST =============")

# # covariance  = statistics.analyze_covariance("Rating","Number_of_reviews")
# # print("\nCovariance Result")
# # print(covariance)



# # ------------------------------------------------z test two tailed
# # print("\n============= Z TEST TWO TAILED =============")
# # z_result = statistics.z_two_tailed_test("Rating",4.2,0.05)

# # print("Z test result")
# # print(z_result)     # A Z-score is not the original value. It's telling us how far the mean of our data is from the hypothesized mean, measured in standard-error units.


# # df = manager.dataframe

# # print(f'population median = {df["Rating"].median()}')
# # print(f'population mean = {df["Rating"].mean()}')



# # ---------------------------------------------------z test one tailed (right)
# # z_result = statistics.z_one_tailed_test(
# #     "Rating",
# #     "right",
# #     4.2,
# #     0.05
# # )

# # print(z_result)




# # ---------------------------------------------------z test one tailed (left)
# # z_result = statistics.z_one_tailed_test(
# #     "Rating",
# #     "left",
# #     4.2,
# #     0.05
# # )

# # print(z_result)






# # --------------------------------------------------T test two tailed
# # t_result = statistics.t_two_tailed_test(
# #     "Rating",
# #     4.2,
# #     0.05
# # )

# # print(t_result)



# # --------------------------------------------------T test one tailed(right)
# # t_result = statistics.t_test_one_tailed(
# #     "Rating",
# #     "right",
# #     4.2,
# #     0.05
# # )

# # print(t_result)


# # # -------------------------------------------------- T test one tailed(left)
# # t_result = statistics.t_test_one_tailed(
# #     "Rating",
# #     "left",
# #     4.2,
# #     0.05
# # )

# # print(t_result)


# # ----------------------------------------------------------ANOVA test
# # # Run ANOVA on the three temporary groups
# # anova_result = statistics.anova(
# #     ["15mg", "30mg", "45mg"],
# #     0.05
# # )

# # print(anova_result)




# # --------------------------------------------------------Chi Square test
# # chi_result = statistics.chi_square_test(
# #     "is_best_seller",
# #     "is_sponsored",
# #     0.05
# # )

# # print(chi_result)



# # ----------------------------------------------------------Confidence interval test
# # ci_result = statistics.confidence_interval(
# #     "Rating",
# #     0.95
# # )

# # print(ci_result)



# # --------------------------------------------------------Final summery test
# # summary_result = statistics.statistical_summary(
# #     "Rating",
# #     "Number_of_reviews"
# # )

# # print("\nSTATISTICAL SUMMARY")
# # print(summary_result)

















