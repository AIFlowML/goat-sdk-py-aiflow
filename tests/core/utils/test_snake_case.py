"""Tests for snake_case utility functions."""

import pytest
from goat_sdk.core.utils.snake_case import (
    to_snake_case,
    from_snake_case,
    to_camel_case,
    to_pascal_case,
    to_kebab_case,
)

def test_to_snake_case():
    """Test converting strings to snake case."""
    test_cases = [
        ("", ""),  # Empty string
        ("hello", "hello"),  # Already lowercase
        ("helloWorld", "hello_world"),  # Camel case
        ("HelloWorld", "hello_world"),  # Pascal case
        ("hello_world", "hello_world"),  # Already snake case
        ("hello-world", "hello_world"),  # Kebab case
        ("HELLO_WORLD", "hello_world"),  # Upper snake case
        ("helloWORLD", "hello_world"),  # Mixed case
        ("hello123World", "hello123_world"),  # With numbers
        ("hello__world", "hello_world"),  # Multiple underscores
        ("hello--world", "hello_world"),  # Multiple hyphens
        ("hello.world", "hello_world"),  # With dots
    ]
    
    for input_str, expected in test_cases:
        assert to_snake_case(input_str) == expected

def test_from_snake_case():
    """Test converting from snake case to other formats."""
    test_cases = [
        ("", ""),  # Empty string
        ("hello", "hello"),  # Single word
        ("hello_world", "helloWorld"),  # Basic case
        ("hello_world_test", "helloWorldTest"),  # Multiple words
        ("_hello_world", "_helloWorld"),  # Leading underscore
        ("hello_world_", "helloWorld"),  # Trailing underscore
    ]
    
    for input_str, expected in test_cases:
        assert from_snake_case(input_str) == expected
        
    # Test with different separators
    assert from_snake_case("hello_world", "-") == "hello-world"
    assert from_snake_case("hello_world_test", ".") == "hello.world.test"

def test_to_camel_case():
    """Test converting strings to camel case."""
    test_cases = [
        ("", ""),  # Empty string
        ("hello", "hello"),  # Single word
        ("hello_world", "helloWorld"),  # Snake case
        ("HelloWorld", "helloWorld"),  # Pascal case
        ("hello-world", "helloWorld"),  # Kebab case
        ("HELLO_WORLD", "helloWorld"),  # Upper snake case
        ("helloWorld", "helloWorld"),  # Already camel case
    ]
    
    for input_str, expected in test_cases:
        assert to_camel_case(input_str) == expected

def test_to_pascal_case():
    """Test converting strings to pascal case."""
    test_cases = [
        ("", ""),  # Empty string
        ("hello", "Hello"),  # Single word
        ("hello_world", "HelloWorld"),  # Snake case
        ("helloWorld", "HelloWorld"),  # Camel case
        ("hello-world", "HelloWorld"),  # Kebab case
        ("HELLO_WORLD", "HelloWorld"),  # Upper snake case
        ("HelloWorld", "HelloWorld"),  # Already pascal case
    ]
    
    for input_str, expected in test_cases:
        assert to_pascal_case(input_str) == expected

def test_to_kebab_case():
    """Test converting strings to kebab case."""
    test_cases = [
        ("", ""),  # Empty string
        ("hello", "hello"),  # Single word
        ("hello_world", "hello-world"),  # Snake case
        ("helloWorld", "hello-world"),  # Camel case
        ("HelloWorld", "hello-world"),  # Pascal case
        ("HELLO_WORLD", "hello-world"),  # Upper snake case
        ("hello-world", "hello-world"),  # Already kebab case
    ]
    
    for input_str, expected in test_cases:
        assert to_kebab_case(input_str) == expected
