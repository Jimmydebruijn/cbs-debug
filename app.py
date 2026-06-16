import streamlit as st
import requests

st.title("🔍 CBS 85064NED Debug v2")

BASE = "https://opendata.cbs.nl/ODataApi/OData/85064NED"

# Test: UntypedDataSet zonder filter, met nextLink paginering
st.header("1. UntypedDataSet eerste pagina")

r = requests.get(f"{BASE}/UntypedDataSet?$format=json&$top=5", timeout=30)
st.write(f"Status: {r.status_code}")
if r.status_code == 200:
    d = r.json()
    st.write(f"nextLink aanwezig: {'odata.nextLink' in d}")
    st.write(f"nextLink: {d.get('odata.nextLink','geen')[:100]}")
    rows = d.get("value", [])
    st.write(f"Aantal rijen: {len(rows)}")
    if rows:
        st.write("Eerste rij keys:", list(rows[0].keys()))
        st.write("Eerste rij:", rows[0])

st.header("2. TypedDataSet zonder filter, eerste pagina")
r2 = requests.get(f"{BASE}/TypedDataSet?$format=json&$top=5", timeout=30)
st.write(f"Status: {r2.status_code}")
if r2.status_code == 200:
    d2 = r2.json()
    st.write(f"nextLink: {d2.get('odata.nextLink','geen')[:100]}")
    rows2 = d2.get("value", [])
    for row in rows2:
        st.write(f"RegioS=`{repr(row.get('RegioS',''))}` Perioden=`{repr(row.get('Perioden',''))}`")

st.header("3. TypedDataSet zonder filter, skip=0 top=10")
r3 = requests.get(f"{BASE}/TypedDataSet?$format=json&$top=10&$skip=0", timeout=30)
st.write(f"Status: {r3.status_code}")
if r3.status_code == 200:
    d3 = r3.json()
    st.write(f"nextLink: {d3.get('odata.nextLink','geen')[:120]}")
    rows3 = d3.get("value", [])
    for row in rows3:
        st.write(f"RegioS=`{repr(row.get('RegioS',''))}` Perioden=`{repr(row.get('Perioden',''))}`")

st.header("4. Volg nextLink — hoeveel periodes zijn er?")
if st.button("Volg nextLink keten"):
    url = f"{BASE}/TypedDataSet?$format=json&$top=100"
    seen_regio = set()
    periodes = set()
    stappen = 0
    postcode_gevonden = False

    with st.spinner("Bezig..."):
        while url and stappen < 50:
            r = requests.get(url, timeout=30)
            if r.status_code != 200:
                st.error(f"Status {r.status_code} bij stap {stappen}")
                break
            d = r.json()
            rows = d.get("value", [])
            for row in rows:
                regio = row.get("RegioS","").strip()
                periode = row.get("Perioden","").strip()
                periodes.add(periode)
                seen_regio.add(regio[:6])
                if regio.startswith("PO") and not postcode_gevonden:
                    st.success(f"✅ Eerste postcode bij stap {stappen}: RegioS=`{repr(regio)}` Periode=`{periode}`")
                    st.write(row)
                    postcode_gevonden = True
            url = d.get("odata.nextLink")
            stappen += 1
            if stappen % 5 == 0:
                st.write(f"Stap {stappen}, periodes gezien: {periodes}, laatste RegioS: `{repr(list(seen_regio)[-1])}`")
            if postcode_gevonden:
                break

    if not postcode_gevonden:
        st.warning(f"Geen postcode gevonden na {stappen} stappen")
        st.write(f"Geziene periodes: {periodes}")
        st.write(f"Geziene RegioS prefixes: {set(r[:4] for r in seen_regio)}")
