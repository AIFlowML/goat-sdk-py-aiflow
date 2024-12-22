"""Utility for converting strings to snake case."""
import re
from typing import Any, Dict, Optional


def to_snake_case(s: str) -> str:
    """Convert a string to snake case."""
    # Replace hyphens and dots with underscores
    s = s.replace('-', '_').replace('.', '_')
    
    # Insert underscore between camelCase
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s)
    
    # Convert to lowercase and normalize multiple underscores
    return re.sub(r'_+', '_', s.lower())


def from_snake_case(s: str, separator: str = '') -> str:
    """Convert a snake case string to camelCase, preserving leading underscores.
    
    Args:
        s: String to convert
        separator: Optional separator for words (default: '')
    """
    # Count and preserve leading underscores
    leading_underscores = ''
    for char in s:
        if char == '_':
            leading_underscores += '_'
        else:
            break
            
    # Remove leading/trailing underscores for processing
    s = s.strip('_')
    
    # Split into parts
    parts = s.split('_')
    
    if separator:
        # If separator provided, join with separator
        return leading_underscores + separator.join(parts)
    else:
        # Convert to camelCase
        return leading_underscores + parts[0] + ''.join(p.title() for p in parts[1:])


def to_camel_case(s: str) -> str:
    """Convert a string to camelCase."""
    # First convert to snake case to normalize
    s = to_snake_case(s)
    
    # Then convert to camelCase
    return from_snake_case(s)


def to_pascal_case(s: str) -> str:
    """Convert a string to PascalCase."""
    # First convert to camelCase
    s = to_camel_case(s)
    
    # Then capitalize first letter
    return s[0].upper() + s[1:] if s else s


def to_kebab_case(s: str) -> str:
    """Convert a string to kebab-case."""
    # First convert to snake case
    s = to_snake_case(s)
    
    # Then replace underscores with hyphens
    return s.replace('_', '-')


def snake_case_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """Convert all dictionary keys to snake case.
    
    Args:
        d: Dictionary to convert
        
    Returns:
        Dictionary with snake case keys
    """
    return {to_snake_case(k): v for k, v in d.items()}
