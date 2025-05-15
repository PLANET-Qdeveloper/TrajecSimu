"""パラメータの組み合わせ生成を行うモジュール"""

import itertools

import pandas as pd


def generate_dicts_product(data_input: dict[str, dict[str, list[int]]]) -> pd.DataFrame:
    """Generate the Cartesian product of all parameter combinations.

    Args:
        data_input (dict[str, dict[str, list[int]]]): The input dictionary containing parameter lists.

    Returns:
        pd.DataFrame: DataFrame containing all parameter combinations.
    """
    # Extract all lists and their corresponding hierarchical column names
    lists_for_product = []
    product_column_names = []  # Tuples like ('A', 'a') for MultiIndex

    # Iterate through data_input. To ensure consistent column order in df_step2_product,
    # especially if the input dictionary order could vary, sort keys.
    sorted_outer_keys = sorted(data_input.keys())

    for outer_key in sorted_outer_keys:
        inner_dict = data_input[outer_key]
        sorted_inner_keys = sorted(inner_dict.keys())
        for inner_key in sorted_inner_keys:
            value_list = inner_dict[inner_key]
            lists_for_product.append(value_list)
            product_column_names.append((outer_key, inner_key))

    if lists_for_product and all(len(lst) == 1 for lst in lists_for_product):
        single_row = [lst[0] for lst in lists_for_product]
        return pd.DataFrame([single_row], columns=pd.MultiIndex.from_tuples(product_column_names))

    # Generate the Cartesian product using itertools.product
    cartesian_product_tuples = list(itertools.product(*lists_for_product))

    # Create the product DataFrame with MultiIndex columns
    return pd.DataFrame(cartesian_product_tuples, columns=pd.MultiIndex.from_tuples(product_column_names))
