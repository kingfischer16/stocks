"""
# ============================================================================
# UTILS.PY
# ----------------------------------------------------------------------------
# Utility functions.
#
# ============================================================================
"""


def check_and_convert_value_to_list(val_or_list, expected_type):
    """
    Checks to make sure the argument is either of the expected type
    or that the list contains only values of this type. If the argument
    is not a list, it is converted to a list.
    
    Args:
        val_or_list (*, list): A value or a list of values for checking.
        
        expected_type (type): The type to check.
    
    Returns:
        (list): A list of the expected type.
    
    Raises:
        ValueError: if the value or list does not match with the expected type.
    """
    # If it is a list.
    if isinstance(val_or_list, list):
        for val in val_or_list:
            # Handle incorrect type.
            if not isinstance(val, expected_type):
                raise ValueError(f"Value {val} in list is not of expected type {expected_type}.")
        return val_or_list
    # If it is not a list.
    else:
        if not isinstance(val_or_list, expected_type):
            raise ValueError(f"Value {val_or_list} is not of expected type {expected_type}.")
        return [val_or_list]
    