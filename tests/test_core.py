from simulator.core import *
import pytest
def test_a_excludes_absent_mode():
 s={'MAIN':.5,'SUB':.5}; assert evaluate_a(s,{'MAIN':1,'SUB':0},{'MAIN':.2,'SUB':1})==.2
def test_scope_zero():
 s,fb=power_normalize([Mode('MAIN',1,0,1,.5),Mode('FALLBACK',0,0,1,0)]); assert s['FALLBACK']==1 and fb
def test_a_channels_align_with_presence():
 s={'MAIN':.5,'SUB':.5}; sel,dom,mode=evaluate_a_channels(s,{'MAIN':1,'SUB':0},{'MAIN':.2,'SUB':1}); assert sel==.2 and dom==.2 and mode=='MAIN'
def test_zero_reasons():
 assert normalize_capacity({'a':0})[1]=='POSITION_ALL_ZERO'
 with pytest.raises(ValueError, match='MISSING_FACT'): normalize_capacity({'a':0},missing=True)
def test_fact_dag_and_revision():
 assert validate_fact_dag([{'id':'raw'},{'id':'derived','dependsOn':['raw']}])
 try: validate_fact_dag([{'id':'a','dependsOn':['b']},{'id':'b','dependsOn':['a']}]); assert False
 except ValueError as e: assert str(e).startswith('FACT_DAG_CYCLE')
 assert environment_revision({'x':1},{'ema':0})==environment_revision({'x':1},{'ema':0})

def test_revision_independent_of_mapping_insertion_order():
 assert environment_revision({'a':1,'b':2},{'x':0})==environment_revision({'b':2,'a':1},{'x':0})
 assert environment_revision({'a':1},{'x':0})!=environment_revision({'a':2},{'x':0})
 assert environment_revision({'a':1},{'x':0})!=environment_revision({'a':1},{'x':1})

@pytest.mark.parametrize('bad',[-1,float('nan'),float('inf'),True])
def test_position_weights_reject_invalid_inputs(bad):
 with pytest.raises(ValueError,match='INVALID_POSITION_WEIGHT'): normalize_capacity({'a':bad,'b':2})
