import streamlit as st
import requests

st.title("🔍 Gemeentecode test Pijnacker-Nootdorp")

BASE = "https://opendata.cbs.nl/ODataApi/OData/85318NED"

# PDOK reverse geocode voor een punt in Pijnacker-Nootdorp
st.header("1. PDOK reverse geocode")
lat, lon = 52.0, 4.43  # rond Pijnacker
r = requests.get(
    "https://api.pdok.nl/bzk/locatieserver/search/v3_1/reverse",
    params={"lat": lat, "lon": lon, "type": "gemeente", "rows": 1,
            "fl": "gemeentecode,weergavenaam"},
    timeout=10
)
st.write(f"Status: {r.status_code}")
if r.status_code == 200:
    docs = r.json().get("response",{}).get("docs",[])
    st.write(docs)
    if docs:
        gm_code_raw = docs[0].get("gemeentecode","")
        st.write(f"Gemeentecode raw: `{repr(gm_code_raw)}`")
        gm_code = f"GM{gm_code_raw}"
        st.write(f"Opgebouwde key: `{repr(gm_code)}`")

st.header("2. Test verschillende GM-key formaten")
per_key = "2022JJ00"
test_codes = ["GM1926", "GM01926", "GM 1926", "GM1926 "]
for code in test_codes:
    r2 = requests.get(
        f"{BASE}/TypedDataSet?$format=json"
        f"&$filter=Perioden eq '{per_key}' and WijkenEnBuurten eq '{code}'"
        f"&$select=WijkenEnBuurten,GemiddeldInkomenPerInwoner_72&$top=1",
        timeout=15
    )
    st.write(f"`{code}`: Status {r2.status_code}, data: {r2.json().get('value',[]) if r2.status_code==200 else r2.text[:100]}")

st.header("3. Zoek Pijnacker-Nootdorp in WijkenEnBuurten dimensie")
r3 = requests.get(
    f"{BASE}/WijkenEnBuurten?$format=json&$filter=substringof('Pijnacker',Title)",
    timeout=15
)
st.write(f"Status: {r3.status_code}")
if r3.status_code == 200:
    items = r3.json().get("value", [])
    for item in items[:10]:
        st.write(f"Key=`{repr(item['Key'])}` Title=`{repr(item.get('Title',''))}`")
