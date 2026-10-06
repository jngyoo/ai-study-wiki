---
source_id: class3
model: gemma4:e2b
review_status: pending
---

# Model Training

A model has adjustable parameters that are chosen during training to fit historical examples, and inference uses these fitted parameters to make predictions. Training involves minimizing a loss measure, often using gradient descent to update the parameters.

## Key points

- A model has adjustable parameters, such as the slope ($w$) and intercept ($b$) in the equation $	ext{predicted revenue} = w 	imes 	ext{ad spend} + b$.
- Training chooses parameter values that fit historical examples.
- Loss measures prediction error, and training tries to reduce this average error, where squaring makes large misses count more.
- Gradient Descent updates the parameters by moving them downhill on a loss curve, using the gradient to determine the direction and the learning rate to control the step size.

## Sources

- [[Sources/class3#A Model Has Adjustable Parameters|A Model Has Adjustable Parameters]]
- [[Sources/class3#Loss Measures Prediction Error|Loss Measures Prediction Error]]
- [[Sources/class3#Gradient Descent Updates the Parameters|Gradient Descent Updates the Parameters]]
- [[Sources/class3#Training and Inference Use Different Information|Training and Inference Use Different Information]]

## Related notes

- [[Model Evaluation]] — Evaluate generalization after training
- [[Text Embeddings]] — Learned numerical representations
- [[Retrieval Augmented Generation]] — Retraining versus adding retrieved context
