import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ==========================================
# LOAD STUDY MATERIAL
# ==========================================

def load_documents():

    documents = []

    folder = "study_materials"

    for filename in os.listdir(folder):

        if filename.endswith(".txt"):

            path = os.path.join(folder, filename)

            with open(path, "r", encoding="utf-8") as file:

                text = file.read()

                documents.append({
                    "filename": filename,
                    "text": text
                })

    return documents


# ==========================================
# SPLIT TEXT INTO CHUNKS
# ==========================================

def create_chunks(text, chunk_size=500):

    words = text.split()

    chunks = []

    for i in range(0, len(words), chunk_size):

        chunk = " ".join(
            words[i:i + chunk_size]
        )

        chunks.append(chunk)

    return chunks


# ==========================================
# CREATE ALL CHUNKS
# ==========================================

def get_all_chunks():

    documents = load_documents()

    chunks = []

    for document in documents:

        document_chunks = create_chunks(
            document["text"]
        )

        for chunk in document_chunks:

            chunks.append({
                "filename": document["filename"],
                "text": chunk
            })

    return chunks


# ==========================================
# RETRIEVE RELEVANT CHUNKS
# ==========================================

def retrieve_context(question, top_k=3):

    chunks = get_all_chunks()

    if not chunks:
        return ""

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    vectors = vectorizer.fit_transform(
        texts + [question]
    )

    similarities = cosine_similarity(
        vectors[-1],
        vectors[:-1]
    )[0]

    ranked_indices = similarities.argsort()[::-1]

    selected_chunks = []

    for index in ranked_indices[:top_k]:

        if similarities[index] > 0:

           selected_chunks.append(
    f"[Source: {chunks[index]['filename']}]\n"
    f"{chunks[index]['text']}"
)

    return "\n\n".join(
        selected_chunks
    )