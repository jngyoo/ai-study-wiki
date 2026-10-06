---
source_id: class4
model: gemma4:e2b
review_status: pending
---

# Attention and Context

Attention is a mechanism that adjusts word representations based on context, changes how information is combined, and updates the meaning of words.

## Key points

- Context determines meaning, as a single vector for a word, like "bank," must account for different meanings depending on the context.
- Modern models create contextual representations where the vector for a word is adjusted on the fly by the words around it, with attention being the mechanism for this adjustment.
- Attention combines information from available token positions, allowing a recurrent network to connect directly to earlier positions within the context window.
- Attention updates meaning by pulling an embedding toward a specific meaning based on its context, such as "American shrew" pulling "mole" toward the animal direction.

## Sources

- [[Sources/class4#Context Determines Meaning|Context Determines Meaning]]
- [[Sources/class4#Attention Changes the Question|Attention Changes the Question]]
- [[Sources/class4#Attention Updates Meaning|Attention Updates Meaning]]

## Related notes

- [[Text Embeddings]] — Representations used by attention
- [[Context Windows]] — The context available to the model
