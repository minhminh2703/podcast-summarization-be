import re
from models.podcast import HeadingSection
from typing import List, Tuple


def parse_headings_and_overall(text: str) -> Tuple[List[HeadingSection], str]:
    heading_pattern = r"Heading\s+(\d+)\s*-\s*(.*?)\s*-\s*([\d.]+)\s*-\s*([\d.]+)\n(.*?)(?=\nHeading\s+\d+\s*-|\nOverall\b|\Z)"
    heading_matches = re.findall(heading_pattern, text, flags=re.DOTALL)

    heading_sections = [
        HeadingSection(
            header=f"Heading {number}",
            title=title.strip(),
            start=float(start),
            end=float(end),
            content=content.strip()
        )
        for number, title, start, end, content in heading_matches
    ]

    # Parse phần Overall
    overall_match = re.search(r"\bOverall\b\s*\n*(.*)", text, flags=re.DOTALL)
    overall_summary = overall_match.group(1).strip() if overall_match else ""

    return heading_sections, overall_summary
