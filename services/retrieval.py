from services.embeddings import embed_text
from services.transcript import extract_video_id
from services.vector_store import search


def retrieve(url, question, top_k=5):
  video_id = extract_video_id(url)
  question_embedding = embed_text(question)
  return search(video_id, question_embedding, top_k)
