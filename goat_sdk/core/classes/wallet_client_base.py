"""Base class for wallet clients."""

from abc import ABC, abstractmethod
from typing import Dict, List
from typing_extensions import TypedDict
from pydantic import BaseModel


class Balance(TypedDict):
    """Balance information for a token or native currency."""
    decimals: int
    symbol: str
    name: str
    value: str
    in_base_units: str


class Signature(TypedDict):
    """Signature information."""
    signature: str


class GetAddressParams(BaseModel):
    """Parameters for getting an address."""
    pass


class GetChainParams(BaseModel):
    """Parameters for getting chain information."""
    pass


class SignMessageParams(BaseModel):
    """Parameters for signing a message."""
    message: str


class BalanceOfParams(BaseModel):
    """Parameters for getting balance information."""
    address: str


class SignTransactionParams(BaseModel):
    """Parameters for signing a transaction."""
    transaction: str


class SendTransactionParams(BaseModel):
    """Parameters for sending a transaction."""
    transaction: str


class WalletClientBase(ABC, BaseModel):
    """Base class for wallet clients.
    
    This class defines the interface that all wallet clients must implement.
    Wallet clients are used to interact with blockchain networks and manage
    private keys.
    
    Attributes:
        provider_url: URL of the blockchain provider
        private_key: Private key for signing transactions
    """
    
    provider_url: str
    private_key: str
    
    @abstractmethod
    def get_address(self, params: GetAddressParams) -> str:
        """Get the wallet address.
        
        Args:
            params: Parameters for getting the address
            
        Returns:
            Wallet address as a string
        """
        pass

    @abstractmethod
    def get_chain(self, params: GetChainParams) -> Dict:
        """Get information about the current chain.
        
        Args:
            params: Parameters for getting chain information
            
        Returns:
            Chain information as a dictionary
        """
        pass

    @abstractmethod
    async def sign_message(self, params: SignMessageParams) -> Signature:
        """Sign a message with the wallet's private key.
        
        Args:
            params: Parameters for signing the message
            
        Returns:
            Signature information
        """
        pass

    @abstractmethod
    async def balance_of(self, params: BalanceOfParams) -> Balance:
        """Get the balance for a given address.
        
        Args:
            params: Parameters for getting balance information
            
        Returns:
            Balance information
        """
        pass

    @abstractmethod
    async def sign_transaction(self, params: SignTransactionParams) -> str:
        """Sign a transaction with the wallet's private key.
        
        Args:
            params: Parameters for signing the transaction
            
        Returns:
            Signed transaction as a string
        """
        pass

    @abstractmethod
    async def send_transaction(self, params: SendTransactionParams) -> str:
        """Send a signed transaction to the blockchain.
        
        Args:
            params: Parameters for sending the transaction
            
        Returns:
            Transaction hash as a string
        """
        pass

    def get_core_tools(self) -> List[Dict]:
        """Get the core tools available for this wallet client.
        
        Returns:
            List of tool definitions as dictionaries
        """
        return [
            {
                "name": "get_address",
                "description": "Get the wallet address",
                "parameters": GetAddressParams.model_json_schema()
            },
            {
                "name": "get_chain",
                "description": "Get information about the current chain",
                "parameters": GetChainParams.model_json_schema()
            },
            {
                "name": "sign_message",
                "description": "Sign a message with the wallet's private key",
                "parameters": SignMessageParams.model_json_schema()
            },
            {
                "name": "balance_of",
                "description": "Get the balance for a given address",
                "parameters": BalanceOfParams.model_json_schema()
            },
            {
                "name": "sign_transaction",
                "description": "Sign a transaction with the wallet's private key",
                "parameters": SignTransactionParams.model_json_schema()
            },
            {
                "name": "send_transaction",
                "description": "Send a signed transaction to the blockchain",
                "parameters": SendTransactionParams.model_json_schema()
            }
        ]
