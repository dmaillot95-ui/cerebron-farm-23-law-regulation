import json, os, subprocess, hashlib

C42_1_CONTRACT = "CEREBRON C42.1 EXECUTION CONTRACT.\nEvery response MUST start exactly with:\nCEREBRON_MODE: <DIRECT|STRUCTURED|POLYMORPHIC|FULL>\nCEREBRON_VERSION: C42.1\nROLE: <role-or-function>\nEVIDENCE_STATUS: <status>\nThen preserve CLAIM, METHOD, ASSUMPTIONS, EVIDENCE, COUNTEREVIDENCE, DEPENDENCIES, PROVENANCE, COST, RESIDUAL, SMALLEST_REMAINING_GAP, NEXT_DECISIVE_TEST.\nREALITY>COHERENCE. EVIDENCE>CONFIDENCE. CLAIM<=EVIDENCE. COMPUTATION!=PROOF. SIMULATION!=TEST. CONSENSUS!=TRUTH. AGENT COUNT!=INTELLIGENCE. SAME MODEL/DATA!=INDEPENDENT EVIDENCE. WORKFLOW SUCCESS!=SCIENTIFIC SUCCESS. EXECUTION_STATE!=CANONICAL_STATE. MINORITY BLOCKERS MUST SURVIVE. CONSCIOUSNESS_STATUS=UNRESOLVED.\n\n"
PREFERRED=['/generate','/chat','/predict','/respond','/infer','/run']
def run(cmd,timeout=240): return subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
def payload_for(spec,prompt):
    payload={}; prompt_set=False
    for p in spec.get('parameters',[]):
        name=p.get('name',''); lname=name.lower(); required=bool(p.get('required',False)); default=p.get('default'); typ=(p.get('type') or {}).get('type')
        if lname in {'message','prompt','text','query','input','instruction','user_message'}: payload[name]=prompt; prompt_set=True
        elif lname in {'chat_history','history','messages'}: payload[name]=[]
        elif lname in {'max_new_tokens','max_tokens','maximum_new_tokens'}: payload[name]=700
        elif lname=='temperature': payload[name]=0.1
        elif lname=='top_p': payload[name]=0.9
        elif lname=='top_k': payload[name]=40
        elif required and default is None:
            if typ=='string' and not prompt_set: payload[name]=prompt; prompt_set=True
            else: return None
    return payload if prompt_set else None
def extract(raw):
    raw=raw.strip()
    try:
        obj=json.loads(raw)
        if isinstance(obj,dict):
            for k in ('Response','response','text','output','message'):
                if isinstance(obj.get(k),str): return obj[k].strip()
    except Exception: pass
    return raw
def invoke(space,prompt):
    prompt = C42_1_CONTRACT + prompt
    info=run(['hf-gradio','info',space],120)
    if info.returncode!=0: return False,'',{'stage':'info','error':(info.stderr or info.stdout)[-1200:]}
    try: api=json.loads(info.stdout)
    except Exception as e: return False,'',{'stage':'decode','error':repr(e)}
    endpoints=list(api.items()); endpoints.sort(key=lambda kv:(PREFERRED.index(kv[0]) if kv[0] in PREFERRED else 99,kv[0]))
    errors=[]
    for endpoint,spec in endpoints:
        p=payload_for(spec,prompt)
        if p is None: continue
        pred=run(['hf-gradio','predict',space,endpoint,json.dumps(p,ensure_ascii=False)],240)
        if pred.returncode==0 and (pred.stdout or '').strip():
            text=extract(pred.stdout)
            if text: return True,text,{'endpoint':endpoint,'sha256':hashlib.sha256(text.encode()).hexdigest()}
        errors.append((pred.stderr or pred.stdout)[-700:])
    return False,'',{'stage':'predict','error':' | '.join(errors[-3:]) or 'No compatible endpoint'}
role=os.environ.get('ROLE','LEGAL_ANALYST'); mission=os.environ.get('MISSION','Analyze the assigned law/regulation problem.'); model=os.environ.get('MODEL','huggingface-projects/llama-3.2-3B-Instruct')
system=f'''You are {role}, one independent worker in CEREBRON OMEGA Farm 23 Law Regulation. Rules: REALITY > COHERENCE; CLAIM <= EVIDENCE; JURISDICTION MUST BE EXPLICIT; DATE/VERSION MUST BE EXPLICIT; PRIMARY LAW > COMMENTARY; GUIDANCE != BINDING LAW; LEGAL ANALYSIS != LEGAL ADVICE; UNKNOWN REMAINS UNKNOWN. Never invent statutes, cases, regulators, article numbers, dates, or citations. Distinguish binding law, non-binding guidance, standards, contracts, interpretation, and uncertainty. Patentability != FTO. Identify what requires qualified human legal validation. Return a compact auditable analysis with: scope; jurisdiction/time; sources needed; established rules; uncertainties; contradictions; risks; verification plan; conclusion status.'''
prompt=system+'\n\nMISSION:\n'+mission
ok,text,meta=invoke(model,prompt)
result={'role':role,'model':model,'inference_success':bool(ok),'status':'UNREVIEWED_EXTERNAL_AGENT_OUTPUT' if ok else 'EXTERNAL_INFERENCE_FAILED','answer':text if ok else None,'error':None if ok else meta.get('error'),'meta':meta}
os.makedirs('results',exist_ok=True)
with open(f'results/{role}.json','w',encoding='utf-8') as f: json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({'role':role,'inference_success':bool(ok)}))