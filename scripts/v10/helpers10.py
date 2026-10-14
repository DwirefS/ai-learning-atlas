"""Helpers for v10 subjects. A subject is built from compact tuples so every field of the v9 lesson bar is present."""
def R(title, url, kind, level, why): return dict(title=title, url=url, kind=kind, level=level, why=why)
def Q(q, choices, answer, why): return dict(q=q, choices=choices, answer=answer, why=why)
def T(sid, key, title, explainer, subs):
    return dict(id=f"{sid}-{key}", title=title, explainer=explainer,
                subtopics=[dict(id=f"{sid}-{key}-s{i+1}", title=a, text=b) for i, (a, b) in enumerate(subs)])
def SUBJ(sid, title, why, explainer, project, topics, quiz, resources, lesson, case=None, concepts=()):
    L = dict(lesson); L["enterpriseLabel"] = "Illustrative scenario"
    if case: L["case"] = case
    return dict(id=sid, title=title, why=why, explainer=explainer, resources=resources, project=project,
                topics=topics, quiz=quiz, conceptIds=list(concepts), lesson=L)
def C(org, title, url, summary, lesson): return dict(org=org, title=title, url=url, summary=summary, lesson=lesson)
