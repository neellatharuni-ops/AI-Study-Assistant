
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
                        "text": text
                    }
                )

        except Exception as e:

            print(
                f"Could not read {file_path.name}: {e}"
            )

    return documents


# ============================================================
# SPLIT DOCUMENT INTO CHUNKS
# ============================================================

def create_chunks(
    text,
    chunk_size=1000,
    overlap=200
):

    text = text.strip()

    if not text:

        return []

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        if chunk.strip():

            chunks.append(
                chunk.strip()
            )

        start += chunk_size - overlap

    return chunks


# ============================================================
# BUILD KNOWLEDGE BASE
# ============================================================

def build_knowledge_base():

    documents = load_documents()

    knowledge_base = []

    for document in documents:

        chunks = create_chunks(
            document["text"]
        )

        for chunk in chunks:

            knowledge_base.append(
                {
                    "filename": document["filename"],
                    "text": chunk
                }
            )

    return knowledge_base


# ============================================================
# RETRIEVE RELEVANT STUDY MATERIAL
# ============================================================

def retrieve_context(
    question,
    top_k=3
):

    knowledge_base = build_knowledge_base()

    if not knowledge_base:

        return ""


    documents = [
        item["text"]
        for item in knowledge_base
    ]


    # --------------------------------------------------------
    # TF-IDF VECTOR REPRESENTATION
    # --------------------------------------------------------

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )


    try:

        document_vectors = vectorizer.fit_transform(
            documents
        )

        question_vector = vectorizer.transform(
            [question]
        )

    except ValueError:

        return ""


    # --------------------------------------------------------
    # CALCULATE SIMILARITY
    # --------------------------------------------------------

    similarities = cosine_similarity(
        question_vector,
        document_vectors
    )[0]


    # --------------------------------------------------------
    # GET TOP MATCHES
    # --------------------------------------------------------

    ranked_indices = similarities.argsort()[
        ::-1
    ]


    selected_chunks = []


    for index in ranked_indices[:top_k]:

        score = similarities[index]

        if score <= 0:

            continue

        item = knowledge_base[index]

        selected_chunks.append(
            f"Source: {item['filename']}\n"
            f"{item['text']}"
        )


    # --------------------------------------------------------
    # RETURN CONTEXT
    # --------------------------------------------------------

    if not selected_chunks:

        return ""


    return "\n\n---\n\n".join(
        selected_chunks
    )


# ============================================================
# TEST RAG
# ============================================================

if __name__ == "__main__":

    print()
    print("===================================")
    print("       RAG STUDY MATERIAL TEST")
    print("===================================")
    print()

    question = input(
        "Ask a question about your study material: "
    )


    context = retrieve_context(
        question
    )


    print()
    print("===== RETRIEVED CONTENT =====")
    print()


    if context:

        print(context)

    else:

        print(
            "No relevant study material found."
        )

