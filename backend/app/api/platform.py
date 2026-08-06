from __future__ import annotations
import hashlib, json, math, re, uuid
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any
import pandas as pd
from io import BytesIO
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from app.config import settings
from app.core.security import current_user
from app.core.storage import connection, decode_json, row_dict
from app.rag.parser import DocumentParser
from app.rag.chunker import DocumentChunker
from app.services.embedding_service import EmbeddingService
from app.services.groq_service import GroqService
from loguru import logger

router = APIRouter()


@lru_cache(maxsize=1)
def document_embeddings() -> EmbeddingService:
    """One persistent Chroma/SentenceTransformers service per API process."""
    return EmbeddingService()


def build_rag_context(matches: list[dict[str, Any]]) -> str:
    """Build a robust RAG context from retrieval hits that may contain legacy metadata."""
    safe_matches = [document_embeddings().normalize_match(match) for match in matches or []]
    context_parts: list[str] = []
    for match in safe_matches:
        text = str(match.get("text") or "").strip()
        if not text:
            continue
        filename = str(match.get("filename") or "<missing-filename>").strip() or "<missing-filename>"
        chunk_id = str(match.get("chunk_id") or "<missing-chunk-id>").strip() or "<missing-chunk-id>"
        context_parts.append(f"[{filename} | {chunk_id}] {text}")
    return "\n\n".join(context_parts)


def norm(columns: list[str], names: list[str]) -> str | None:
    lowered = {str(c).lower().replace(" ", "_"): str(c) for c in columns}
    return next((lowered[n] for n in names if n in lowered), None)
def load_dataset(dataset_id: str, owner_id: str | None = None) -> tuple[dict[str, Any], pd.DataFrame]:
    with connection() as conn:
        row = row_dict(conn.execute("SELECT * FROM datasets WHERE id=?" + (" AND owner_id=?" if owner_id else ""), (dataset_id, owner_id) if owner_id else (dataset_id,)).fetchone())
    if not row: raise HTTPException(404, "Dataset not found")
    try: return row, pd.read_csv(row["path"])
    except Exception as exc: raise HTTPException(500, "Dataset file cannot be read") from exc
def metrics(df: pd.DataFrame) -> dict[str, Any]:
    revenue = norm(list(df.columns), ["revenue", "amount", "sales", "total_amount", "spend"])
    customer = norm(list(df.columns), ["customer_id", "id", "email"])
    churn = norm(list(df.columns), ["churn", "churn_score"])
    risk = norm(list(df.columns), ["risk", "risk_score"])
    ltv = norm(list(df.columns), ["ltv", "lifetime_value"])
    return {"total_customers": int(df[customer].nunique()) if customer else int(len(df)), "revenue": float(pd.to_numeric(df[revenue], errors="coerce").fillna(0).sum()) if revenue else 0, "transactions": int(len(df)), "predicted_churn": int((pd.to_numeric(df[churn], errors="coerce").fillna(0) >= .5).sum()) if churn else 0, "high_risk_customers": int((pd.to_numeric(df[risk], errors="coerce").fillna(0) >= .6).sum()) if risk else 0, "average_lifetime_value": float(pd.to_numeric(df[ltv], errors="coerce").mean()) if ltv else 0, "average_revenue": float(pd.to_numeric(df[revenue], errors="coerce").mean()) if revenue else 0}

