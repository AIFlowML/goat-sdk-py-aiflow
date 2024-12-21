"""Utility for converting strings to snake case."""
import re
from typing import Any, Dict, Optional


def to_snake_case(text: str) -> str:
    """Convert a string to snake case.
    
    Args:
        text: String to convert
        
    Returns:
        Snake case version of the string
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def from_snake_case(text: str) -> str:
    """Convert a string from snake case to camel case.
    
    Args:
        text: String to convert
        
    Returns:
        Camel case version of the string
    """
    components = text.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def to_camel_case(text: str) -> str:
    """Convert a string to camel case.
    
    Args:
        text: String to convert
        
    Returns:
        Camel case version of the string
    """
    components = text.split('_')
    return ''.join(x.title() for x in components)


def to_pascal_case(text: str) -> str:
    """Convert a string to pascal case.
    
    Args:
        text: String to convert
        
    Returns:
        Pascal case version of the string
    """
    return ''.join(word.capitalize() for word in text.split('_'))


def to_kebab_case(text: str) -> str:
    """Convert a string to kebab case.
    
    Args:
        text: String to convert
        
    Returns:
        Kebab case version of the string
    """
    return to_snake_case(text).replace('_', '-')


def snake_case_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """Convert all dictionary keys to snake case.
    
    Args:
        d: Dictionary to convert
        
    Returns:
        Dictionary with snake case keys
    """
    return {to_snake_case(k): v for k, v in d.items()}
