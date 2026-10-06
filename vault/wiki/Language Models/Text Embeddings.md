---
source_id: class4
model: gemma4:e2b
review_status: pending
---

# Text Embeddings

A word embedding is a learned vector of numbers that represents a word or token, allowing words with similar contexts to have similar embeddings. The distance between these vectors reflects the semantic similarity between the words.

## Key points

- An embedding is a learned vector (a list of numbers) that represents a word or token, which is adjusted during training to help the model make predictions.
- Word2Vec learned that words in similar contexts receive similar vectors, causing words with similar meanings to cluster together in vector space.
- The distance between word vectors reflects meaning; nearby vectors indicate related meanings, such as 'dog' and 'puppy' being closer than 'dog' and 'airplane'.
- The model learned concepts like gender as directions in vector space without explicit teaching.

## Sources

- [[Sources/class4#The Problem: Words Aren’t Numbers|The Problem: Words Aren’t Numbers]]
- [[Sources/class4#Words as Points in Space|Words as Points in Space]]
- [[Sources/class4#Distance Reflects Meaning|Distance Reflects Meaning]]

## Related notes

- [[Attention and Context]] — How context changes word representations
- [[Retrieval Augmented Generation]] — Vector representations for finding relevant passages