def live_insights(frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Generate UI-ready insights only from columns available in uploaded data."""
    if frame.empty:
        return []
    result = metrics(frame)
    items = [{"title": "Dataset is ready for analysis", "description": f"{result['total_customers']:,} uploaded customer records are available.", "priority": "info", "confidence": 1.0, "action": "Open Customer 360 to explore uploaded customers."}]
    if result["high_risk_customers"]:
        items.append({"title": "High-risk customers detected", "description": f"{result['high_risk_customers']:,} records meet the uploaded risk-score threshold.", "priority": "high", "confidence": .9, "action": "Review these customers and run a prediction."})
    if result["predicted_churn"]:
        items.append({"title": "Churn signals detected", "description": f"{result['predicted_churn']:,} records have a churn score of 0.5 or higher.", "priority": "high", "confidence": .9, "action": "Prioritize retention outreach for the affected customers."})
    if result["revenue"]:
        items.append({"title": "Revenue available", "description": f"Uploaded records total ${result['revenue']:,.2f} in revenue.", "priority": "medium", "confidence": .95, "action": "Use Analytics to inspect revenue trends."})
    return items

def structured_answer(question: str, user_id: str) -> dict[str, Any] | None:
    """Answer common analytical questions directly from the user's data, never from an LLM."""
    text=question.lower()
    structured_words=("revenue","sales","average","highest","top customer","customer count","how many customer","churn","risk","segment","trend","distribution","show customer","find customer")
    if not any(word in text for word in structured_words): return None
    with connection() as conn: rows=conn.execute("SELECT id,filename,path FROM datasets WHERE owner_id=?",(user_id,)).fetchall()
    frames=[]; names=[]
    for row in rows:
        try: frames.append(pd.read_csv(row["path"])); names.append(row["filename"])
        except Exception: continue
    if not frames: return {"answer":"No uploaded structured dataset is available yet.","sources":[],"confidence":0.0}
    frame=pd.concat(frames,ignore_index=True); revenue=norm(list(frame.columns),["revenue","amount","sales","total_amount","spend"]); name=norm(list(frame.columns),["name","customer_name","customer_id","email"]); churn=norm(list(frame.columns),["churn","churn_score"]); risk=norm(list(frame.columns),["risk","risk_score"]); segment=norm(list(frame.columns),["segment","customer_segment"])
    if "customer count" in text or "how many customer" in text: answer=f"There are {len(frame):,} uploaded customer records."
    elif ("highest" in text or "top" in text) and revenue:
        ranked=frame.assign(_revenue=pd.to_numeric(frame[revenue],errors="coerce").fillna(0)).sort_values("_revenue",ascending=False).head(5); label=name or "_revenue"; answer="Top revenue customers: " + "; ".join(f"{r[label]} (${r['_revenue']:,.2f})" for _,r in ranked.iterrows())
    elif "average" in text and revenue: answer=f"Average {revenue} is ${pd.to_numeric(frame[revenue],errors='coerce').mean():,.2f}."
    elif "average" in text and churn: answer=f"Average {churn} is {pd.to_numeric(frame[churn],errors='coerce').mean():.2%}."
    elif "risk" in text and risk: answer=f"{int((pd.to_numeric(frame[risk],errors='coerce').fillna(0)>=.6).sum()):,} records have a high risk score (>= 0.60)."
    elif "churn" in text and churn: answer=f"{int((pd.to_numeric(frame[churn],errors='coerce').fillna(0)>=.5).sum()):,} records have a churn score of 0.50 or above."
    elif "segment" in text and segment: answer="Segment distribution: " + ", ".join(f"{k}: {v}" for k,v in frame[segment].fillna("Unknown").value_counts().items())
    elif "show customer" in text or "find customer" in text:
        query=re.sub(r".*?(?:show|find) customer\s+", "", text).strip(); matches=frame[frame.astype(str).apply(lambda c:c.str.lower().str.contains(query,na=False)).any(axis=1)].head(10); answer="Matching customers: " + ("; ".join(str(row.to_dict()) for _,row in matches.iterrows()) if not matches.empty else "none found.")
    elif revenue: answer=f"Uploaded data contains {len(frame):,} records with total {revenue} of ${pd.to_numeric(frame[revenue],errors='coerce').fillna(0).sum():,.2f}."
    else: answer=f"Uploaded datasets contain {len(frame):,} records and columns: {', '.join(map(str,frame.columns))}."
    return {"answer":answer,"sources":names,"confidence":0.98}

@router.post("/datasets", status_code=201)
async def upload_dataset(file: UploadFile = File(...), user: dict = Depends(current_user)):
    if not file.filename or Path(file.filename).suffix.lower() not in {".csv", ".json", ".xlsx", ".xls"}: raise HTTPException(422, "Supported dataset files: CSV, JSON, XLSX, XLS")
    data = await file.read()
    if not data: raise HTTPException(422, "Uploaded file is empty")
    dataset_id = str(uuid.uuid4()); directory = Path(settings.upload_dir) / "datasets"; directory.mkdir(parents=True, exist_ok=True); path = directory / f"{dataset_id}.csv"
    source = Path(file.filename).suffix.lower()
    try:
        from io import BytesIO
        frame = pd.read_csv(BytesIO(data)) if source == ".csv" else (pd.read_json(BytesIO(data)) if source == ".json" else pd.read_excel(BytesIO(data)))
    except Exception as exc: raise HTTPException(422, f"Unable to parse dataset: {exc}") from exc
    frame.to_csv(path, index=False); summary = {"missing_values": {str(k): int(v) for k,v in frame.isna().sum().items()}, "data_types": {str(k): str(v) for k,v in frame.dtypes.items()}, "quality_score": round(100 * (1 - frame.isna().sum().sum() / max(1, frame.size)), 2)}
    with connection() as conn:
        conn.execute("INSERT INTO datasets(id,filename,path,rows,columns,schema_json,summary_json,owner_id) VALUES(?,?,?,?,?,?,?,?)", (dataset_id,file.filename,str(path),len(frame),len(frame.columns),json.dumps(list(map(str,frame.columns))),json.dumps(summary),user["sub"]))
        customer_id=norm(list(frame.columns), ["customer_id", "id", "email"]); name=norm(list(frame.columns), ["name", "customer_name"]); email=norm(list(frame.columns), ["email"]); phone=norm(list(frame.columns), ["phone", "phone_number"]); rev=norm(list(frame.columns), ["revenue", "amount", "sales"]); tx=norm(list(frame.columns), ["transactions", "transaction_count"]); ltv=norm(list(frame.columns), ["ltv", "lifetime_value"]); risk=norm(list(frame.columns), ["risk", "risk_score"]); churn=norm(list(frame.columns), ["churn", "churn_score"])
        for i,row in frame.iterrows():
            cid=str(row[customer_id]) if customer_id and pd.notna(row[customer_id]) else f"{dataset_id}:{i}"
            value=lambda col: float(pd.to_numeric(pd.Series([row[col]]),errors='coerce').fillna(0).iloc[0]) if col else 0
            conn.execute("INSERT OR REPLACE INTO customers VALUES(?,?,?,?,?,?,?,?,?,?,?)", (cid,dataset_id,json.dumps({str(k):(None if pd.isna(v) else str(v)) for k,v in row.items()}),str(row[name]) if name and pd.notna(row[name]) else cid,str(row[email]) if email and pd.notna(row[email]) else None,str(row[phone]) if phone and pd.notna(row[phone]) else None,value(rev),value(tx),value(ltv),value(risk),value(churn)))
        conn.execute("INSERT INTO uploads(id,dataset_id,owner_id,filename,file_type,size_bytes,status) VALUES(?,?,?,?,?,?,?)",(str(uuid.uuid4()),dataset_id,user["sub"],file.filename,source,len(data),"ready"))
    return {"dataset_id":dataset_id,"filename":file.filename,"row_count":len(frame),"column_count":len(frame.columns),"columns":list(map(str,frame.columns)),**summary}

@router.get("/datasets")
def datasets(user: dict = Depends(current_user)):
    with connection() as conn: return [dict(r) for r in conn.execute("SELECT id,filename,rows,columns,created_at FROM datasets WHERE owner_id=? ORDER BY created_at DESC",(user["sub"],))]
@router.get("/uploads")
def upload_history(user: dict = Depends(current_user)):
    with connection() as conn:
        return [dict(row) for row in conn.execute("SELECT id,dataset_id,document_id,filename,file_type,size_bytes,status,created_at FROM uploads WHERE owner_id=? ORDER BY created_at DESC",(user["sub"],))]
@router.get("/datasets/{dataset_id}/summary")
def dataset_summary(dataset_id: str, user: dict = Depends(current_user)):
    row,frame=load_dataset(dataset_id, user["sub"]); return {"dataset_id":dataset_id,"filename":row["filename"],"rows":row["rows"],"columns":row["columns"],**decode_json(row["summary_json"],{})}
@router.get("/datasets/{dataset_id}/columns")
def dataset_columns(dataset_id: str, user: dict = Depends(current_user)):
    _,frame=load_dataset(dataset_id, user["sub"]); return [{"name":str(c),"type":str(frame[c].dtype),"missing":int(frame[c].isna().sum()),"unique":int(frame[c].nunique())} for c in frame.columns]
@router.get("/datasets/{dataset_id}/preview")
def dataset_preview(dataset_id: str, offset: int=0, limit:int=Query(25,le=200), q:str="", user: dict = Depends(current_user)):
    _,frame=load_dataset(dataset_id, user["sub"]); filtered=frame[frame.astype(str).apply(lambda c:c.str.contains(q,case=False,na=False)).any(axis=1)] if q else frame; return {"total":len(filtered),"rows":filtered.iloc[offset:offset+limit].where(filtered.notna(),None).to_dict(orient="records")}
@router.get("/datasets/{dataset_id}")
def dataset(dataset_id: str, user: dict = Depends(current_user)): return dataset_summary(dataset_id,user)
@router.delete("/datasets/{dataset_id}", status_code=204)
def delete_dataset(dataset_id: str, user: dict = Depends(current_user)):
    row,_=load_dataset(dataset_id, user["sub"])
    with connection() as conn: conn.execute("DELETE FROM datasets WHERE id=?",(dataset_id,))
    Path(row["path"]).unlink(missing_ok=True)

@router.get("/dashboard")
def dashboard(user: dict = Depends(current_user)):
    with connection() as conn: rows=conn.execute("SELECT * FROM datasets WHERE owner_id=? ORDER BY created_at DESC",(user["sub"],)).fetchall(); uploads=[dict(r) for r in conn.execute("SELECT filename,status,created_at FROM uploads ORDER BY created_at DESC LIMIT 5").fetchall()]
    frames=[]
    for row in rows:
        try: frames.append(pd.read_csv(row["path"]))
        except Exception: continue
    frame=pd.concat(frames,ignore_index=True) if frames else pd.DataFrame(); result=metrics(frame) if not frame.empty else metrics(pd.DataFrame())
    segment=norm(list(frame.columns),["segment","customer_segment"]); risk=norm(list(frame.columns),["risk","risk_score"]); date=norm(list(frame.columns),["date","transaction_date","created_at"]); revenue=norm(list(frame.columns),["revenue","amount","sales"])
    result.update({"datasets":len(rows),"documents":0,"recent_uploads":uploads,"segment_distribution":([{ "name":str(k),"value":int(v)} for k,v in frame[segment].fillna("Unknown").value_counts().items()] if segment else []),"risk_distribution":([{ "name":str(k),"value":int(v)} for k,v in pd.cut(pd.to_numeric(frame[risk],errors='coerce').fillna(0),[-1,.3,.6,1],labels=["Low","Medium","High"]).value_counts().items()] if risk else []),"revenue_trend":[], "ai_insights": live_insights(frame)})
    if date and revenue:
        tmp=pd.DataFrame({"date":pd.to_datetime(frame[date],errors="coerce"),"revenue":pd.to_numeric(frame[revenue],errors="coerce").fillna(0)}).dropna(); result["revenue_trend"]=[{"period":str(k),"revenue":float(v)} for k,v in tmp.groupby(tmp.date.dt.to_period("M"))["revenue"].sum().items()]
    return result

@router.get("/customers")
def customers(q: str = "", limit: int = Query(50, le=200), user: dict = Depends(current_user)):
    with connection() as conn:
        sql="SELECT c.* FROM customers c JOIN datasets d ON c.dataset_id=d.id WHERE d.owner_id=?"; args=[user["sub"]]
        if q: sql += " AND (c.id LIKE ? OR c.name LIKE ? OR c.email LIKE ? OR c.phone LIKE ?)"; args += [f"%{q}%"]*4
        rows=conn.execute(sql+" LIMIT ?",(*args,limit)).fetchall()
    return [{**dict(r),"payload":decode_json(r["payload_json"],{})} for r in rows]
@router.get("/customers/search")
def customer_search(q: str, user: dict = Depends(current_user)): return customers(q,50,user)
@router.get("/customers/{customer_id}")
def customer(customer_id: str, user: dict = Depends(current_user)):
    records=customers(customer_id,200,user); item=next((r for r in records if r["id"]==customer_id),None)
    if not item: raise HTTPException(404,"Customer not found")
    return {"profile":item,"revenue":item["revenue"],"transactions":item["transactions"],"lifetime_value":item["ltv"],"risk_score":item["risk"],"churn_score":item["churn"],"complaint_history":[],"purchase_timeline":[],"ai_summary":f"Customer risk is {'high' if item['risk'] >= .6 else 'low'} based on values present in the uploaded dataset."}

@router.get("/analytics")
def analytics(dataset_id: str | None = None, user: dict = Depends(current_user)):
    if dataset_id: _,frame=load_dataset(dataset_id)
    else:
        with connection() as conn: row=conn.execute("SELECT id FROM datasets WHERE owner_id=? ORDER BY created_at DESC LIMIT 1",(user["sub"],)).fetchone()
        frame=load_dataset(row["id"])[1] if row else pd.DataFrame()
    segment=norm(list(frame.columns), ["segment", "customer_segment"])
    revenue=norm(list(frame.columns), ["revenue", "amount", "sales", "total_amount", "spend"])
    date=norm(list(frame.columns), ["date", "transaction_date", "created_at"])
    trends=[]
    if date and revenue:
        tmp=pd.DataFrame({"date":pd.to_datetime(frame[date],errors="coerce"),"revenue":pd.to_numeric(frame[revenue],errors="coerce").fillna(0)}).dropna()
        trends=[{"period":str(k),"revenue":float(v)} for k,v in tmp.groupby(tmp.date.dt.to_period("M"))["revenue"].sum().items()]
    return {"kpis":metrics(frame),"columns":list(map(str,frame.columns)),"records":len(frame),"revenue_trend":trends,"segments":[{"name":str(k),"value":int(v)} for k,v in frame[segment].fillna("Unknown").value_counts().items()] if segment else []}

@router.get("/insights")
def insights(user: dict = Depends(current_user)):
    data = dashboard(user)
    return data["ai_insights"]

@router.get("/activity")
def activity(user: dict = Depends(current_user)):
    with connection() as conn:
        uploads = conn.execute("SELECT filename,status,created_at FROM uploads WHERE owner_id=? ORDER BY created_at DESC LIMIT 20",(user["sub"],)).fetchall()
        predictions = conn.execute("SELECT p.customer_id,p.prediction,p.created_at FROM predictions p JOIN datasets d ON p.dataset_id=d.id WHERE d.owner_id=? ORDER BY p.created_at DESC LIMIT 20",(user["sub"],)).fetchall()
    events = ([{"who": "You", "what": f"uploaded {row['filename']} ({row['status']})", "when": row['created_at'], "type": "upload"} for row in uploads] + [{"who": "You", "what": f"ran {row['prediction']} for customer {row['customer_id']}", "when": row['created_at'], "type": "prediction"} for row in predictions])
    return sorted(events, key=lambda item: item["when"], reverse=True)[:20]

@router.get("/notifications")
def notifications(user: dict = Depends(current_user)):
    data = dashboard(user)
    return [{"title": item["title"], "description": item["description"], "priority": item["priority"], "created_at": datetime.utcnow().isoformat(), "read": False} for item in data["ai_insights"]]

@router.post("/predict")
def predict(body: dict[str,Any], user: dict = Depends(current_user)):
    customer_id=str(body.get("customer_id", "")); features=body.get("features",{})
    records=customers(customer_id,200,user); customer=next((x for x in records if x["id"]==customer_id),None)
    if not customer: raise HTTPException(404,"Customer not found in your uploaded data")
    dataset,frame=load_dataset(customer["dataset_id"],user["sub"]); target=norm(list(frame.columns),["churn","churn_score","churned","target"])
    if not target: raise HTTPException(422,"A churn/target column is required to train predictions from this dataset")
    numeric=[str(c) for c in frame.select_dtypes(include="number").columns if str(c)!=target]
    if not numeric: raise HTTPException(422,"The dataset needs numeric feature columns to train predictions")
    import joblib
    model_dir=Path(settings.upload_dir)/"models"; model_dir.mkdir(parents=True,exist_ok=True); model_path=model_dir/f"{dataset['id']}.joblib"
    if model_path.exists(): artifact=joblib.load(model_path); model=artifact["model"]; numeric=artifact["features"]
    else:
        from sklearn.impute import SimpleImputer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import make_pipeline
        y=(pd.to_numeric(frame[target],errors="coerce").fillna(0)>=.5).astype(int)
        if y.nunique()<2: raise HTTPException(422,"The uploaded target column needs both churn outcomes to train a model")
        model=make_pipeline(SimpleImputer(strategy="median"),LogisticRegression(max_iter=1000,class_weight="balanced")); X=frame[numeric].apply(pd.to_numeric,errors="coerce"); model.fit(X,y); joblib.dump({"model":model,"features":numeric},model_path)
    # Customer records are created in source row order, so locate by its stored payload where possible.
    values=features or customer["payload"]; sample=pd.DataFrame([{c:values.get(c) for c in numeric}]); probability=float(model.predict_proba(sample[numeric].apply(pd.to_numeric,errors="coerce"))[0][1]); confidence=round(max(probability,1-probability),3); prediction="high_churn_risk" if probability>=.5 else "low_churn_risk"; pid=str(uuid.uuid4())
    coefficients=model.named_steps["logisticregression"].coef_[0]; explanation=sorted([{"feature":name,"contribution":round(float(coef),4)} for name,coef in zip(numeric,coefficients)],key=lambda item:abs(item["contribution"]),reverse=True)[:5]
    with connection() as conn: conn.execute("INSERT INTO predictions(id,customer_id,dataset_id,prediction,probability,confidence,explanation_json) VALUES(?,?,?,?,?,?,?)",(pid,customer_id,customer["dataset_id"] if customer else None,prediction,probability,confidence,json.dumps(explanation)))
    return {"id":pid,"prediction":prediction,"probability":probability,"confidence":confidence,"explanation":explanation}
@router.post("/predict/batch")
def predict_batch(body: dict[str,Any], user: dict = Depends(current_user)):
    return [predict({"customer_id":str(item.get("customer_id","")),"features":item.get("features",{})},user) for item in body.get("items",[])]
@router.get("/predictions/history")
def prediction_history(_: dict = Depends(current_user)):
    with connection() as conn: rows=conn.execute("SELECT p.* FROM predictions p JOIN datasets d ON p.dataset_id=d.id WHERE d.owner_id=? ORDER BY p.created_at DESC LIMIT 100",(_["sub"],)).fetchall()
    return [{**dict(r),"explanation":decode_json(r["explanation_json"],[])} for r in rows]

@router.post("/documents", status_code=201)
async def upload_document(file: UploadFile=File(...), user: dict=Depends(current_user)):
    if not file.filename or Path(file.filename).suffix.lower() not in {".pdf", ".docx", ".txt", ".md", ".markdown", ".json"}:
        raise HTTPException(422, "Supported document files: PDF, DOCX, TXT, Markdown, JSON")
    raw=await file.read()
    if not raw: raise HTTPException(422, "Uploaded file is empty")
    checksum=hashlib.sha256(raw).hexdigest()
    with connection() as conn:
        existing=conn.execute("SELECT id,filename,chunks_json FROM documents WHERE owner_id=? AND checksum=?",(user["sub"],checksum)).fetchone()
    if existing:
        return {"document_id":existing["id"],"filename":existing["filename"],"chunks":len(decode_json(existing["chunks_json"],[])),"status":"indexed"}
    did=str(uuid.uuid4())
    base_dir=Path(settings.upload_dir)/"documents"
    base_dir.mkdir(parents=True, exist_ok=True)
    path=base_dir/f"{did}{Path(file.filename).suffix.lower()}"
    path.write_bytes(raw)
    try:
        content=DocumentParser.extract_text(path)
    except Exception as exc:
        path.unlink(missing_ok=True)
        raise HTTPException(422, f"Unable to parse document: {exc}") from exc
    if not content.strip():
        path.unlink(missing_ok=True)
        raise HTTPException(422, "No readable text was found in this document")
    chunks=DocumentChunker(chunk_size=900,overlap=150).chunk_text(content)
    upload_time=datetime.now(timezone.utc).isoformat()
    logger.info("Document upload started filename={} size_bytes={} collection={}", file.filename, len(raw), document_embeddings().collection_name)
    try:
        document_embeddings().embed_chunks([
            {
                "text": chunk,
                "document_id": did,
                "owner_id": str(user["sub"]),
                "filename": file.filename,
                "chunk_id": f"{did}:{index}",
                "upload_time": upload_time,
                "checksum": checksum,
            }
            for index, chunk in enumerate(chunks)
        ])
    except Exception as exc:
        path.unlink(missing_ok=True)
        raise HTTPException(503, f"Document indexing is unavailable: {exc}") from exc
    with connection() as conn:
        conn.execute("INSERT INTO documents(id,filename,path,content,chunks_json,checksum,indexed_at,owner_id,file_type,size_bytes) VALUES(?,?,?,?,?,?,?,?,?,?)",(did,file.filename,str(path),content,json.dumps(chunks),checksum,datetime.now(timezone.utc).isoformat(),user["sub"],Path(file.filename).suffix.lower(),len(raw)))
        conn.execute("INSERT INTO uploads(id,document_id,owner_id,filename,file_type,size_bytes,status) VALUES(?,?,?,?,?,?,?)",(str(uuid.uuid4()),did,user["sub"],file.filename,Path(file.filename).suffix.lower(),len(raw),"indexed"))
    logger.info("Document upload completed filename={} chunks_created={} collection={} document_id={}", file.filename, len(chunks), document_embeddings().collection_name, did)
    return {"document_id":did,"filename":file.filename,"chunks":len(chunks),"status":"indexed"}

@router.get("/documents")
def list_documents(user: dict=Depends(current_user)):
    with connection() as conn:
        rows=conn.execute("SELECT id,filename,path,file_type,size_bytes,checksum,indexed_at,created_at FROM documents WHERE owner_id=? ORDER BY created_at DESC",(user["sub"],)).fetchall()
    return [{"id": row["id"], "filename": row["filename"], "path": row["path"], "file_type": row["file_type"], "size_bytes": row["size_bytes"], "checksum": row["checksum"], "indexed_at": row["indexed_at"], "created_at": row["created_at"]} for row in rows]

@router.get("/documents/{document_id}")
def get_document(document_id: str, user: dict=Depends(current_user)):
    with connection() as conn:
        row=conn.execute("SELECT id,filename,path,file_type,size_bytes,checksum,indexed_at,content,created_at FROM documents WHERE id=? AND owner_id=?",(document_id,user["sub"])).fetchone()
    if not row:
        raise HTTPException(404, "Document not found")
    return {"id": row["id"], "filename": row["filename"], "path": row["path"], "file_type": row["file_type"], "size_bytes": row["size_bytes"], "checksum": row["checksum"], "indexed_at": row["indexed_at"], "content": row["content"], "created_at": row["created_at"]}

@router.delete("/documents/{document_id}", status_code=204)
def delete_document(document_id: str, user: dict=Depends(current_user)):
    with connection() as conn:
        row=conn.execute("SELECT path FROM documents WHERE id=? AND owner_id=?",(document_id,user["sub"])).fetchone()
        if not row:
            raise HTTPException(404, "Document not found")
        conn.execute("DELETE FROM documents WHERE id=? AND owner_id=?",(document_id,user["sub"]))
    if row["path"]:
        Path(row["path"]).unlink(missing_ok=True)
    document_embeddings().delete_document(document_id)
@router.post("/rag/query")
def rag_query(body:dict[str,str], user:dict=Depends(current_user)):
    q=body.get("question","").strip()
    if not q: raise HTTPException(422,"question is required")
    analytical=structured_answer(q,user["sub"])
    matches=[]
    try:
        matches=document_embeddings().similarity_search(q, top_k=5, owner_id=user["sub"])
    except Exception as exc:
        raise HTTPException(503, f"Document retrieval is unavailable: {exc}") from exc

    if analytical and matches:
        context=build_rag_context(matches)
        answer=context[:4000]
        if settings.groq_api_key:
            try:
                answer = GroqService(api_key=settings.groq_api_key, model=settings.groq_model).generate_answer(q, context)
            except Exception as exc:
                logger.warning("Groq generation failed for RAG query: {}", exc)
                answer = "I couldn't find enough information in the uploaded documents to answer this question."
        combined = f"{analytical['answer']}\n\nDocument context:\n{answer}"
        confidence=round(max(float(analytical.get("confidence",0.0)), round(sum(m["score"] for m in matches)/len(matches),2)),2)
        best_match=matches[0] if matches else None
        safe_matches=[document_embeddings().normalize_match(m) for m in matches]
        sources=list(dict.fromkeys([*(analytical.get("sources",[]) or []), *[f"{m['filename']} ({m['chunk_id']})" for m in safe_matches]]))
        logger.info("Hybrid Copilot query question={} dataset_sources={} document_matches={} collection={} similarity_scores={}", q, analytical.get("sources",[]), len(matches), document_embeddings().collection_name, [round(m.get("score",0.0),3) for m in safe_matches])
        with connection() as conn: conn.execute("INSERT INTO chat_history(id,user_id,question,answer,sources_json,confidence) VALUES(?,?,?,?,?,?)",(str(uuid.uuid4()),user["sub"],q,combined,json.dumps(sources),confidence))
        return {"answer":combined,"confidence":confidence,"sources":sources,"citations":[{"filename":m["filename"],"chunk_id":m["chunk_id"],"document_id":m["document_id"]} for m in safe_matches],"chunks":[{"document_id":m["document_id"],"chunk_id":m["chunk_id"],"filename":m["filename"],"score":round(m["score"],3)} for m in safe_matches],"filename":best_match.get("filename") if best_match else None,"retrieved_chunks":len(matches),"similarity_score":round(best_match.get("score",0.0),3) if best_match else 0.0}

    if analytical:
        with connection() as conn: conn.execute("INSERT INTO chat_history(id,user_id,question,answer,sources_json,confidence) VALUES(?,?,?,?,?,?)",(str(uuid.uuid4()),user["sub"],q,analytical["answer"],json.dumps(analytical["sources"]),analytical["confidence"]))
        return analytical
    if not matches:
        logger.info("Copilot query found no document matches question={} collection={}", q, document_embeddings().collection_name)
        return {"answer":"No information exists in the uploaded documents relevant to this question.","confidence":0.0,"sources":[],"citations":[],"chunks":[],"filename":None,"retrieved_chunks":0,"similarity_score":0.0}
    context=build_rag_context(matches)
    answer=context[:4000]
    if settings.groq_api_key:
        try:
            answer = GroqService(api_key=settings.groq_api_key, model=settings.groq_model).generate_answer(q, context)
        except Exception as exc:
            logger.warning("Groq generation failed for RAG query: {}", exc)
            answer = "I couldn't find enough information in the uploaded documents to answer this question."
    confidence=round(sum(m["score"] for m in matches)/len(matches),2)
    best_match=matches[0] if matches else None
    safe_matches=[document_embeddings().normalize_match(m) for m in matches]
    citations=[{"filename":m["filename"],"chunk_id":m["chunk_id"],"document_id":m["document_id"]} for m in safe_matches]
    sources=list(dict.fromkeys(f"{m['filename']} ({m['chunk_id']})" for m in safe_matches))
    logger.info("Copilot document retrieval question={} chunks_found={} filenames={} similarity_scores={} collection={}", q, len(matches), [m.get("filename") for m in safe_matches], [round(m.get("score",0.0),3) for m in safe_matches], document_embeddings().collection_name)
    with connection() as conn: conn.execute("INSERT INTO chat_history(id,user_id,question,answer,sources_json,confidence) VALUES(?,?,?,?,?,?)",(str(uuid.uuid4()),user["sub"],q,answer,json.dumps(sources),confidence))
    return {"answer":answer,"confidence":confidence,"sources":sources,"citations":citations,"chunks":[{"document_id":m["document_id"],"chunk_id":m["chunk_id"],"filename":m["filename"],"score":round(m["score"],3)} for m in safe_matches],"filename":best_match.get("filename") if best_match else None,"retrieved_chunks":len(matches),"similarity_score":round(best_match.get("score",0.0),3) if best_match else 0.0}

@router.get("/rag/debug")
def rag_debug():
    emb = document_embeddings()

    return {
        "collection": emb.collection_name,
        "count": emb.collection.count(),
        "stats": emb.collection_stats(),
    }

@router.post("/rag/reindex")
def reindex_rag_documents(user: dict = Depends(current_user)):
    try:
        result = document_embeddings().reindex_documents(owner_id=user["sub"])
    except Exception as exc:
        logger.exception("RAG reindex failed for owner {}", user["sub"])
        raise HTTPException(503, f"RAG reindex is unavailable: {exc}") from exc
    return result

@router.get("/search")
def search(q: str, user: dict = Depends(current_user)):
    q=q.strip()
    if not q: raise HTTPException(422,"q is required")
    pattern=f"%{q}%"; results=[]
    with connection() as conn:
        for row in conn.execute("SELECT c.id,c.name,c.email FROM customers c JOIN datasets d ON d.id=c.dataset_id WHERE d.owner_id=? AND (c.id LIKE ? OR c.name LIKE ? OR c.email LIKE ?)",(user["sub"],pattern,pattern,pattern)): results.append({"type":"customer","id":row["id"],"title":row["name"] or row["id"],"subtitle":row["email"]})
        for row in conn.execute("SELECT id,filename FROM datasets WHERE owner_id=? AND filename LIKE ?",(user["sub"],pattern)): results.append({"type":"dataset","id":row["id"],"title":row["filename"]})
        for row in conn.execute("SELECT id,filename FROM documents WHERE owner_id=? AND (filename LIKE ? OR content LIKE ?)",(user["sub"],pattern,pattern)): results.append({"type":"document","id":row["id"],"title":row["filename"]})
        for row in conn.execute("SELECT p.id,p.prediction,p.customer_id FROM predictions p JOIN datasets d ON p.dataset_id=d.id WHERE d.owner_id=? AND (p.prediction LIKE ? OR p.customer_id LIKE ?)",(user["sub"],pattern,pattern)): results.append({"type":"prediction","id":row["id"],"title":row["prediction"],"subtitle":row["customer_id"]})
        for row in conn.execute("SELECT id,question,answer FROM chat_history WHERE user_id=? AND (question LIKE ? OR answer LIKE ?)",(user["sub"],pattern,pattern)): results.append({"type":"chat","id":row["id"],"title":row["question"],"subtitle":row["answer"][:160]})
    return {"query":q,"results":results[:100]}

@router.get("/reports/dashboard")
def report_dashboard(format: str="json", user: dict=Depends(current_user)):
    data=dashboard(user)
    if format == "json": return data
    if format == "csv":
        stream=BytesIO(pd.DataFrame([data]).to_csv(index=False).encode())
        return StreamingResponse(stream,media_type="text/csv",headers={"Content-Disposition":"attachment; filename=dashboard-report.csv"})
    if format == "xlsx":
        try:
            stream=BytesIO(); pd.DataFrame([data]).to_excel(stream,index=False); stream.seek(0)
            return StreamingResponse(stream,media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",headers={"Content-Disposition":"attachment; filename=dashboard-report.xlsx"})
        except ImportError as exc: raise HTTPException(503,"Excel export dependency is unavailable") from exc
    raise HTTPException(422,"format must be json, csv, or xlsx")
