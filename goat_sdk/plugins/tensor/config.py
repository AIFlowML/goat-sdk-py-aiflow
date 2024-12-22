"""Configuration for Tensor plugin."""

import os
from pydantic import BaseModel, ConfigDict, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class TensorConfig(BaseModel):
    """Configuration for Tensor plugin."""
    model_config = ConfigDict(populate_by_name=True)

    api_key: str = Field(
        default_factory=lambda: os.getenv("TENSOR_API_KEY", ""),
        description="API key for Tensor API"
    )
    api_url: str = Field(
        default=os.getenv("TENSOR_API_URL", "https://api.mainnet.tensordev.io/api/v1"),
        description="Base URL for Tensor API"
    )