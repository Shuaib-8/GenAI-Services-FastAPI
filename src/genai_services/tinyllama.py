"""TinyLlama model module for text generation on Apple Silicon.

This module provides a simple interface to load and use the TinyLlama-1.1B-Chat
model with Hugging Face Transformers, optimized for Mac M4 using MPS backend.
"""

import torch
from loguru import logger
from transformers import AutoModelForCausalLM, AutoTokenizer

# Model configuration
MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

class TinyLlamaChat:
    """TinyLlama chat model wrapper for easy text generation."""

    def __init__(self, model_id: str = MODEL_ID) -> None:
        """Initialize the TinyLlama model and tokenizer.

        Args:
            model_id: Hugging Face model identifier. Defaults to TinyLlama-1.1B-Chat.
        """
        self.model_id = model_id
        self.device = self.get_device()

        logger.info(f"Loading tokenizer from {model_id}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)

        logger.info(f"Loading model from {model_id}...")
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            dtype=torch.float16,
            device_map="auto",
        )

        # Move model to the appropriate device
        self.model.to(self.device)
        logger.success(f"Model loaded successfully on {self.device}")

    @staticmethod
    def get_device() -> torch.device:
        """Detect and return the best available device for inference.

        Returns:
            torch.device: MPS device if available on Apple Silicon, otherwise CPU.
        """
        if torch.backends.mps.is_available():
                logger.info("MPS (Metal Performance Shaders) device detected - using Apple Silicon GPU")
                return torch.device("mps")
        
        logger.warning("MPS not available - falling back to CPU")
        return torch.device("cpu")

    def generate(
        self,
        user_message: str,
        system_prompt: str = "You are a helpful assistant.",
        max_new_tokens: int = 128,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """Generate a response to the user message.

        Args:
            user_message: The user's input message.
            system_prompt: System prompt to set the assistant's behavior.
            max_new_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (higher = more creative).
            top_p: Nucleus sampling parameter.

        Returns:
            The generated response text.
        """
        # Format prompt using TinyLlama chat template
        prompt = f"<|system|>\n{system_prompt}<|user|>\n{user_message}<|assistant|>\n"

        # Tokenize input
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=temperature,
                top_p=top_p,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        # Decode and extract response
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract only the assistant's response (after the last prompt section)
        if "<|assistant|>" in prompt:
            # Find where the assistant response starts
            assistant_start = full_response.rfind(user_message) + len(user_message)
            response = full_response[assistant_start:].strip()
        else:
            response = full_response

        return response


def quick_test() -> None:
    """Quick test function to verify the model works correctly."""
    logger.info("Running TinyLlama quick test...")

    # Check MPS availability
    logger.info(f"PyTorch version: {torch.__version__}")
    logger.info(f"MPS available: {torch.backends.mps.is_available()}")
    logger.info(f"MPS built: {torch.backends.mps.is_built()}")

    # Initialize model
    chat = TinyLlamaChat()

    # Test generation
    test_message = "Hello! Can you tell me a short joke?"
    logger.info(f"Test prompt: {test_message}")

    response = chat.generate(test_message)
    logger.info(f"Response: {response}")

    logger.success("Quick test completed successfully!")


if __name__ == "__main__":
    quick_test()
