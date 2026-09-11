from dataclasses import dataclass
from math import exp, log
import hashlib
import json
from math import isfinite
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
 payload=json.dumps({'facts':facts,'emaInitial':ema_initial},sort_keys=True,
                    separators=(',', ':'),ensure_ascii=False,allow_nan=False).encode('utf-8')
 return hashlib.sha256(payload).hexdigest()

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

def evaluate_mode_response(shares, p, a, matches, gamma=1.0):
    """Mode-preserving response: sum(pi_m,t * A_m,t^gamma * Match_m,t)."""
    presence={k:max(0.0,shares.get(k,0.0)*p.get(k,0.0)) for k in shares}
    z=sum(presence.values())
    if z<=0: return 0.0, {}
    pi={k:v/z for k,v in presence.items()}
    contributions={k:pi[k]*(max(0.0,min(1.0,a.get(k,0.0)))**gamma)*max(0.0,min(1.0,matches.get(k,0.0))) for k in pi}
    return sum(contributions.values()), contributions

def validate_signal_map(signal_map, name):
    for mode, values in signal_map.items():
        for target, value in values.items():
            if isinstance(value,bool) or not isinstance(value,(int,float)) or not isfinite(value) or value<0 or value>1:
                raise ValueError(f'INVALID_{name.upper()}:{mode}:{target}')
    return True

def normalize_capacity(raw, missing=False):
 if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not isfinite(v) or v<0 for v in raw.values()):
  raise ValueError('INVALID_POSITION_WEIGHT')
 if missing: raise ValueError('MISSING_FACT')
 z=sum(raw.values())
 if z: return {k:v/z for k,v in raw.items()},None
 return ({k:0.0 for k in raw},'MISSING_FACT' if missing else 'POSITION_ALL_ZERO')
