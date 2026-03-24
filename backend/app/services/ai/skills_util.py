def user_skill_tokens(skills: dict) -> set[str]:
    if not skills:
        return set()
    out: set[str] = set()
    for k, v in skills.items():
        out.add(str(k).lower())
        if isinstance(v, list):
            for x in v:
                out.add(str(x).lower())
        elif isinstance(v, str):
            out.add(v.lower())
    return out


def skill_match_score(skills: dict, required: list[str]) -> float:
    if not required:
        return 1.0
    tokens = user_skill_tokens(skills)
    matched = 0
    for r in required:
        rl = r.lower()
        if any(rl == t or rl in t or t in rl for t in tokens):
            matched += 1
    return matched / len(required)
