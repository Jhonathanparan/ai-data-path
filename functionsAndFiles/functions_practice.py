def analyze_numbers(nums, precision=2):
    if not nums:
        return (None, None, None)
    total = 0
    count = 0
    min_val = nums[0]
    max_val = nums[0]
    for num in nums:
        if min_val > num:
            min_val = num
        if max_val < num:
            max_val = num
        total += num
        count += 1
    average = round(total / count, precision)
    return (average, min_val, max_val)


def flexible_stats(operation, *numbers):
    if not numbers:
        return None
    if operation == "avg":
        return sum(numbers) / len(numbers)
    elif operation == "min":
        return min(numbers)
    elif operation == "max":
        return max(numbers)
    elif operation == "count":
        return len(numbers)
    else:
        return "Invalid Operation"


def multi_stats(*numbers):
    if not numbers:
        return None
    return (
        sum(numbers) / len(numbers),
        min(numbers),
        max(numbers),
        len(numbers),
        sum(numbers),
    )


def write_message_to_file(file_name, message):
    with open(file_name, "w") as f:
        f.write(message)
    return True


def read_file_contents(file_name):
    try:
        with open(file_name, "r") as f:
            return f.read(file_name)
    except FileNotFoundError:
        print("file not found")
