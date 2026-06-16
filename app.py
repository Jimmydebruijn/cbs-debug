import streamlit as st
import requests

st.title("🔍 Uitkeringskolommen 85318NED")

BASE = "https://opendata.cbs.nl/ODataApi/OData/85318NED"

r = requests.get(f"{BASE}/DataProperties?$format=json", timeout=15)
props = r.json().get("value", [])
uitk = [p for p in props if any(w in p.get("Title","").lower() 
        for w in ["uitkering","bijstand","ww","arbeidsongeschikt","aow","wwb","wia","wajong"])]
for p in uitk:
    st.write(f"`{p['Key']}` — {p.get('Title','')}")
