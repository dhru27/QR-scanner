COURSES = [
    {
        "code": "ME401",
        "name": "Advanced Thermodynamics",
        "credits": 6,
        "slot": "Slot 2",
        "prerequisite": "ME201",
    },
    {
        "code": "ME402",
        "name": "Robotics & Automation",
        "credits": 6,
        "slot": "Slot 3",
        "prerequisite": "ME202",
    },
    {
        "code": "ME403",
        "name": "Finite Element Methods",
        "credits": 6,
        "slot": "Slot 2",
        "prerequisite": "ME203",
    },
    {
        "code": "ME404",
        "name": "Computational Fluid Dynamics",
        "credits": 6,
        "slot": "Slot 4",
        "prerequisite": "ME301",
    },
    {
        "code": "ME405",
        "name": "Product Design & Innovation",
        "credits": 6,
        "slot": "Slot 1",
        "prerequisite": None,
    },
    {
        "code": "ME406",
        "name": "AI in Manufacturing",
        "credits": 6,
        "slot": "Slot 3",
        "prerequisite": None,
    },
]


def course_context_text() -> str:
    lines = ["Fictional course catalog (authoritative):"]
    for c in COURSES:
        prereq = c["prerequisite"] if c["prerequisite"] else "None"
        lines.append(
            f'- {c["code"]}: {c["name"]} | Credits: {c["credits"]} | {c["slot"]} | Prerequisite: {prereq}'
        )
    return "\n".join(lines)


def normalize(s: str) -> str:
    return " ".join((s or "").strip().lower().split())


def by_code(code: str):
    code_n = normalize(code).upper()
    for c in COURSES:
        if c["code"].upper() == code_n:
            return c
    return None


def by_name_loose(name: str):
    n = normalize(name)
    if not n:
        return None
    # Loose match: substring against normalized course names
    for c in COURSES:
        if n in normalize(c["name"]):
            return c
    return None
