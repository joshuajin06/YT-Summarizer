from services.summarizer import _complete

GENERATION_PROMPT = (
  "You answer questions about a YouTube video using only the transcript "
  "excerpts provided below. Each excerpt is labeled with its timestamp in "
  "[MM:SS] format. Cite the timestamp(s) you drew on in your answer using "
  "the same [MM:SS] format. If the excerpts don't contain enough "
  "information to answer, say so — do not use outside knowledge."
)

NO_CONTEXT_ANSWER = "I don't have any indexed transcript content to answer that from."


def _format_timestamp(seconds):
  minutes, secs = divmod(int(seconds), 60)
  return f"{minutes:02d}:{secs:02d}"


def _format_chunks(chunks):
  return "\n\n".join(
    f"[{_format_timestamp(c['start'])}] {c['text']}" for c in chunks
  )


def answer_question(question, chunks):
  if not chunks:
    return NO_CONTEXT_ANSWER
  user_content = f"Transcript Contents:\n{_format_chunks(chunks)}\n\nQuestion: {question}"
  return _complete(GENERATION_PROMPT, user_content)
