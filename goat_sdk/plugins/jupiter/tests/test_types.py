"""Tests for Jupiter types."""

import pytest
from pydantic import ValidationError

from goat_sdk.plugins.jupiter.types import (
    SwapMode,
    SwapInfo,
    PlatformFee,
    RoutePlanStep,
    QuoteResponse,
    SwapRequest,
    SwapResponse,
    SwapResult,
)


def test_swap_mode():
    """Test SwapMode enum."""
    assert SwapMode.EXACT_IN == "ExactIn"
    assert SwapMode.EXACT_OUT == "ExactOut"

    with pytest.raises(ValueError):
        SwapMode("InvalidMode")


def test_swap_info():
    """Test SwapInfo model."""
    info = SwapInfo(
        ammKey="amm1",
        label="Orca",
        inputMint="0x" + "11" * 32,
        outputMint="0x" + "22" * 32,
        inAmount="1000000",
        outAmount="2000000",
        feeAmount="1000",
        feeMint="0x" + "33" * 32,
    )

    assert info.amm_key == "amm1"
    assert info.label == "Orca"
    assert info.input_mint == "0x" + "11" * 32
    assert info.output_mint == "0x" + "22" * 32
    assert info.in_amount == "1000000"
    assert info.out_amount == "2000000"
    assert info.fee_amount == "1000"
    assert info.fee_mint == "0x" + "33" * 32


def test_platform_fee():
    """Test PlatformFee model."""
    fee = PlatformFee(
        amount="1000",
        feeMint="0x" + "11" * 32,
        feeBps=50,
    )

    assert fee.amount == "1000"
    assert fee.fee_mint == "0x" + "11" * 32
    assert fee.fee_bps == 50

    with pytest.raises(ValidationError):
        PlatformFee(amount="invalid", feeMint="0x" + "11" * 32, feeBps=50)

    with pytest.raises(ValidationError):
        PlatformFee(amount="1000", feeMint="0x" + "11" * 32, feeBps=-1)


def test_route_plan_step():
    """Test RoutePlanStep model."""
    step = RoutePlanStep(
        swapInfo=SwapInfo(
            ammKey="amm1",
            label="Orca",
            inputMint="0x" + "11" * 32,
            outputMint="0x" + "22" * 32,
            inAmount="1000000",
            outAmount="2000000",
            feeAmount="1000",
            feeMint="0x" + "33" * 32,
        ),
        percent=100,
    )

    assert step.swap_info.amm_key == "amm1"
    assert step.swap_info.label == "Orca"
    assert step.percent == 100

    with pytest.raises(ValidationError):
        RoutePlanStep(
            swapInfo=SwapInfo(
                ammKey="amm1",
                label="Orca",
                inputMint="0x" + "11" * 32,
                outputMint="0x" + "22" * 32,
                inAmount="1000000",
                outAmount="2000000",
                feeAmount="1000",
                feeMint="0x" + "33" * 32,
            ),
            percent=101,
        )


def test_quote_response():
    """Test QuoteResponse model."""
    quote = QuoteResponse(
        inputMint="0x" + "11" * 32,
        inAmount="1000000",
        outputMint="0x" + "22" * 32,
        outAmount="2000000",
        otherAmountThreshold="1950000",
        swapMode=SwapMode.EXACT_IN,
        slippageBps=50,
        priceImpactPct="1.5",
        routePlan=[
            RoutePlanStep(
                swapInfo=SwapInfo(
                    ammKey="amm1",
                    label="Orca",
                    inputMint="0x" + "11" * 32,
                    outputMint="0x" + "22" * 32,
                    inAmount="1000000",
                    outAmount="2000000",
                    feeAmount="1000",
                    feeMint="0x" + "33" * 32,
                ),
                percent=100,
            ),
        ],
    )

    assert quote.input_mint == "0x" + "11" * 32
    assert quote.in_amount == "1000000"
    assert quote.output_mint == "0x" + "22" * 32
    assert quote.out_amount == "2000000"
    assert quote.other_amount_threshold == "1950000"
    assert quote.swap_mode == SwapMode.EXACT_IN
    assert quote.slippage_bps == 50
    assert quote.price_impact_pct == "1.5"
    assert len(quote.route_plan) == 1


def test_swap_request():
    """Test SwapRequest model."""
    quote = QuoteResponse(
        inputMint="0x" + "11" * 32,
        inAmount="1000000",
        outputMint="0x" + "22" * 32,
        outAmount="2000000",
        otherAmountThreshold="1950000",
        swapMode=SwapMode.EXACT_IN,
        slippageBps=50,
        priceImpactPct="1.5",
        routePlan=[
            RoutePlanStep(
                swapInfo=SwapInfo(
                    ammKey="amm1",
                    label="Orca",
                    inputMint="0x" + "11" * 32,
                    outputMint="0x" + "22" * 32,
                    inAmount="1000000",
                    outAmount="2000000",
                    feeAmount="1000",
                    feeMint="0x" + "33" * 32,
                ),
                percent=100,
            ),
        ],
    )

    request = SwapRequest(
        userPublicKey="0x" + "44" * 32,
        quoteResponse=quote,
        dynamicComputeUnitLimit=True,
        prioritizationFeeLamports="auto",
    )

    assert request.user_public_key == "0x" + "44" * 32
    assert request.quote_response == quote
    assert request.dynamic_compute_unit_limit is True
    assert request.prioritization_fee_lamports == "auto"


def test_swap_response():
    """Test SwapResponse model."""
    response = SwapResponse(
        swapTransaction="bW9ja190cmFuc2FjdGlvbl9iYXNlNjQ=",  # base64 encoded "mock_transaction_base64"
        addressLookupTables=["0x" + "44" * 32],
    )

    assert response.swap_transaction == "bW9ja190cmFuc2FjdGlvbl9iYXNlNjQ="
    assert response.address_lookup_tables == ["0x" + "44" * 32]


def test_swap_result():
    """Test SwapResult model."""
    result = SwapResult(
        transaction_hash="0x" + "11" * 32,
        input_amount="1000000",
        output_amount="2000000",
        price_impact="1.5",
        fee_amount="1000",
        platform_fee=None,
        route_plan=[],
    )

    assert result.transaction_hash == "0x" + "11" * 32
    assert result.input_amount == "1000000"
    assert result.output_amount == "2000000"
    assert result.price_impact == "1.5"
    assert result.fee_amount == "1000"
    assert result.platform_fee is None
    assert result.route_plan == [] 