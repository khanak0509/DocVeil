import asyncio
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langgraph.graph import START , END  , StateGraph
from pydantic import BaseModel , Field
from typing import List, Annotated , Dict
from healper_function import * 


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
    pdf_path : str
    total_page : int 
    page_text :List[str]
    page_summaries : List[str]
    refined_summaries :List[str]
    current_page_index :  int 


loder = PyPDFLoader('five_page_detailed_document.pdf')
data = loder.load()


def load_pdf(state: State) -> Dict:
    loder = PyPDFLoader(state.pdf_path)
    data = loder.load()
    print(len(data))

    return {
        'total_page': len(data),
        'page_text': [page.page_content for page in data],
       
    }


async def page_summaries(state:State) ->dict:
   page_texts = state['page_text']
   task = [summery_asycn(page_contnet=page_text) for page_text in page_texts]
   result =  await asyncio.gather(*task)
   print(result)

   return {
       'page_summaries' : result
   }
   

def refined_summaries(state:State) -> dict:
    index = State['current_page_index']
    refined = []
    current_summary = state['page_summaries'][index]
    if index ==0:
        refined.append(current_summary)

    else :
        previous = state['page_summaries'][index-1]
        chain = REFINE_PROMPT | llm
        refined.append(chain.invoke(
            {"previous": previous, "current": current_summary}
        ).content)

        return {
            'refined_summaries' :  state['refined_summaries'] + refined,
            'current_page_index' : index+1,


        }

        
def should_continue(state: State)->Dict:
    if state['current_page_index'] < state['total_page']:
        return {
            "refine_page"
        }
    return END



graph = StateGraph(State)

graph.add_node('load_pdf', load_pdf)
graph.add_node('page_summaries', page_summaries)
graph.add_node('refined_summaries', refined_summaries)

graph.add_edge(START, 'load_pdf')
graph.add_edge('load_pdf', 'page_summaries')
graph.add_edge('page_summaries', 'refined_summaries')
graph.add_conditional_edges(
    "refine_page",
    should_continue,
)
workflow = graph.compile()

initial_state = State(
    pdf_path='five_page_detailed_document.pdf',
    total_page=0,
    page_text=[],
    page_summaries=[],
    refined_summaries=[],
    current_page_index=0
)