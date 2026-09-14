import json
from common import db, save, records
ALLOWED={'analyst':{'report'},'operator':{'report','create_task'},'approver':{'report','create_task'}}
def plan(tenant,action,arguments):
    if action not in {'report','create_task'}: raise ValueError('Unknown tool')
    if action=='create_task' and (set(arguments)!={'title'} or not isinstance(arguments.get('title'),str) or not 1<=len(arguments['title'])<=200): raise ValueError('create_task requires a title of 1-200 characters')
    if action=='report' and arguments: raise ValueError('report accepts no arguments')
    return save(tenant,'plan',{'action':action,'arguments':arguments,'status':'pending','approved':False})
def approve(tenant,plan_id,role):
    if role!='approver':
        save(tenant,'audit',{'event':'approval_denied','plan_id':plan_id,'role':role})
        raise PermissionError('Approver role required')
    with db() as conn:
        conn.execute('BEGIN IMMEDIATE')
        row=conn.execute("SELECT payload FROM records WHERE id=? AND tenant=? AND kind='plan'",(plan_id,tenant)).fetchone()
        if not row: raise LookupError('Plan not found')
        p=json.loads(row[0])
        if p['status']!='pending': raise ValueError('Plan already executed')
        p['approved']=True
        conn.execute('UPDATE records SET payload=? WHERE id=?',(json.dumps(p),plan_id))
        conn.execute('INSERT INTO records(tenant,kind,payload) VALUES(?,?,?)',(tenant,'audit',json.dumps({'event':'approved','plan_id':plan_id,'role':role})))
    return {'approved':True,'plan_id':plan_id}
def execute(tenant,plan_id,role):
    with db() as conn:
        conn.execute('BEGIN IMMEDIATE')
        row=conn.execute("SELECT payload FROM records WHERE id=? AND tenant=? AND kind='plan'",(plan_id,tenant)).fetchone()
        if not row: raise LookupError('Plan not found')
        p=json.loads(row[0])
        reason=None
        if p['action'] not in ALLOWED.get(role,set()): reason='Tool not permitted for role'
        elif p['action']=='create_task' and not p['approved']: reason='Approval required before write'
        if reason:
            conn.execute('INSERT INTO records(tenant,kind,payload) VALUES(?,?,?)',(tenant,'audit',json.dumps({'event':'execution_denied','plan_id':plan_id,'role':role,'reason':reason})))
            conn.commit()
            raise PermissionError(reason)
        if p['status']=='executed': return p['result']
        if p['action']=='report':
            count=conn.execute("SELECT COUNT(*) FROM records WHERE tenant=? AND kind='task'",(tenant,)).fetchone()[0]
            result={'task_count':count}
        else:
            task_id=conn.execute('INSERT INTO records(tenant,kind,payload) VALUES(?,?,?)',(tenant,'task',json.dumps(p['arguments']))).lastrowid
            result={'task_id':task_id,**p['arguments']}
        p.update(status='executed',result=result)
        conn.execute('UPDATE records SET payload=? WHERE id=?',(json.dumps(p),plan_id))
        conn.execute('INSERT INTO records(tenant,kind,payload) VALUES(?,?,?)',(tenant,'audit',json.dumps({'event':'executed','plan_id':plan_id,'role':role,'action':p['action']})))
        return result
