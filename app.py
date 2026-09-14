import json
import os
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from common import identity, records
from automation import plan,approve,execute
app=FastAPI(title='MCP Business Automation')
def principal(tenant=Depends(identity)):
    # Roles are configured by the server, never accepted from the request body.
    return tenant,json.loads(os.getenv('TENANT_ROLES_JSON','{"demo":"analyst"}')).get(tenant,'analyst')
class Plan(BaseModel):
    action:str
    arguments:dict=Field(default_factory=dict)
def call(fn,*args):
    try: return fn(*args)
    except PermissionError as exc: raise HTTPException(403,str(exc))
    except LookupError as exc: raise HTTPException(404,str(exc))
    except ValueError as exc: raise HTTPException(422,str(exc))
@app.get('/health')
def health(): return {'status':'ok'}
@app.post('/plans')
def planning(body:Plan,p=Depends(principal)): return {'plan_id':call(plan,p[0],body.action,body.arguments)}
@app.post('/plans/{plan_id}/approve')
def approval(plan_id:int,p=Depends(principal)): return call(approve,p[0],plan_id,p[1])
@app.post('/plans/{plan_id}/execute')
def execution(plan_id:int,p=Depends(principal)): return call(execute,p[0],plan_id,p[1])
@app.get('/audit')
def audit(p=Depends(principal)): return records(p[0],'audit')
