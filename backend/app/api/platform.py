from __future__ import annotations
import json, math, re, uuid
from datetime import datetime
from pathlib import Path
from typing import Any
import pandas as pd
from io import BytesIO
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from app.config import settings
from app.core.security import current_user
from app.core.storage import connection, decode_json, row_dict

router = APIRouter()
def norm(columns: list[str], names: list[str]) -> str | None:
    lowered = {str(c).lower().replace(" ", "_"): str(c) for c in columns}
    return next((lowered[n] for n in names if n in lowered), None)
def load_dataset(dataset_id: str) -> tuple[dict[str, Any], pd.DataFrame]:
    with connection() as conn: row = row_dict(conn.execute("SELECT * FROM datasets WHERE id=?", (dataset_id,)).fetchone())
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
        conn.execute("INSERT INTO uploads(id,dataset_id,filename,status) VALUES(?,?,?,?)",(str(uuid.uuid4()),dataset_id,file.filename,"ready"))
    return {"dataset_id":dataset_id,"filename":file.filename,"row_count":len(frame),"column_count":len(frame.columns),"columns":list(map(str,frame.columns)),**summary}

@router.get("/datasets")
def datasets(user: dict = Depends(current_user)):
    with connection() as conn: return [dict(r) for r in conn.execute("SELECT id,filename,rows,columns,created_at FROM datasets WHERE owner_id=? ORDER BY created_at DESC",(user["sub"],))]
@router.get("/datasets/{dataset_id}/summary")
def dataset_summary(dataset_id: str, _: dict = Depends(current_user)):
    row,frame=load_dataset(dataset_id); return {"dataset_id":dataset_id,"filename":row["filename"],"rows":row["rows"],"columns":row["columns"],**decode_json(row["summary_json"],{})}
@router.get("/datasets/{dataset_id}/columns")
def dataset_columns(dataset_id: str, _: dict = Depends(current_user)):
    _,frame=load_dataset(dataset_id); return [{"name":str(c),"type":str(frame[c].dtype),"missing":int(frame[c].isna().sum()),"unique":int(frame[c].nunique())} for c in frame.columns]
@router.get("/datasets/{dataset_id}/preview")
def dataset_preview(dataset_id: str, offset: int=0, limit:int=Query(25,le=200), q:str="", _: dict = Depends(current_user)):
    _,frame=load_dataset(dataset_id); filtered=frame[frame.astype(str).apply(lambda c:c.str.contains(q,case=False,na=False)).any(axis=1)] if q else frame; return {"total":len(filtered),"rows":filtered.iloc[offset:offset+limit].where(filtered.notna(),None).to_dict(orient="records")}
@router.get("/datasets/{dataset_id}")
def dataset(dataset_id: str, user: dict = Depends(current_user)): return dataset_summary(dataset_id,user)
@router.delete("/datasets/{dataset_id}", status_code=204)
def delete_dataset(dataset_id: str, _: dict = Depends(current_user)):
    row,_=load_dataset(dataset_id)
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
    result.update({"datasets":len(rows),"documents":0,"recent_uploads":uploads,"segment_distribution":([{ "name":str(k),"value":int(v)} for k,v in frame[segment].fillna("Unknown").value_counts().items()] if segment else []),"risk_distribution":([{ "name":str(k),"value":int(v)} for k,v in pd.cut(pd.to_numeric(frame[risk],errors='coerce').fillna(0),[-1,.3,.6,1],labels=["Low","Medium","High"]).value_counts().items()] if risk else []),"revenue_trend":[]})
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
    return {"kpis":metrics(frame),"columns":list(map(str,frame.columns)),"records":len(frame)}

@router.post("/predict")
def predict(body: dict[str,Any], user: dict = Depends(current_user)):
    customer_id=str(body.get("customer_id", "")); features=body.get("features",{})
    records=customers(customer_id,200,user); customer=next((x for x in records if x["id"]==customer_id),None)
    values=features or (customer["payload"] if customer else {})
    risk=float(customer["risk"]) if customer else float(values.get("risk_score",values.get("risk",0)))
    churn=float(customer["churn"]) if customer else float(values.get("churn_score",values.get("churn",0)))
    probability=max(0,min(1,.15 + .45*risk + .40*churn)); confidence=round(.55 + abs(probability-.5)*.7,3); prediction="high_churn_risk" if probability>=.5 else "low_churn_risk"; pid=str(uuid.uuid4())
    explanation=[{"feature":"risk_score","contribution":risk},{"feature":"churn_score","contribution":churn}]
    with connection() as conn: conn.execute("INSERT INTO predictions(id,customer_id,dataset_id,prediction,probability,confidence,explanation_json) VALUES(?,?,?,?,?,?,?)",(pid,customer_id,customer["dataset_id"] if customer else None,prediction,probability,confidence,json.dumps(explanation)))
    return {"id":pid,"prediction":prediction,"probability":probability,"confidence":confidence,"explanation":explanation}
