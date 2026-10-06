from pathlib import Path

def load_chunks(docs_folder):
    chunks = []
    for path in Path(docs_folder).glob("*.md"):
        content = path.read_text(encoding="utf-8")
        sections = content.split("\n### ")
        for section in sections[1:]:
            lines = section.split("\n")
            heading = lines[0]
            text = "\n".join(lines[1:]).strip()

            chunk_id, title = heading.split(" ", 1)
            chunks.append({
                "id": chunk_id,
                "doc": path.stem,
                "title": title,
                "text": text
            })
        pass
    return chunks


def search(query, chunks, k=3):
    ignored_words = {"the", "a", "is", "and", "of", "to"}
    query_words = [w.strip("?.,()") for w in query.lower().split()]
    query_words = [w for w in query_words if w not in ignored_words]    
    scored = []
    for chunk in chunks:
        chunk_words = [w.strip("?.,()") for w in (chunk["title"] + " " + chunk["text"]).lower().split()]
        score = 0
        for word in query_words:
            if word in chunk_words:
                score = score + 1
        scored.append(score, chunk)
    scored.sort(key=lambda pair: pair[0], reverse=True)
    top = [chunk for score, chunk in scored[:k]]
    return top

if __name__ == "__main__":
    chunks = load_chunks("docs")
    print(len(chunks), "chunks")

    tests = [
    ("Do you enforce multi-factor authentication for all employees?", "AC-1.1"),
    ("How often are production backups performed?", "BR-1.1"),
    ("Is customer data encrypted at rest?", "DP-1.1"),
    ("Do your staff need a second factor to log in to company systems?", "AC-1.1"),
]

    for question, expected in tests:
        results = search(question, chunks)
        ids = [c["id"] for c in results]
        print(question)
        print("  top 3:", ids)
        print("  expected", expected, "->", "FOUND" if expected in ids else "MISSING")