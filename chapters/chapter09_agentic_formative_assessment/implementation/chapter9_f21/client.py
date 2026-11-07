"""Local-only Ollama client with two per-call JSON Schema contracts.

JSON Schema constrains the output shape, not mathematical correctness. No retry
or silent coercion is performed. Unsupported Ollama versions fail closed.
"""
import json
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from chapter9_system.client import ModelError

_REQUIRED_D = ('target_quote','error_status','evidence_quote','diagnosis','strategy','arithmetic_expression')
_REQUIRED_F = ('teacher_draft','scaffold_question')

def _schema(keys):
    props = {k: {'type':'string'} for k in keys}
    if 'error_status' in keys:
        props['error_status']['enum']=['identified','possible','none','uncertain']
        props['strategy']['enum']=['target_check','unit_check','step_check','relation_check']
    return {'type':'object', 'properties':props, 'required':list(keys), 'additionalProperties':False}

DIAGNOSIS_SCHEMA = _schema(_REQUIRED_D)
FEEDBACK_SCHEMA = _schema(_REQUIRED_F)

class StructuredOllamaClient:
    def __init__(self, model='qwen3:4b-instruct', url='http://127.0.0.1:11434',timeout=240):
        if not (url.startswith('http://127.0.0.1:') or url.startswith('http://localhost:') or url.startswith('http://[::1]:')):
            raise ValueError('Only local Ollama allowed')
        self.model,self.url,self.timeout=model,url.rstrip('/'),timeout
    def ask(self,messages):
        if not isinstance(messages,list) or not messages or not isinstance(messages[0],dict):
            raise ModelError('Invalid messages')
        system=messages[0].get('content','')
        if 'target_quote' in system and 'arithmetic_expression' in system:
            schema=DIAGNOSIS_SCHEMA
        elif 'teacher_draft' in system and 'scaffold_question' in system:
            schema=FEEDBACK_SCHEMA
        else: raise ModelError('Unrecognized prompt role')
        payload={'model':self.model,'stream':False,'format':schema,'messages':messages,
                 'options':{'temperature':0,'num_predict':1100}}
        req=Request(self.url+'/api/chat',data=json.dumps(payload,ensure_ascii=False).encode('utf-8'),
                    headers={'Content-Type':'application/json'},method='POST')
        t0=time.perf_counter()
        try:
            with urlopen(req,timeout=self.timeout) as reply:
                response=json.loads(reply.read().decode('utf-8'))
            parsed=json.loads(response['message']['content'])
            if not isinstance(parsed,dict): raise ModelError('NOT_OBJECT')
            if set(parsed)!=set(schema['required']): raise ModelError('SCHEMA_KEYS_INCORRECT')
            if not all(isinstance(parsed[k],str) for k in schema['required']):
                raise ModelError('SCHEMA_TYPE_INCORRECT')
            for k,p in schema['properties'].items():
                if 'enum' in p and parsed[k] not in p['enum']:
                    raise ModelError('SCHEMA_ENUM_INCORRECT')
            return {'parsed':parsed,'seconds':round(time.perf_counter()-t0,3),
                    'model':self.model,'tokens_in':response.get('prompt_eval_count'),
                    'tokens_out':response.get('eval_count'),'schema_contract':'ollama_json_schema_v1'}
        except (HTTPError,URLError,TimeoutError,KeyError,TypeError,ValueError,
                json.JSONDecodeError,UnicodeDecodeError,ModelError) as exc:
            raise ModelError('Structured Ollama failure: '+type(exc).__name__+': '+str(exc)[:160]) from exc
