import streamlit as st
import requests

BASE = "https://opendata.cbs.nl/ODataApi/OData/85318NED"

st.title("🔍 Woning + uitkering kolommen")

r = requests.get(f"{BASE}/DataProperties?$format=json", timeout=15)
props = r.json().get("value", [])

st.header("Woningkolommen")
woning = [p for p in props if any(w in p.get("Title","").lower()
          for w in ["koop","huur","woning","eigen","corporatie","particulier"])]
for p in woning:
    st.write(f"`{p['Key']}` — {p.get('Title','')}")

st.header("Test data GM0344 + NL00")
per_key = requests.get(f"{BASE}/Perioden?$format=json", timeout=10).json().get("value",[{}])[-1].get("Key","")
cols = "PersonenPerSoortUitkeringBijstand_83,PersonenPerSoortUitkeringAO_84,PersonenPerSoortUitkeringWW_85,PersonenPerSoortUitkeringAOW_86"
if woning:
    cols += "," + ",".join(p["Key"] for p in woning[:4])

for gm in ["GM0344", "NL00  "]:
    r2 = requests.get(
        f"{BASE}/TypedDataSet?$format=json"
        f"&$filter=Perioden eq '{per_key}' and WijkenEnBuurten eq '{gm}'"
        f"&$select=WijkenEnBuurten,{cols}&$top=1",
        timeout=15
    )
    st.write(f"**{gm}** Status {r2.status_code}")
    if r2.status_code == 200 and r2.json().get("value"):
        st.json(r2.json()["value"][0])
