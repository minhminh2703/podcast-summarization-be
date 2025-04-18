# backend/models/summarizer.py
import os
from typing import Optional
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.docstore.document import Document

# Ensure OpenAI API key is set
if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError("Please set the OPENAI_API_KEY environment variable")

# Define prompt templates for different summary types
SUMMARY_PROMPTS = {
    "concise": """
        Write a concise summary of the following podcast transcript:
        
        {text}
        
        CONCISE SUMMARY:
    """,
    "detailed": """
        Write a comprehensive and detailed summary of the following podcast transcript. 
        Include the main topics, key insights, and important discussions.
        
        {text}
        
        DETAILED SUMMARY:
    """,
    "bullets": """
        Extract the main points from the following podcast transcript as a bulleted list:
        
        {text}
        
        MAIN POINTS:
    """
}

def generate_summary(
    transcript: str, 
    summary_type: str = "concise",
    max_length: Optional[int] = 300,
    model_name: str = "gpt-3.5-turbo"
) -> str:
    """
    Generate a summary of the podcast transcript using GPT and LangChain.
    
    Args:
        transcript: The podcast transcript to summarize
        summary_type: Type of summary to generate (concise, detailed, bullets)
        max_length: Maximum length of the summary in tokens
        model_name: The GPT model to use
        
    Returns:
        Generated summary text
    """
    # Check if transcript is too short to summarize
    if len(transcript.split()) < 50:
        return "The transcript is too short to generate a meaningful summary."
    
    # Configure the LLM
    llm = ChatOpenAI(
        model_name=model_name,
        temperature=0.5,
        max_tokens=max_length
    )
    
    # Split the text if it's too long
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    # Get the prompt based on summary type
    prompt_template = SUMMARY_PROMPTS.get(summary_type, SUMMARY_PROMPTS["concise"])
    prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
    
    # Split the transcript into chunks
    texts = text_splitter.split_text(transcript)
    docs = [Document(page_content=t) for t in texts]
    
    # Choose the right chain type based on document length
    if len(docs) == 1:
        # Use stuff chain for short documents
        chain = load_summarize_chain(
            llm, 
            chain_type="stuff",
            prompt=prompt
        )
    else:
        # Use map_reduce for longer documents
        chain = load_summarize_chain(
            llm,
            chain_type="map_reduce",
            map_prompt=prompt,
            combine_prompt=prompt
        )
    
    # Generate the summary
    summary = chain.invoke(docs)
    
    return summary["output_text"].strip()