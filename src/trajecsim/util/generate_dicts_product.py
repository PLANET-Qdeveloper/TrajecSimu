import itertools

import pandas as pd

# Define the input data as per the example
# A={"a":[1,2,3], "b":[4,5,6]}, B ={"a":[3,4,5], "c":[4,5,6]}
data_input = {"A": {"a": [1, 2, 3], "b": [4, 5, 6]}, "B": {"a": [3, 4, 5], "c": [4, 5, 6]}}

# Step 1: Create a DataFrame from a dictionary of lists, using two keys.
# The problem describes the desired output format:
# “A” "a" [1,2,3]
# “A” "b" [4,5,6]
# “B” "a" [3,4,5]
# “B” “c” [4,5,6]
# This corresponds to a DataFrame with columns representing the outer key, inner key, and the list of values.

step1_data_for_df = []
for outer_key, inner_dict in data_input.items():
    for inner_key, value_list in inner_dict.items():
        step1_data_for_df.append(
            {
                "key1": outer_key,  # First key (e.g., "A", "B")
                "key2": inner_key,  # Second key (e.g., "a", "b", "c")
                "list_values": value_list,  # The list of values
            }
        )
df_step1 = pd.DataFrame(step1_data_for_df)

print("--- Step 1 DataFrame ---")
print(df_step1)
print("\n")


# Step 2: Create a DataFrame representing the Cartesian product of all lists.
# The column names for this product DataFrame should correspond to the origin of each list.
# Using (OuterKey, InnerKey) tuples for MultiIndex columns is a standard way to represent this.
# Example values for the product:
# 1,4,3,4 (from A['a'][0], A['b'][0], B['a'][0], B['c'][0])
# 1,4,3,5 (from A['a'][0], A['b'][0], B['a'][0], B['c'][1])
# ...

# Extract all lists and their corresponding hierarchical column names
lists_for_product = []
product_column_names = []  # Tuples like ('A', 'a') for MultiIndex

# Iterate through data_input. To ensure consistent column order in df_step2_product,
# especially if the input dictionary order could vary, sort keys.
# For Python 3.7+, dicts preserve insertion order, but explicit sorting is safer for portability/older versions.
sorted_outer_keys = sorted(data_input.keys())

for outer_key in sorted_outer_keys:
    inner_dict = data_input[outer_key]
    sorted_inner_keys = sorted(inner_dict.keys())
    for inner_key in sorted_inner_keys:
        value_list = inner_dict[inner_key]
        lists_for_product.append(value_list)
        product_column_names.append((outer_key, inner_key))

# Generate the Cartesian product using itertools.product
# The '*' unpacks lists_for_product into separate arguments for product()
cartesian_product_tuples = list(itertools.product(*lists_for_product))

# Create the product DataFrame with MultiIndex columns
df_step2_product = pd.DataFrame(cartesian_product_tuples, columns=pd.MultiIndex.from_tuples(product_column_names))

print("--- Step 2 DataFrame (Cartesian Product) ---")
print(df_step2_product)

print("\n")


# Step 3: For each combination (each row in df_step2_product),
# execute a for loop and print values as specified in the prompt:
# For A B in ():  (This implies iterating through each combination/row)
#   print(A[“a”])
#   print(A[“b”])
#   print(B[“a”])
#   print(B[“c”])
# This means for each row, we access the elements corresponding to the
# original structure (e.g., the element from A['a'], A['b'], B['a'], B['c']
# that form the current combination).

print("--- Step 3 Iteration ---")
# Iterate over each row of the product DataFrame (df_step2_product)
for index, row in df_step2_product.iterrows():
    print(f"Combination index {index}:")
    print(row["A"].to_dict())
    print(row["B"].to_dict())


# Example of the first few outputs for Step 3:
# Combination index 0:
#   A['a']: 1
#   A['b']: 4
#   B['a']: 3
#   B['c']: 4
# Combination index 1:
#   A['a']: 1
#   A['b']: 4
#   B['a']: 3
#   B['c']: 5
# ... and so on for all 3*3*3*3 = 81 combinations.
