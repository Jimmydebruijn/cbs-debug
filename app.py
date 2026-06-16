import streamlit as st
import requests

st.title("🔍 CBS 85064NED Debug v4 — Volledige fetch")

BASE = "https://opendata.cbs.nl/ODataApi/OData/85064NED"

st.header("1. Fetch $top=50000 — alle data")
if st.button("Laad alles ($top=50000) — kan 30-60 sec duren"):
    with st.spinner("Laden... (dit kan even duren)"):
        r = requests.get(
            f"{BASE}/TypedDataSet?$format=json"
            f"&$select=RegioS,Perioden,MediaanGestandaardiseerdInkomen_4"
            f"&$top=50000",
            timeout=120
        )
    st.write(f"Status: {r.status_code}")
    if r.status_code == 200:
        rows = r.json().get("value", [])
        st.write(f"Totaal rijen: {len(rows)}")
        pcs = [r for r in rows
               if str(r.get("RegioS","")).strip().startswith("PC")
               or str(r.get("RegioS","")).strip().startswith("PO")
               or str(r.get("RegioS","")).strip()[:4].isdigit()]
        st.write(f"Postcode rijen: {len(pcs)}")
        if pcs:
            st.write(f"Eerste postcode rij: {pcs[0]}")
            st.write(f"RegioS formaat: `{repr(pcs[0].get('RegioS',''))}`")
            pc8251 = [r for r in pcs if "8251" in str(r.get("RegioS",""))]
            if pc8251:
                st.success(f"✅ 8251 gevonden: {pc8251[0]}")
        # Toon rijen 9990-10010 om de grens gemeente/postcode te zien
        st.write("Rijen 9990-10010:")
        for row in rows[9990:10010]:
            st.write(f"RegioS=`{repr(row.get('RegioS',''))}` Perioden=`{row.get('Perioden','')}`")
    else:
        st.error(r.text[:300])

st.header("2. Bekijk rijen 10000-10020")
if st.button("Fetch rijen 10000-10020 via $skip"):
    r2 = requests.get(
        f"{BASE}/TypedDataSet?$format=json"
        f"&$select=RegioS,Perioden"
        f"&$top=20&$skip=10000",
        timeout=30
    )
    st.write(f"Status: {r2.status_code}")
    if r2.status_code == 200:
        for row in r2.json().get("value", []):
            st.write(f"RegioS=`{repr(row.get('RegioS',''))}` Perioden=`{row.get('Perioden','')}`")
    else:
        st.error(f"Status 500 — $skip werkt niet zonder filter")
        st.write("Probeer anders...")

st.header("3. Alleen meest recente jaar — filter op Perioden anders")
# Probeer Perioden filter via substring
if st.button("Filter via substringof Perioden"):
    r3 = requests.get(
        f"{BASE}/TypedDataSet?$format=json"
        f"&$filter=substringof('2020',Perioden)"
        f"&$select=RegioS,Perioden,MediaanGestandaardiseerdInkomen_4"
        f"&$top=20",
        timeout=30
    )
    st.write(f"Status: {r3.status_code}")
    if r3.status_code == 200:
        rows = r3.json().get("value", [])
        st.write(f"Rijen: {len(rows)}")
        for row in rows[:5]:
            st.write(f"RegioS=`{repr(row.get('RegioS',''))}` val={row.get('MediaanGestandaardiseerdInkomen_4')}")

st.header("4. Filter Perioden eq zonder quotes variant")
for periode_fmt in ["'2020JJ00'", "2020JJ00", "'2020'"]:
    r4 = requests.get(
        f"{BASE}/TypedDataSet?$format=json"
        f"&$filter=Perioden eq {periode_fmt}"
        f"&$select=RegioS,Perioden,MediaanGestandaardiseerdInkomen_4"
        f"&$top=3",
        timeout=15
    )
    st.write(f"Periode filter `{periode_fmt}`: Status {r4.status_code}, rijen: {len(r4.json().get('value',[]) if r4.status_code==200 else [])}")
