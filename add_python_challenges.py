"""
Script to add 100 Python coding challenges to the database.
Run: python3 add_python_challenges.py
"""
from app import create_app
from app.models.learning import CodingChallenge
from app.extensions import db
import json

app = create_app()

# 100 Python coding challenges with test cases
CHALLENGES = [
    {
        "title": "Hello World",
        "description": "Write a function that returns the string 'Hello, World!'",
        "difficulty": "easy",
        "starter_code": "def hello_world():\n    # Your code here\n    pass",
        "test_cases": [
            {"input": "", "expected_output": "Hello, World!"}
        ],
        "points": 5
    },
    {
        "title": "Sum Two Numbers",
        "description": "Write a function that takes two numbers and returns their sum.",
        "difficulty": "easy",
        "starter_code": "def sum_numbers(a, b):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": "2, 3", "expected_output": "5"},
            {"input": "-1, 1", "expected_output": "0"},
            {"input": "0, 0", "expected_output": "0"}
        ],
        "points": 5
    },
    {
        "title": "Find Maximum",
        "description": "Write a function that finds the maximum of two numbers.",
        "difficulty": "easy",
        "starter_code": "def find_max(a, b):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": "5, 3", "expected_output": "5"},
            {"input": "-2, -5", "expected_output": "-2"},
            {"input": "10, 10", "expected_output": "10"}
        ],
        "points": 5
    },
    {
        "title": "Check Even or Odd",
        "description": "Write a function that returns 'even' if a number is even, 'odd' otherwise.",
        "difficulty": "easy",
        "starter_code": "def check_even_odd(n):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": "4", "expected_output": "even"},
            {"input": "7", "expected_output": "odd"},
            {"input": "0", "expected_output": "even"}
        ],
        "points": 5
    },
    {
        "title": "Factorial",
        "description": "Write a function that calculates the factorial of a number. Return 1 for 0.",
        "difficulty": "easy",
        "starter_code": "def factorial(n):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": "5", "expected_output": "120"},
            {"input": "0", "expected_output": "1"},
            {"input": "3", "expected_output": "6"}
        ],
        "points": 10
    },
    {
        "title": "Reverse String",
        "description": "Write a function that reverses a string.",
        "difficulty": "easy",
        "starter_code": "def reverse_string(s):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": "'hello'", "expected_output": "olleh"},
            {"input": "'Python'", "expected_output": "nohtyP"},
            {"input": "''", "expected_output": ""}
        ],
        "points": 5
    },
    {
        "title": "Count Vowels",
        "description": "Write a function that counts the number of vowels (a, e, i, o, u) in a string (case-insensitive).",
        "difficulty": "easy",
        "starter_code": "def count_vowels(s):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": "'hello'", "expected_output": "2"},
            {"input": "'Python'", "expected_output": "1"},
            {"input": "'AEIOU'", "expected_output": "5"}
        ],
        "points": 10
    },
    {
        "title": "Check Palindrome",
        "description": "Write a function that checks if a string is a palindrome (reads the same forwards and backwards).",
        "difficulty": "easy",
        "starter_code": "def is_palindrome(s):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": "'racecar'", "expected_output": "True"},
            {"input": "'hello'", "expected_output": "False"},
            {"input": "'a'", "expected_output": "True"}
        ],
        "points": 10
    },
    {
        "title": "Sum List",
        "description": "Write a function that returns the sum of all numbers in a list.",
        "difficulty": "easy",
        "starter_code": "def sum_list(numbers):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": "[1, 2, 3, 4, 5]", "expected_output": "15"},
            {"input": "[-1, 0, 1]", "expected_output": "0"},
            {"input": "[]", "expected_output": "0"}
        ],
        "points": 5
    },
    {
        "title": "Find Maximum in List",
        "description": "Write a function that finds the maximum number in a list.",
        "difficulty": "easy",
        "starter_code": "def find_max_in_list(numbers):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": "[3, 7, 2, 9, 1]", "expected_output": "9"},
            {"input": "[-5, -2, -10]", "expected_output": "-2"},
            {"input": "[42]", "expected_output": "42"}
        ],
        "points": 5
    },
    {
        "title": "Count Words",
        "description": "Write a function that counts the number of words in a string.",
        "difficulty": "easy",
        "starter_code": "def count_words(s):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": "'hello world'", "expected_output": "2"},
            {"input": "'Python is great'", "expected_output": "3"},
            {"input": "''", "expected_output": "0"}
        ],
        "points": 5
    },
    {
        "title": "FizzBuzz",
        "description": "Write a function that returns 'Fizz' if n is divisible by 3, 'Buzz' if divisible by 5, 'FizzBuzz' if divisible by both, otherwise return the number as string.",
        "difficulty": "easy",
        "starter_code": "def fizzbuzz(n):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": "3", "expected_output": "Fizz"},
            {"input": "5", "expected_output": "Buzz"},
            {"input": "15", "expected_output": "FizzBuzz"},
            {"input": "7", "expected_output": "7"}
        ],
        "points": 10
    },
    {
        "title": "Find Duplicates",
        "description": "Write a function that returns a list of duplicate elements in a list.",
        "difficulty": "medium",
        "starter_code": "def find_duplicates(lst):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": "[1, 2, 2, 3, 4, 4, 5]", "expected_output": "[2, 4]"},
            {"input": "[1, 2, 3]", "expected_output": "[]"},
            {"input": "[1, 1, 1, 1]", "expected_output": "[1]"}
        ],
        "points": 15
    },
    {
        "title": "Remove Duplicates",
        "description": "Write a function that removes duplicates from a list while preserving order.",
        "difficulty": "medium",
        "starter_code": "def remove_duplicates(lst):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": "[1, 2, 2, 3, 4, 4, 5]", "expected_output": "[1, 2, 3, 4, 5]"},
            {"input": "[1, 1, 1, 1]", "expected_output": "[1]"},
            {"input": "[]", "expected_output": "[]"}
        ],
        "points": 10
    },
    {
        "title": "Merge Lists",
        "description": "Write a function that merges two sorted lists into one sorted list.",
        "difficulty": "medium",
        "starter_code": "def merge_lists(list1, list2):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": "[1, 3, 5], [2, 4, 6]", "expected_output": "[1, 2, 3, 4, 5, 6]"},
            {"input": "[1, 2], [3, 4]", "expected_output": "[1, 2, 3, 4]"},
            {"input": "[], [1, 2]", "expected_output": "[1, 2]"}
        ],
        "points": 15
    },
    {
        "title": "List Comprehension: Squares",
        "description": "Write a function that uses list comprehension to return a list of squares of numbers from 1 to n.",
        "difficulty": "easy",
        "starter_code": "def squares_list(n):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": "5", "expected_output": "[1, 4, 9, 16, 25]"},
            {"input": "3", "expected_output": "[1, 4, 9]"},
            {"input": "1", "expected_output": "[1]"}
        ],
        "points": 10
    },
    {
        "title": "Dictionary: Word Frequency",
        "description": "Write a function that counts the frequency of each word in a string and returns a dictionary.",
        "difficulty": "medium",
        "starter_code": "def word_frequency(s):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": "'hello world hello'", "expected_output": "{'hello': 2, 'world': 1}"},
            {"input": "'a a a'", "expected_output": "{'a': 3}"},
            {"input": "''", "expected_output": "{}"}
        ],
        "points": 15
    },
    {
        "title": "Fibonacci Sequence",
        "description": "Write a function that returns the nth Fibonacci number (0, 1, 1, 2, 3, 5, 8, ...).",
        "difficulty": "medium",
        "starter_code": "def fibonacci(n):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": "0", "expected_output": "0"},
            {"input": "1", "expected_output": "1"},
            {"input": "5", "expected_output": "5"},
            {"input": "10", "expected_output": "55"}
        ],
        "points": 15
    },
    {
        "title": "Prime Check",
        "description": "Write a function that checks if a number is prime.",
        "difficulty": "medium",
        "starter_code": "def is_prime(n):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": "7", "expected_output": "True"},
            {"input": "10", "expected_output": "False"},
            {"input": "2", "expected_output": "True"},
            {"input": "1", "expected_output": "False"}
        ],
        "points": 15
    },
    {
        "title": "GCD (Greatest Common Divisor)",
        "description": "Write a function that finds the greatest common divisor of two numbers.",
        "difficulty": "medium",
        "starter_code": "def gcd(a, b):\n    # Your code here\n    pass",
        "test_cases": [
            {"input": "48, 18", "expected_output": "6"},
            {"input": "17, 13", "expected_output": "1"},
            {"input": "100, 25", "expected_output": "25"}
        ],
        "points": 15
    },
    # Adding more challenges to reach 100...
    # I'll add a variety covering different Python concepts
]

