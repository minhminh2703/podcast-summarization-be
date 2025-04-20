import re
from models.podcast import HeadingSection
from typing import List


def parse_heading_sections(text: str) -> List[HeadingSection]:
    pattern = r"Heading\s+(\d+)\s*-\s*(.*?)\s*-\s*([\d.]+)\s*-\s*([\d.]+)\n(.*?)(?=\nHeading\s+\d+\s*-|\nOverall\n|\Z)"
    matches = re.findall(pattern, text, flags=re.DOTALL)

    result = []

    for number, title, start, end, content in matches:
        result.append(HeadingSection(
            header=f"Heading {number}",
            title=title.strip(),
            start=float(start),
            end=float(end),
            content=content.strip()
        ))

    return result


def parse_overall_summary(text: str) -> str:
    match = re.search(r"\nOverall\n(.*)", text, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""
