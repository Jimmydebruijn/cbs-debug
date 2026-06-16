import streamlit as st
import requests

st.title("🔍 Debug v9 — RegioS dimensie direct")

BASE = "https://opendata.cbs.nl/ODataApi/OData/85064NED"

st.header("1. RegioS tabel — hoeveel items totaal?")
r = requests.get(f"{BASE}/RegioS?$format=json&$inlinecount=allpages&$top=1", timeout=10)
st.write(f"Status: {r.status_code}")
if r.status_code == 200:
    d = r.json()
    st.write(f"odata.count: {d.get('odata.count','niet aanwezig')}")
    st.write(f"Keys: {list(d.keys())}")

st.header("2. RegioS met $top=9999")
r2 = requests.get(f"{BASE}/RegioS?$format=json&$top=9999", timeout=30)
st.write(f"Status: {r2.status_code}")
if r2.status_code == 200:
    items = r2.json().get("value", [])
    st.write(f"Totaal items: {len(items)}")
    pcs = [i for i in items if str(i.get("Key","")).strip().startswith("PC")]
    st.write(f"PC items: {len(pcs)}")
    if pcs:
        st.write(f"Eerste PC: {pcs[0]}")
        pc8251 = [i for i in pcs if "8251" in str(i.get("Key","")) or "8251" in str(i.get("Title",""))]
        if pc8251:
            st.success(f"✅ 8251: {pc8251[0]}")

st.header("3. RegioS filter op Title eq '8251'")
r3 = requests.get(
    f"{BASE}/RegioS?$format=json&$filter=Title eq '8251'",
    timeout=10
)
st.write(f"Status: {r3.status_code}")
if r3.status_code == 200:
    items3 = r3.json().get("value", [])
    st.write(f"Items: {len(items3)}")
    for i in items3:
        st.code(f"Key={repr(i.get('Key',''))} Title={repr(i.get('Title',''))}")

st.header("4. TypedDataSet met RegioS eq (exacte key uit dimensie)")
# Als we de key kennen uit test 3, probeer die hier
if st.button("Test met bekende key PC8251"):
    for key_try in ["PC8251", "PC8251 ", "PC8251  ", "PC8251   "]:
        r4 = requests.get(
            f"{BASE}/TypedDataSet?$format=json"
            f"&$filter=RegioS eq '{key_try}'"
            f"&$select=RegioS,Perioden,MediaanGestandaardiseerdInkomen_4"
            f"&$top=3",
            timeout=10
        )
        st.write(f"RegioS eq '{key_try}': Status {r4.status_code}, rijen: {len(r4.json().get('value',[]) if r4.status_code==200 else [])}")
        if r4.status_code == 200 and r4.json().get("value"):
            st.success(f"✅ Werkt! {r4.json()['value'][0]}")
            break

st.header("5. RegioS next link test")
r5 = requests.get(f"{BASE}/RegioS?$format=json&$top=100", timeout=10)
if r5.status_code == 200:
    d5 = r5.json()
    st.write(f"nextLink: {d5.get('odata.nextLink','geen')[:150]}")
    items5 = d5.get("value",[])
    st.write(f"Items in eerste batch: {len(items5)}")
    st.write(f"Laatste key: {repr(items5[-1].get('Key','')) if items5 else '?'}")
