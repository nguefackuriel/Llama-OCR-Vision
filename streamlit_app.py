
import os
import base64
from typing import Literal, Optional
import together
from together import AsyncTogether
import argparse
import requests
import asyncio
import streamlit as st
from PIL import Image
import io

# Page configuration
st.set_page_config(
    page_title="Llama OCR",
    page_icon="🦙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description in main area
st.title("🦙 Llama OCR")

# Add clear button to top right
col1, col2 = st.columns([6,1])
with col2:
    if st.button("Clear 🗑️"):
        if 'ocr_result' in st.session_state:
            del st.session_state['ocr_result']
        st.rerun()

st.markdown('<p style="margin-top: -20px;">Extract structured text from images using Llama 3.2 Vision!</p>', unsafe_allow_html=True)
st.markdown("---")

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


with st.sidebar:
    st.header("Upload Image")
    uploaded_file = st.file_uploader("Choose an image...", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image")
        


        if st.button("Extract Text 🔍", type="primary"):
            with st.spinner("Processing image..."):
                try:
                    # Convert the image to RGB mode 
                    image = image.convert("RGB")
                    # Save the uploaded image to a temporary file
                    temp_file_path = "temp_image.jpg"
                    image.save(temp_file_path)

                    # Pass the temporary file path to the OCR function
                    st.session_state['ocr_result'] = asyncio.run(ocr(temp_file_path))
                    
                    # Delete the temporary file after processing
                    os.remove(temp_file_path)
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")

    
    st.header("Save Output")
    output_file_name = st.text_input("Enter output file name (with extension, e.g., output.md):", value="output.md")
    
    # Save the output
    if st.button("Save Output"):
        if 'ocr_result' in st.session_state:
            try:
                with open(output_file_name, "w", encoding="utf-8") as f:
                    f.write(st.session_state['ocr_result'])
                st.success(f"Output saved as {output_file_name}")
            except Exception as e:
                st.error(f"Error saving file: {str(e)}")
        else:
            st.warning("No OCR result to save. Please extract text first.")

if 'ocr_result' in st.session_state:
    st.markdown(st.session_state['ocr_result'])
else:
    st.info("Upload an image and click 'Extract Text' to see the results here.")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Llama Vision and Together AI | [Report an Issue](https://github.com/Nutlope/llama-ocr/issues)")