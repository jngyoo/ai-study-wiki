---
source_id: class5
model: gemma4:e2b
review_status: pending
---

# Retrieval Augmented Generation

Retrieval Augmented Generation (RAG) grounds answers in evidence to reduce hallucinations and allows the use of private knowledge without retraining the model. It works by finding relevant information, providing it as context to the AI.

## Key points

- RAG grounds answers in evidence, meaning the model answers from retrieved documents rather than memory, citing specific information from the source.
- RAG uses private knowledge by retrieving and injecting it into the prompt, avoiding the need for fine-tuning or retraining the model.
- How RAG works involves finding relevant information based on a question, which is then given to the AI as context.
- Chunking splits long documents into smaller, useful passages to keep one idea and its context together before retrieval.

## Sources

- [[Sources/class5#Why RAG Matters|Why RAG Matters]]
- [[Sources/class5#How RAG Works|How RAG Works]]
- [[Sources/class5#Chunking Text|Chunking Text]]
- [[Sources/class5#Vector Databases & Vector Search|Vector Databases & Vector Search]]

## Related notes

- [[Text Embeddings]] — Representations used in vector search
- [[Context Windows]] — Add search results to input context
- [[Model Training]] — Distinguish RAG from weight updates
