---
source_id: class3
model: gemma4:e2b
review_status: pending
---

# Model Evaluation

It is crucial to keep a test set separate from the development process to ensure that model evaluation reflects future performance accurately. The process should involve separating fitting, choosing, and testing steps to avoid letting the test score guide development.

## Key points

- Keep a Test Set Outside Development: The final test set should remain untouched until choices are fixed, as changing the model after seeing its test score allows that score to guide development.
- Separate Fitting, Choosing, and Testing: Training data, validation data, and test data should be kept separate for fitting, choosing model settings, and estimating final performance.
- Overfitting vs. Underfitting: Overfitting occurs when a model fits noise along with the signal from the training details, whereas underfitting means the model is too limited to capture the pattern.
- Data Handling: Keep related records together when necessary, as near-duplicate images from the same person in both sets can make the score misleading.

## Sources

- [[Sources/class3#Keep a Test Set Outside Development|Keep a Test Set Outside Development]]
- [[Sources/class3#Separate Fitting, Choosing, and Testing|Separate Fitting, Choosing, and Testing]]
- [[Sources/class3#Overfitting Fits Noise Along With Signal|Overfitting Fits Noise Along With Signal]]

## Related notes

- [[Model Training]] — Separate training from validation
- [[Debugging and Tests]] — Compare expected and actual results
