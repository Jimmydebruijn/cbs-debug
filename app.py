import streamlit as st
import requests

st.title("🔍 Buurt inkomen test")

# Test 1: PDOK WFS buurtcode via coördinaten
st.header("1. Coördinaten → buurtcode (PDOK WFS)")

test_coords = [
    ("Den Haag centrum", 52.0705, 4.3007),
    ("Amsterdam Jordaan", 52.3745, 4.8820),
    ("Pijnacker", 52.0134, 4.4276),
]

buurten = {}
for naam, lat, lon in test_coords:
    r = requests.get(
        "https://service.pdok.nl/cbs/wijkenbuurten/2024/wfs/v1_0",
        params={
            "service": "WFS", "version": "2.0.0",
            "request": "GetFeature",
            "typeName": "wijkenbuurten:buurten",
            "outputFormat": "application/json",
            "srsName": "EPSG:4326",
            "cql_filter": f"INTERSECTS(geom, POINT({lon} {lat}))"
        },
        timeout=15
    )
    st.write(f"**{naam}** — Status: {r.status_code}")
    if r.status_code == 200:
        features = r.json().get("features", [])
        st.write(f"  Features: {len(features)}")
        if features:
            props = features[0]["properties"]
            st.write(f"  buurtcode: `{props.get('buurtcode','')}` naam: `{props.get('buurtnaam','')}`")
            st.write(f"  wijkcode: `{props.get('wijkcode','')}` gem: `{props.get('gemeentecode','')}`")
            buurten[naam] = props.get("buurtcode","")
    else:
        st.write(f"  Fout: {r.text[:100]}")

# Test 2: CBS 85318NED op buurtniveau
st.header("2. Buurtcode → inkomen (85318NED)")
BASE = "https://opendata.cbs.nl/ODataApi/OData/85318NED"
per_r = requests.get(f"{BASE}/Perioden?$format=json", timeout=10)
per_key = per_r.json().get("value",[{}])[-1].get("Key","2022JJ00") if per_r.status_code==200 else "2022JJ00"
st.write(f"Periode: {per_key}")

for naam, buurtcode in buurten.items():
    if not buurtcode: continue
    r2 = requests.get(
        f"{BASE}/TypedDataSet?$format=json"
        f"&$filter=Perioden eq '{per_key}' and WijkenEnBuurten eq '{buurtcode}'"
        f"&$select=WijkenEnBuurten,GemiddeldInkomenPerInwoner_72,GemiddeldInkomenPerInkomensontvanger_71"
        f"&$top=1",
        timeout=15
    )
    st.write(f"**{naam}** ({buurtcode}) — Status: {r2.status_code}")
    if r2.status_code == 200 and r2.json().get("value"):
        row = r2.json()["value"][0]
        inw = row.get("GemiddeldInkomenPerInwoner_72")
        st.success(f"  ✅ Gem. inkomen/inwoner: € {round(inw*1000):,}".replace(",",".") if inw else "  Geen data")
    else:
        st.write(f"  Geen data of fout")

# Test 3: WijkenEnBuurten dimensie — hoe ziet buurtcode eruit?
st.header("3. WijkenEnBuurten dimensie — buurt format check")
r3 = requests.get(
    f"{BASE}/WijkenEnBuurten?$format=json"
    f"&$filter=substringof('BU',Key)&$top=5",
    timeout=10
)
st.write(f"Status: {r3.status_code}")
if r3.status_code == 200:
    for item in r3.json().get("value",[])[:5]:
        st.write(f"Key=`{repr(item['Key'])}` Title=`{repr(item.get('Title',''))}`")
