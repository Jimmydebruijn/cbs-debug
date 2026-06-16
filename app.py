import streamlit as st
import requests

st.title("🔍 CBS 85064NED Debug v5 — substringof combinatie")

BASE = "https://opendata.cbs.nl/ODataApi/OData/85064NED"

st.header("1. substringof Perioden + substringof RegioS")

combos = [
    ("substringof('2020',Perioden) and substringof('PO',RegioS)", "PO prefix"),
    ("substringof('2020',Perioden) and substringof('PC',RegioS)", "PC prefix"),
    ("substringof('2020',Perioden) and substringof('8251',RegioS)", "8251 direct"),
]

for filt, label in combos:
    r = requests.get(
        f"{BASE}/TypedDataSet?$format=json"
        f"&$filter={filt}"
        f"&$select=RegioS,Perioden,MediaanGestandaardiseerdInkomen_4"
        f"&$top=5",
        timeout=20
    )
    st.write(f"**{label}** — Status: {r.status_code}")
    if r.status_code == 200:
        rows = r.json().get("value", [])
        st.write(f"  Rijen: {len(rows)}")
        for row in rows[:3]:
            st.write(f"  RegioS=`{repr(row.get('RegioS',''))}` val={row.get('MediaanGestandaardiseerdInkomen_4')}")
    else:
        st.write(f"  Fout: {r.text[:100]}")

st.header("2. Als PO werkt — haal alle postcodes op")
if st.button("Haal alle PO postcodes 2020 op"):
    with st.spinner("Laden..."):
        r2 = requests.get(
            f"{BASE}/TypedDataSet?$format=json"
            f"&$filter=substringof('2020',Perioden) and substringof('PO',RegioS)"
            f"&$select=RegioS,MediaanGestandaardiseerdInkomen_4,GemiddeldGestandaardiseerdInkomen_3"
            f"&$top=10000",
            timeout=60
        )
    st.write(f"Status: {r2.status_code}")
    if r2.status_code == 200:
        rows = r2.json().get("value", [])
        st.write(f"Totaal: {len(rows)} rijen")
        if rows:
            st.write(f"Eerste: {rows[0]}")
            st.write(f"Laatste: {rows[-1]}")
            pc8251 = [r for r in rows if "8251" in str(r.get("RegioS",""))]
            if pc8251:
                st.success(f"✅ 8251 gevonden: {pc8251[0]}")
            else:
                st.warning("8251 niet gevonden")
    else:
        st.error(r2.text[:200])
