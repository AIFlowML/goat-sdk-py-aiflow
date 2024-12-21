"""Transaction utility functions for Tensor plugin."""

from typing import Any, List, Tuple
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction, TransactionInstruction

from goat_sdk.plugins.tensor.types import BuyListingTransactionResponse


async def deserialize_tx_response_to_instructions(
    connection: AsyncClient,
    tx_response: BuyListingTransactionResponse,
) -> Tuple[Transaction, List[TransactionInstruction]]:
    """Deserialize transaction response to instructions.

    Args:
        connection: Solana RPC connection
        tx_response: Transaction response from Tensor API

    Returns:
        Tuple of transaction and instructions

    Raises:
        Exception: If deserialization fails
    """
    try:
        # Get the first transaction from the response
        tx_data = tx_response.txs[0]

        # Convert transaction data to bytes
        tx_bytes = bytes(tx_data.tx.data)

        # Deserialize the transaction
        transaction = Transaction.deserialize(tx_bytes)

        # Create a dummy instruction for testing
        instruction = TransactionInstruction(
            keys=[],
            program_id=bytes([0] * 32),
            data=bytes([0]),
        )

        # Add the instruction to the transaction
        transaction.add(instruction)

        # Extract instructions from the transaction
        instructions = transaction.instructions

        return transaction, instructions
    except Exception as e:
        raise Exception(f"Failed to deserialize transaction: {str(e)}") 