def generate_more_challenges():
    """Generate additional challenges to reach 100 total"""
    challenges = CHALLENGES.copy()
    
    # More basic challenges
    basic_templates = [
        ("Multiply Numbers", "Write a function that multiplies two numbers.", "def multiply(a, b):\n    pass", [("3, 4", "12"), ("-2, 5", "-10")], "easy", 5),
        ("Power", "Write a function that calculates a raised to the power of b.", "def power(a, b):\n    pass", [("2, 3", "8"), ("5, 0", "1")], "easy", 5),
        ("Absolute Value", "Write a function that returns the absolute value of a number.", "def absolute(n):\n    pass", [("-5", "5"), ("5", "5")], "easy", 5),
        ("Check Positive", "Write a function that returns True if number is positive, False otherwise.", "def is_positive(n):\n    pass", [("5", "True"), ("-3", "False"), ("0", "False")], "easy", 5),
        ("Length of String", "Write a function that returns the length of a string (without using len()).", "def string_length(s):\n    pass", [("'hello'", "5"), ("''", "0")], "easy", 5),
        ("Uppercase", "Write a function that converts a string to uppercase.", "def to_uppercase(s):\n    pass", [("'hello'", "HELLO"), ("'Python'", "PYTHON")], "easy", 5),
        ("Lowercase", "Write a function that converts a string to lowercase.", "def to_lowercase(s):\n    pass", [("'HELLO'", "hello"), ("'Python'", "python")], "easy", 5),
        ("Count Characters", "Write a function that counts occurrences of a character in a string.", "def count_char(s, char):\n    pass", [("'hello', 'l'", "2"), ("'python', 'p'", "1")], "easy", 10),
        ("Replace Character", "Write a function that replaces all occurrences of old char with new char.", "def replace_char(s, old, new):\n    pass", [("'hello', 'l', 'x'", "hexxo"), ("'python', 'p', 'P'", "Python")], "easy", 10),
        ("List Length", "Write a function that returns the length of a list (without using len()).", "def list_length(lst):\n    pass", [("[1, 2, 3]", "3"), ("[]", "0")], "easy", 5),
        ("Get First Element", "Write a function that returns the first element of a list, or None if empty.", "def first_element(lst):\n    pass", [("[1, 2, 3]", "1"), ("[]", "None")], "easy", 5),
        ("Get Last Element", "Write a function that returns the last element of a list, or None if empty.", "def last_element(lst):\n    pass", [("[1, 2, 3]", "3"), ("[]", "None")], "easy", 5),
        ("Sum Range", "Write a function that returns the sum of numbers from 1 to n.", "def sum_range(n):\n    pass", [("5", "15"), ("10", "55")], "easy", 10),
        ("Average", "Write a function that calculates the average of a list of numbers.", "def average(numbers):\n    pass", [("[1, 2, 3, 4, 5]", "3.0"), ("[10, 20]", "15.0")], "easy", 10),
        ("Multiply List", "Write a function that multiplies all numbers in a list.", "def multiply_list(numbers):\n    pass", [("[2, 3, 4]", "24"), ("[5, 2]", "10")], "easy", 10),
    ]
    
    for title, desc, code, tests, diff, pts in basic_templates:
        challenges.append({
            "title": title,
            "description": desc,
            "difficulty": diff,
            "starter_code": code,
            "test_cases": [{"input": inp, "expected_output": out} for inp, out in tests],
            "points": pts
        })
    
    # Medium challenges
    medium_templates = [
        ("Binary Search", "Write a function that performs binary search on a sorted list. Return index or -1.", "def binary_search(lst, target):\n    pass", [("[1, 2, 3, 4, 5], 3", "2"), ("[1, 2, 3], 5", "-1")], "medium", 20),
        ("Bubble Sort", "Write a function that sorts a list using bubble sort algorithm.", "def bubble_sort(lst):\n    pass", [("[3, 1, 4, 1, 5]", "[1, 1, 3, 4, 5]"), ("[5, 4, 3, 2, 1]", "[1, 2, 3, 4, 5]")], "medium", 20),
        ("List Intersection", "Write a function that returns common elements in two lists.", "def intersection(list1, list2):\n    pass", [("[1, 2, 3], [2, 3, 4]", "[2, 3]"), ("[1, 2], [3, 4]", "[]")], "medium", 15),
        ("List Union", "Write a function that returns union of two lists (no duplicates).", "def union(list1, list2):\n    pass", [("[1, 2, 3], [2, 3, 4]", "[1, 2, 3, 4]"), ("[1, 2], [3, 4]", "[1, 2, 3, 4]")], "medium", 15),
        ("Anagram Check", "Write a function that checks if two strings are anagrams.", "def is_anagram(s1, s2):\n    pass", [("'listen', 'silent'", "True"), ("'hello', 'world'", "False")], "medium", 15),
        ("Longest Word", "Write a function that finds the longest word in a string.", "def longest_word(s):\n    pass", [("'hello world python'", "python"), ("'a bb ccc'", "ccc")], "medium", 10),
        ("Title Case", "Write a function that converts a string to title case.", "def title_case(s):\n    pass", [("'hello world'", "Hello World"), ("'python programming'", "Python Programming")], "medium", 10),
        ("Capitalize Words", "Write a function that capitalizes the first letter of each word.", "def capitalize_words(s):\n    pass", [("'hello world'", "Hello World"), ("'python'", "Python")], "easy", 10),
        ("Remove Spaces", "Write a function that removes all spaces from a string.", "def remove_spaces(s):\n    pass", [("'hello world'", "helloworld"), ("'  python  '", "python")], "easy", 5),
        ("Count Lines", "Write a function that counts the number of lines in a multi-line string.", "def count_lines(s):\n    pass", [("'line1\\nline2\\nline3'", "3"), ("'single'", "1")], "easy", 10),
        ("Reverse List", "Write a function that reverses a list (without using reverse() or [::-1]).", "def reverse_list(lst):\n    pass", [("[1, 2, 3, 4]", "[4, 3, 2, 1]"), ("[]", "[]")], "medium", 10),
        ("Rotate List", "Write a function that rotates a list k positions to the right.", "def rotate_list(lst, k):\n    pass", [("[1, 2, 3, 4, 5], 2", "[4, 5, 1, 2, 3]"), ("[1, 2], 1", "[2, 1]")], "medium", 15),
        ("Find Missing Number", "Write a function that finds the missing number in a list of 1 to n (one missing).", "def find_missing(numbers, n):\n    pass", [("[1, 2, 4, 5], 5", "3"), ("[1, 3, 4], 4", "2")], "medium", 15),
        ("Two Sum", "Write a function that finds two numbers in a list that add up to target. Return indices.", "def two_sum(nums, target):\n    pass", [("[2, 7, 11, 15], 9", "[0, 1]"), ("[3, 2, 4], 6", "[1, 2]")], "medium", 20),
        ("Valid Parentheses", "Write a function that checks if parentheses in a string are balanced.", "def valid_parentheses(s):\n    pass", [("'()'", "True"), ("'()[]{}'", "True"), ("'(]'", "False")], "medium", 20),
        ("String Compression", "Write a function that compresses a string: 'aaabb' -> 'a3b2'.", "def compress(s):\n    pass", [("'aaabb'", "a3b2"), ("'abc'", "a1b1c1")], "medium", 20),
        ("Longest Common Prefix", "Write a function that finds the longest common prefix in a list of strings.", "def longest_prefix(strings):\n    pass", [("['flower', 'flow', 'flight']", "fl"), ("['dog', 'racecar', 'car']", "")], "medium", 20),
        ("Is Substring", "Write a function that checks if one string is a substring of another.", "def is_substring(s1, s2):\n    pass", [("'hello', 'ell'", "True"), ("'python', 'java'", "False")], "easy", 10),
        ("Count Substring", "Write a function that counts occurrences of a substring in a string.", "def count_substring(s, sub):\n    pass", [("'hello hello', 'hello'", "2"), ("'aaa', 'aa'", "2")], "medium", 15),
        ("Split String", "Write a function that splits a string by a delimiter (without using split()).", "def split_string(s, delimiter):\n    pass", [("'hello,world', ','", "['hello', 'world']"), ("'a-b-c', '-'", "['a', 'b', 'c']")], "medium", 15),
    ]
    
    for title, desc, code, tests, diff, pts in medium_templates:
        challenges.append({
            "title": title,
            "description": desc,
            "difficulty": diff,
            "starter_code": code,
            "test_cases": [{"input": inp, "expected_output": out} for inp, out in tests],
            "points": pts
        })
    
    # Continue adding more to reach 100...
    # I'll add a few more categories
    more_challenges = [
        # Dictionary operations
        ("Get Dictionary Keys", "Write a function that returns all keys from a dictionary as a list.", "def get_keys(d):\n    pass", [("{'a': 1, 'b': 2}", "['a', 'b']")], "easy", 5),
        ("Get Dictionary Values", "Write a function that returns all values from a dictionary as a list.", "def get_values(d):\n    pass", [("{'a': 1, 'b': 2}", "[1, 2]")], "easy", 5),
        ("Merge Dictionaries", "Write a function that merges two dictionaries.", "def merge_dicts(d1, d2):\n    pass", [("{'a': 1}, {'b': 2}", "{'a': 1, 'b': 2}")], "easy", 10),
        ("Invert Dictionary", "Write a function that inverts a dictionary (keys become values, values become keys).", "def invert_dict(d):\n    pass", [("{'a': 1, 'b': 2}", "{1: 'a', 2: 'b'}")], "medium", 15),
        
        # Tuple operations
        ("Tuple to List", "Write a function that converts a tuple to a list.", "def tuple_to_list(t):\n    pass", [("(1, 2, 3)", "[1, 2, 3]")], "easy", 5),
        ("List to Tuple", "Write a function that converts a list to a tuple.", "def list_to_tuple(lst):\n    pass", [("[1, 2, 3]", "(1, 2, 3)")], "easy", 5),
        
        # Set operations
        ("List to Set", "Write a function that converts a list to a set.", "def list_to_set(lst):\n    pass", [("[1, 2, 2, 3]", "{1, 2, 3}")], "easy", 5),
        ("Set Intersection", "Write a function that returns intersection of two sets.", "def set_intersection(s1, s2):\n    pass", [("{1, 2, 3}, {2, 3, 4}", "{2, 3}")], "easy", 10),
        ("Set Union", "Write a function that returns union of two sets.", "def set_union(s1, s2):\n    pass", [("{1, 2}, {3, 4}", "{1, 2, 3, 4}")], "easy", 10),
        
        # More algorithms
        ("Linear Search", "Write a function that performs linear search. Return index or -1.", "def linear_search(lst, target):\n    pass", [("[1, 2, 3, 4, 5], 3", "2"), ("[1, 2, 3], 5", "-1")], "easy", 10),
        ("Selection Sort", "Write a function that sorts a list using selection sort.", "def selection_sort(lst):\n    pass", [("[3, 1, 4, 1, 5]", "[1, 1, 3, 4, 5]")], "medium", 20),
        ("Insertion Sort", "Write a function that sorts a list using insertion sort.", "def insertion_sort(lst):\n    pass", [("[3, 1, 4, 1, 5]", "[1, 1, 3, 4, 5]")], "medium", 20),
        ("Quick Sort", "Write a function that sorts a list using quicksort algorithm.", "def quicksort(lst):\n    pass", [("[3, 1, 4, 1, 5]", "[1, 1, 3, 4, 5]")], "hard", 25),
        
        # More string operations
        ("Strip Whitespace", "Write a function that removes leading and trailing whitespace.", "def strip(s):\n    pass", [("'  hello  '", "hello"), ("'python'", "python")], "easy", 5),
        ("Left Strip", "Write a function that removes leading whitespace.", "def lstrip(s):\n    pass", [("'  hello'", "hello")], "easy", 5),
        ("Right Strip", "Write a function that removes trailing whitespace.", "def rstrip(s):\n    pass", [("'hello  '", "hello")], "easy", 5),
        ("Starts With", "Write a function that checks if a string starts with a prefix.", "def starts_with(s, prefix):\n    pass", [("'hello', 'he'", "True"), ("'hello', 'lo'", "False")], "easy", 5),
        ("Ends With", "Write a function that checks if a string ends with a suffix.", "def ends_with(s, suffix):\n    pass", [("'hello', 'lo'", "True"), ("'hello', 'he'", "False")], "easy", 5),
        ("Find Index", "Write a function that finds the index of a substring in a string, or -1.", "def find_index(s, sub):\n    pass", [("'hello', 'll'", "2"), ("'hello', 'x'", "-1")], "easy", 10),
        ("Replace Substring", "Write a function that replaces all occurrences of a substring.", "def replace(s, old, new):\n    pass", [("'hello world', 'world', 'python'", "hello python")], "medium", 10),
        
        # Number operations
        ("Is Even", "Write a function that checks if a number is even.", "def is_even(n):\n    pass", [("4", "True"), ("5", "False")], "easy", 5),
        ("Is Odd", "Write a function that checks if a number is odd.", "def is_odd(n):\n    pass", [("5", "True"), ("4", "False")], "easy", 5),
        ("Is Divisible", "Write a function that checks if a is divisible by b.", "def is_divisible(a, b):\n    pass", [("10, 2", "True"), ("10, 3", "False")], "easy", 5),
        ("Square Root", "Write a function that calculates square root (use approximation).", "def sqrt(n):\n    pass", [("16", "4.0"), ("25", "5.0")], "medium", 15),
        ("LCM", "Write a function that finds the least common multiple of two numbers.", "def lcm(a, b):\n    pass", [("4, 6", "12"), ("5, 3", "15")], "medium", 15),
        ("Perfect Number", "Write a function that checks if a number is perfect (sum of divisors equals number).", "def is_perfect(n):\n    pass", [("6", "True"), ("10", "False")], "medium", 20),
        ("Armstrong Number", "Write a function that checks if a number is an Armstrong number.", "def is_armstrong(n):\n    pass", [("153", "True"), ("123", "False")], "medium", 20),
        
        # List operations
        ("Flatten List", "Write a function that flattens a nested list one level.", "def flatten(lst):\n    pass", [("[[1, 2], [3, 4]]", "[1, 2, 3, 4]")], "medium", 15),
        ("Chunk List", "Write a function that splits a list into chunks of size n.", "def chunk_list(lst, n):\n    pass", [("[1, 2, 3, 4, 5], 2", "[[1, 2], [3, 4], [5]]")], "medium", 15),
        ("Zip Lists", "Write a function that zips two lists into list of tuples.", "def zip_lists(list1, list2):\n    pass", [("[1, 2], [3, 4]", "[(1, 3), (2, 4)]")], "medium", 10),
        ("Unzip List", "Write a function that unzips a list of tuples into two lists.", "def unzip(lst):\n    pass", [("[(1, 3), (2, 4)]", "([1, 2], [3, 4])")], "medium", 15),
        ("Find Index of Element", "Write a function that finds the index of an element in a list, or -1.", "def find_index_list(lst, item):\n    pass", [("[1, 2, 3], 2", "1"), ("[1, 2, 3], 5", "-1")], "easy", 5),
        ("Count Occurrences", "Write a function that counts occurrences of an item in a list.", "def count_occurrences(lst, item):\n    pass", [("[1, 2, 2, 3], 2", "2"), ("[1, 2, 3], 5", "0")], "easy", 5),
        ("Remove Item", "Write a function that removes all occurrences of an item from a list.", "def remove_item(lst, item):\n    pass", [("[1, 2, 2, 3], 2", "[1, 3]")], "easy", 10),
        ("Insert at Index", "Write a function that inserts an item at a specific index in a list.", "def insert_at(lst, index, item):\n    pass", [("[1, 2, 3], 1, 9", "[1, 9, 2, 3]")], "easy", 10),
        ("Sublist", "Write a function that extracts a sublist from index start to end.", "def sublist(lst, start, end):\n    pass", [("[1, 2, 3, 4, 5], 1, 3", "[2, 3]")], "easy", 10),
        ("Count Even Numbers", "Write a function that counts even numbers in a list.", "def count_even(numbers):\n    pass", [("[1, 2, 3, 4, 5]", "2")], "easy", 5),
        ("Count Odd Numbers", "Write a function that counts odd numbers in a list.", "def count_odd(numbers):\n    pass", [("[1, 2, 3, 4, 5]", "3")], "easy", 5),
        ("Filter Even", "Write a function that returns only even numbers from a list.", "def filter_even(numbers):\n    pass", [("[1, 2, 3, 4, 5]", "[2, 4]")], "easy", 10),
        ("Filter Odd", "Write a function that returns only odd numbers from a list.", "def filter_odd(numbers):\n    pass", [("[1, 2, 3, 4, 5]", "[1, 3, 5]")], "easy", 10),
        ("Double List", "Write a function that doubles each number in a list.", "def double_list(numbers):\n    pass", [("[1, 2, 3]", "[2, 4, 6]")], "easy", 5),
        ("Square List", "Write a function that squares each number in a list.", "def square_list(numbers):\n    pass", [("[1, 2, 3]", "[1, 4, 9]")], "easy", 5),
        ("Add Lists", "Write a function that adds corresponding elements of two lists.", "def add_lists(list1, list2):\n    pass", [("[1, 2, 3], [4, 5, 6]", "[5, 7, 9]")], "easy", 10),
        ("Multiply Lists", "Write a function that multiplies corresponding elements of two lists.", "def multiply_lists(list1, list2):\n    pass", [("[1, 2, 3], [2, 3, 4]", "[2, 6, 12]")], "easy", 10),
        ("Dot Product", "Write a function that calculates the dot product of two lists.", "def dot_product(list1, list2):\n    pass", [("[1, 2, 3], [4, 5, 6]", "32")], "medium", 15),
        
        # More string challenges
        ("Capitalize First", "Write a function that capitalizes the first letter of a string.", "def capitalize_first(s):\n    pass", [("'hello'", "Hello"), ("'python'", "Python")], "easy", 5),
        ("Swap Case", "Write a function that swaps uppercase and lowercase letters.", "def swap_case(s):\n    pass", [("'Hello World'", "hELLO wORLD")], "medium", 10),
        ("Remove Vowels", "Write a function that removes all vowels from a string.", "def remove_vowels(s):\n    pass", [("'hello'", "hll"), ("'python'", "pythn")], "medium", 10),
        ("Remove Consonants", "Write a function that removes all consonants from a string.", "def remove_consonants(s):\n    pass", [("'hello'", "eo"), ("'python'", "o")], "medium", 10),
        ("Is Digit", "Write a function that checks if all characters in a string are digits.", "def is_digit(s):\n    pass", [("'123'", "True"), ("'12a'", "False")], "easy", 5),
        ("Is Alpha", "Write a function that checks if all characters in a string are letters.", "def is_alpha(s):\n    pass", [("'hello'", "True"), ("'hello123'", "False")], "easy", 5),
        ("Is Alphanumeric", "Write a function that checks if all characters are alphanumeric.", "def is_alnum(s):\n    pass", [("'hello123'", "True"), ("'hello!'", "False")], "easy", 5),
        ("Extract Digits", "Write a function that extracts all digits from a string.", "def extract_digits(s):\n    pass", [("'hello123world'", "123"), ("'abc'", "")], "medium", 10),
        ("Extract Letters", "Write a function that extracts all letters from a string.", "def extract_letters(s):\n    pass", [("'hello123world'", "helloworld"), ("'123'", "")], "medium", 10),
        ("Word Count Dict", "Write a function that returns a dictionary with word counts.", "def word_count_dict(s):\n    pass", [("'hello world hello'", "{'hello': 2, 'world': 1}")], "medium", 15),
        
        # More algorithms
        ("Reverse Digits", "Write a function that reverses the digits of a number.", "def reverse_digits(n):\n    pass", [("123", "321"), ("-123", "-321")], "medium", 15),
        ("Sum of Digits", "Write a function that calculates the sum of digits of a number.", "def sum_digits(n):\n    pass", [("123", "6"), ("456", "15")], "easy", 10),
        ("Product of Digits", "Write a function that calculates the product of digits of a number.", "def product_digits(n):\n    pass", [("123", "6"), ("456", "120")], "easy", 10),
        ("Count Digits", "Write a function that counts the number of digits in a number.", "def count_digits(n):\n    pass", [("123", "3"), ("0", "1")], "easy", 5),
        ("Is Palindrome Number", "Write a function that checks if a number is a palindrome.", "def is_palindrome_num(n):\n    pass", [("121", "True"), ("123", "False")], "medium", 15),
        ("Next Prime", "Write a function that finds the next prime number after n.", "def next_prime(n):\n    pass", [("10", "11"), ("17", "19")], "medium", 20),
        ("Prime Factors", "Write a function that returns prime factors of a number.", "def prime_factors(n):\n    pass", [("12", "[2, 2, 3]"), ("17", "[17]")], "hard", 25),
        
        # Final batch to reach 100
        ("All Permutations", "Write a function that generates all permutations of a list.", "def permutations(lst):\n    pass", [("[1, 2]", "[(1, 2), (2, 1)]")], "hard", 30),
        ("Combinations", "Write a function that generates all combinations of r elements from a list.", "def combinations(lst, r):\n    pass", [("[1, 2, 3], 2", "[(1, 2), (1, 3), (2, 3)]")], "hard", 30),
        ("Matrix Transpose", "Write a function that transposes a matrix (list of lists).", "def transpose(matrix):\n    pass", [("[[1, 2], [3, 4]]", "[[1, 3], [2, 4]]")], "medium", 20),
        ("Matrix Multiply", "Write a function that multiplies two matrices.", "def matrix_multiply(m1, m2):\n    pass", [("[[1, 2], [3, 4]], [[5, 6], [7, 8]]", "[[19, 22], [43, 50]]")], "hard", 30),
        ("Depth First Search", "Write a function that performs DFS on a graph represented as adjacency list.", "def dfs(graph, start):\n    pass", [("{}", "[]")], "hard", 35),
    ]
    
    for title, desc, code, tests, diff, pts in more_challenges:
        challenges.append({
            "title": title,
            "description": desc,
            "difficulty": diff,
            "starter_code": code,
            "test_cases": [{"input": inp, "expected_output": out} for inp, out in tests],
            "points": pts
        })
    
    return challenges

if __name__ == '__main__':
    with app.app_context():
        all_challenges = generate_more_challenges()
        print(f"Generated {len(all_challenges)} challenges")
        
        # Check how many already exist
        existing = CodingChallenge.query.count()
        print(f"Existing challenges in database: {existing}")
        
        if existing >= 100:
            print("Database already has 100+ challenges. Skipping insertion.")
        else:
            added = 0
            for challenge_data in all_challenges:
                # Check if challenge with same title already exists
                existing_challenge = CodingChallenge.query.filter_by(title=challenge_data["title"]).first()
                if not existing_challenge:
                    challenge = CodingChallenge(
                        title=challenge_data["title"],
                        description=challenge_data["description"],
                        difficulty=challenge_data["difficulty"],
                        starter_code=challenge_data["starter_code"],
                        test_cases_json=json.dumps(challenge_data["test_cases"]),
                        points=challenge_data["points"],
                        is_active=True
                    )
                    db.session.add(challenge)
                    added += 1
            
            db.session.commit()
            print(f"✓ Added {added} new challenges to database")
            print(f"Total challenges now: {CodingChallenge.query.count()}")

