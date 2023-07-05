import argparse
import os

import torch
from tenacity import retry, stop_after_attempt, wait_fixed
from transformers import AutoModelForCausalLM, AutoTokenizer

parser = argparse.ArgumentParser()
parser.add_argument("--model", help="Model to download")
args = parser.parse_args()

print(f"Downloading model {args.model}")


@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def download_model() -> None:
    _ = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    _ = AutoModelForCausalLM.from_pretrained(
        args.model,
        trust_remote_code=True,
        torch_dtype=torch.float16,
        device_map=os.getenv("DEVICE", "auto"),
    )


download_model()
