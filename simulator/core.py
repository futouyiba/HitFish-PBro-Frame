from dataclasses import dataclass
from math import exp, log
import hashlib
@dataclass(frozen=True)
class Mode: id:str; priority:float; scope:float; mixability:float; abase:float

def validate_fact_dag(nodes):
 graph={n['id']:n.get('dependsOn',[]) for n in nodes}; seen=set(); active=set()
 def visit(k):
  if k in active: raise ValueError('FACT_DAG_CYCLE:'+k)
  if k in seen:return
  active.add(k)
  for d in graph.get(k,[]):
   if d not in graph: raise ValueError('FACT_DEP_MISSING:'+d)
   visit(d)
  active.remove(k); seen.add(k)
 for k in graph: visit(k)
 return True

def environment_revision(facts, ema_initial):
 payload=repr((facts,ema_initial)).encode(); return hashlib.sha256(payload).hexdigest()[:16]

def power_normalize(modes,tau=2.0):
 if tau<=0: raise ValueError('TAU_INVALID')
 fallbacks=[m for m in modes if m.id=='FALLBACK']
 if len(fallbacks)!=1: raise ValueError('FALLBACK_MODE_REQUIRED')
 w={m.id:(max(0,m.priority*m.scope*m.mixability))**tau for m in modes}; z=sum(w.values())
 if z==0:
  return {m.id:float(m.id=='FALLBACK') for m in modes},'SCOPE_ALL_ZERO'
 return {k:v/z for k,v in w.items()},None

def geometric(values,weights=None):
 if not values:return 0.0
 weights=weights or [1.0]*len(values); z=sum(weights)
 if any(v<=0 for v in values) or z<=0:return 0.0
 return exp(sum(w*log(v) for v,w in zip(values,weights))/z)

def evaluate_a(shares,p,a):
 den=sum(shares.get(k,0)*p.get(k,0) for k in shares)
 return sum(shares.get(k,0)*p.get(k,0)*a.get(k,0) for k in shares)/den if den else 0.0

def evaluate_a_channels(shares,p,a):
    selection=evaluate_a(shares,p,a)
    present={k:shares.get(k,0)*p.get(k,0) for k in shares}
    dominant=max(present,key=present.get) if present and max(present.values())>0 else None
    return selection, (a.get(dominant,0.0) if dominant else 0.0), dominant

def normalize_capacity(raw, missing=False):
 z=sum(max(0,v) for v in raw.values())
 if z: return {k:v/z for k,v in raw.items()},None
 return ({k:0.0 for k in raw},'MISSING_FACT' if missing else 'POSITION_ALL_ZERO')
