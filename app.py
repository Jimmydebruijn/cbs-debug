import streamlit as st
import requests

st.title("🔍 CBS 85064NED Debug v3 — Grote fetch")

BASE = "https://opendata.cbs.nl/ODataApi/OData/85064NED"

st.header("1. Totaal aantal rijen in tabel")
r = requests.get(f"{BASE}/TypedDataSet?$format=json&$inlinecount=allpages&$top=1", timeout=30)
st.write(f"Status: {r.status_code}")
if r.status_code == 200:
    d = r.json()
    st.write(f"odata.count: {d.get('odata.count', 'niet aanwezig')}")
    st.write(f"Alle keys in response: {list(d.keys())}")

st.header("2. Fetch met $top=10000 — hoeveel rijen komen terug?")
if st.button("Laad alles ($top=10000)"):
    with st.spinner("Laden..."):
        r2 = requests.get(
            f"{BASE}/TypedDataSet?$format=json"
            f"&$select=RegioS,Perioden,MediaanGestandaardiseerdInkomen_4"
            f"&$top=10000",
            timeout=60
        )
    st.write(f"Status: {r2.status_code}")
    if r2.status_code == 200:
        rows = r2.json().get("value", [])
        st.write(f"Totaal rijen ontvangen: {len(rows)}")
        # Toon unieke perioden
        perioden = set(r.get("Perioden","").strip() for r in rows)
        st.write(f"Perioden: {perioden}")
        # Zoek postcodes
        pcs = [r for r in rows if r.get("RegioS","").strip().startswith("PO")]
        st.write(f"Postcode rijen: {len(pcs)}")
        if pcs:
            st.write(f"Eerste postcode rij: {pcs[0]}")
            st.write(f"RegioS formaat: `{repr(pcs[0].get('RegioS',''))}`")
            # Zoek specifiek 8251
            pc8251 = [r for r in pcs if "8251" in r.get("RegioS","")]
            st.write(f"Rijen met 8251: {len(pc8251)}")
            if pc8251:
                st.success(f"✅ Gevonden: {pc8251[0]}")
        else:
            # Toon laatste 5 rijen
            st.write("Geen postcodes — laatste 5 rijen:")
            for row in rows[-5:]:
                st.write(f"RegioS=`{repr(row.get('RegioS',''))}` Perioden=`{row.get('Perioden','')}`")
    else:
        st.error(f"Fout: {r2.text[:200]}")

st.header("3. Test UntypedDataSet met $top=10000")
if st.button("Laad UntypedDataSet"):
    with st.spinner("Laden..."):
        r3 = requests.get(
            f"{BASE}/UntypedDataSet?$format=json&$top=10000",
            timeout=60
        )
    st.write(f"Status: {r3.status_code}")
    if r3.status_code == 200:
        rows = r3.json().get("value", [])
        st.write(f"Totaal rijen: {len(rows)}")
        pcs = [r for r in rows if str(r.get("RegioS","")).strip().startswith("PO")]
        st.write(f"Postcode rijen: {len(pcs)}")
        if pcs:
            st.write(f"Eerste: {pcs[0]}")
            pc8251 = [r for r in pcs if "8251" in str(r.get("RegioS",""))]
            if pc8251:
                st.success(f"✅ 8251 gevonden: {pc8251[0]}")
