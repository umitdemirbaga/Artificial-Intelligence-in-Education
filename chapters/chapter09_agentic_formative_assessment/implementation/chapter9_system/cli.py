"""Reproducible command-line interface; intentionally no automatic test-set evaluation."""
from argparse import ArgumentParser
import json
from pathlib import Path
from .client import OllamaClient
from .contracts import Case
from .experiments import read_cases, run_cases
from .historical import analyze
from .pipeline import assess
from .review import create_review_sheet,score_review_sheet


def main(argv=None):
    p=ArgumentParser(prog="chapter9")
    sub=p.add_subparsers(dest="command",required=True)
    a=sub.add_parser("analyze-existing",help="Audit archived development results offline")
    a.add_argument("--data-dir",default="data/restricted_local")
    a.add_argument("--out",default="results/historical")
    r=sub.add_parser("run-dev",help="Run F1 on development inputs using local Ollama")
    r.add_argument("--input",required=True)
    r.add_argument("--out",default="results/f1_dev_run")
    r.add_argument("--model",default="qwen3:4b-instruct")
    r.add_argument("--limit",type=int)
    d=sub.add_parser("demo",help="Offline synthetic stub; never an empirical measurement")
    g=sub.add_parser("review-sheet",help="Create blank human assessment template")
    g.add_argument("--records",required=True); g.add_argument("--out",required=True)
    h=sub.add_parser("score-reviews",help="Aggregate explicitly completed human-review ratings")
    h.add_argument("--input",required=True); h.add_argument("--out",required=True)
    args=p.parse_args(argv)
    if args.command=="analyze-existing":
        x=analyze(args.data_dir,args.out)
        print(json.dumps({k:v for k,v in x.items() if k!="source_sha256"},indent=2,ensure_ascii=False))
    elif args.command=="run-dev":
        if args.limit is not None and args.limit<1:p.error("limit must be >=1")
        cases=read_cases(args.input)
        # Fail closed against accidental use of explicitly held-out data.
        if any(c.case_id.startswith(("test_","heldout_")) for c in cases):
            p.error("Held-out cases are not enabled by run-dev. Freeze and review the protocol first.")
        result=run_cases(cases,OllamaClient(args.model),args.out,max_cases=args.limit)
        print(json.dumps(result,indent=2))
    elif args.command=="review-sheet":
        print("Blank review rows:",create_review_sheet(args.records,args.out))
    elif args.command=="score-reviews":
        print(json.dumps(score_review_sheet(args.input,args.out),indent=2))
    elif args.command=="demo":
        class Stub:
            model="SYNTHETIC_MOCK_NO_LLM"
            def __init__(self):self.n=0
            def ask(self,_):
                self.n+=1
                if self.n==1:
                    return {"parsed":{"error_status":"possible", "evidence_quote":"2 + 2 = 5",
                            "diagnosis":"Check the addition step.","strategy":"step_check",
                            "arithmetic_expression":"2+2"},"seconds":0}
                return {"parsed":{"teacher_draft":"Ask the learner to verify the addition step.",
                        "scaffold_question":"Can you recompute the sum?"},"seconds":0}
        c=Case("SYNTHETIC_001","What is 2 + 2?","2 + 2 = 5")
        print(json.dumps(assess(c,Stub()),indent=2))

if __name__=="__main__":main()
