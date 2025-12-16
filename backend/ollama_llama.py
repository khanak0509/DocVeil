from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate


llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0.3
)

prompt = PromptTemplate(
    input_types= {'q':str},
    template="""
give ans of this question {q}"""
)

chain = prompt | llm 

print(chain.invoke({'q':'what is 2+2'}).content)