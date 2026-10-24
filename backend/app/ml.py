from pathlib import Path
import joblib, numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
VERSION = "ecorevive-synthetic-v1"
PATHWAYS = {0:"Reuse", 1:"Repair", 2:"Refurbish", 3:"Component Recovery", 4:"Recycle"}

def synthetic_data(n=3000, seed=42):
    rng=np.random.default_rng(seed)
    age=rng.uniform(0,15,n); battery=rng.uniform(5,100,n); repairs=rng.integers(0,7,n)
    functional=rng.integers(0,3,n); ratio=rng.uniform(0,1.2,n); resale=rng.uniform(0,1500,n)
    material=rng.uniform(5,350,n); hazard=rng.uniform(0,1,n); laptop=rng.integers(0,2,n)
    X=np.column_stack([age,battery,repairs,functional,ratio,resale,material,hazard,laptop])
    logit=-3+age*.25+(100-battery)*.025+repairs*.18+functional*.55+hazard*.45
    yr=(rng.random(n)<1/(1+np.exp(-logit))).astype(int)
    yp=[]
    for i in range(n):
        if functional[i]==0 and battery[i]>65 and age[i]<5 and ratio[i]<.25: yp.append(0)
        elif functional[i]==2 and (resale[i]<120 or ratio[i]>.85): yp.append(4)
        elif functional[i]==2: yp.append(3)
        elif ratio[i]<.35 and battery[i]>35: yp.append(1)
        else: yp.append(2)
    yv=np.maximum(0,resale*.55+material*.8-ratio*resale*.25+rng.normal(0,30,n))
    return X,yr,np.array(yp),yv

def train_models(force=False):
    names=["return_model.joblib","pathway_model.joblib","value_model.joblib"]
    paths=[MODEL_DIR/n for n in names]
    if not force and all(p.exists() for p in paths): return
    X,yr,yp,yv=synthetic_data()
    Xtr,Xte,ytr,yte=train_test_split(X,yr,test_size=.2,random_state=42,stratify=yr)
    ret=RandomForestClassifier(n_estimators=120,max_depth=10,random_state=42,class_weight="balanced").fit(Xtr,ytr)
    path=RandomForestClassifier(n_estimators=120,max_depth=12,random_state=42,class_weight="balanced").fit(X,yp)
    val=RandomForestRegressor(n_estimators=100,max_depth=12,random_state=42).fit(X,yv)
    for p,m in zip(paths,[ret,path,val]): joblib.dump(m,p)
    joblib.dump({"version":VERSION,"synthetic_holdout_accuracy":float(accuracy_score(yte,ret.predict(Xte)))},MODEL_DIR/"metadata.joblib")

def get_models():
    train_models()
    return tuple(joblib.load(MODEL_DIR/n) for n in ["return_model.joblib","pathway_model.joblib","value_model.joblib"])

def features(p):
    age=max(0,2026-int(p["manufacture_year"]))
    fs=str(p["functional_status"]).lower()
    functional=0 if fs=="functional" else 1 if fs=="partially functional" else 2
    resale=float(p["resale_value"] or 0); repair=float(p["repair_cost"] or 0)
    ratio=min(1.2,repair/max(resale,1))
    battery=float(p["battery_health"] if p["battery_health"] is not None else 50)
    return np.array([[age,battery,int(p["repair_count"]),functional,ratio,resale,float(p["material_value"] or 0),float(p["hazard_level"] or 0),1 if p["category"]=="Laptop" else 0]])

def predict(p):
    ret,path,val=get_models(); X=features(p)
    rp=float(ret.predict_proba(X)[0][list(ret.classes_).index(1)])
    probs=path.predict_proba(X)[0]; idx=int(np.argmax(probs))
    pathway=PATHWAYS[int(path.classes_[idx])]; conf=float(probs[idx])
    recovery=max(0,float(val.predict(X)[0]))
    age=max(0,2026-int(p["manufacture_year"])); battery=float(p["battery_health"] if p["battery_health"] is not None else 50)/100
    value_norm=min(1,recovery/1000)
    urgency=min(1,age/10*.45+(1-battery)*.35+(.25 if p["functional_status"]=="Non-functional" else .1 if p["functional_status"]=="Partially functional" else 0))
    hazard=float(p["hazard_level"] or 0); cost=min(1,float(p["repair_cost"] or 0)/1000)
    score=max(0,min(100,round(100*(.30*rp+.25*value_norm+.20*urgency+.25*hazard-.20*cost),1)))
    return {"return_probability":round(rp,4),"pathway":pathway,"pathway_confidence":round(conf,4),"recovery_value":round(recovery,2),"priority_score":score,"model_version":VERSION}
