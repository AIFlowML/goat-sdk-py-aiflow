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
     
     Path: examples/hyperliquid/test_hyperliquid.py
"""

"""
Test file for verifying Hyperliquid functionality on testnet.
This is a temporary file for testing purposes only.

Available Methods:

Market Data:
- get_markets() -> List[MarketInfo]
  Gets list of all available markets
  
- get_market_summary(coin: str) -> MarketSummary
  Gets detailed market info including price, volume, etc.
  
- get_orderbook(coin: str, depth: int = 100) -> OrderbookResponse
  Gets market orderbook with bids and asks
  
- get_recent_trades(coin: str, limit: int = 100) -> List[TradeInfo]
  Gets recent trades for a market

Order Management:
- create_order(request: OrderRequest) -> OrderResult
  Places a new order (limit, market, etc.)
  
- cancel_order(coin: str, order_id: str) -> OrderResult
  Cancels a specific order
  
- cancel_all_orders(coin: Optional[str] = None) -> List[OrderResult]
  Cancels all open orders, optionally filtered by coin
  
- get_open_orders(coin: Optional[str] = None) -> List[OrderResponse]
  Gets all open orders, optionally filtered by coin
  
- get_order_history(
      coin: Optional[str] = None,
      limit: int = 100,
      start_time: Optional[int] = None,
      end_time: Optional[int] = None
  ) -> List[OrderResponse]
  Gets historical orders with optional filters

Agent Wallet Management:
- approve_agent_wallet(
      agent_address: str,
      agent_name: Optional[str] = None,
      chain_id: str = "0xa4b1"
  ) -> Dict[str, Any]
  Approves an agent wallet for trading on behalf of the main wallet
