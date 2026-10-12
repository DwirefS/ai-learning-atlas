def R(t,u): return {"title":t,"url":u}
def Q(q,c,a,w): return {"q":q,"choices":c,"answer":a,"why":w}
def T(id,title,expl,subs):
    return {"id":id,"title":title,"explainer":expl,"subtopics":[{"id":f"{id}-s{i+1}","title":s} for i,s in enumerate(subs)]}
def S(id,title,why,expl,res,project,topics,quiz,concepts):
    return {"id":id,"title":title,"why":why,"explainer":expl,"resources":res,"project":project,"topics":topics,"quiz":quiz,"conceptIds":concepts}
