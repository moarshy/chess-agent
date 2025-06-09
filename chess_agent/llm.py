# llm.py

import litellm
from litellm.exceptions import APIError

def get_llm_completion(messages: list[dict], model_name: str) -> str | None:
    """
    Gets a completion from the specified LLM for a given message history.
    
    Args:
        messages: A list of message dictionaries (e.g., [{'role': 'user', ...}]).
        model_name: The name of the model to use.

    Returns:
        The content of the LLM's response as a string, or None if an error occurs.
    """
    try:
        response = litellm.completion(
            model=model_name,
            messages=messages,
            max_tokens=4000,
            temperature=0.0,
        )
        if response and response.choices:
            return response.choices[0].message.content.strip()
        print(f"🔴 Invalid response structure from {model_name}.")
        return None
    except APIError as e:
        print(f"🔴 API Error: Could not get completion from {model_name}. Error: {e}")
        return None
    except Exception as e:
        print(f"🔴 An unexpected error occurred: {e}")
        return None