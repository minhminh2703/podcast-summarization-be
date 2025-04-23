from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import List, Dict
from langchain.chains.summarize import load_summarize_chain
from langchain_experimental.text_splitter import SemanticChunker
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.docstore.document import Document
from utils.formatter import format_sections
from utils.segmentation import get_embedder

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_PODCAST_SUMMARY_PROMPT = """
You are an assistant summarizing a podcast transcript. The transcript is broken into segments, each with a start time, end time, and spoken text.

Your task is to:
- Group segments that talk about the same topic.
- Break into logical sections based on topic transitions.
- For each section, write a heading and a summary.
- Each section must include the start time of the first segment and the end time of the last segment.

Format output exactly like this (repeat for each heading):

Heading {{n}} - {{Heading title}} - {{start_time}} - {{end_time}}
{{summary for that section}}

After you have listed all sections, write an **overall summary** of the full episode.
Start the overall summary with the word `Overall` on its own line, so it can be parsed separately.
Do not include any extra explanation or formatting outside this structure.

Only return the summary in that format. Do not explain. Start from Heading 1.
"""


MAP_PROMPT ="""
    You are an assistant summarizing a part of a podcast transcript. The transcript is broken into sentences, each begins start time, end time, and spoken text, formatted like this for example [5:48 - 5:54]: {{text}}I 

Your task is to:
- Summarize the whole part you were given
- Final output must include the start time of the first segment and the end time of the last segment.

Format output exactly like this:

{{start_time}} - {{end_time}}
{{summary for that section}}

Do not include any extra explanation or formatting outside this structure.

Here is the transcript:
{text}
"""

REDUCE_PROMPT = """
You are an assistant summarizing a podcast transcript. The transcript is broken into segments, each is already summarized and begin with a start time, end time, and spoken text.

Your task is to:

- Group segments that talk about the same topic but also continuous. NOTE that only do it IF NECCESSARY, if do so each section must include the start time of the first segment and the end time of the last segment.
- For each section, write a heading. Write a summary ONLY IF NECCESSARY.
- Each section must include the start time of the first segment and the end time of the last segment.


Format output exactly like this (repeat for each heading):

Heading {{n}} - {{Heading title}} - {{start_time}} - {{end_time}}
{{summary for that section in {language}}}

After you have listed all sections, write an **overall summary** of the full episode.
Start the overall summary with the word `Overall` on its own line, so it can be parsed separately.
Do not include any extra explanation or formatting outside this structure.

Only return the summary in that format. Do not explain. Start from Heading 1.
Here is the transcript:
{text}

"""

def generate_heading_summary(
    segments: List[Dict[str, str]],
    target_language: str = "English",
) -> str:
    # Format transcript
    transcript_lines = []
    for seg in segments:
        start = seg["start"]
        end = seg["end"]
        text = seg["text"].strip().replace("\n", " ")
        transcript_lines.append(f"[{start} - {end}]: {text}")
    transcript = "\n".join(transcript_lines)

    # Compose full prompt with language
    full_prompt = BASE_PODCAST_SUMMARY_PROMPT.strip() + f"\n\nLanguage: {target_language}\n\nHere is the transcript:\n{transcript}"

    # Call chat completion API
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.3,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes podcasts into structured sections."},
            {"role": "user", "content": full_prompt}
        ]
    )

    return response.choices[0].message.content.strip()

def generate_summary_map_reduce(
    segments: List[Dict[str, str]],
    target_language: str = "English",
) -> str:
    """
    Generate a summary of the podcast transcript using GPT and LangChain. 
    Using SemanticChunker for splitting text and map-reduce for final summary.
    
    Args:
        segments: List of segments with start, end, and text
        target_language: Language for the summary (default: "English")

    Returns:
        Generated summary text
    """
    transcript = format_sections(segments)
    
    llm = ChatOpenAI(
        model_name="gpt-4o",
        temperature=0.5,
    )
    
    embedder = get_embedder()
    if embedder is None:
        raise ValueError("Embedder model not initialized. Call initialize_embedder() first.")
    # Split the text if it's too long
    text_splitter = SemanticChunker(
        embedder,
        buffer_size= 3,
        breakpoint_threshold_type="percentile"
    )
    

    prompt_template = BASE_PODCAST_SUMMARY_PROMPT.strip() + f"\n\nLanguage: {target_language}\n\nHere is the transcript:\n{{text}}"
    prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
    
    # Split the transcript into chunks
    texts = text_splitter.split_text(transcript)
    docs = [Document(page_content=t) for t in texts]
    
    # Print number of chunks and their lengths
    print(f"Number of chunks: {len(docs)}")
    for i, doc in enumerate(docs):
        print(f"\n--- Chunk {i + 1} (length: {len(doc.page_content)} characters) ---")
        print(doc.page_content)


    if len(docs) == 1:
        # Use stuff chain for short documents
        chain = load_summarize_chain(
            llm, 
            chain_type="stuff",
            prompt=prompt
        )
    else:
        map_prompt_template = MAP_PROMPT.strip()
        map_prompt = PromptTemplate(template=map_prompt_template, input_variables=["text"])
        reduce_prompt_template = REDUCE_PROMPT.strip()
        reduce_prompt = PromptTemplate(template=reduce_prompt_template, input_variables=["language","text"])
        # Use map_reduce for longer documents
        chain = load_summarize_chain(
            llm,
            chain_type="map_reduce",
            map_prompt=map_prompt,
            combine_prompt=reduce_prompt
        )
    
    # Generate the summary
    summary = chain.invoke({"input_documents": docs, "language": target_language})
    
    return summary["output_text"].strip()