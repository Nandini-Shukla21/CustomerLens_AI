from __future__ import annotations

import json
import uuid
from fastapi import APIRouter, Depends, HTTPException

from app.api.platform import (
    build_rag_context,
    document_embeddings,
    generate_rag_answer,
    structured_answer,
)
from app.config import settings
from app.core.security import current_user
from app.core.storage import connection

router = APIRouter()


@router.post("/rag/query")
def rag_query(body: dict[str, str], user: dict = Depends(current_user)):
    q = body.get("question", "").strip()
    dataset_id = body.get("dataset_id")

    if not q:
        raise HTTPException(422, "question is required")

    analytical = structured_answer(q, user["sub"], dataset_id=dataset_id)

    if analytical:
        with connection() as conn:
            conn.execute(
                "INSERT INTO chat_history("
                "id,user_id,question,answer,sources_json,confidence"
                ") VALUES(?,?,?,?,?,?)",
                (
                    str(uuid.uuid4()),
                    user["sub"],
                    q,
                    analytical["answer"],
                    json.dumps(analytical["sources"]),
                    analytical["confidence"],
                ),
            )

        return analytical

    matches = []

    try:
        matches = document_embeddings().similarity_search(
            q,
            top_k=5,
            owner_id=user["sub"],
        )
    except Exception as exc:
        raise HTTPException(
            503,
            f"Document retrieval is unavailable: {exc}",
        ) from exc

    if not matches:
        return {
            "answer": (
                "No information exists in the uploaded "
                "documents relevant to this question."
            ),
            "confidence": 0.0,
            "sources": [],
            "citations": [],
            "chunks": [],
            "filename": None,
            "retrieved_chunks": 0,
            "similarity_score": 0.0,
        }

    context = build_rag_context(matches)
    answer = context[:4000]

    if settings.groq_api_key:
        try:
            answer = generate_rag_answer(q, context)
        except Exception:
            answer = (
                "I couldn't find enough information in the "
                "uploaded documents to answer this question."
            )

    confidence = round(
        sum(m.get("score", 0.0) for m in matches) / len(matches),
        2,
    )

    safe_matches = [
        document_embeddings().normalize_match(m)
        for m in matches
    ]

    best_match = safe_matches[0] if safe_matches else None

    citations = [
        {
            "filename": m["filename"],
            "chunk_id": m["chunk_id"],
            "document_id": m["document_id"],
        }
        for m in safe_matches
    ]

    sources = list(
        dict.fromkeys(
            f"{m['filename']} ({m['chunk_id']})"
            for m in safe_matches
        )
    )

    with connection() as conn:
        conn.execute(
            "INSERT INTO chat_history("
            "id,user_id,question,answer,sources_json,confidence"
            ") VALUES(?,?,?,?,?,?)",
            (
                str(uuid.uuid4()),
                user["sub"],
                q,
                answer,
                json.dumps(sources),
                confidence,
            ),
        )

    return {
        "answer": answer,
        "confidence": confidence,
        "sources": sources,
        "citations": citations,
        "chunks": [
            {
                "document_id": m["document_id"],
                "chunk_id": m["chunk_id"],
                "filename": m["filename"],
                "score": round(m["score"], 3),
            }
            for m in safe_matches
        ],
        "filename": best_match.get("filename") if best_match else None,
        "retrieved_chunks": len(matches),
        "similarity_score": (
            round(best_match.get("score", 0.0), 3)
            if best_match
            else 0.0
        ),
    }
