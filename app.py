import streamlit as st
import requests

st.title("🔍 Debug v8 — 84639NED postcode format")

# 84639NED werkt met PC filter — zoek het exacte format
BASE = "https://opendata.cbs.nl/ODataApi/OData/84639NED"

st.header("1. Exacte RegioS waarde voor postcodes in 84639NED")
r = requests.get(
    f"{BASE}/TypedDataSet?$format=json"
    f"&$filter=substringof('PC',RegioS)"
    f"&$select=RegioS,MediaanGestandaardiseerdInkomen_4"
    f"&$top=5",
    timeout=15
)
st.write(f"Status: {r.status_code}")
if r.status_code == 200:
    rows = r.json().get("value", [])
    st.write(f"Rijen: {len(rows)}")
    for row in rows:
        st.code(f"RegioS={repr(row.get('RegioS',''))} val={row.get('MediaanGestandaardiseerdInkomen_4')}")

st.header("2. Filter op postcode 8251 in 84639NED")
for zoek in ["PC8251", "8251"]:
    r2 = requests.get(
        f"{BASE}/TypedDataSet?$format=json"
        f"&$filter=substringof('{zoek}',RegioS)"
        f"&$select=RegioS,MediaanGestandaardiseerdInkomen_4,GemiddeldGestandaardiseerdInkomen_3"
        f"&$top=3",
        timeout=15
    )
    st.write(f"substringof('{zoek}',RegioS): Status {r2.status_code}")
    if r2.status_code == 200 and r2.json().get("value"):
        for row in r2.json()["value"]:
            st.success(f"✅ RegioS={repr(row.get('RegioS',''))} mediaan={row.get('MediaanGestandaardiseerdInkomen_4')} gem={row.get('GemiddeldGestandaardiseerdInkomen_3')}")

st.header("3. Perioden in 84639NED")
r3 = requests.get(f"{BASE}/Perioden?$format=json", timeout=10)
if r3.status_code == 200:
    perioden = r3.json().get("value", [])
    st.write(f"Perioden: {[p['Key'] for p in perioden]}")
    st.write(f"Laatste: {perioden[-1]['Key'] if perioden else '?'}")

st.header("4. 83765NED — exact format postcode")
BASE2 = "https://opendata.cbs.nl/ODataApi/OData/83765NED"
r4 = requests.get(
    f"{BASE2}/TypedDataSet?$format=json"
    f"&$filter=substringof('PC',RegioS)"
    f"&$select=RegioS,GemiddeldInkomenPerInwoner_66"
    f"&$top=5",
    timeout=15
)
st.write(f"83765NED Status: {r4.status_code}")
if r4.status_code == 200:
    for row in r4.json().get("value",[])[:3]:
        st.code(f"RegioS={repr(row.get('RegioS',''))} val={row.get('GemiddeldInkomenPerInwoner_66')}")

st.header("5. 84639NED — haal 8251 t/m 8254 op in één query")
pcs = ["PC8251", "PC8252", "PC8253", "PC8254"]
filter_str = " or ".join(f"substringof('{pc}',RegioS)" for pc in pcs)
r5 = requests.get(
    f"{BASE}/TypedDataSet?$format=json"
    f"&$filter={filter_str}"
    f"&$select=RegioS,MediaanGestandaardiseerdInkomen_4,GemiddeldGestandaardiseerdInkomen_3"
    f"&$top=20",
    timeout=15
)
st.write(f"Multi-postcode query: Status {r5.status_code}")
if r5.status_code == 200:
    rows5 = r5.json().get("value", [])
    st.write(f"Rijen: {len(rows5)}")
    for row in rows5:
        st.write(f"RegioS={repr(row.get('RegioS',''))} mediaan={row.get('MediaanGestandaardiseerdInkomen_4')}")
