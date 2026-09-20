---
title: Model Roundtable
emoji: 🗣️
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 5.49.1
python_version: 3.12
app_file: app.py
pinned: false
---

# Model Roundtable

[![Try on Hugging Face Spaces](https://img.shields.io/badge/🤗%20Hugging%20Face-Try%20the%20demo-yellow)](https://huggingface.co/spaces/anilvarmakav/model-roundtable)

**A Python app for exploring how different language models respond to one another in a shared conversation.**

[Open the hosted app](https://huggingface.co/spaces/anilvarmakav/model-roundtable) · [Sample and observations](examples/README.md) · [JSON transcript](examples/roundtable.json) · [Source on GitHub](https://github.com/anilvarma-kav/model-roundtable)

Built with **Python, LiteLLM, Gradio, and Ollama integration**. OpenAI, Claude, Grok, and a local model take turns, reading earlier replies before responding. The interface displays the transcript, reported token usage, and estimated API cost.

## Try the demo — no API keys needed

1. Open [Model Roundtable on Hugging Face](https://huggingface.co/spaces/anilvarmakav/model-roundtable).
2. Click **Load saved demo · no API calls**.
3. Read the four perspectives and download the conversation as JSON.

The demo loads a recorded four-provider conversation. It makes no new model requests and requires no model downloads. **Start conversation** runs new requests and requires configured providers. If the Space is sleeping, allow it to start before using the controls.

![Model Roundtable interface showing a saved conversation](examples/preview.png)

## Engineering highlights

| Area | Implementation |
| --- | --- |
| Provider integration | One LiteLLM interface for cloud APIs and local Ollama inference |
| Orchestration | A sequential round-robin loop with shared context and distinct participant prompts |
| Context management | Complete recent turns retained within a 12,000-character history budget |
| Failure handling | Validation before requests, bounded output, timeouts, and preserved partial results |
| Inspectability | Model names, token usage, estimated costs, truncation notices, and JSON exports |
| Delivery | Gradio UI, mocked provider tests, and GitHub Actions deployment to Spaces |

## What it does

- Choose one to four participants and one to three rounds.
- Watch the conversation appear one completed reply at a time.
- Run local inference with `gpt-oss:20b` through Ollama.
- Track reported tokens and estimated API costs.
- Download the conversation as JSON, including model and usage metadata.
- Keep earlier replies available if a later provider fails.

## Quick start

Use **Python 3.11 or 3.12**. These dependency versions are pinned to the tested environment.

```bash
git clone https://github.com/anilvarma-kav/model-roundtable.git
cd model-roundtable
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

On Windows, use `python` instead of `python3` and activate with `.venv\Scripts\Activate.ps1` in PowerShell.

Open **http://127.0.0.1:7860**, then click **Load saved demo · no API calls**. The demo reads the included JSON file; it makes no model requests.

## Deploy to Hugging Face Spaces

The public demo is deployed at **[anilvarmakav/model-roundtable](https://huggingface.co/spaces/anilvarmakav/model-roundtable)**. The saved demo works without secrets.

To deploy your own copy, create a **Gradio** Space and upload the repository files, or configure the GitHub workflow described below with your Space ID. The README metadata, `app.py`, and `requirements.txt` provide the build configuration.

### Configure live models on a Space

In your Space's **Settings → Variables and secrets**, use **New secret** for each provider you want:

| Secret | Participant |
| --- | --- |
| `OPENAI_API_KEY` | OpenAI |
| `ANTHROPIC_API_KEY` | Claude |
| `XAI_API_KEY` | Grok |

After the app restarts, select only participants with configured credentials. Model overrides such as `OPENAI_MODEL` belong in **variables**. Do not upload a `.env` file or put API keys in public variables. `HF_TOKEN` is used for deployment and does not replace these provider keys. Cloud model usage is billed separately by each provider.

If the app says **“Add these keys to .env or deselect those models”** while running on Hugging Face, add the named keys as **Space secrets** instead. The `.env` instructions apply to local runs. See the [Spaces configuration guide](https://huggingface.co/docs/hub/spaces-overview#managing-secrets-and-environment-variables).

Ollama is intended for local use unless the Space has a separately reachable Ollama service. A Space cannot reach your laptop's Ollama server through `localhost`; leave **Local GPT-OSS** unchecked on the hosted app unless that service is configured.

## Run a live conversation

Create your local configuration:

```bash
cp .env.example .env
```

On Windows, use `Copy-Item .env.example .env`. Add only the keys for the cloud providers you want to select:

```dotenv
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
XAI_API_KEY=your-xai-key
```

`GROK_API_KEY` also works as an alias for `XAI_API_KEY`. API billing and access are managed by each provider. You do not need all three keys; deselect providers you have not configured. Restart the app after editing `.env`.

1. Enter a topic.
2. Select participants and set the number of rounds.
3. Click **Start conversation**.
4. Read the replies, check usage, and download the JSON file.

Four participants × two rounds means **eight model requests**. Each request includes recent conversation history, so later turns usually consume more input tokens.

### Use Ollama locally

Install [Ollama](https://ollama.com), start the Ollama app, and download the model:

```bash
ollama pull gpt-oss:20b
```

If Ollama is not already serving requests, run `ollama serve` in a separate terminal. Select **Local GPT-OSS** in the interface. This participant needs no cloud API key.

The 20B model needs substantial local memory and can be slow. To try a smaller model:

```bash
ollama pull llama3.2:1b
```

Then set `OLLAMA_MODEL=llama3.2:1b` in `.env` and restart. The participant label stays “Local GPT-OSS”, but every reply shows the actual configured model.

### Model configuration

| Participant | Default LiteLLM model | Environment variable |
| --- | --- | --- |
| OpenAI | `openai/gpt-4.1-mini` | `OPENAI_MODEL` |
| Claude | `anthropic/claude-haiku-4-5` | `ANTHROPIC_MODEL` |
| Grok | `xai/grok-4.6` | `GROK_MODEL` |
| Local GPT-OSS | `ollama_chat/gpt-oss:20b` | `OLLAMA_MODEL` |

Bare model names or matching `provider/model` names both work. Model availability depends on your account and may change. `OLLAMA_API_BASE` defaults to `http://localhost:11434`.

Set these values in `.env` locally or in **Space variables** on Hugging Face.

## How it works

```text
Topic + selected participants
          |
          v
    Round-robin loop
          |
          +--> LiteLLM --> selected model
          |                   |
          |            reply + usage
          |                   |
          +<-- shared transcript
                              |
                       Gradio + JSON
```

The participant order is OpenAI → Claude → Grok → local model, skipping unchecked entries. Calls run sequentially so each participant can react to the previous speaker. Participants have different prompts: framing the problem, examining tradeoffs, challenging ideas, and focusing on implementation.

The loop sends complete recent turns within a 12,000-character history budget. Each call has a 1,500-token output allowance and a 180-second timeout. There are no automatic retries or hidden fallback calls. Replies that hit the output limit are marked as potentially incomplete. The 140-word instruction is a prompt preference, not a guaranteed limit.

## Real sample conversation

The included [JSON transcript](examples/roundtable.json) is an actual four-provider run from the original notebook experiment. Its topic was:

> Should a beginner build a multi-model roundtable as a first LLM portfolio project?

The discussion raised useful disagreements: start simple, constrain the scope, explain the model choices, and avoid building a demo without a clear purpose. Read the [full sample and observations](examples/README.md).

That run reported **3,231 tokens** and **$0.01029 estimated cloud cost**. It used the older `ollama/` route; this app uses LiteLLM's recommended `ollama_chat/` route. The saved outputs are preserved as received, including imperfect suggestions and replies longer than requested.

## Project structure

```text
model-roundtable/
├── app.py                 # Gradio interface and download handling
├── roundtable.py          # Provider configuration and conversation loop
├── requirements.txt       # Three direct dependencies
├── .env.example           # Configuration template; no real keys
├── examples/
│   ├── README.md          # Sample transcript and observations
│   └── roundtable.json    # Real model replies and usage
└── tests/
    └── test_roundtable.py # Orchestration and failure-path tests
```

## Test

```bash
python -m unittest discover -s tests -v
```

Tests mock provider calls and require no API keys or Ollama server. They cover shared history, validation before paid requests, complete-turn context trimming, empty responses, truncated replies, unknown pricing, partial results, and exports.

## Design choices and limits

This is a learning project for practicing Python, API integration, prompt design, state management, and error handling. LiteLLM keeps the provider-specific code small; the loop is plain Python so it is easy to follow.

- A group discussion does not guarantee correct answers or meaningful consensus. This project has no factual evaluation or voting system.
- Roles are prompts. Changing the role or speaking order can change the outcome.
- Cost figures are estimates based on LiteLLM's pricing data. Unknown prices are shown as unavailable, not zero. Local inference has no provider API fee, but uses your hardware and electricity.
- A mixed cloud/local conversation sends the shared transcript, including local replies, to selected cloud providers. Select only the local participant for local model inference.
- `.env` is ignored by Git. Keys are read by the Python process and are not included in downloads. Use Space secrets for hosted credentials.
- The app binds to `0.0.0.0` for Spaces and containers, with Gradio share links disabled. The hosted Space is publicly accessible; use deployment access controls when enabling paid calls with your keys.
- JSON exports use temporary files on the app server (your machine when running locally). Download results you want to keep; the hosted app does not provide durable conversation storage.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Missing API key | Locally, add the key to `.env`. On Hugging Face, add it under Settings → Variables and secrets → New secret. Reload after restart, or deselect that provider. |
| Authentication or quota error | Check the provider's API key, billing, and rate limits. |
| Model request fails | Confirm the model name and account access; update the corresponding model variable. |
| Local model fails or times out | Locally, run `ollama list` and check the server and model. On a Space, deselect Local GPT-OSS unless a reachable Ollama service is configured. |
| No visible reply | A reasoning model may have used its output budget internally. Try a chat model or increase `max_tokens` in `roundtable.py`. |
| Port 7860 is occupied | Gradio prints the chosen local URL; use that address. |

References: [LiteLLM](https://docs.litellm.ai/), [Gradio](https://www.gradio.app/guides/quickstart), [Ollama integration](https://docs.litellm.ai/docs/providers/ollama).

## Automatic deployment from GitHub

The `Deploy to Hugging Face Spaces` workflow syncs `main` to [the hosted app](https://huggingface.co/spaces/anilvarmakav/model-roundtable) on every push. Add a Hugging Face token with write permission for this Space as the GitHub repository Actions secret `HF_TOKEN`. You can also run the workflow manually from the Actions tab.

The workflow is defined in [`.github/workflows/deploy-space.yml`](https://github.com/anilvarma-kav/model-roundtable/blob/main/.github/workflows/deploy-space.yml). For a fork, change `huggingface_repo_id` to your own Space. It syncs repository files; configure model provider keys separately in Space secrets. The hosted demo uses CPU Basic.

## Related project

[AI Decision Room](https://github.com/anilvarma-kav/ai-decision-room) extends the exploration to parallel role analysis, peer critique, and structured decision memos. [Try its hosted demo](https://huggingface.co/spaces/anilvarmakav/ai-decision-room).
