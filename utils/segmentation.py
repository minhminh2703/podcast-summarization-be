import re
from models.podcast import HeadingSection
from typing import List, Dict, Tuple
from langchain_ollama import ChatOllama
from langchain_ollama import ChatOllama
from typing import Optional
from sentence_transformers import SentenceTransformer, util
from langchain_huggingface import HuggingFaceEmbeddings
import torch

_Embedder = None

_LLM = None

_MiniLM = None
#==========================INITIALIZE MODELS==========================
def initialize_mini_llm(model_name: str = "tinyllama") -> None:
    global _LLM
    try:
        print(f"Loading Mini LLM model: {model_name}...")
        _LLM = ChatOllama(model=model_name)
        print("Mini LLM model loaded successfully.")
    except Exception as e:
        print(f"Error loading Mini LLM model: {e}")
        raise

def get_mini_llm() -> Optional[ChatOllama]:
    global _LLM
    if _LLM is None:
        raise ValueError("Mini LLM model not initialized. Call initialize_mini_llm() first.")
    return _LLM

def initialize_miniLM(model_name: str = "all-MiniLM-L6-v2") -> None:

    global _MiniLM
    try:
        print(f"Loading MiniLM model: {model_name}...")
        _MiniLM = SentenceTransformer(model_name)
        print("MiniLM model loaded successfully.")
    except Exception as e:
        print(f"Error loading MiniLM model: {e}")
        raise

def get_miniLM() -> Optional[SentenceTransformer]:

    global _MiniLM
    if _MiniLM is None:
        raise ValueError("MiniLM model not initialized. Call initialize_miniLM() first.")
    return _MiniLM

def initialize_embedder(model_name: str = "all-MiniLM-L6-v2") -> None:
    global _Embedder
    device = "cuda" if torch.cuda.is_available() else "cpu"
    try:
        print(f"Loading Embedder model: {model_name}...")
        _Embedder = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": device}
        )
        print("Embedder model loaded successfully.")
    except Exception as e:
        print(f"Error loading Embedder model: {e}")
        raise

def get_embedder() -> Optional[HuggingFaceEmbeddings]:
    global _Embedder
    if _Embedder is None:
        raise ValueError("Embedder model not initialized. Call initialize_embedder() first.")
    return _Embedder
#=====================================================================


#==========================UTILITY FUNCTIONS==========================

def are_same_topic(sent1: str, sent2: str) -> bool:
    """
    check if two sentences are about the same topic using Mini LLM model.
    - sent1: str - first sentence
    - sent2: str - second sentence
    """

    
    prompt = f"""
Are the following two sentences about the same topic?

Sentence 1: "{sent1}"
Sentence 2: "{sent2}"

Answer with only "Yes" or "No".
"""
    model = get_mini_llm()
    response = model.invoke(input=prompt)


    answer = response.content.strip().lower()
    return "yes" in answer
#======================================================================

#==========================TRANSCRIPT SEGMENTATION===================
def llm_topic_segmentation(segments: List[Dict[str, str]]) -> List[str]:
    """
    Cluster segments into topics based on their content.
    - segments: List[Dict[str, str]] - list of segments with start, end, and text

    OUTPUT:
    - List[str] - list of formatted strings for each segment, each with start, end, and content.
    """

    clusters, current_cluster = [], []
    pre_transcript = segments[0]["text"].strip().replace("\n", " ")
    cur_start, cur_end = segments[0]["start"], segments[0]["end"]

    for seg in segments:
        
        text = seg["text"].strip().replace("\n", " ")

        if are_same_topic(pre_transcript, text):
            current_cluster.append(text)
        else:
            joined = " ".join(current_cluster)
            clusters.append(f"[{cur_start} - {cur_end}]: {joined}")
            cur_start = seg["start"]
            current_cluster = [text]
        
        pre_transcript = text
        cur_end = seg["end"]
        
    joined = " ".join(current_cluster)
    clusters.append(f"[{cur_start} - {cur_end}]: {joined}")
    return clusters


def minilm_topic_segmentation(
    segments: List[Dict[str, str]],
    window_size: int = 3,
    threshold: float = 0.7
) -> List[str]:
    """
    Cluster segments into topics using MiniLM embeddings and cosine similarity between sliding windows.

    OUTPUT:
    - List[str] - list of formatted strings for each segment, each with start, end, and content.
    """
    if len(segments) < window_size * 2:
        return [f"[{segments[0]['start']} - {segments[-1]['end']}]: " +
                " ".join(seg["text"].strip().replace("\n", " ") for seg in segments)]

    model = get_miniLM()
    clusters = []
    current_cluster = [segments[0]]
    cur_start, cur_end = segments[0]["start"], segments[0]["end"]

    for i in range(1, len(segments) - window_size):
        # Create sliding windows
        prev_window = " ".join(segments[j]["text"].strip().replace("\n", " ")
                               for j in range(i - window_size, i))
        
        next_window = " ".join(segments[j]["text"].strip().replace("\n", " ")
                               for j in range(i, i + window_size))

        # Encode windows
        emb1 = model.encode(prev_window, convert_to_tensor=True)
        emb2 = model.encode(next_window, convert_to_tensor=True)

        similarity = util.cos_sim(emb1, emb2).item()

        if similarity < threshold:
            # End current cluster and start a new one
            formatted = f"[{cur_start} - {cur_end}]: " + " ".join(
                seg["text"].strip().replace("\n", " ") for seg in current_cluster)
            clusters.append(formatted)

            cur_start = segments[i]["start"]
            current_cluster = []

        current_cluster.append(segments[i])
        cur_end = segments[i]["end"]

    # Append the last cluster
    current_cluster.extend(segments[-window_size:])
    if current_cluster:
        formatted = f"[{cur_start} - {segments[-1]['end']}]: " + " ".join(
            seg["text"].strip().replace("\n", " ") for seg in current_cluster)
        clusters.append(formatted)

    return clusters

#=====================================================================


