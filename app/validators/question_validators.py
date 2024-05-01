def is_only_numbers(value: str | None) -> bool:
    """
    Validate that the string contains only numbers.

    Args:
        value (str | None): The string to validate.

    Returns:
        bool: True if the string contains only numbers, False otherwise.
    """
    if not value:
        return False
    return value.isdigit()


def is_digit_between(start: int, end: int, value: str | None) -> bool:
    """
    Validate that the give value is a digit between start and end.

    Args:
        start (int): The start of the range.
        end (int): The end of the range.
        value (str | None): The value to validate.

    Returns:
        bool: True if the value is a digit between start and end, False otherwise.
    """
    if not value:
        return False
    if not is_only_numbers(value):
        return False
    return start <= int(value) <= end


def is_len_between(start: int, end: int, value: str | None) -> bool:
    """
    Validate that the length of the value is between start and end.

    Args:
        start (int): The start of the range.
        end (int): The end of the range.
        value (str | None): The value to validate.

    Returns:
        bool: True if the length of the value is between start and end, False otherwise.
    """
    if not value:
        return False
    return start <= len(value) <= end
