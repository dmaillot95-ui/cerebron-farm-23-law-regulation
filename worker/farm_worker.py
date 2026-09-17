import json, os, sys, time
from gradio_client import Client

role = os.environ.get('ROLE', 'LEGAL_ANALYST')
mission = os.environ.get('MISSION', 'Analyze the assigned law/regulation problem.')
model = os.environ.get('MODEL', 'huggingface-projects/llama-3.2-3B-Instruct')

system = f'''You are {role}, one independent worker in CEREBRON OMEGA Farm 23 Law Regulation.
Rules: REALITY > COHERENCE; CLAIM <= EVIDENCE; JURISDICTION MUST BE EXPLICIT; DATE/VERSION MUST BE EXPLICIT; PRIMARY LAW > COMMENTARY; GUIDANCE != BINDING LAW; LEGAL ANALYSIS != LEGAL ADVICE; UNKNOWN REMAINS UNKNOWN.
Never invent statutes, cases, regulators, article numbers, dates, or citations. Distinguish binding law, non-binding guidance, standards, contracts, interpretation, and uncertainty. Patentability != FTO. Identify what requires qualified human legal validation.
Return a compact auditable analysis with: scope; jurisdiction/time; sources needed; established rules; uncertainties; contradictions; risks; verification plan; conclusion status.'''

prompt = system + "\n\nMISSION:\n" + mission
result = {"role": role, "model": model, "status": "UNREVIEWED_EXTERNAL_AGENT_OUTPUT", "ok": False}
try:
    client = Client(model)
    answer = client.predict(message=prompt, api_name="/chat")
    result.update({"ok": True, "answer": answer})
except Exception as e:
    result.update({"error": repr(e)})

os.makedirs('results', exist_ok=True)
path = f"results/{role}.json"
with open(path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(json.dumps(result, ensure_ascii=False))
if not result['ok']:
    sys.exit(1)
