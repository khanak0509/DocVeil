import asyncio
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langgraph.graph import START, END, StateGraph
from pydantic import BaseModel
from typing import List, Dict, AsyncGenerator
from helper_function import summery_asycn
from pathlib import Path
from datetime import datetime
from encryption import decrypt_file_to_memory, is_encrypted_file
from pypdf import PdfReader



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
        "Provide an improved version of the current page summary that is clearer, more detailed, "
        "and consistent with the previous context. Do NOT repeat the previous page.\n\n"
        "IMPORTANT formatting rules:\n"
        "- Start with a brief heading in bold: **Topic/Heading**\n"
        "- Then provide numbered points: (1), (2), (3), (4), (5), etc. - as many as needed\n"
        "- Provide a DETAILED summary - aim for 7-10 points or more for comprehensive content\n"
        "- Do NOT limit yourself to just 3 points\n"
        "- Do NOT include any meta-text like 'Rewritten summary' or 'Here is the summary'\n"
        "- Do NOT use asterisks in the points themselves\n"
        "- Output ONLY the heading and summary points"
    ),
)


class State(BaseModel):
    pdf_path: str
    total_page: int = 0
    page_text: List[str] = []
    page_summaries: List[str] = []
    refined_summaries: List[str] = []
    current_page_index: int = 0


def load_pdf(state: State) -> Dict:
    pdf_path = state.pdf_path
    
    if is_encrypted_file(pdf_path):
        print(f"Decrypting PDF to memory: {pdf_path}")
        pdf_bytes = decrypt_file_to_memory(pdf_path)
        
        reader = PdfReader(pdf_bytes)
        page_texts = []
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            page_texts.append(text)
        
        print(f"Loaded encrypted PDF with {len(page_texts)} pages (in-memory)")
        
        return {
            'total_page': len(page_texts),
            'page_text': page_texts,
        }
    else:
        loader = PyPDFLoader(pdf_path)
        data = loader.load()
        print(f"Loaded PDF with {len(data)} pages")
        
        return {
            'total_page': len(data),
            'page_text': [page.page_content for page in data],
        }




async def page_summaries(state: State) -> dict:
    page_texts = state.page_text
    tasks = [summery_asycn(page_contnet=page_text) for page_text in page_texts]
    summaries = await asyncio.gather(*tasks)

    print(f"Generated {len(summaries)} page summaries")

    return {
        'page_summaries': summaries,
        'current_page_index': 0
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


def save_summaries_to_file(refined_summaries: List[str], pdf_path: str) -> str:
    output_dir = Path("summaries_output")
    output_dir.mkdir(exist_ok=True)
    
    pdf_name = Path(pdf_path).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{pdf_name}_summary_{timestamp}.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"PDF Summary: {pdf_name}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Pages: {len(refined_summaries)}\n")
        f.write("=" * 80 + "\n\n")
        
        for i, summary in enumerate(refined_summaries, 1):
            f.write(f"========== PAGE {i} ==========\n\n")
            f.write(summary)
            f.write("\n\n" + "-" * 80 + "\n\n")
    
    print(f"Summaries saved to: {output_file}")
    return str(output_file)


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
                current_page_index=node_output.get('current_page_index', current_state.current_page_index)
            )
            
            if 'refined_summaries' in node_output and node_output['refined_summaries']:
                page_num = len(current_state.refined_summaries)
                yield {
                    'page': page_num,
                    'total_pages': current_state.total_page,
                    'summary': current_state.refined_summaries[-1],
                    'status': 'processing'
                }
    
    saved_file = save_summaries_to_file(current_state.refined_summaries, pdf_path)
    
    yield {
        'page': current_state.total_page,
        'total_pages': current_state.total_page,
        'summary': '',
        'status': 'complete',
        'saved_file': saved_file
    }

