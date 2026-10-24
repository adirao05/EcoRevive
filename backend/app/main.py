from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import uuid, json, math, base64, io
import qrcode
from .db import init_db, connect
from .schemas import ProductCreate, EventCreate, OptimizeRequest
from .ml import predict, train_models
from .ledger import append_event, get_events, verify_chain
from . import blockchain as evm

app=FastAPI(title="EcoRevive API",version="1.0.0",description="AI predictive e-waste reverse logistics and digital passports")
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
FACILITIES=[
 {"id":"FAC-CH-01","name":"Chennai Refurbishment Hub","lat":13.0569,"lon":80.2425,"cap":["Laptop","Smartphone"]},
 {"id":"FAC-CH-02","name":"Chennai E-Waste Recycler","lat":13.1143,"lon":80.1548,"cap":["Laptop","Smartphone"]},
 {"id":"FAC-CH-03","name":"South Chennai Repair Centre","lat":12.9716,"lon":80.2206,"cap":["Laptop","Smartphone"]},
]
@app.on_event("startup")
def startup(): init_db(); train_models()

def product(pid):
    with connect() as c: r=c.execute("SELECT * FROM products WHERE product_id=?",(pid,)).fetchone()
    if not r: raise HTTPException(404,"Product not found")
    return dict(r)
def latest(pid):
    with connect() as c: r=c.execute("SELECT * FROM predictions WHERE product_id=? ORDER BY id DESC LIMIT 1",(pid,)).fetchone()
    return dict(r) if r else None
def assess(pid):
    p=product(pid); pred=predict(p); now=datetime.now(timezone.utc).isoformat()
    with connect() as c:
        c.execute("INSERT INTO predictions(product_id,return_probability,pathway,pathway_confidence,recovery_value,priority_score,model_version,created_at) VALUES(?,?,?,?,?,?,?,?)",
        (pid,pred["return_probability"],pred["pathway"],pred["pathway_confidence"],pred["recovery_value"],pred["priority_score"],pred["model_version"],now))
        c.execute("INSERT OR IGNORE INTO collection_requests(product_id,region,latitude,longitude,status,priority_score) VALUES(?,?,?,?,?,?)",
        (pid,p["region"],13.0827+(len(pid)%5)*.01,80.2707+(len(pid)%7)*.01,"OPEN",pred["priority_score"]))
        c.execute("UPDATE collection_requests SET priority_score=? WHERE product_id=? AND status='OPEN'",(pred["priority_score"],pid)); c.commit()
    return {**pred,"product_id":pid,"created_at":now}

@app.get("/api/health")
def health(): return {"status":"ok","project":"EcoRevive","supported_categories":["Laptop","Smartphone"]}

@app.get("/api/blockchain/status")
def blockchain_status(): return evm.status()
@app.get("/api/dashboard")
def dashboard():
    with connect() as c:
        total=c.execute("SELECT COUNT(*) n FROM products").fetchone()["n"]
        opened=c.execute("SELECT COUNT(*) n FROM collection_requests WHERE status='OPEN'").fetchone()["n"]
        events=c.execute("SELECT COUNT(*) n FROM lifecycle_events").fetchone()["n"]
        done=c.execute("SELECT COUNT(*) n FROM products WHERE lifecycle_status IN ('REFURBISHED','RECYCLED','COMPONENT_RECOVERY')").fetchone()["n"]
        cats=[dict(x) for x in c.execute("SELECT category,COUNT(*) count FROM products GROUP BY category").fetchall()]
        rows=c.execute("SELECT * FROM products ORDER BY created_at DESC LIMIT 8").fetchall()
    recent=[]
    for r in rows:
        p=dict(r); p["prediction"]=latest(p["product_id"]); recent.append(p)
    return {"total_products":total,"open_collection_requests":opened,"verified_events":events,"completed_recoveries":done,"by_category":cats,"recent_products":recent,"ledger":verify_chain()}
@app.get("/api/products")
def products():
    with connect() as c: rows=c.execute("SELECT * FROM products ORDER BY created_at DESC").fetchall()
    out=[]
    for r in rows:
        p=dict(r); p["latest_prediction"]=latest(p["product_id"]); out.append(p)
    return out
