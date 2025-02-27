import argparse
from platform import machine

import torch
from petals import AutoDistributedModelForCausalLM
from tenacity import retry, stop_after_attempt, wait_fixed
from transformers import AutoTokenizer, LlamaTokenizer

parser = argparse.ArgumentParser()
parser.add_argument("--model", help="Model to download")
args = parser.parse_args()

print(f"Downloading model {args.model}")


@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def download_model() -> None:
    Tokenizer = LlamaTokenizer if "llama" in args.model.lower() else AutoTokenizer
    _ = Tokenizer.from_pretrained(args.model)

    kwargs = {}
    if "x86_64" in machine():
        kwargs["torch_dtype"] = torch.float32
    _ = AutoDistributedModelForCausalLM.from_pretrained(args.model, **kwargs)


download_model()
