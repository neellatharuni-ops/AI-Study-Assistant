import os
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# STUDY MATERIALS DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MATERIALS_DIR = BASE_DIR / "study_materials"


# ============================================================
# LOAD STUDY MATERIALS
# ============================================================

def load_documents():

    documents = []

    if not MATERIALS_DIR.exists():

        return documents

    for file_path in MATERIALS_DIR.glob("*.txt"):

        try:

            text = file_path.read_text(
                encoding="utf-8"
            )

            if text.strip():

                documents.append(
                    {
                        "filename": file_path.name,
                        "content": text
                    }
                )

        except Exception as e:

            print(
                f"Could not read {file_path}: {e}"
            )

    return documents


# ============================================================
# RETRIEVE RELEVANT CONTENT
# ============================================================

def retrieve_relevant_content(
    query,
    top_k=2
):

    documents = load_documents()

    if not documents:

        return (
            "No study materials were found."
        )

    texts = [
        document["content"]
        for document in documents
    ]

    # Create TF-IDF representation
    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    try:

        document_vectors = vectorizer.fit_transform(
            texts
        )

        query_vector = vectorizer.transform(
            [query]
        )

    except ValueError:

        return (
            "Unable to process the study materials."
        )

    # Calculate similarity
    similarities = cosine_similarity(
        query_vector,
        document_vectors
    )[0]

    # Get best matching documents
    ranked_indices = similarities.argsort()[
        ::-1
    ]

    results = []

    for index in ranked_indices[:top_k]:

        if similarities[index] <= 0:

            continue

        results.append(
            {
                "filename": documents[index]["filename"],
                "content": documents[index]["content"],
                "score": similarities[index]
            }
        )

    if not results:

        return (
            "No relevant content was found "
            "in your study materials."
        )

    # Format retrieved content
    output = []

    for result in results:

        output.append(
            f"""
===== {result["filename"]} =====

{result["content"]}
"""
        )

    return "\n".join(output)


# ============================================================
# RAG CONTEXT
# ============================================================

def get_rag_context(
    query,
    top_k=2
):

    documents = load_documents()

    if not documents:

        return ""

    texts = [
        document["content"]
        for document in documents
    ]

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    try:

        document_vectors = vectorizer.fit_transform(
            texts
        )

        query_vector = vectorizer.transform(
            [query]
        )

    except ValueError:

        return ""

    similarities = cosine_similarity(
        query_vector,
        document_vectors
    )[0]

    ranked_indices = similarities.argsort()[
        ::-1
    ]

    selected = []

    for index in ranked_indices[:top_k]:

        if similarities[index] > 0:

            selected.append(
                documents[index]["content"]
            )

    return "\n\n".join(selected)


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 50)
    print("           RAG STUDY SEARCH")
    print("=" * 50)
    print()

    question = input(
        "Ask a question about your study material: "
    )

    result = retrieve_relevant_content(
        question
    )

    print()
    print("===== RETRIEVED CONTENT =====")
    print()
    print(result)