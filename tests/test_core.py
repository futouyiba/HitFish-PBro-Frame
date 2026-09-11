from simulator.core import *
def test_a_excludes_absent_mode():
 s={'MAIN':.5,'SUB':.5}; assert evaluate_a(s,{'MAIN':1,'SUB':0},{'MAIN':.2,'SUB':1})==.2
def test_scope_zero():
 s,fb=power_normalize([Mode('MAIN',1,0,1,.5),Mode('FALLBACK',0,0,1,0)]); assert s['FALLBACK']==1 and fb
def test_a_channels_align_with_presence():
 s={'MAIN':.5,'SUB':.5}; sel,dom,mode=evaluate_a_channels(s,{'MAIN':1,'SUB':0},{'MAIN':.2,'SUB':1}); assert sel==.2 and dom==.2 and mode=='MAIN'
def test_zero_reasons():
 assert normalize_capacity({'a':0})[1]=='POSITION_ALL_ZERO'
 assert normalize_capacity({'a':0},missing=True)[1]=='MISSING_FACT'
def test_fact_dag_and_revision():
 assert validate_fact_dag([{'id':'raw'},{'id':'derived','dependsOn':['raw']}])
 try: validate_fact_dag([{'id':'a','dependsOn':['b']},{'id':'b','dependsOn':['a']}]); assert False
 except ValueError as e: assert str(e).startswith('FACT_DAG_CYCLE')
 assert environment_revision({'x':1},{'ema':0})==environment_revision({'x':1},{'ema':0})
