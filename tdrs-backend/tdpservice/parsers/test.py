def make_validator(validator_func, error_func):
    """Return a function accepting a value input and returning (bool, string) to represent validation state."""
    def validator(value, record_type=None, friendly_name=None, item_num=None):
        try:
            if validator_func(value):
                return (True, None)
            return (False, error_func(value, record_type, friendly_name, item_num))
        except Exception as e:
            return (False, error_func(value, record_type, friendly_name, item_num))
    return validator

def isInStringRange(lower, upper):
    """Validate that string value is in a specific range."""
    return make_validator(
        lambda value: int(value) >= lower and int(value) <= upper,
        lambda value, record_type, friendly_name, item_num: f"{value} is not in range {[str(num) for num in range(lower, upper + 1)]}.",
    )

print(isInStringRange(0, 2)(-1))
print(isInStringRange(4, 6)(-1))
print(isInStringRange(8, 13)(-1))
print(isInStringRange(15, 42)(-1))
print(isInStringRange(44, 51)(-1))
print(isInStringRange(53, 56)(-1))

def func():
    return  "s3://{}/{}."

print(func().format(1, 2))