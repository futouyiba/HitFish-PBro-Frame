from dataclasses import dataclass
from math import exp, log
@dataclass(frozen=True)
class Mode: id:str; priority:float; scope:float; mixability:float; abase:float

def power_normalize(modes,tau=2.0):
 w={m.id:(max(0,m.priority*m.scope*m.mixability))**tau for m in modes}; z=sum(w.values())
 if z==0:
  main=next((m.id for m in modes if m.id=='MAIN'),modes[0].id if modes else None)
  return {m.id:float(m.id==main) for m in modes},'SCOPE_ALL_ZERO'
 return {k:v/z for k,v in w.items()},None

def geometric(values,weights=None):
 if not values:return 0.0
 weights=weights or [1.0]*len(values); z=sum(weights)
 if any(v<=0 for v in values) or z<=0:return 0.0
 return exp(sum(w*log(v) for v,w in zip(values,weights))/z)

def evaluate_a(shares,p,a):
 den=sum(shares.get(k,0)*p.get(k,0) for k in shares)
 return sum(shares.get(k,0)*p.get(k,0)*a.get(k,0) for k in shares)/den if den else 0.0

def normalize_capacity(raw):
 z=sum(max(0,v) for v in raw.values())
 return ({k:v/z for k,v in raw.items()},'P_ALL_ZERO') if z else ({k:0.0 for k in raw},'P_ALL_ZERO')
