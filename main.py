
import os
import base64
from typing import Literal, Optional
from together import AsyncTogether
import argparse
import requests
import asyncio
import streamlit as st


def encode_image(image_path: str) -> str:
    """Encode an image file to base64 string."""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def is_remote_file(file_path: str) -> bool:
    """Check if the file path is a remote URL."""
    return file_path.startswith(('http://', 'https://'))


async def get_markdown(together_client: AsyncTogether, vision_llm: str, file_path: str) -> str:
    """Generate markdown from image using Together AI."""
    system_prompt = """Convert the provided image into Markdown format. Ensure that all content from the page is included, such as headers, footers, subtexts, images (with alt text if possible), tables, and any other elements.

    Requirements:

    - Output Only Markdown: Return solely the Markdown content without any additional explanations or comments.
    - No Delimiters: Do not use code fences or delimiters like ```markdown.
    - Complete Content: Do not omit any part of the page, including headers, footers, and subtext.
    """




    final_image_url = file_path if is_remote_file(
        file_path) else f"data:image/jpeg;base64,{encode_image(file_path)}"

    output = await together_client.chat.completions.create(
        model=vision_llm,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": system_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": final_image_url
                        }
                    }
                ]
            }
        ]
    )

    return output.choices[0].message.content


async def ocr(
    file_path: str,
    api_key: Optional[str] = None,
    model: Literal["Llama-3.2-90B-Vision",
                   "Llama-3.2-11B-Vision", "free"] = "Llama-3.2-90B-Vision"
) -> str:
    """
    Perform OCR on an image using Together AI.

    Args:
        file_path: Path to the image file or URL
        api_key: Together AI API key (defaults to TOGETHER_API_KEY environment variable)
        model: Model to use for vision processing

    Returns:
        Markdown string of the image content
    """
    if api_key is None:
        api_key = st.secrets["TOGETHER_API_KEY"] 
        if not api_key:
            raise ValueError(
                "API key must be provided either directly or through TOGETHER_API_KEY environment variable")

    vision_llm = f"meta-llama/{model}-Instruct-Turbo" if model != "free" else "meta-llama/Llama-Vision-Free"

    together_client = AsyncTogether(api_key=api_key)

    final_markdown = await get_markdown(together_client, vision_llm, file_path)

    return final_markdown





if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Perform OCR on an image using Together AI.")
    parser.add_argument("input_file", help="Path to the input image file")
    parser.add_argument("output_file", help="Path to the output file to save the result")
    args = parser.parse_args()

    try:
        # Run the OCR function
        result = asyncio.run(ocr(args.input_file))
        
        # Save the result to the specified output file
        with open(args.output_file, "w", encoding="utf-8") as output_file:
            output_file.write(result)
        
        print(f"OCR result was saved to {args.output_file}")
    except Exception as e:
        print(f"Error: {e}")