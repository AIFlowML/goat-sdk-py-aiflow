"""
          _____                    _____                    _____                    _____           _______                   _____          
         /\    \                  /\    \                  /\    \                  /\    \         /::\    \                 /\    \         
        /::\    \                /::\    \                /::\    \                /::\____\       /::::\    \               /::\____\        
       /::::\    \               \:::\    \              /::::\    \              /:::/    /      /::::::\    \             /:::/    /        
      /::::::\    \               \:::\    \            /::::::\    \            /:::/    /      /::::::::\    \           /:::/   _/___      
     /:::/\:::\    \               \:::\    \          /:::/\:::\    \          /:::/    /      /:::/~~\:::\    \         /:::/   /\    \     
    /:::/__\:::\    \               \:::\    \        /:::/__\:::\    \        /:::/    /      /:::/    \:::\    \       /:::/   /::\____\    
   /::::\   \:::\    \              /::::\    \      /::::\   \:::\    \      /:::/    /      /:::/    / \:::\    \     /:::/   /:::/    /    
  /::::::\   \:::\    \    ____    /::::::\    \    /::::::\   \:::\    \    /:::/    /      /:::/____/   \:::\____\   /:::/   /:::/   _/___  
 /:::/\:::\   \:::\    \  /\   \  /:::/\:::\    \  /:::/\:::\   \:::\    \  /:::/    /      |:::|    |     |:::|    | /:::/___/:::/   /\    \ 
/:::/  \:::\   \:::\____\/::\   \/:::/  \:::\____\/:::/  \:::\   \:::\____\/:::/____/       |:::|____|     |:::|    ||:::|   /:::/   /::\____\
\::/    \:::\  /:::/    /\:::\  /:::/    \::/    /\::/    \:::\   \::/    /\:::\    \        \:::\    \   /:::/    / |:::|__/:::/   /:::/    /
 \/____/ \:::\/:::/    /  \:::\/:::/    / \/____/  \/____/ \:::\   \/____/  \:::\    \        \:::\    \ /:::/    /   \:::\/:::/   /:::/    / 
          \::::::/    /    \::::::/    /                    \:::\    \       \:::\    \        \:::\    /:::/    /     \::::::/   /:::/    /  
           \::::/    /      \::::/____/                      \:::\____\       \:::\    \        \:::\__/:::/    /       \::::/___/:::/    /   
           /:::/    /        \:::\    \                       \::/    /        \:::\    \        \::::::::/    /         \:::\__/:::/    /    
          /:::/    /          \:::\    \                       \/____/          \:::\    \        \::::::/    /           \::::::::/    /     
         /:::/    /            \:::\    \                                        \:::\    \        \::::/    /             \::::::/    /      
        /:::/    /              \:::\____\                                        \:::\____\        \::/____/               \::::/    /       
        \::/    /                \::/    /                                         \::/    /         ~~                      \::/____/        
         \/____/                  \/____/                                           \/____/                                   ~~              
                                                                                                                                              

         
 
     GOAT-SDK Python - Unofficial SDK for GOAT - Igor Lessio - AIFlow.ml
     
     Path: goat_sdk/plugins/hyperliquid/utils.py
"""

"""Error classes for Hyperliquid API."""

class HyperliquidError(Exception):
    """Base error class for Hyperliquid API."""
    pass

class RequestError(HyperliquidError):
    """Error raised when a request fails."""
    
    def __init__(self, message: str, status_code: int = None):
        """Initialize error.
        
        Args:
            message: Error message
            status_code: Optional HTTP status code
        """
        super().__init__(message)
        self.status_code = status_code

class AuthenticationError(HyperliquidError):
    """Error raised when authentication fails."""
    pass

class RateLimitError(HyperliquidError):
    """Error raised when rate limit is exceeded."""
    pass

class OrderError(HyperliquidError):
    """Error raised when order operation fails."""
    pass

class MarketError(HyperliquidError):
    """Error raised when market operation fails."""
    pass

class WebSocketError(HyperliquidError):
    """Error raised when WebSocket operation fails."""
    pass 