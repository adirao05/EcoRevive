import hashlib, json
from datetime import datetime, timezone
from .db import connect
GENESIS="0"*64
def sha(text): return hashlib.sha256(text.encode()).hexdigest()

def append_event(pid,typ,actor,notes=""):
    now=datetime.now(timezone.utc).isoformat()
    evidence=sha(json.dumps({"product_id":pid,"event_type":typ,"actor":actor,"notes":notes,"created_at":now},sort_keys=True))
    with connect() as c:
        row=c.execute("SELECT event_hash FROM lifecycle_events ORDER BY id DESC LIMIT 1").fetchone()
        prev=row["event_hash"] if row else GENESIS
        payload={"product_id":pid,"event_type":typ,"actor":actor,"notes":notes,"evidence_hash":evidence,"previous_hash":prev,"created_at":now}
        eh=sha(json.dumps(payload,sort_keys=True))
        c.execute("INSERT INTO lifecycle_events(product_id,event_type,actor,notes,evidence_hash,previous_hash,event_hash,created_at) VALUES(?,?,?,?,?,?,?,?)",
                  (pid,typ,actor,notes,evidence,prev,eh,now)); c.commit()
    return {**payload,"event_hash":eh}

def get_events(pid=None):
    with connect() as c:
        rows=c.execute("SELECT * FROM lifecycle_events WHERE product_id=? ORDER BY id" if pid else "SELECT * FROM lifecycle_events ORDER BY id DESC LIMIT 200",(pid,) if pid else ()).fetchall()
    return [dict(r) for r in rows]

def verify_chain():
    events=sorted(get_events(),key=lambda x:x["id"]); prev=GENESIS
    for e in events:
        payload={k:e[k] for k in ["product_id","event_type","actor","notes","evidence_hash","previous_hash","created_at"]}
        expected=sha(json.dumps(payload,sort_keys=True))
        if e["previous_hash"]!=prev or e["event_hash"]!=expected:
            return {"valid":False,"checked_events":len(events),"failed_event_id":e["id"],"message":"Hash-chain mismatch detected"}
        prev=e["event_hash"]
    return {"valid":True,"checked_events":len(events),"message":"All local hash-chain links are consistent"}
