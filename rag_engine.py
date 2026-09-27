import os

try:
    import streamlit as st
except ImportError:
    st = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from google import genai
except ImportError as exc:
    raise ImportError(
        "google-genai is not installed. Run: "
        "python -m pip install -U google-genai python-dotenv"
    ) from exc


def get_secret(name, default=""):
    """Read a value from environment variables first, then Streamlit Secrets."""
    value = os.getenv(name, "").strip()
    if value:
        return value

    if st is not None:
        try:
            value = str(st.secrets.get(name, default)).strip()
            if value:
                return value
        except Exception:
            # st.secrets may not exist when running locally without secrets.toml
            pass

    return default


class RAGEngine:
    """Gemini-only answer engine for CampusAI.

    No Ollama, ChromaDB, sentence-transformers, or local FAQ files are used.
    The class keeps the same answer() interface expected by app.py.
    """

    def __init__(self):
        self.gemini_api_key = get_secret("GEMINI_API_KEY")
        self.gemini_model = get_secret(
            "GEMINI_MODEL",
            "gemini-3.5-flash-lite",
        )

        if not self.gemini_api_key:
            raise Exception(
                "GEMINI_API_KEY is missing. "
                "Open Streamlit Cloud -> your app -> Settings -> Secrets "
                "and add GEMINI_API_KEY."
            )

        self.client = genai.Client(api_key=self.gemini_api_key)

        print(f"CampusAI Gemini API enabled: {self.gemini_model}")
        print("Ollama disabled")
        print("ChromaDB disabled")
        print("Local FAQ files disabled")

    def answer(
        self,
        question,
        chat_history=None,
        response_style="detailed",
        user_context=None,
    ):
        if not question or not question.strip():
            return {
                "answer": "Please enter a question.",
                "sources": [],
                "retrieved_chunks": [],
            }

        question = question.strip()

        style_map = {
            "concise": "Be concise and answer in a few clear sentences.",
            "detailed": (
                "Give a clear, useful answer with enough detail "
                "to understand the topic."
            ),
            "balanced": (
                "Give a balanced answer with the key points "
                "and moderate detail."
            ),
        }

        style_instruction = style_map.get(
            str(response_style).lower(),
            style_map["detailed"],
        )

        history_text = ""
        if chat_history:
            lines = []
            for message in chat_history[-8:]:
                role = message.get("role")
                content = message.get("content")
                if role in {"user", "assistant"} and content:
                    lines.append(f"{role.capitalize()}: {content}")

            if lines:
                history_text = (
                    "\n\nRecent conversation:\n"
                    + "\n".join(lines)
                )

        personalization_text = ""
        if user_context:
            personalization_text = (
                f"\n\nUser context:\n{user_context}"
            )

        prompt = f"""
You are CampusAI, a helpful and accurate AI assistant for students.

Answer the user's question using your own Gemini knowledge and reasoning.
Do not use, mention, or depend on any local FAQ, text file, ChromaDB database,
Ollama model, retrieval system, or hidden knowledge-base source.

Never write labels such as:
- User Question:
- Answer:
- According to the Knowledge Base Context:
- A user question has been received...

Do not repeat the user's question before answering.
Do not claim you used a source you did not use.
If you are uncertain about a college-specific fact, clearly say that you are not
certain rather than inventing a specific fact.

Response style:
{style_instruction}
{history_text}
{personalization_text}

Current user question:
{question}

Write only the final answer.
""".strip()

        try:
            response = self.client.models.generate_content(
                model=self.gemini_model,
                contents=prompt,
            )

            answer_text = getattr(response, "text", None)

            if not answer_text:
                raise Exception("Gemini returned an empty response.")

            return {
                "answer": answer_text.strip(),
                "sources": [],
                "retrieved_chunks": [],
            }

        except Exception as exc:
            raise Exception(f"Gemini API error: {exc}") from exc
