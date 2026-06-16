import streamlit as st
import requests

st.title("🔍 Gemeente inkomen test")

# 85318NED — Kerncijfers wijken en buurten
# Heeft GemiddeldInkomenPerInwoner per gemeente
BASE = "https://opendata.cbs.nl/ODataApi/OData/85318NED"

st.header("1. DataProperties — inkomenskolommen")
r = requests.get(f"{BASE}/DataProperties?$format=json", timeout=15)
st.write(f"Status: {r.status_code}")
if r.status_code == 200:
    props = r.json().get("value", [])
    ink_cols = [p for p in props if any(w in p.get("Title","").lower() 
                for w in ["inkomen","income","besteedbaar","uitkering","bijstand"])]
    for p in ink_cols:
        st.write(f"`{p['Key']}` — {p.get('Title','')}")

st.header("2. Perioden")
r2 = requests.get(f"{BASE}/Perioden?$format=json", timeout=10)
if r2.status_code == 200:
    perioden = r2.json().get("value", [])
    st.write([p["Key"] for p in perioden[-3:]])

st.header("3. Test gemeente Utrecht + NL")
per_key = r2.json().get("value", [])[-1]["Key"] if r2.status_code == 200 else "2022JJ00"
for regio in ["GM0344", "NL00  "]:
    r3 = requests.get(
        f"{BASE}/TypedDataSet?$format=json"
        f"&$filter=Perioden eq '{per_key}' and WijkenEnBuurten eq '{regio}'"
        f"&$select=WijkenEnBuurten,GemiddeldInkomenPerInwoner_72,GemiddeldInkomenPerInkomensontvanger_71"
        f"&$top=1",
        timeout=15
    )
    st.write(f"Regio `{regio}`: Status {r3.status_code}")
    if r3.status_code == 200 and r3.json().get("value"):
        st.write(r3.json()["value"][0])
