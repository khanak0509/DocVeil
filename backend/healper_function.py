from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
import asyncio
from pydantic import BaseModel
from typing import List, Dict

llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0.3
)


class Image(BaseModel):
    image_name : List[str] = []

llm_stuc = llm.with_structured_output(Image)

async def summery_asycn(page_contnet:str):
    prompt = PromptTemplate(
        input_types={'page_contnet':str},
        template= """
you are a sumuarizer ow genegrate a detiald summeruot of {page_contnet}
"""
    )
    chain = prompt | llm
    result = await chain.ainvoke({'page_contnet' : page_contnet})
    return result.content


async def image(summary_text:str) -> Image:
    propmt_for_image = PromptTemplate(
        input_variables=["summary_text"],
        template="""
You are an expert visual content designer. Read the following summary and suggest only 1 highly relevant, creative, and descriptive image names that would best illustrate or visually represent the key ideas, concepts, or themes in the summary. 

Guidelines:
- Use concise, vivid, and specific phrases (not generic words)
- Focus on the main topics, actions, or entities described
- Avoid repeating the summary text verbatim
- Do not include file extensions or numbers (e.g., no .jpg, no 'Image 1')
- Only output a Python list of image names (e.g., ['Data Flow Diagram', 'Legal Contract Review'])
you can say none also 

Summary:
{summary_text}
"""
    )
    chain = propmt_for_image | llm_stuc
    return await chain.ainvoke({"summary_text": summary_text})

    


