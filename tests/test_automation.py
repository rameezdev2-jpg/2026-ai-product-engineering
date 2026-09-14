import pytest
from automation import plan,approve,execute
from common import records
def test_permission_approval_and_idempotence():
    p=plan('a','create_task',{'title':'Review invoice'})
    with pytest.raises(PermissionError): execute('a',p,'operator')
    with pytest.raises(PermissionError): approve('a',p,'operator')
    approve('a',p,'approver')
    first=execute('a',p,'operator')
    assert execute('a',p,'operator')==first
    assert len(records('a','task'))==1
    assert any(r['event']=='execution_denied' for r in records('a','audit'))
def test_cross_tenant_and_unknown_tool():
    p=plan('a','report',{})
    with pytest.raises(LookupError): execute('b',p,'approver')
    with pytest.raises(ValueError): plan('a','shell',{'command':'anything'})
def test_api_role_cannot_be_spoofed():
    from fastapi.testclient import TestClient
    from app import app
    c=TestClient(app);h={'Authorization':'Bearer local-demo-key','X-Role':'approver'}
    p=c.post('/plans',headers=h,json={'action':'create_task','arguments':{'title':'hello'}}).json()['plan_id']
    assert c.post(f'/plans/{p}/approve',headers=h).status_code==403
