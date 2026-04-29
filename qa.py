from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from course_data import COURSES, by_code, by_name_loose, course_context_text, normalize
from gemini_client import generate_text


@dataclass(frozen=True)
class RoutedAnswer:
    kind: str
    facts: str


_CODE_RE = re.compile(r"\bME\d{3}\b", re.IGNORECASE)


def _extract_codes(q: str) -> list[str]:
    return [m.group(0).upper() for m in _CODE_RE.finditer(q or "")]


def _detect_course_by_name_or_code(q: str):
    codes = _extract_codes(q)
    if codes:
        c = by_code(codes[0])
        if c:
            return c
    # Try common abbreviation for CFD
    if "cfd" in normalize(q):
        return by_name_loose("Computational Fluid Dynamics")
    # Otherwise: try loose by name using some heuristics (strip question words)
    qn = normalize(q)
    qn = re.sub(r"\b(what|which|how|many|is|are|the|for|of|do|does|have|has|a|an)\b", " ", qn)
    qn = " ".join(qn.split())
    return by_name_loose(qn)


def route_question(q: str) -> Optional[RoutedAnswer]:
    qn = normalize(q)
    codes = _extract_codes(q)

    # 1) Courses with no prerequisites
    if ("no prerequisite" in qn) or ("no prerequisites" in qn) or ("without prerequisite" in qn):
        no_pr = [c for c in COURSES if not c["prerequisite"]]
        names = ", ".join([f'{c["code"]} ({c["name"]})' for c in no_pr]) if no_pr else "None"
        return RoutedAnswer(kind="no_prereq", facts=f"Courses with no prerequisites: {names}.")

    # 2) Prerequisite for a specific course (by code or name)
    if "prereq" in qn or "prerequisite" in qn:
        c = _detect_course_by_name_or_code(q)
        if c:
            prereq = c["prerequisite"] if c["prerequisite"] else "None"
            return RoutedAnswer(
                kind="prereq_for_course",
                facts=f'Prerequisite for {c["code"]} ({c["name"]}): {prereq}.',
            )

    # 3) Slot clash between two codes
    if ("slot clash" in qn) or ("clash" in qn and "slot" in qn) or ("same slot" in qn):
        if len(codes) >= 2:
            c1, c2 = by_code(codes[0]), by_code(codes[1])
            if c1 and c2:
                same = normalize(c1["slot"]) == normalize(c2["slot"])
                if same:
                    facts = f'Yes. {c1["code"]} is {c1["slot"]} and {c2["code"]} is {c2["slot"]} (clash).'
                else:
                    facts = f'No. {c1["code"]} is {c1["slot"]} and {c2["code"]} is {c2["slot"]} (no clash).'
                return RoutedAnswer(kind="slot_clash", facts=facts)

    # 4) Credits for a course
    if "credit" in qn or "credits" in qn:
        c = _detect_course_by_name_or_code(q)
        if c:
            return RoutedAnswer(
                kind="credits_for_course",
                facts=f'{c["code"]} ({c["name"]}) has {c["credits"]} credits.',
            )

    # 5) Slot for a course
    if re.search(r"\bslot\b", qn):
        c = _detect_course_by_name_or_code(q)
        if c:
            return RoutedAnswer(
                kind="slot_for_course",
                facts=f'{c["code"]} ({c["name"]}) is scheduled in {c["slot"]}.',
            )

    # 6) List courses / catalog
    if "list" in qn and "course" in qn:
        names = ", ".join([f'{c["code"]} ({c["name"]})' for c in COURSES])
        return RoutedAnswer(kind="list_courses", facts=f"Available courses: {names}.")

    return None


def answer_with_gemini(*, user_question: str, chat_history: list[dict] | None = None) -> str:
    """
    Always calls Gemini. For common catalog queries, we route and provide
    deterministic facts; Gemini then formats a friendly answer.
    """
    routed = route_question(user_question)
    context = course_context_text()

    # Keep history small and safe (only user/assistant text)
    history_lines: list[str] = []
    for m in (chat_history or [])[-6:]:
        role = m.get("role", "")
        content = (m.get("content", "") or "").strip()
        if role in ("user", "assistant") and content:
            history_lines.append(f"{role.upper()}: {content}")
    history_block = "\n".join(history_lines) if history_lines else "(none)"

    if routed:
        task = f"""You are a helpful course-catalog Q&A chatbot.

Use ONLY the catalog context below as truth. Do not invent any policy details.

Catalog context:
{context}

Conversation history (may be empty):
{history_block}

User question:
{user_question}

Verified facts you MUST incorporate:
{routed.facts}

Write a concise answer (1-4 sentences)."""
        return generate_text(prompt=task)

    # Unknown / unsupported question: respond gracefully
    task = f"""You are a helpful course-catalog Q&A chatbot.

Use ONLY the catalog context below as truth. If the user asks anything not in the catalog (attendance policy, grading, fees, faculty, syllabus, exam date, etc.), say you don't have that information and suggest 2-3 example questions you *can* answer.

Catalog context:
{context}

Conversation history (may be empty):
{history_block}

User question:
{user_question}

Return a helpful refusal (2-5 sentences)."""
    return generate_text(prompt=task)

