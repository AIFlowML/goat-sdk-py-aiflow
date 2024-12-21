"""Configuration for Tensor plugin."""

from pydantic import BaseModel, ConfigDict


class TensorConfig(BaseModel):
    """Configuration for Tensor plugin."""
    model_config = ConfigDict(populate_by_name=True)

    api_key: str
    api_url: str = "https://api.mainnet.tensordev.io/api/v1" 