import argparse,json
from .core import *
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('fixture'); args=ap.parse_args(); d=json.load(open(args.fixture))
 modes=[Mode(**m) for m in d['modes']]; shares,fb=power_normalize(modes,d.get('tau',2)); p=d['p']; a=d['a']; raw={t:d['capacity'][t]*sum(shares[m]*p[m].get(t,0) for m in shares) for t in d['capacity']}; dist,pfb=normalize_capacity(raw)
 out={'shares':shares,'fallback':fb,'distribution':dist,'pFallback':pfb,'a':{t:evaluate_a(shares,{m:p[m].get(t,0) for m in shares},{m:a[m].get(t,0) for m in shares}) for t in d['capacity']}}
 print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
