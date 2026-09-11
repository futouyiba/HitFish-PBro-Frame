import argparse,json
from .core import *
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('fixture'); ap.add_argument('--html'); args=ap.parse_args(); d=json.load(open(args.fixture))
 validate_fact_dag(d.get('factNodes',[])); validate_signal_map(d['p'],'p'); validate_signal_map(d['a'],'a'); rev=environment_revision(
  {'factNodes':d.get('factNodes',[]),'p':d['p'],'a':d['a'],'capacity':d['capacity']},d.get('emaInitial',{}))
 modes=[Mode(**m) for m in d['modes']]; shares,fb=power_normalize(modes,d.get('tau',2)); p=d['p']; a=d['a']; raw={t:d['capacity'][t]*sum(shares[m]*p[m].get(t,0) for m in shares) for t in d['capacity']}; dist,pfb=normalize_capacity(raw)
 channels={}
 for t in d['capacity']:
  ps={m:p.get(m,{}).get(t,0) for m in shares}; aa={m:a.get(m,{}).get(t,0) for m in shares}
  sel,dom,mode=evaluate_a_channels(shares,ps,aa); channels[t]={'a_selection':sel,'a_dominant':dom,'dominantModeId':mode}
 supply=d.get('supply',1.0); quality_share=d.get('qualityShare',1.0)
 env_weight={t:supply*quality_share*dist[t] for t in dist}
 if 'match' not in d: raise ValueError('MISSING_MATCH')
 if set(d['match']) != set(d['capacity']): raise ValueError('MISSING_MATCH_TARGET')
 response={t:evaluate_mode_response(shares,{m:p.get(m,{}).get(t,0) for m in shares},{m:a.get(m,{}).get(t,0) for m in shares},d['match'].get(t,{})) for t in d['capacity']}
 out={'revisions':{'config':d.get('configRevision','CFG-DEMO'),'rule':d.get('ruleRevision','RULE-DEMO'),'environment':rev,'bake':d.get('bakeRevision','BAKE-DEMO')},'supply':supply,'qualityShare':quality_share,'shares':shares,'fallback':fb,'distribution':dist,'envWeight':env_weight,'conservation':sum(env_weight.values()),'pFallback':pfb,'channels':channels,'modeResponse':{t:v[0] for t,v in response.items()},'modeContributions':{t:v[1] for t,v in response.items()},'trace':{'fallbackReason':pfb or fb,'targetCount':len(dist)}}
 if args.html:
  rows=''.join(f'<tr><td>{t}</td><td>{dist[t]:.4f}</td><td>{env_weight[t]:.4f}</td><td>{channels[t]["a_selection"]:.4f}</td><td>{channels[t]["a_dominant"]:.4f}</td><td>{channels[t]["dominantModeId"]}</td></tr>' for t in dist)
  open(args.html,'w').write('<!doctype html><meta charset="utf-8"><title>PBro 模拟报告</title><style>body{font:16px system-ui;max-width:1000px;margin:32px auto}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:8px}</style><h1>PBro 模拟器报告</h1><p>EnvWeight 守恒：'+str(sum(env_weight.values()))+'；Fallback：'+str(pfb or fb)+'</p><table><tr><th>Target</th><th>分布</th><th>EnvWeight</th><th>A selection</th><th>A dominant</th><th>模式</th></tr>'+rows+'</table>')
 print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
