from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
import asyncio
from pydantic import BaseModel
from typing import List, Dict
import torch
import os
from diffusers import AutoPipelineForText2Image
from PIL import Image as PILImage


llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0.3
)

device = "mps" if torch.backends.mps.is_available() else "cpu"
pipe = AutoPipelineForText2Image.from_pretrained(
    "stabilityai/sdxl-turbo",
    torch_dtype=torch.float16,
    variant="fp16"
).to(device)

pipe.set_progress_bar_config(disable=True)
GPU_SEMAPHORE = asyncio.Semaphore(2)
def build_prompt(image_name: str) -> str:
    return f"""
Clean, flat vector-style illustration of {image_name}.
Minimal design, professional, white background.
No text, no watermark, no logo.
"""

class Image(BaseModel):
    image_name : List[str] = []

llm_stuc = llm.with_structured_output(Image)

async def summery_asycn(page_contnet:str):
    prompt = PromptTemplate(
        input_types={'page_contnet':str},
        template= """
You are a summarizer who can generate a detailed summary of {page_contnet}
"""
    )
    chain = prompt | llm
    result = await chain.ainvoke({'page_contnet' : page_contnet})
    return result.content


async def get_image_metadata(summary_text:str) -> Image:
    prompt_for_image = PromptTemplate(
        input_variables=["summary_text"],
        template="""
You are an expert visual content designer. Read the following summary and suggest only 1 highly relevant, creative, and descriptive image names that would best illustrate or visually represent the key ideas, concepts, or themes in the summary. 

Guidelines:
- Use concise, vivid, and specific phrases (not generic words)
- Focus on the main topics, actions, or entities described
- Avoid repeating the summary text verbatim
- Do not include file extensions or numbers (e.g., no .jpg, no 'Image 1')
- Only output a Python list of image names (e.g., ['Data Flow Diagram', 'Legal Contract Review'])
You can say none also 

Summary:
{summary_text}
"""
    )
    chain = prompt_for_image | llm_stuc
    return await chain.ainvoke({"summary_text": summary_text})

    


# async def generate_image(
#     image_name: str,
#     output_dir: str = "save"
# ) -> str:
#     os.makedirs(output_dir, exist_ok=True)

#     file_name = image_name.lower().replace(" ", "_") + ".png"
#     output_path = os.path.join(output_dir, file_name)

#     # Cache check
#     if os.path.exists(output_path):
#         return output_path

#     prompt = build_prompt(image_name)

#     async with GPU_SEMAPHORE:
#         result = await asyncio.to_thread(
#             pipe,
#             prompt=prompt,
#             num_inference_steps=2,
#             guidance_scale=0.0
#         )

#         image: PILImage.Image = result.images[0]
#         image.save(output_path)

#     return output_path




# async def generate_images_parallel(image_names: list[str]) -> list[str]:
#     tasks = [
#         generate_image(name)
#         for name in image_names
#     ]
#     return await asyncio.gather(*tasks)


