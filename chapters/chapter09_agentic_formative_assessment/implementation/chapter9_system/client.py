"""Local Ollama JSON interface; no third-party API, no training-time uploads."""
import json
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

class ModelError(RuntimeError):
    pass

class OllamaClient:
    def __init__(self, model="qwen3:4b-instruct", url="http://127.0.0.1:11434", timeout=240):
        if not url.startswith(("http://127.0.0.1:","http://localhost:", "http://[::1]:")):
            raise ValueError("Only loopback Ollama endpoints are enabled by default")
        self.model, self.url, self.timeout = model, url.rstrip("/"), timeout

    def ask(self, messages):
        payload = {"model":self.model,"stream":False,"format":"json","messages":messages,
                   "options":{"temperature":0,"num_predict":750}}
        data = json.dumps(payload,ensure_ascii=False).encode("utf-8")
        req = Request(self.url+"/api/chat",data=data,headers={"Content-Type":"application/json"},method="POST")
        t0=time.perf_counter()
        try:
            with urlopen(req,timeout=self.timeout) as reply:
                response = json.loads(reply.read().decode("utf-8"))
            content = response["message"]["content"]
            proposal = json.loads(content)
            if not isinstance(proposal,dict):
                raise ModelError("Model JSON not an object")
            return {"parsed":proposal,"seconds":round(time.perf_counter()-t0,3),"model":self.model,
                    "tokens_in":response.get("prompt_eval_count"),"tokens_out":response.get("eval_count")}
        except (HTTPError,URLError,TimeoutError,KeyError,json.JSONDecodeError,UnicodeDecodeError,ModelError) as e:
            raise ModelError(f"Ollama call failed: {type(e).__name__}: {str(e)[:250]}") from e
