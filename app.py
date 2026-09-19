"""Run with `python app.py` and open http://127.0.0.1:7860."""

import os
import tempfile

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")

import gradio as gr

from roundtable import (
    ConversationError, api_key, configured_participants, export_conversation,
    generate_conversation, load_sample, transcript_markdown, usage_summary,
)


def run_discussion(topic, names, rounds):
    participants = [p for p in configured_participants() if p.name in (names or [])]
    turns = []
    yield "", "Starting conversation…", None
    try:
        for turn in generate_conversation(topic, participants, int(rounds)):
            turns.append(turn)
            yield transcript_markdown(topic, turns), usage_summary(turns), None
    except ConversationError as exc:
        status = f"Stopped: {exc}\n\n{usage_summary(turns)}"
    else:
        status = "Complete. " + usage_summary(turns)
    output = None
    if turns:
        output = export_conversation(topic, turns, tempfile.mkdtemp(prefix="roundtable-"))
    yield transcript_markdown(topic, turns) if turns else "", status, output


def show_sample():
    topic, turns = load_sample()
    output = export_conversation(topic, turns, tempfile.mkdtemp(prefix="roundtable-sample-"))
    return (topic, transcript_markdown(topic, turns),
            "Saved sample — no new API calls. " + usage_summary(turns), output)


def build_app():
    participants = configured_participants()
    default = [p.name for p in participants if p.key_env and api_key(p)]
    model_list = "\n".join(f"- **{p.name}:** `{p.model}`" for p in participants)
    with gr.Blocks(title="Model Roundtable", theme=gr.themes.Soft(primary_hue="teal"),
                   css=".gradio-container {max-width: 1080px !important; margin: auto}") as demo:
        gr.Markdown("# Model Roundtable\nOne topic. Four perspectives. A conversation across cloud and local models.")
        with gr.Row():
            with gr.Column(scale=1):
                topic = gr.Textbox(label="Discussion topic", lines=4,
                                   value="What makes a small LLM project useful?", max_length=2000)
                names = gr.CheckboxGroup(label="Participants", choices=[p.name for p in participants],
                                         value=default,
                                         info="Replies follow this order. Select local only for an Ollama run.")
                rounds = gr.Slider(1, 3, value=1, step=1, label="Rounds",
                                   info="Each selected participant speaks once per round.")
                run = gr.Button("Start conversation", variant="primary")
                sample = gr.Button("Load saved demo · no API calls")
                with gr.Accordion("Models and setup", open=False):
                    gr.Markdown(model_list + "\n\nChange models in `.env` and restart the app. "
                                "Cloud participants require API keys. Start Ollama before selecting Local GPT-OSS.")
                gr.Markdown("Cloud models receive the topic and shared transcript, including local replies. "
                            "Cost estimates exclude local electricity and hardware.")
            with gr.Column(scale=2):
                status = gr.Markdown("Choose a topic and participants, or load the saved demo.")
                transcript = gr.Markdown()
                download = gr.File(label="Download conversation (JSON)", interactive=False)
        outputs = [transcript, status, download]
        run.click(run_discussion, [topic, names, rounds], outputs,
                  concurrency_id="conversation", concurrency_limit=1)
        sample.click(show_sample, outputs=[topic, *outputs],
                     concurrency_id="conversation", concurrency_limit=1)
    return demo


if __name__ == "__main__":
    build_app().queue().launch(server_name="127.0.0.1", share=False)
