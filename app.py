import streamlit as st
import requests

st.title("🔍 Alternatieve CBS inkomen tabellen")

# Test alternatieve tabellen die inkomen per postcode hebben
tabellen = [
    ("84639NED", "Inkomen per postcode (ouder)"),
    ("85064NED", "Inkomen personen postcode (huidig)"),
    ("83765NED", "Kerncijfers postcode"),
    ("85318NED", "Kerncijfers wijken buurten 2023"),
    ("85984NED", "Kerncijfers wijken buurten 2022"),
]

for tabel_id, omschrijving in tabellen:
    BASE = f"https://opendata.cbs.nl/ODataApi/OData/{tabel_id}"

    # Check of tabel bestaat
    r = requests.get(f"{BASE}/TypedDataSet?$format=json&$top=1", timeout=10)
    if r.status_code != 200:
        st.write(f"❌ **{tabel_id}** ({omschrijving}) — Status {r.status_code}")
        continue

    rows = r.json().get("value", [])
    if not rows:
        st.write(f"⚠️ **{tabel_id}** — Geen rijen")
        continue

    first = rows[0]
    regio = first.get("RegioS", first.get("Postcode", first.get("WijkenEnBuurten", "?")))
    st.write(f"✅ **{tabel_id}** ({omschrijving})")
    st.write(f"   Eerste RegioS/key: `{repr(regio)}`")

    # Check of inkomen kolommen beschikbaar zijn
    props = requests.get(f"{BASE}/DataProperties?$format=json", timeout=10)
    if props.status_code == 200:
        ink_cols = [p["Key"] for p in props.json().get("value",[])
                   if any(w in p.get("Title","").lower() for w in ["inkomen","income","besteedbaar","mediaan"])]
        if ink_cols:
            st.write(f"   💰 Inkomen kolommen: {ink_cols[:5]}")

    # Test postcode filter
    for prefix in ["PC", "PO", "BU", "WK"]:
        r2 = requests.get(
            f"{BASE}/TypedDataSet?$format=json"
            f"&$filter=substringof('{prefix}',RegioS)"
            f"&$top=1",
            timeout=10
        )
        if r2.status_code == 200 and r2.json().get("value"):
            test_regio = r2.json()["value"][0].get("RegioS","")
            st.write(f"   🎯 Filter '{prefix}' werkt! RegioS=`{repr(test_regio)}`")
            break
    st.divider()
