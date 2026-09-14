"""Repeatable local demo; its temporary database is independent of your app data."""
import json, os, tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from app import app
scratch=Path(tempfile.mkdtemp(prefix='portfolio-demo-'))
os.environ['DATABASE_PATH']=str(scratch/'demo.sqlite3')
os.environ['API_KEYS_JSON']='{"local-demo-key":"demo"}'
os.environ['TENANT_ROLES_JSON']='{"demo":"operator"}'
os.environ.pop('LLM_ENDPOINT',None)
os.environ['DAILY_QUOTA']='20'
client=TestClient(app)
H={'Authorization':'Bearer local-demo-key'}
from automation import approve
p=client.post('/plans',headers=H,json={'action':'create_task','arguments':{'title':'Review the invoice'}}).json()['plan_id']
blocked=client.post(f'/plans/{p}/execute',headers=H).status_code
approve('demo',p,'approver')  # Simulates the separate human approval in this isolated demo.
result={'blocked_before_approval':blocked,'execution':client.post(f'/plans/{p}/execute',headers=H).json(),'audit':client.get('/audit',headers=H).json()}
Path('docs/demo-output.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
