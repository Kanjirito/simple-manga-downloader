import requests
import time
from functools import wraps
from html import unescape


REPLACEMENT_RULES = None


def set_replacement_rules(rules):
    """Sets the replacment rules to be used"""
    global REPLACEMENT_RULES
    REPLACEMENT_RULES = rules


def clean_up_string(string):
    """Cleans up the given string from unwanted characters"""
    if not type(string) == str:
        return string

    fixed_html = unescape(string)
    new_string_list = []
    for char in fixed_html:
        if char in REPLACEMENT_RULES:
            new_string_list.append(REPLACEMENT_RULES[char])
        else:
            new_string_list.append(char)
    return "".join(new_string_list)


def limiter(seconds):
    """
    Limits the decorated func to be called after given amount of seconds
    """
    def middle(func):

        last_called = 0

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_called

            before = time.time()
            difference = before - last_called
            if difference < seconds:
                time.sleep(seconds - difference)

            result = func(*args, **kwargs)

            last_called = time.time()
            return result
        return wrapper
    return middle


def request_exception_handler(func):
    """
    Decorator that handles any request exceptions
    Returns True func result if nothing failed otherwise a error string
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            status = func(*args, **kwargs)
        except requests.Timeout:
            status = "Request Timeout"
        except requests.ConnectionError:
            status = "Connection Error"
        except requests.HTTPError as e:
            error_code = str(e).split(":", 1)[0]
            status = f"HTTP code error: {error_code}"
        except requests.RequestException as e:
            status = f"A unexpected problem {e}"

        return status

    return wrapper


def ask_confirmation(text, expected):
    confirm = input(f"{text}: ").lower()
    if confirm == expected:
        return True
    else:
        return False
