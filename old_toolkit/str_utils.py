def no_format_str(my_str: str) -> str:
    special_characters = ('*_~`@#|-[]()>')
    for char in special_characters:
        my_str = my_str.replace(char,"\\" + char)
    return my_str