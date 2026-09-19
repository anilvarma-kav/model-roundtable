# Sample conversation

This is the actual output from a one-round notebook run using four providers. The replies below are preserved without editing. This file can be read directly on GitHub; the app also loads the same JSON without making API calls.

**Topic:** Should a beginner build a multi-model roundtable as a first LLM portfolio project?

**Reported usage:** 3,231 tokens · **Estimated API cost:** $0.01029.

## Observations

- Later speakers respond to earlier ones by name, demonstrating shared context.
- The models disagree about scope, which is useful for comparing perspectives.
- Some replies exceed the requested 140 words. Prompt instructions are not hard limits.
- The local model's sample code is incomplete as deployment guidance: it suggests `docker compose up` without providing a Compose file. Generated advice needs checking.
- This sample predates the standalone app: it used an 800-token allowance and the `ollama/` route. The app uses a 1,500-token allowance, the `ollama_chat/` route, and explicit handling for empty or truncated replies.

## Transcript

### OpenAI

Model: `openai/gpt-4.1-mini`

A beginner building a multi-model roundtable for their first LLM portfolio project could be ambitious but also rewarding. It showcases understanding of model capabilities and prompts diverse perspectives. However, it involves complexities like coordinating models, managing context, and integrating outputs, which might be challenging without prior experience. A practical approach is to start with simpler single-model projects to build foundational skills. Then, gradually integrate multiple models with clear goals (e.g., comparing responses or collaboration). This progression balances learning curve and portfolio impact. What specific goals do you have for demonstrating your skills in the portfolio?

### Claude

Model: `anthropic/claude-haiku-4-5`

I'd push back slightly on the sequencing here. While OpenAI's caution is reasonable, the real question is *scope*, not necessarily avoiding multi-model work entirely.

A beginner could succeed with a **focused multi-model project** if they constrain it smartly: pick 2-3 models with a clear reason for comparison (e.g., "How do open-source vs. closed models handle reasoning?"), use a single, well-defined task, and automate the plumbing rather than hand-wiring everything.

The portfolio value comes from demonstrating *intentional design choices*—why these models, why this structure. That's actually clearer in a multi-model setup than in a single-model project, provided you don't overreach.

**The real tradeoff**: A simpler project done excellently (clean code, clear documentation, thoughtful evaluation) beats an ambitious project that's half-finished or poorly documented. The question isn't "multi-model or not?" but "Can I ship something with clear narrative?"

What's the actual problem you're trying to solve with this roundtable?

### Grok

Model: `xai/grok-4.6`

Grok: OpenAI's "start simple" and Claude's "scope it" both underplay the gimmick risk. A roundtable is mostly API glue plus a cute UI—hiring folks have seen that demo. It rarely proves LLM skill.

Better first signal: a two-model pipeline, not a panel. One drafts, one critic-scores (or routes by task). Log disagreements. That's use, not theater, and cheaper.

Ship test: if you can't state one crisp insight in 90 seconds, skip it. Else do Claude's tight 2-model version, document failures, and stop. Don't let "roundtable" become the product.

### Local GPT-OSS

Model: `ollama/gpt-oss:20b`

**Local GPT-OSS Point**

Start with a *2‑model pipeline*—not a full roundtable—to keep the scope tight and reproducible locally.

**Responding to OpenAI**:

Instead of “start simple,” begin with the *simplest* multi‑model setup: two models, one task, one API.

**Responding to Claude**:

Scope matters. Pick models that differ on a single axis (e.g., open‑source vs. closed) and document that choice.

**Responding to Grok**:

Avoid gimmick UI. Deliver a CLI/REST endpoint that logs both responses and the disagreement metric.

**Concrete Next Step**

```bash
# Dockerfile
FROM python:3.12-slim
RUN pip install fastapi uvicorn transformers torch
COPY app.py .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]
```

```python
# app.py
from fastapi import FastAPI
from transformers import pipeline

app = FastAPI()
model_a = pipeline("text-generation", model="meta-llama/Llama-2-7b-chat-hf")
model_b = pipeline("text-generation", model="EleutherAI/gpt-j-6b")

@app.post("/compare")
async def compare(prompt: str):
    a = model_a(prompt, max_new_tokens=50)[0]["generated_text"]
    b = model_b(prompt, max_new_tokens=50)[0]["generated_text"]
    return {"model_a": a, "model_b": b}
```

Run with `docker compose up`. Add unit tests and a README that explains the “why” of each choice. This delivers a locally runnable, documented portfolio piece that satisfies all viewpoints.
