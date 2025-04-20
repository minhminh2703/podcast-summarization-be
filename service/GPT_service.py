from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import List, Dict

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
