import string,types
string.replace=lambda v,a,b:v.replace(a,b)
string.strip=lambda v:v.strip()
string.lower=lambda v:v.lower()
string.upper=lambda v:v.upper()
string.find=lambda v,q:v.find(q)
string.split=lambda v,q=None:v.split(q)
string.join=lambda vs,q=' ':q.join(vs)
types.StringType=str
types.TupleType=tuple
types.ListType=list
types.IntType=int