"""

import asyncio
import logging
import os
from decimal import Decimal
from typing import List, Dict, Any
import time

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich import box
from rich.prompt import Confirm

from goat_sdk import GoatSDK
from goat_sdk.types import Network, Chain
from goat_sdk.plugins.hyperliquid import HyperliquidPlugin, HyperliquidConfig
from goat_sdk.plugins.hyperliquid.types.order import OrderRequest, OrderType, OrderSide

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Rich console
console = Console()

# Test configuration from .env
os.environ["API_KEY"] = "your_api_key"
os.environ["API_SECRET"] = "your_api_secret"
os.environ["MAINNET"] = "false"
os.environ["HYPERLIQUID_INFO_URL"] = "https://api.hyperliquid.xyz/info"
os.environ["HYPERLIQUID_EXCHANGE_URL"] = "https://api.hyperliquid.xyz/exchange"

# For testnet, override the URLs
if os.getenv("MAINNET", "false").lower() == "false":
    os.environ["HYPERLIQUID_INFO_URL"] = "https://api.hyperliquid-testnet.xyz/info"
    os.environ["HYPERLIQUID_EXCHANGE_URL"] = "https://api.hyperliquid-testnet.xyz/exchange"

TEST_WALLET = "0xEfDaFA4Cc07BbF8421477db4E3Ce79C96Baf5465"
AGENT_WALLET = "0x" + "1" * 40  # Example agent wallet address

# Dummy private key for testing (32 bytes hex)
DUMMY_KEY = "0" * 64  # This is just for testing, never use in production!

def create_markets_table(markets: List[Dict[str, Any]]) -> Table:
    """Create a rich table for markets data."""
    table = Table(
        title="Available Markets",
        box=box.ROUNDED,
        header_style="bold magenta",
        border_style="blue"
    )
    
    table.add_column("Market", style="cyan")
    table.add_column("Price", justify="right", style="green")
    table.add_column("24h Volume", justify="right", style="yellow")
    table.add_column("Open Interest", justify="right", style="red")
    table.add_column("Funding Rate", justify="right", style="magenta")
    
    for market in markets[:10]:  # Show top 10 markets
        table.add_row(
            market.coin,
            f"${float(market.price):,.2f}",
            f"${float(market.volume_24h):,.0f}",
            f"${float(market.open_interest):,.0f}",
            f"{float(market.funding_rate):.4%}"
        )
    
    return table

def create_orderbook_table(orderbook: Dict[str, Any], market: str) -> Table:
    """Create a rich table for orderbook data."""
    table = Table(
        title=f"Orderbook - {market}",
        box=box.ROUNDED,
        header_style="bold magenta",
        border_style="blue"
    )
    
    table.add_column("Bid Size", justify="right", style="green")
    table.add_column("Bid Price", justify="right", style="green")
    table.add_column("Spread", justify="center", style="yellow")
    table.add_column("Ask Price", justify="right", style="red")
    table.add_column("Ask Size", justify="right", style="red")
    
    # Calculate spread for each level
    for i in range(min(len(orderbook.bids), len(orderbook.asks), 5)):  # Show top 5 levels
        bid = orderbook.bids[i]
        ask = orderbook.asks[i]
        spread = float(ask.price) - float(bid.price)
        spread_pct = (spread / float(bid.price)) * 100
        
        table.add_row(
            f"{float(bid.size):,.4f}",
            f"${float(bid.price):,.2f}",
            f"{spread_pct:.2f}%" if i == 0 else "",  # Only show spread for top level
            f"${float(ask.price):,.2f}",
            f"{float(ask.size):,.4f}"
        )
    
    return table

def create_trades_table(trades: List[Dict[str, Any]], market: str) -> Table:
    """Create a rich table for recent trades."""
    table = Table(
        title=f"Recent Trades - {market}",
        box=box.ROUNDED,
        header_style="bold magenta",
        border_style="blue"
    )
    
    table.add_column("Time", style="cyan")
    table.add_column("Side", style="bold")
    table.add_column("Price", justify="right")
    table.add_column("Size", justify="right")
    
    for trade in trades[:5]:  # Show last 5 trades
        # Convert timestamp to relative time
        timestamp = time.strftime('%H:%M:%S', time.localtime(trade.timestamp / 1000))
        
        table.add_row(
            timestamp,
            "[green]BUY[/green]" if trade.side == OrderSide.BUY else "[red]SELL[/red]",
            f"${float(trade.price):,.2f}",
            f"{float(trade.size):.4f}"
        )
    
    return table

async def test_market_data(hyperliquid: HyperliquidPlugin):
    """Test basic market data retrieval."""
    try:
        with console.status("[bold green]Fetching market data..."):
            # Test 1: Get markets
            console.print("\n[bold cyan]Getting markets data...[/bold cyan]")
            markets = await hyperliquid.get_markets()
            console.print(Panel(create_markets_table(markets)))
            
            if not markets:
                console.print("[bold red]No markets found![/bold red]")
                return False
                
            # Test 2: Get orderbook for first market
            first_market = markets[0]
            console.print(f"\n[bold cyan]Getting orderbook for {first_market.coin}...[/bold cyan]")
            orderbook = await hyperliquid.get_orderbook(first_market.coin)
            console.print(Panel(create_orderbook_table(orderbook, first_market.coin)))
            
            # Test 3: Get recent trades
            console.print(f"\n[bold cyan]Getting recent trades for {first_market.coin}...[/bold cyan]")
            trades = await hyperliquid.get_recent_trades(first_market.coin)
            console.print(Panel(create_trades_table(trades, first_market.coin)))
            
            return True
            
    except Exception as e:
        console.print(f"[bold red]Error during testing: {str(e)}[/bold red]")
        return False

async def test_trading_operations(hyperliquid: HyperliquidPlugin, wallet_address: str = None):
    """Test basic trading operations if wallet is provided."""
    if not wallet_address:
        logger.warning("No wallet address provided")
        console.print("[yellow]No wallet address provided, skipping trading operations test[/yellow]")
        return False
        
    if not hyperliquid._get_service(testnet=True).api_key:
        logger.warning("No API key provided")
        console.print("[yellow]No API key provided, skipping trading operations test[/yellow]")
        return False
        
    try:
        # Get BTC-USDC market
        markets = await hyperliquid.get_markets()
        btc_market = next((m for m in markets if m.coin == "BTC"), None)
        
        if not btc_market:
            logger.error("BTC market not found")
            console.print("[bold red]BTC market not found![/bold red]")
            return False
            
        # Test 4: Place a small limit order
        console.print("\n[bold cyan]Testing order placement...[/bold cyan]")
        try:
            # Use current market price for the order
            price = float(btc_market.price) * 0.95  # 5% below market
            size = Decimal("0.001")  # Very small size for testing
            
            logger.info(f"Creating limit order - Market: {btc_market.coin}, Side: BUY, Price: ${price:,.2f}, Size: {size}")
            
            order_request = OrderRequest(
                coin=btc_market.coin,
                side=OrderSide.BUY,
                price=Decimal(str(price)),
                size=size,
                type=OrderType.LIMIT,
                reduce_only=False,
                post_only=True
            )
            
            order_result = await hyperliquid.create_order(order_request)
            
            if not order_result.success:
                logger.error(f"Order failed: {order_result.error}")
                console.print(Panel(f"[red]Order failed: {order_result.error}[/red]"))
                return False
                
            order_id = order_result.order.id
            logger.info(f"Order placed successfully: {order_id}")
            console.print(Panel(f"[green]Order placed successfully: {order_id}[/green]"))
            
            # Test 5: Cancel the order
            console.print("\n[bold cyan]Testing order cancellation...[/bold cyan]")
            result = await hyperliquid.cancel_order(
                coin=btc_market.coin,
                order_id=order_id
            )
            console.print(Panel(f"[green]Order cancelled: {result.success}[/green]"))
            
        except Exception as e:
            logger.exception("Order operation failed")
            console.print(Panel(f"[red]Order failed: {str(e)}[/red]"))
            return False
            
        return True
        
    except Exception as e:
        logger.exception("Trading test failed")
        console.print(f"[bold red]Error during testing: {str(e)}[/bold red]")
        return False

async def test_agent_wallet(hyperliquid: HyperliquidPlugin):
    """Test agent wallet approval and usage."""
    if not hyperliquid._get_service(testnet=True).api_key:
        logger.warning("No API key provided")
        console.print("[yellow]No API key provided, skipping agent wallet test[/yellow]")
        return False
        
    try:
        console.print("\n[bold cyan]Approving agent wallet...[/bold cyan]")
        logger.info(f"Approving agent wallet - Address: {AGENT_WALLET}, Name: TestAgent")
        
        result = await hyperliquid._get_service(testnet=True).approve_agent_wallet(
            agent_address=AGENT_WALLET,
            agent_name="TestAgent"
        )
        
        if not result.get("success"):
            error = result.get("error", "Unknown error")
            logger.error(f"Agent wallet approval failed: {error}")
            console.print(f"[red]Agent wallet approval failed: {error}[/red]")
            return False
            
        logger.info("Agent wallet successfully approved")
        console.print("[green]Agent wallet successfully approved[/green]")
        return True
        
    except Exception as e:
        logger.exception("Agent wallet test failed")
        console.print(f"Error during agent wallet test: {str(e)}")
        return False

async def main():
    """Run all tests."""
    console.print(Panel.fit(
        "[bold green]Hyperliquid Testnet Functionality Tests[/bold green]",
        border_style="green"
    ))
    
    try:
        # Initialize SDK for testnet
        sdk = GoatSDK(
            private_key=DUMMY_KEY,  # We don't need a real key for read operations
            network=Network.TESTNET,  # Using testnet
            chain=Chain.SOLANA,
            options={
                "eth_wallet": TEST_WALLET
            }
        )
        
        # Create Hyperliquid config
        config = HyperliquidConfig(
            api_key=os.getenv("API_KEY"),
            api_secret=os.getenv("API_SECRET"),
            testnet=True,
            api_url=os.getenv("HYPERLIQUID_INFO_URL"),
            exchange_url=os.getenv("HYPERLIQUID_EXCHANGE_URL")
        )
        
        # Initialize plugin with config
        hyperliquid = HyperliquidPlugin(config=config)  # testnet is in config
        
        try:
            # Test market data operations
            market_data_success = await test_market_data(hyperliquid)
            console.print(Panel(
                f"[{'green' if market_data_success else 'red'}]Market data tests: "
                f"{'✓ PASSED' if market_data_success else '✗ FAILED'}[/]"
            ))
            
            # Test trading operations (optional)
            if Confirm.ask("Would you like to test trading operations?"):
                trading_success = await test_trading_operations(hyperliquid, TEST_WALLET)
                console.print(Panel(
                    f"[{'green' if trading_success else 'red'}]Trading operations tests: "
                    f"{'✓ PASSED' if trading_success else '✗ FAILED'}[/]"
                ))
            
            # Test agent wallet operations (optional)
            if Confirm.ask("Would you like to test agent wallet functionality?"):
                agent_success = await test_agent_wallet(hyperliquid)
                console.print(Panel(
                    f"[{'green' if agent_success else 'red'}]Agent wallet test: "
                    f"{'✓ PASSED' if agent_success else '✗ FAILED'}[/]"
                ))
                
        finally:
            # Clean up
            await hyperliquid.close()
            await sdk.close()
            
    except Exception as e:
        console.print(f"[bold red]Error during test setup: {str(e)}[/bold red]")
    
    console.print(Panel.fit(
        "[bold green]Tests completed![/bold green]",
        border_style="green"
    ))

if __name__ == "__main__":
    asyncio.run(main()) 