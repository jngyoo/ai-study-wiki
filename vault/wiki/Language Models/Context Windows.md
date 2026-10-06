---
source_id: class5
model: gemma4:e2b
review_status: pending
---

# Context Windows

A context window is the maximum amount of information, including messages and replies, a model can hold at once. Increasing the context window does not automatically improve performance and introduces costs and latency.

## Key points

- The context window is the space where your messages and the model's replies share space.
- Bigger context is not a free solution because it raises cost, increases latency, and may cause the model to miss or contradict important evidence.
- The model only sees the active context and does not have durable memory of previous chats unless relevant information is deliberately resent.
- System instructions and durable project files are better places for rules than long casual conversations because they survive compaction and new chats.

## Sources

- [[Sources/class5#What Is a Context Window?|What Is a Context Window?]]
- [[Sources/class5#Bigger Context Is Not a Free Solution|Bigger Context Is Not a Free Solution]]
- [[Sources/class5#Context Rot Is Real|Context Rot Is Real]]
- [[Sources/class5#Put Stable Rules in Stable Places|Put Stable Rules in Stable Places]]

## Related notes

- [[Attention and Context]] — How models use context
- [[Retrieval Augmented Generation]] — Supply relevant passages as context
