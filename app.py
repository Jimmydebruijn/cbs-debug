import streamlit as st
import requests

BASE = "https://opendata.cbs.nl/ODataApi/OData/85318NED"

st.title("🔍 Woning + uitkering kolommen v2")

st.header("Stap 1: DataProperties")
try:
    r = requests.get(f"{BASE}/DataProperties?$format=json", timeout=20)
    st.write(f"Status: {r.status_code}")
    props = r.json().get("value", [])
    st.write(f"Aantal properties: {len(props)}")
except Exception as e:
    st.error(f"Fout: {e}")
    props = []

st.header("Stap 2: Woningkolommen zoeken")
woning = [p for p in props if any(w in p.get("Title","").lower()
          for w in ["koop","huur","woning","eigen","corporatie","particulier"])]
if woning:
    for p in woning:
        st.write(f"`{p['Key']}` — {p.get('Title','')}")
else:
    st.write("Geen woningkolommen gevonden in DataProperties")

st.header("Stap 3: Perioden ophalen")
per_key = None
try:
    r_per = requests.get(f"{BASE}/Perioden?$format=json", timeout=20)
    st.write(f"Status: {r_per.status_code}")
    st.write(f"Content-Type: {r_per.headers.get('content-type','?')}")
    if r_per.status_code == 200:
        try:
            data = r_per.json()
            perioden = data.get("value", [])
            st.write(f"Aantal perioden: {len(perioden)}")
            if perioden:
                per_key = perioden[-1]["Key"]
                st.write(f"Laatste periode: {per_key}")
        except Exception as je:
            st.error(f"JSON decode fout: {je}")
            st.code(r_per.text[:500])
    else:
        st.code(r_per.text[:500])
except Exception as e:
    st.error(f"Request fout: {e}")

st.header("Stap 4: Test data GM0344 + NL00")
if per_key:
    cols = "PersonenPerSoortUitkeringBijstand_83,PersonenPerSoortUitkeringAO_84,PersonenPerSoortUitkeringWW_85,PersonenPerSoortUitkeringAOW_86"
    if woning:
        cols += "," + ",".join(p["Key"] for p in woning[:4])

    for gm in ["GM0344", "NL00  "]:
        try:
            url = (f"{BASE}/TypedDataSet?$format=json"
                   f"&$filter=Perioden eq '{per_key}' and WijkenEnBuurten eq '{gm}'"
                   f"&$select=WijkenEnBuurten,{cols}&$top=1")
            r2 = requests.get(url, timeout=20)
            st.write(f"**{gm}** Status {r2.status_code}")
            if r2.status_code == 200:
                try:
                    d2 = r2.json()
                    if d2.get("value"):
                        st.json(d2["value"][0])
                    else:
                        st.write("Geen data (lege value)")
                except Exception as je2:
                    st.error(f"JSON fout: {je2}")
                    st.code(r2.text[:500])
            else:
                st.code(r2.text[:300])
        except Exception as e2:
            st.error(f"Fout bij {gm}: {e2}")
else:
    st.warning("Geen periode beschikbaar, kan stap 4 niet uitvoeren")
