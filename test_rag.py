from rag import retrieve_context

question = input(
    "Ask a question about your study material: "
)

context = retrieve_context(question)

print("\n===== RETRIEVED CONTENT =====\n")

print(context)