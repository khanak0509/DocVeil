from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
import asyncio

llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0.3
)


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


