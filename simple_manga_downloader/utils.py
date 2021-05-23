import time
from functools import wraps
from html import unescape

import requests

REPLACEMENT_RULES = None


def clean_up_string(string):
    """Cleans up the given string from unwanted characters"""
    if type(string) != str or not REPLACEMENT_RULES:
        return string

    fixed_html = unescape(string).strip()
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
        except requests.exceptions.RetryError:
            status = "Max retries reached"
        except requests.RequestException as e:
            status = f"A unexpected problem {e}"

        return status

    return wrapper


def ask_confirmation(text, accepted=None):
    """Asks of confirmation

    text = the message do display
    accepted = the string that the input will be checked against,
    'y' by default
    """
    if accepted is None:
        accepted = "y"
    print(text)
    confirm = (
        input(f"[{accepted} to confirm/anything else to cancel]: ").lower().strip()
    )
    return confirm == accepted


def ask_number(text, min_=None, max_=None, num_type=int):
    """Asks the user for a number

    If min_ given it will check if the number is bigger or equal, if max_
    given it will check if number is smaller or equal
    num_type is the type of number to convert to, int or float"""
    try:
        number = num_type(input(f"{text} [number]: "))
    except ValueError:
        print("Not a valid number")
        return False

    if min_ is not None and number < min_:
        print("Number too small")
        return False
    if max_ is not None and number > max_:
        print("Number too big")
        return False

    return number
