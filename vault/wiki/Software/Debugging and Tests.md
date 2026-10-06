---
source_id: class1
model: gemma4:e2b
review_status: pending
---

# Debugging and Tests

Software errors fall into syntax, runtime, and logic errors, and testing is important because logic errors hide without error messages. Debugging follows a hypothesis testing method, and tests turn examples into executable promises.

## Key points

- Syntax errors occur when the code cannot be read, usually due to a missing quote, bracket, colon, or indentation, and the program has not started.
- Runtime errors occur when the code has started but hits a bad situation, such as a missing dictionary key, dividing by zero, or asking for a non-existent file.
- Logic errors are dangerous because the program runs and returns a believable wrong answer without any error message or crash.
- Debugging is hypothesis testing, which involves reproducing behavior, finding the smallest surprising value or branch, stating a hypothesis, changing one thing, and re-running the case, changing only one thing at a time to avoid adding new bugs.

## Sources

- [[Sources/class1#Three Flavors of Broken|Three Flavors of Broken]]
- [[Sources/class1#Debugging is Hypothesis Testing|Debugging is Hypothesis Testing]]
- [[Sources/class1#Tests Turn Examples into Executable Promises|Tests Turn Examples into Executable Promises]]

## Related notes

- [[Programming Basics]] — The building blocks being tested
- [[Model Evaluation]] — Both software and models need evaluation
