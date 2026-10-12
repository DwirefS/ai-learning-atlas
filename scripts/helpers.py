
def S(id, title, why, explainer, resources, project, topics, quiz=None, concepts=None):
    return {
        "id": id, "title": title, "why": why, "explainer": explainer,
        "resources": resources, "project": project, "topics": topics,
        "quiz": quiz or [], "conceptIds": concepts or [],
    }

def T(id, title, subtopics):
    return {"id": id, "title": title,
            "subtopics": [{"id": f"{id}-s{i+1}", "title": s} for i,s in enumerate(subtopics)]}

def L(id, name, subjects):
    return {"id": id, "name": name, "subjects": subjects}

def Q(q, choices, answer, why):
    return {"q": q, "choices": choices, "answer": answer, "why": why}
