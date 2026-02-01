"""
Ollama async model serving for local and cloud inference.

Simple functional approach for text generation using aiohttp.
Supports both local (localhost:11434) and cloud (ollama.com) endpoints.
"""

from typing import Any, Self

import aiohttp
from aiohttp import ClientResponse
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field, model_validator

from genai_services.settings import settings


class OllamaEndpointConfig(BaseModel):
    """Immutable configuration for an Ollama endpoint."""

    model_config = ConfigDict(frozen=True)

    base_url: str
    api_path: str
    default_model: str
    allowed_models: frozenset[str] = Field(
        description="Set of models allowed for this endpoint"
    )
    requires_auth: bool = False
    response_path: tuple[str | int, ...] = Field(
        description="JSON path to extract content from response"
    )

    @model_validator(mode="after")
    def validate_default_model_in_allowed(self) -> Self:
        """Ensure default_model is in allowed_models."""
        if self.default_model not in self.allowed_models:
            raise ValueError(
                f"default_model '{self.default_model}' must be in "
                f"allowed_models: {sorted(self.allowed_models)}"
            )
        return self

    @property
    def url(self) -> str:
        """Construct the full endpoint URL."""
        return f"{self.base_url}/{self.api_path}"

    def validate_model(self, model: str) -> None:
        """Validate that a model is allowed for this endpoint.

        Args:
            model: Model name to validate

        Raises:
            ValueError: If model is not in allowed_models
        """
        if model not in self.allowed_models:
            raise ValueError(
                f"Model '{model}' is not allowed for endpoint {self.base_url}. "
                f"Allowed models: {sorted(self.allowed_models)}"
            )

    def extract_content(self, response: dict[str, Any]) -> str:
        """Extract content from response using configured path."""
        result: Any = response
        for key in self.response_path:
            result = result[key]
        return result


LOCAL_CONFIG = OllamaEndpointConfig(
    base_url="http://localhost:11434",
    api_path="v1/chat/completions",
    default_model="tinyllama:latest",
    allowed_models=frozenset(
        [
            "tinyllama:latest",
        ]
    ),
    requires_auth=False,
    response_path=("choices", 0, "message", "content"),
)

CLOUD_CONFIG = OllamaEndpointConfig(
    base_url="https://ollama.com",
    api_path="api/chat",
    default_model="gpt-oss:120b",
    allowed_models=frozenset(
        [
            "gpt-oss:120b",
            "gpt-oss:120b-cloud",
        ]
    ),
    requires_auth=True,
    response_path=("message", "content"),
)


async def generate_text_completion(
    prompt: str,
    model: str,
    config: OllamaEndpointConfig,
    use_cloud: bool = False,
    temperature: float = 0.01,
    stream: bool = False,
) -> str:
    """Generate text completion from Ollama.

    Args
    -----
        - prompt: Text prompt for generation
        - model: Model name (optional, uses config default if not provided)
        - config: Endpoint configuration (optional, uses `LOCAL_CONFIG` or `CLOUD_CONFIG` based on `use_cloud`)
        - use_cloud: If `True`, use Ollama cloud endpoint with API key (backwards compatibility)
        - temperature: Temperature for generation (0.0 to 1.0)
        - stream: If `True`, return streaming response (not implemented in this function)

    Returns
    --------
        Generated text response

    Examples
    --------
    ### Using local model
    ```python
    >>> response = await generate_text_completion(
    ...     prompt='What is Python? Answer in one sentence.',
    ...     model='tinyllama:latest',
    ...     config=LOCAL_CONFIG,
    ... )
    >>> print(response)
    >>> ...
    ```
    ### Using cloud model
    ```python
    >>> response = await generate_text_completion(
    ...     prompt='What is Python? Answer in one sentence.',
    ...     model='gpt-oss:120b',
    ...     config=CLOUD_CONFIG,
    ...     use_cloud=True,
    ... )
    >>> print(response)
    >>> ...
    ```
    """
    # Resolve configuration
    if config is None:
        config = CLOUD_CONFIG if use_cloud else LOCAL_CONFIG

    # Use provided model or fall back to config default
    model_name = model or config.default_model

    # Validate that the model is allowed for this endpoint
    try:
        config.validate_model(model_name)
    except ValueError as e:
        raise ValueError(f"Model {model_name} is not allowed for this endpoint") from e

    # Build headers
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if config.requires_auth:
        headers["Authorization"] = f"Bearer {settings.ollama_api_key}"

    # Build request payload
    system_prompt = "You are a helpful assistant."
    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]

    data: dict[str, Any] = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "stream": stream,
    }

    try:
        async with aiohttp.ClientSession() as session:
            response: ClientResponse = await session.post(
                config.url, json=data, headers=headers
            )
            response.raise_for_status()  # type: ignore
            predictions = await response.json()  # type: ignore
    except aiohttp.ClientError as e:
        logger.error(f"HTTP error during text generation: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during text generation: {e}")
        raise

    try:
        output = config.extract_content(predictions)
        logger.debug(f"Generated text: {output}")
        return output
    except (KeyError, IndexError, TypeError) as e:
        logger.error(f"Failed to parse response from Ollama - Error: {e}")
        logger.error(f"Response structure: {predictions}")
        return f"Failed to parse response from Ollama - Error: {e}"


async def quick_test() -> None:
    """Quick test function to verify the local model works correctly."""
    logger.info("Running Ollama quick test (local)...")
    test_message = "What is Python? Answer in one sentence."
    logger.info(f"Test prompt: {test_message}")
    response = await generate_text_completion(
        test_message, model="tinyllama:latest", config=LOCAL_CONFIG
    )
    logger.success(f"Response: {response}")
    logger.success("Quick test completed successfully!")


async def quick_test_cloud() -> None:
    """Quick test function to verify the cloud model works correctly."""
    logger.info("Running Ollama quick test (cloud)...")
    test_message = "What is Python? Answer in one sentence."
    logger.info(f"Test prompt: {test_message}")
    response = await generate_text_completion(
        test_message, model="gpt-oss:120b", config=CLOUD_CONFIG
    )
    logger.success(f"Response: {response}")
    logger.success("Quick test cloud completed successfully!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(quick_test())
    asyncio.run(quick_test_cloud())
