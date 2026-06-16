import streamlit as st
import requests

st.title("🔍 CBS 85064NED Debug v6 — Exacte RegioS waarden")

BASE = "https://opendata.cbs.nl/ODataApi/OData/85064NED"

st.header("1. Alle RegioS waarden in 2020 data ($top=100)")
r = requests.get(
    f"{BASE}/TypedDataSet?$format=json"
    f"&$filter=substringof('2020',Perioden)"
    f"&$select=RegioS,Perioden,MediaanGestandaardiseerdInkomen_4"
    f"&$top=100",
    timeout=30
)
st.write(f"Status: {r.status_code}, Rijen: {len(r.json().get('value',[]))}")
if r.status_code == 200:
    rows = r.json().get("value", [])
    st.write(f"Totaal rijen: {len(rows)}")
    # Toon ALLE unieke RegioS waarden
    all_regio = set(repr(row.get("RegioS","")) for row in rows)
    st.write("Alle unieke RegioS waarden:")
    for regio in sorted(all_regio):
        st.code(regio)

st.header("2. substringof met top=500")
r2 = requests.get(
    f"{BASE}/TypedDataSet?$format=json"
    f"&$filter=substringof('2020',Perioden)"
    f"&$select=RegioS,MediaanGestandaardiseerdInkomen_4"
    f"&$top=500",
    timeout=30
)
st.write(f"Status: {r2.status_code}")
if r2.status_code == 200:
    rows2 = r2.json().get("value", [])
    st.write(f"Totaal rijen: {len(rows2)}")
    # Toon laatste 10 — wat is de laatste RegioS?
    st.write("Laatste 10 RegioS waarden:")
    for row in rows2[-10:]:
        st.code(repr(row.get("RegioS","")))
    # Zoek patronen
    prefixes = set(row.get("RegioS","")[:2].strip() for row in rows2)
    st.write(f"Unieke 2-teken prefixes: {prefixes}")

st.header("3. Zoek postcode 8251 via substringof RegioS direct")
for zoekterm in ["8251", "8252", "825"]:
    r3 = requests.get(
        f"{BASE}/TypedDataSet?$format=json"
        f"&$filter=substringof('{zoekterm}',RegioS)"
        f"&$select=RegioS,MediaanGestandaardiseerdInkomen_4"
        f"&$top=5",
        timeout=15
    )
    st.write(f"substringof('{zoekterm}',RegioS): Status {r3.status_code}, rijen: {len(r3.json().get('value',[]) if r3.status_code==200 else [])}")
    if r3.status_code == 200 and r3.json().get("value"):
        for row in r3.json()["value"][:3]:
            st.code(f"RegioS={repr(row.get('RegioS',''))} val={row.get('MediaanGestandaardiseerdInkomen_4')}")
