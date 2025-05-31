import itertools

import pandas as pd


def generate_dicts_product(data_input: dict[str, dict[str, list[int]]]) -> pd.DataFrame:
    """Generate the Cartesian product of all parameter combinations.

    Args:
        data_input (dict[str, dict[str, list[int]]]): The input dictionary containing parameter lists.

    Returns:
        pd.DataFrame: DataFrame containing all parameter combinations with representative values as index.
    """
    # Extract all lists and their corresponding hierarchical column names
    lists_for_product = []
    product_column_names = []  # Tuples like ('A', 'a') for MultiIndex

    # For representative values (excluding single-element lists)
    representative_lists = []
    representative_column_names = []

    # Iterate through data_input. To ensure consistent column order in df_step2_product,
    # especially if the input dictionary order could vary, sort keys.
    sorted_outer_keys = sorted(data_input.keys())

    for outer_key in sorted_outer_keys:
        inner_dict = data_input[outer_key]
        sorted_inner_keys = sorted(inner_dict.keys())
        for inner_key in sorted_inner_keys:
            value_list = inner_dict[inner_key]
            # Skip empty lists
            if not value_list:
                continue
            lists_for_product.append(value_list)
            product_column_names.append((outer_key, inner_key))

            # Only include lists with more than one element for representative values
            if len(value_list) > 1:
                representative_lists.append(value_list)
                representative_column_names.append((outer_key, inner_key))

    # If no valid parameters remain after filtering, return empty DataFrame
    if not lists_for_product:
        return pd.DataFrame(columns=pd.MultiIndex.from_tuples(product_column_names))

    if lists_for_product and all(len(lst) == 1 for lst in lists_for_product):
        single_row = [lst[0] for lst in lists_for_product]
        df = pd.DataFrame([single_row], columns=pd.MultiIndex.from_tuples(product_column_names))
        # Set name for the single case
        df.name = "single_combination"
        return df

    # Generate the Cartesian product using itertools.product
    cartesian_product_tuples = list(itertools.product(*lists_for_product))

    # Create the product DataFrame with MultiIndex columns
    df = pd.DataFrame(cartesian_product_tuples, columns=pd.MultiIndex.from_tuples(product_column_names))

    # Generate representative values (combinations excluding single-element lists)
    if representative_lists:
        representative_combinations = list(itertools.product(*representative_lists))

        # Create representative index names for each row
        representative_index = []

        # Map each full combination to its representative value
        for full_combination in cartesian_product_tuples:
            # Extract only the values corresponding to multi-element lists
            representative_dict = {}
            rep_idx = 0
            for i, (col_name, value) in enumerate(zip(product_column_names, full_combination)):
                # Check if this column corresponds to a multi-element list
                if rep_idx < len(representative_column_names) and col_name == representative_column_names[rep_idx]:
                    # Create key name from the hierarchical column name
                    if isinstance(col_name, tuple):
                        key_name = f"{col_name[0]}_{col_name[1]}"
                    else:
                        key_name = str(col_name)
                    representative_dict[key_name] = value
                    rep_idx += 1

            # Convert dictionary to a string representation
            dict_str = "_".join([f"{k}={v}" for k, v in representative_dict.items()])
            representative_index.append(str(dict_str))

        # Set the representative values as the index
        df.index = representative_index
        df.name = "combinations_with_representative_index"
    else:
        # No lists with multiple elements, so no representative values
        df.name = "all_single_element_lists"

    return df
