from app.db import init_db, connect
from app.ledger import append_event, get_events
from app.main import assess
from datetime import datetime, timezone

def main():
    init_db()
    rows=[
      ("EVR-DEMO001","Laptop","Dell","Latitude 5420",2021,"Chennai",42,2,"Partially functional",2500,5000,220,.15),
      ("EVR-DEMO002","Smartphone","Samsung","Galaxy S21",2021,"Chennai",35,3,"Partially functional",1800,4200,140,.2),
      ("EVR-DEMO003","Laptop","Lenovo","ThinkPad T480",2019,"Chennai",68,1,"Functional",800,6500,300,.1),
      ("EVR-DEMO004","Smartphone","Apple","iPhone 12",2020,"Chennai",78,1,"Functional",1200,12000,180,.1),
      ("EVR-DEMO005","Laptop","HP","ProBook 440",2018,"Chennai",18,4,"Non-functional",4200,1500,350,.55),
      ("EVR-DEMO006","Smartphone","OnePlus","Nord 2",2021,"Chennai",52,2,"Functional",900,3800,120,.15)]
    with connect() as c:
        for i,x in enumerate(rows):
            pid,cat,brand,model,year,region,battery,repairs,status,repair,resale,material,hazard=x
            now=datetime.now(timezone.utc).isoformat()
            c.execute("INSERT OR IGNORE INTO products VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(pid,cat,brand,model,year,region,battery,repairs,status,repair,resale,material,hazard,"REGISTERED",now))
            c.execute("INSERT OR IGNORE INTO collection_requests(product_id,region,latitude,longitude,status,priority_score) VALUES(?,?,?,?,?,?)",(pid,region,13.04+i*.018,80.18+i*.021,"OPEN",0))
        c.commit()
    for x in rows:
        pid=x[0]
        if not get_events(pid): append_event(pid,"REGISTERED","Demo Seeder","Synthetic demo product")
        assess(pid)
    print("Seeded 6 synthetic laptops and smartphones.")
if __name__=="__main__": main()
