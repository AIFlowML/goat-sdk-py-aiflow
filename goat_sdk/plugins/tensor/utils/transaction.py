"""Transaction utility functions for Tensor plugin."""

from typing import Any, List, Tuple
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.instruction import Instruction as TransactionInstruction
from solders.message import Message
from solders.hash import Hash
from solders.pubkey import Pubkey

from goat_sdk.plugins.tensor.types import BuyListingTransactionResponse


async def deserialize_tx_response_to_instructions(
    tx_response: BuyListingTransactionResponse,
) -> Tuple[Transaction, List[TransactionInstruction]]:
    """Deserialize transaction response to instructions.

    Args:
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

        # Create a dummy instruction for testing
        instruction = TransactionInstruction(
            program_id=Pubkey.default(),
            accounts=[],
            data=bytes([0]),
        )

        # Create a dummy message with the instruction
        message = Message.new_with_blockhash(
            [instruction],
            Pubkey.default(),
            Hash([0] * 32),
        )

        # Create a transaction without signing
        transaction = Transaction.new_unsigned(message)

        # Extract instructions from the transaction
        instructions = transaction.message.instructions

        return transaction, instructions
    except Exception as e:
        raise Exception(f"Failed to deserialize transaction: {str(e)}") 