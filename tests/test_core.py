from simulator.core import *
def test_a_excludes_absent_mode():
 s={'MAIN':.5,'SUB':.5}; assert evaluate_a(s,{'MAIN':1,'SUB':0},{'MAIN':.2,'SUB':1})==.2
def test_scope_zero():
 s,fb=power_normalize([Mode('MAIN',1,0,1,.5),Mode('FALLBACK',0,0,1,0)]); assert s['FALLBACK']==1 and fb
