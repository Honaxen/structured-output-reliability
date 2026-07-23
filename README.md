# Structured Output Reliability

Work in progress -- this README is a placeholder and will be replaced once the project is complete.

How reliably can an LLM actually produce valid, schema-conforming JSON -- across different prompting strategies, different schema complexities, and with a validation-feedback retry loop when it fails.

---

## What This Project Will Demonstrate

Every project in this portfolio that needs structured output (llm-prompt-optimizer's extraction task, for instance) has quietly handled JSON parsing failures with a try/except and moved on.
This project treats that failure mode as the actual subject: how often does it happen, what makes it worse, and what actually fixes it.

Concern -> Solution (planned)
- Does prompting strategy affect JSON validity rate?         -> Compare plain prompting, few-shot examples, and Ollama's native format=json (grammar-constrained decoding)
- Does schema complexity make failure more likely?            -> Test schemas ranging from flat/simple to deeply nested with arrays
- What happens when the model produces invalid JSON?           -> A retry loop that shows the model its own validation error and asks it to fix it
- How many retries does it actually take, on average?           -> Measured directly, not assumed

---

## Planned Architecture

Schema Dataset (schemas/)                    simple -> nested -> array-heavy, increasing complexity
  -> Strategy Comparison (strategies/)        plain prompt vs few-shot vs native format=json
  -> Retry Loop (retry/)                      validation error fed back to the model, re-attempted
  -> Evaluation (evaluation/)                 first-attempt success rate, post-retry success rate, avg retries needed, broken down by schema complexity

---

## Project Structure

structured-output-reliability/
  schemas/         - JSON schemas of varying complexity + test prompts
  strategies/       - plain / few-shot / native format=json generation
  retry/            - validation-feedback retry loop
  evaluation/        - success rate measurement, broken down by strategy and complexity
  tests/
  docs/

---

## Stack

Python - Ollama - jsonschema - pytest

---

## Status

- [ ] Schema dataset (varying complexity)
- [ ] Strategy comparison (plain, few-shot, native format=json)
- [ ] Validation-feedback retry loop
- [ ] Success rate evaluation by strategy and complexity

---

## Related Projects

- [llm-prompt-optimizer](https://github.com/Honaxen/llm-prompt-optimizer) -- where a JSON-format instruction was already found to be the single biggest driver of eval score; this project studies that failure mode directly
- [llm-eval-statistics](https://github.com/Honaxen/llm-eval-statistics) -- same emphasis on measuring rather than assuming, applied to output reliability instead of eval significance

---

## Author

[Honaxen](https://github.com/Honaxen)
