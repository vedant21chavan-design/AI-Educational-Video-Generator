from member2.decomposer.llm import generate_content


prompt = """
Return JSON with exactly one field called "message".

The value should explain Newton's First Law
in one simple sentence.
"""


result = generate_content(prompt)

print("\nLLM RESPONSE:\n")
print(result)