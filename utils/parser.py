import re

def extract_experience_section(text):
    keywords = ["pengalaman", "experience", "kerja", "work"]
    for k in keywords:
        if k in text:
            start = text.index(k)
            return text[start:start+1200]  # ambil sebagian saja
    return text


def parse_cv_structured(text):

    # DEGREE
    degree = ""
    if re.search(r"\bs1\b", text):
        degree = "s1"
    elif re.search(r"\bd4\b", text):
        degree = "d4"
    elif re.search(r"\bd3\b", text):
        degree = "d3"
    elif "sma" in text:
        degree = "sma"

    # MAJOR
    major_keywords = [
        "teknik sipil",
        "teknik industri",
        "teknik mesin",
        "akuntansi",
        "hukum",
        "psikologi",
        "ekonomi",
        "manajemen"
    ]

    major = ""
    for m in major_keywords:
        if m in text:
            major = m
            break

    edu = f"{degree} {major}".strip()

    # EXPERIENCE (filtered)
    pengalaman = extract_experience_section(text)

    # SKILL (FULL TEXT → BIAR SEMANTIC KUAT)
    kemampuan = text

    return {
        "edu": edu,
        "exp": pengalaman,
        "skill": kemampuan,
        "all": text,
        "degree": degree,
        "major": major
    }