@app.post("/api/products",status_code=201)
def create(body:ProductCreate):
    pid="EVR-"+uuid.uuid4().hex[:8].upper(); now=datetime.now(timezone.utc).isoformat()
    with connect() as c:
        c.execute("INSERT INTO products VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (pid,body.category,body.brand.strip(),body.model.strip(),body.manufacture_year,body.region,body.battery_health,body.repair_count,body.functional_status,body.repair_cost,body.resale_value,body.material_value,body.hazard_level,"REGISTERED",now)); c.commit()
    append_event(pid,"REGISTERED","EcoRevive Registry","Product and initial passport registered")
    chain_result = {"status": "not_attempted"}
    try:
        registered = product(pid)
        chain_result = evm.register_product(pid, {k: registered.get(k) for k in ["product_id", "category", "brand", "model", "manufacture_year", "region", "lifecycle_status", "created_at"]})
    except Exception as exc:
        chain_result = {"status": "error", "message": str(exc)}
    pred=assess(pid)
    return {"product":product(pid),"prediction":pred,"qr_url":f"/api/products/{pid}/qr","blockchain":chain_result}
@app.get("/api/products/{pid}")
def detail(pid:str):
    p=product(pid); p["latest_prediction"]=latest(pid); p["events"]=get_events(pid)
    p["passport"]={"passport_id":pid,"version":1+len(p["events"]),"note":"Prototype DPP; check provenance of each field."}
    return p
@app.get("/api/products/{pid}/qr")
def qr(pid:str):
    product(pid); url=f"http://localhost:5173/products/{pid}"
    img=qrcode.make(url); b=io.BytesIO(); img.save(b,format="PNG")
    return {"product_id":pid,"url":url,"image_base64":base64.b64encode(b.getvalue()).decode()}
@app.post("/api/products/{pid}/predict")
def predict_product(pid:str): return assess(pid)
@app.post("/api/products/{pid}/events")
def event(pid:str,body:EventCreate):
    p=product(pid); typ=body.event_type; status=p["lifecycle_status"]
    if typ=="RECYCLED" and status not in {"COLLECTED","INSPECTED","COMPONENT_RECOVERY"}: raise HTTPException(409,"Record COLLECTED or INSPECTED before recycling")
    if typ=="REFURBISHED" and status not in {"COLLECTED","INSPECTED","REPAIRED"}: raise HTTPException(409,"Record COLLECTED, INSPECTED, or REPAIRED before refurbishment")
    ev=append_event(pid,typ,body.actor,body.notes)
    chain_result = {"status": "not_attempted"}
    try:
        chain_result = evm.record_lifecycle_event(pid, typ, ev)
    except Exception as exc:
        chain_result = {"status": "error", "message": str(exc)}
    next_status={"COLLECTED":"COLLECTED","INSPECTED":"INSPECTED","REPAIRED":"REPAIRED","REFURBISHED":"REFURBISHED","COMPONENT_RECOVERY":"COMPONENT_RECOVERY","RECYCLED":"RECYCLED","CUSTODY_TRANSFER":status}
    with connect() as c:
        c.execute("UPDATE products SET lifecycle_status=? WHERE product_id=?",(next_status[typ],pid))
        if typ in {"REFURBISHED","COMPONENT_RECOVERY","RECYCLED"}: c.execute("UPDATE collection_requests SET status='COMPLETED' WHERE product_id=?",(pid,))
        c.commit()
    return {"event":ev,"product":product(pid),"ledger":verify_chain(),"blockchain":chain_result}
@app.get("/api/audit")
def audit(): return get_events()
@app.get("/api/audit/verify")
def audit_verify(): return verify_chain()
@app.get("/api/collection/requests")
def collection():
    with connect() as c:
        rows=c.execute("SELECT cr.*,p.category,p.brand,p.model,p.lifecycle_status FROM collection_requests cr JOIN products p ON p.product_id=cr.product_id ORDER BY cr.priority_score DESC").fetchall()
    return [dict(r) for r in rows]
def distance(a,b,c,d):
    R=6371; p1,p2=math.radians(a),math.radians(c); dp=math.radians(c-a); dl=math.radians(d-b)
    x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(x))
@app.post("/api/collection/optimize")
def optimize(body:OptimizeRequest):
    with connect() as c:
        req=[dict(r) for r in c.execute("SELECT cr.*,p.category,p.brand,p.model FROM collection_requests cr JOIN products p ON p.product_id=cr.product_id WHERE cr.status='OPEN' ORDER BY cr.priority_score DESC LIMIT ?",(body.max_stops,)).fetchall()]
    if not req: return {"stops":[],"total_distance_km":0,"estimated_transport_cost":0,"method":"Nearest-neighbour baseline","message":"No open requests"}
    current=(body.start_latitude,body.start_longitude); stops=[]; total=0
    while req:
        nxt=min(req,key=lambda x:distance(current[0],current[1],x["latitude"],x["longitude"]))
        d=distance(current[0],current[1],nxt["latitude"],nxt["longitude"]); total+=d
        fac=min(FACILITIES,key=lambda f:distance(nxt["latitude"],nxt["longitude"],f["lat"],f["lon"]))
        stops.append({"order":len(stops)+1,"product_id":nxt["product_id"],"category":nxt["category"],"brand":nxt["brand"],"model":nxt["model"],"priority_score":nxt["priority_score"],"distance_from_previous_km":round(d,2),"assigned_facility":fac["name"],"facility_id":fac["id"],"facility_distance_km":round(distance(nxt["latitude"],nxt["longitude"],fac["lat"],fac["lon"]),2)})
        current=(nxt["latitude"],nxt["longitude"]); req.remove(nxt)
    with connect() as c:
        for s in stops: c.execute("UPDATE collection_requests SET assigned_facility=?,route_order=? WHERE product_id=?",(s["assigned_facility"],s["order"],s["product_id"]))
        c.commit()
    return {"stops":stops,"total_distance_km":round(total,2),"estimated_transport_cost":round(total*18,2),"method":"Nearest-neighbour heuristic; straight-line distance, not live road routing","message":"Route generated"}
