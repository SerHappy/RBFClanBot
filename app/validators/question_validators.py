def is_only_numbers(value: str | None) -> bool:
    """Проверка, что в строке только цифры."""
    if not value:
        return False
    return value.isdigit()


def is_digit_between(start: int, end: int, value: str | None) -> bool:
    """Проверка, что в строке только цифры."""
    if not value:
        return False
    if not is_only_numbers(value):
        return False
    return start <= int(value) <= end


def is_len_between(start: int, end: int, value: str | None) -> bool:
    """Проверка, что в строке только цифры."""
    if not value:
        return False
    return start <= len(value) <= end
