# llm.py

import litellm
from litellm.exceptions import APIError
import base64
import io
from typing import Optional, List, Dict, Any

def encode_image_to_base64(image_bytes: bytes, format: str = "PNG") -> str:
    """
    Encodes image bytes to base64 string for LLM consumption.
    
    Args:
        image_bytes: Raw image bytes
        format: Image format (PNG, JPEG, etc.)
    
    Returns:
        Base64 encoded string with data URL prefix
    """
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    mime_type = f"image/{format.lower()}"
    return f"data:{mime_type};base64,{base64_image}"

def create_multimodal_content(text: str, image_base64: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Creates content list for multimodal messages in LiteLLM format.
    
    Args:
        text: Text content
        image_base64: Optional base64-encoded image with data URL prefix
    
    Returns:
        Content list in the format expected by LiteLLM
    """
    content = [
        {
            "type": "text",
            "text": text
        }
    ]
    
    if image_base64:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": image_base64,
                "format": "image/png"
            }
        })
    
    return content

def check_vision_support(model_name: str) -> bool:
    """
    Checks if a model supports vision capabilities.
    
    Args:
        model_name: The name of the model to check
        
    Returns:
        True if the model supports vision, False otherwise
    """
    try:
        return litellm.supports_vision(model=model_name)
    except Exception as e:
        print(f"⚠️ Warning: Could not check vision support for {model_name}: {e}")
        # Assume vision is supported for common vision models
        vision_keywords = ['vision', 'gpt-4o', 'claude-3', 'gemini-pro-vision', 'grok-2-vision']
        return any(keyword in model_name.lower() for keyword in vision_keywords)

def get_llm_completion(messages: list[dict], model_name: str) -> str | None:
    """
    Gets a completion from the specified LLM for a given message history.
    Now supports both text-only and multimodal (text + image) messages.
    
    Args:
        messages: A list of message dictionaries. Each message can contain:
                 - Simple text: {'role': 'user', 'content': 'text'}
                 - Multimodal: {'role': 'user', 'content': [{'type': 'text', 'text': '...'}, {'type': 'image_url', 'image_url': {...}}]}
        model_name: The name of the model to use.

    Returns:
        The content of the LLM's response as a string, or None if an error occurs.
    """
    try:
        # Check if any messages contain images
        has_images = any(
            isinstance(msg.get('content'), list) and 
            any(item.get('type') == 'image_url' for item in msg.get('content', []))
            for msg in messages
        )
        
        if has_images:
            print(f"🖼️ Sending multimodal request (text + images) to {model_name}")
            
            # Verify model supports vision
            if not check_vision_support(model_name):
                print(f"⚠️ Warning: {model_name} may not support vision. Proceeding anyway...")
        
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