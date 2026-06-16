import streamlit as st
import requests

st.title("🔍 CBS 85064NED Debug")

BASE = "https://opendata.cbs.nl/ODataApi/OData/85064NED"

@st.cache_data
def fetch_raw(url):
    r = requests.get(url, timeout=30)
    return r.status_code, r.json() if r.status_code == 200 else {}

# Test 1: Perioden
st.header("1. Perioden")
status, data = fetch_raw(f"{BASE}/Perioden?$format=json")
st.write(f"Status: {status}")
if data:
    perioden = data.get("value", [])
    st.write(f"Aantal: {len(perioden)}")
    if perioden:
        st.write(f"Laatste: {perioden[-1]}")
        per_key = perioden[-1]["Key"]

# Test 2: RegioS — eerste 10
st.header("2. RegioS eerste 20 items")
status2, data2 = fetch_raw(f"{BASE}/RegioS?$format=json&$top=20")
st.write(f"Status: {status2}")
if data2:
    items = data2.get("value", [])
    for item in items:
        st.write(f"Key=`{repr(item['Key'])}` | Title=`{repr(item.get('Title',''))}`")

# Test 3: RegioS — skip 400 (waar postcodes beginnen)
st.header("3. RegioS skip=400 (postcode gebied)")
status3, data3 = fetch_raw(f"{BASE}/RegioS?$format=json&$top=10&$skip=400")
st.write(f"Status: {status3}")
if data3:
    items3 = data3.get("value", [])
    for item in items3:
        st.write(f"Key=`{repr(item['Key'])}` | Title=`{repr(item.get('Title',''))}`")

# Test 4: TypedDataSet skip=400
st.header("4. TypedDataSet skip=400 — eerste PostcodeRijen")
try:
    per_key = fetch_raw(f"{BASE}/Perioden?$format=json")[1].get("value",[{}])[-1].get("Key","")
    status4, data4 = fetch_raw(
        f"{BASE}/TypedDataSet?$format=json"
        f"&$filter=Perioden eq '{per_key}'"
        f"&$select=RegioS,MediaanGestandaardiseerdInkomen_4"
        f"&$top=10&$skip=400"
    )
    st.write(f"Status: {status4}, Periode: {per_key}")
    if data4:
        for row in data4.get("value", []):
            st.write(f"RegioS=`{repr(row.get('RegioS',''))}` | Waarde={row.get('MediaanGestandaardiseerdInkomen_4')}")
except Exception as e:
    st.error(str(e))

# Test 5: Zoek postcode 8251 specifiek
st.header("5. Zoek postcode 8251 via skip loop")
if st.button("Start zoeken (pagineert door tabel)"):
    try:
        per_key = fetch_raw(f"{BASE}/Perioden?$format=json")[1].get("value",[{}])[-1].get("Key","")
        gevonden = []
        with st.spinner("Zoeken..."):
            for skip in range(0, 5000, 100):
                r = requests.get(
                    f"{BASE}/TypedDataSet?$format=json"
                    f"&$filter=Perioden eq '{per_key}'"
                    f"&$select=RegioS,MediaanGestandaardiseerdInkomen_4"
                    f"&$top=100&$skip={skip}",
                    timeout=30
                )
                if r.status_code != 200:
                    st.error(f"Status {r.status_code} bij skip={skip}")
                    break
                rows = r.json().get("value", [])
                if not rows:
                    st.info(f"Geen rijen meer bij skip={skip}")
                    break
                for row in rows:
                    regio = row.get("RegioS","")
                    if "8251" in regio or "8252" in regio:
                        gevonden.append(row)
                if gevonden:
                    st.success(f"Gevonden bij skip={skip}!")
                    for g in gevonden:
                        st.write(g)
                    break
                if skip % 500 == 0:
                    st.write(f"skip={skip}, laatste RegioS: `{repr(rows[-1].get('RegioS',''))}`")
    except Exception as e:
        st.error(str(e))
