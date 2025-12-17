import asyncio
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langgraph.graph import START, END, StateGraph
from pydantic import BaseModel
from typing import List, Dict, AsyncGenerator
from helper_function import summery_asycn, get_image_metadata


llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0.3
)


REFINE_PROMPT = PromptTemplate(
    input_variables=["previous", "current"],
    template=(
        "You are refining a document summary page by page.\n\n"
        "Previous page summary (for context):\n{previous}\n\n"
        "Current page summary:\n{current}\n\n"
        "Rewrite the current page summary to be clearer, more detailed, "
        "and consistent with the previous context. Do NOT repeat the previous page."
    ),
)


class State(BaseModel):
    pdf_path: str
    total_page: int = 0
    page_text: List[str] = []
    page_summaries: List[str] = []
    refined_summaries: List[str] = []
    current_page_index: int = 0
    image: List[List[str]] = []


def load_pdf(state: State) -> Dict:
    loader = PyPDFLoader(state.pdf_path)
    data = loader.load()
    print(f"Loaded PDF with {len(data)} pages")

    return {
        'total_page': len(data),
        'page_text': [page.page_content for page in data],
    }


async def page_summaries(state: State) -> dict:
    page_texts = state.page_text
    task1 = [summery_asycn(page_contnet=page_text) for page_text in page_texts]
    result1 = await asyncio.gather(*task1)
    task2 = [get_image_metadata(summary_text=page_text) for page_text in result1]
    result2 = await asyncio.gather(*task2)
    image_names = [img.image_name for img in result2]

    print(f"Generated {len(result1)} page summaries")

    return {
        'page_summaries': result1,
        'current_page_index': 0,
        'image': image_names
    }


def refined_summaries(state: State) -> dict:
    index = state.current_page_index
    current_summary = state.page_summaries[index]
    
    if index == 0:
        refined = [current_summary]
    else:
        previous = state.refined_summaries[-1]
        chain = REFINE_PROMPT | llm
        refined_content = chain.invoke(
            {"previous": previous, "current": current_summary}
        ).content
        refined = [refined_content]

    print(f"Refined page {index + 1}/{state.total_page}")

    return {
        'refined_summaries': state.refined_summaries + refined,
        'current_page_index': index + 1,
    }


def should_continue(state: State) -> str:
    if state.current_page_index < state.total_page:
        return "refined_summaries"
    return END


graph = StateGraph(State)

graph.add_node('load_pdf', load_pdf)
graph.add_node('page_summaries', page_summaries)
graph.add_node('refined_summaries', refined_summaries)

graph.add_edge(START, 'load_pdf')
graph.add_edge('load_pdf', 'page_summaries')
graph.add_edge('page_summaries', 'refined_summaries')
graph.add_conditional_edges(
    "refined_summaries",
    should_continue,
)

workflow = graph.compile()


async def stream_pdf_summaries(pdf_path: str) -> AsyncGenerator[Dict, None]:
    initial_state = State(
        pdf_path=pdf_path,
        total_page=0,
        page_text=[],
        page_summaries=[],
        refined_summaries=[],
        current_page_index=0
    )

    current_state = initial_state
    
    async for event in workflow.astream(initial_state):
        for node_name, node_output in event.items():
            current_state = State(
                pdf_path=current_state.pdf_path,
                total_page=node_output.get('total_page', current_state.total_page),
                page_text=node_output.get('page_text', current_state.page_text),
                page_summaries=node_output.get('page_summaries', current_state.page_summaries),
                refined_summaries=node_output.get('refined_summaries', current_state.refined_summaries),
                current_page_index=node_output.get('current_page_index', current_state.current_page_index),
                image=node_output.get('image', current_state.image)
            )
            
            if 'refined_summaries' in node_output and node_output['refined_summaries']:
                page_num = len(current_state.refined_summaries)
                yield {
                    'page': page_num,
                    'total_pages': current_state.total_page,
                    'summary': current_state.refined_summaries[-1],
                    'status': 'processing'
                }
    
    yield {
        'page': current_state.total_page,
        'total_pages': current_state.total_page,
        'summary': '',
        'status': 'complete'
    }
