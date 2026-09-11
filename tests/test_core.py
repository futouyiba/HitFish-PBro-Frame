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
 assert replay_hash({'seed':7},{'weight':1})==replay_hash({'seed':7},{'weight':1})
 assert replay_hash({'seed':7},{'weight':1})!=replay_hash({'seed':8},{'weight':1})

@pytest.mark.parametrize('bad',[-1,float('nan'),float('inf'),True])
def test_position_weights_reject_invalid_inputs(bad):
 with pytest.raises(ValueError,match='INVALID_POSITION_WEIGHT'): normalize_capacity({'a':bad,'b':2})

def test_mode_response_preserves_joint_a_match():
 s={'m1':.5,'m2':.5}; response,c=evaluate_mode_response(s,{'m1':1,'m2':1},{'m1':1,'m2':0},{'m1':0,'m2':1})
 assert response==0 and c['m1']==0 and c['m2']==0

def test_mode_response_uses_per_mode_nonlinearity():
 s={'m1':.5,'m2':.5}; response,_=evaluate_mode_response(s,{'m1':1,'m2':1},{'m1':1,'m2':.25},{'m1':1,'m2':1},gamma=2)
 assert response==pytest.approx(.53125)

def test_match_requires_complete_valid_modes():
 with pytest.raises(ValueError,match='INVALID_MATCH'): evaluate_mode_response({'m':1},{'m':1},{'m':1},{'m':True})
 with pytest.raises(ValueError,match='MISSING_MATCH_MODE'): evaluate_mode_response({'m':1,'n':0},{'m':1,'n':1},{'m':1,'n':1},{'m':1})

def test_replay_hash_changes_with_result():
 assert replay_hash({'x':1},{'y':2}) != replay_hash({'x':1},{'y':3})

def test_p_a_signal_domain():
 with pytest.raises(ValueError,match='INVALID_P'): validate_signal_map({'m':{'t':True}},'p')
 with pytest.raises(ValueError,match='INVALID_A'): validate_signal_map({'m':{'t':-0.2}},'a')