@router.post("/predict/batch")
def predict_batch(body: dict[str,Any], user: dict = Depends(current_user)):
    return [predict({"customer_id":str(item.get("customer_id","")),"features":item.get("features",{})},user) for item in body.get("items",[])]
@router.get("/predictions/history")
def prediction_history(_: dict = Depends(current_user)):
    with connection() as conn: rows=conn.execute("SELECT * FROM predictions ORDER BY created_at DESC LIMIT 100").fetchall()
    return [{**dict(r),"explanation":decode_json(r["explanation_json"],[])} for r in rows]

@router.post("/documents", status_code=201)
async def upload_document(file: UploadFile=File(...), user: dict=Depends(current_user)):
    if not file.filename or Path(file.filename).suffix.lower() not in {".txt",".md"}: raise HTTPException(422,"Document API currently supports TXT and Markdown content")
    raw=await file.read()
    try: content=raw.decode("utf-8")
    except UnicodeDecodeError: raise HTTPException(422,"Document must be UTF-8 text")
    did=str(uuid.uuid4()); path=Path(settings.upload_dir)/"documents"/f"{did}{Path(file.filename).suffix}"; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(raw); chunks=[content[i:i+1000] for i in range(0,len(content),800)]
    with connection() as conn: conn.execute("INSERT INTO documents(id,filename,path,content,chunks_json,owner_id) VALUES(?,?,?,?,?,?)",(did,file.filename,str(path),content,json.dumps(chunks),user["sub"]))
    return {"document_id":did,"filename":file.filename,"chunks":len(chunks),"status":"indexed"}
@router.post("/rag/query")
def rag_query(body:dict[str,str], user:dict=Depends(current_user)):
    q=body.get("question","").strip()
    if not q: raise HTTPException(422,"question is required")
    terms=set(re.findall(r"\w+",q.lower()))
    with connection() as conn: docs=conn.execute("SELECT id,filename,chunks_json FROM documents WHERE owner_id=?",(user["sub"],)).fetchall()
    hits=[]
    for doc in docs:
        for i,chunk in enumerate(decode_json(doc["chunks_json"],[])):
            score=len(terms & set(re.findall(r"\w+",chunk.lower())))
            if score: hits.append((score,doc["id"],doc["filename"],i,chunk))
    hits=sorted(hits,reverse=True)[:5]
    if not hits: return {"answer":"I could not find this information in the uploaded documents.","confidence":0,"sources":[],"chunks":[]}
    return {"answer":"\n\n".join(x[4] for x in hits)[:4000],"confidence":round(min(1,.4+.1*len(hits)),2),"sources":list(dict.fromkeys(x[2] for x in hits)),"chunks":[{"document_id":x[1],"chunk_index":x[3],"score":x[0]} for x in hits]}

@router.get("/search")
def search(q: str, user: dict = Depends(current_user)):
    q=q.strip()
    if not q: raise HTTPException(422,"q is required")
    pattern=f"%{q}%"; results=[]
    with connection() as conn:
        for row in conn.execute("SELECT c.id,c.name,c.email FROM customers c JOIN datasets d ON d.id=c.dataset_id WHERE d.owner_id=? AND (c.id LIKE ? OR c.name LIKE ? OR c.email LIKE ?)",(user["sub"],pattern,pattern,pattern)): results.append({"type":"customer","id":row["id"],"title":row["name"] or row["id"],"subtitle":row["email"]})
        for row in conn.execute("SELECT id,filename FROM datasets WHERE owner_id=? AND filename LIKE ?",(user["sub"],pattern)): results.append({"type":"dataset","id":row["id"],"title":row["filename"]})
        for row in conn.execute("SELECT id,filename FROM documents WHERE owner_id=? AND (filename LIKE ? OR content LIKE ?)",(user["sub"],pattern,pattern)): results.append({"type":"document","id":row["id"],"title":row["filename"]})
        for row in conn.execute("SELECT id,title,description FROM insights WHERE title LIKE ? OR description LIKE ?",(pattern,pattern)): results.append({"type":"insight","id":row["id"],"title":row["title"],"subtitle":row["description"]})
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
