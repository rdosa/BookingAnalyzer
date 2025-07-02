import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import os
from data_processor import BookingAnalyzer

def get_tshirt_size(value):
    """T-Shirt méret meghatározása TCV érték alapján"""
    try:
        value = float(value) if value != '' else 0
        if value <= 2_000_000:
            return "XS"
        elif value <= 10_000_000:
            return "S"
        elif value <= 25_000_000:
            return "M"
        elif value <= 100_000_000:
            return "L"
        else:
            return "XL"
    except (ValueError, TypeError):
        return "XS"

def check_csv_files():
    """Ellenőrzi, hogy léteznek-e a szükséges CSV fájlok"""
    acv_exists = os.path.exists('ACV.csv')
    tcv_exists = os.path.exists('TCV.csv')
    return acv_exists, tcv_exists

def main():
    st.set_page_config(page_title="Booking Value Analyzer", layout="wide")
    st.title("📊 ACV/TCV Booking Value Elemző")
    st.markdown("12+12 hónapos gördülő elemzés architektúránként")
    
    # Fájlok ellenőrzése
    acv_exists, tcv_exists = check_csv_files()
    
    if not acv_exists or not tcv_exists:
        st.error("❌ Hiányzó CSV fájlok!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not acv_exists:
                st.error("🔍 **ACV.csv** nem található a projekt mappában")
            else:
                st.success("✅ **ACV.csv** megtalálva")
                
        with col2:
            if not tcv_exists:
                st.error("🔍 **TCV.csv** nem található a projekt mappában")
            else:
                st.success("✅ **TCV.csv** megtalálva")
        
        st.markdown("---")
        st.subheader("🔄 Alternatív: Manuális feltöltés")
        
        # Fallback: manuális feltöltés
        col1, col2 = st.columns(2)
        with col1:
            acv_file = st.file_uploader("ACV CSV fájl feltöltése", type=['csv'])
        with col2:
            tcv_file = st.file_uploader("TCV CSV fájl feltöltése", type=['csv'])
            
        if acv_file and tcv_file:
            try:
                st.success("📁 Fájlok feltöltve, inicializálás...")
                analyzer = BookingAnalyzer(acv_file_obj=acv_file, tcv_file_obj=tcv_file)
                run_analysis(analyzer)
            except Exception as e:
                st.error(f"Hiba a feltöltött fájlokkal: {str(e)}")
    else:
        # Automatikus betöltés
        try:
            st.success("✅ CSV fájlok automatikusan betöltve!")
            st.info("📂 Betöltött fájlok: ACV.csv, TCV.csv")
            
            analyzer = BookingAnalyzer(acv_file_path='ACV.csv', tcv_file_path='TCV.csv')
            run_analysis(analyzer)
            
        except Exception as e:
            st.error(f"Hiba történt az automatikus betöltéskor: {str(e)}")
            st.markdown("---")
            st.subheader("🔄 Alternatív: Manuális feltöltés")
            
            # Fallback manuális feltöltés
            col1, col2 = st.columns(2)
            with col1:
                acv_file = st.file_uploader("ACV CSV fájl feltöltése", type=['csv'])
            with col2:
                tcv_file = st.file_uploader("TCV CSV fájl feltöltése", type=['csv'])
                
            if acv_file and tcv_file:
                analyzer = BookingAnalyzer(acv_file_obj=acv_file, tcv_file_obj=tcv_file)
                run_analysis(analyzer)

def run_analysis(analyzer):
    """Elemzés futtatása a megadott analyzer-rel"""
    # Felhasználói vezérlők
    st.sidebar.header("⚙️ Beállítások")
    
    # Hónap választása
    available_months = analyzer.get_available_months()
    selected_month = st.sidebar.selectbox(
        "Válassza ki a végpont hónapot:",
        available_months,
        help="Az elemzés ezen hónaptól visszamenőleg 12 hónapot fog vizsgálni"
    )
    
    # Architektúra szűrő - TÖBBSZÖRÖS VÁLASZTÁS
    available_architectures = analyzer.get_architectures()
    selected_architectures = st.sidebar.multiselect(
        "Architektúrák kiválasztása:",
        options=available_architectures,
        default=[],
        help="Hagyja üresen az összes architektúra megjelenítéséhez, vagy válasszon ki egy vagy több architektúrát."
    )
    
    # Ha semmi sincs kiválasztva, akkor az összes architektúrát mutatjuk
    if not selected_architectures:
        st.sidebar.info("💡 Összes architektúra megjelenítve")
        arch_filter = None
    else:
        st.sidebar.success(f"✅ {len(selected_architectures)} architektúra kiválasztva")
        arch_filter = selected_architectures
    
    # Elemzés futtatása
    results = analyzer.get_rolling_analysis(selected_month, arch_filter)
    
    # Eredmények megjelenítése
    display_results(st, results)

def display_results(st, results):
    """Eredmények megjelenítése"""
    try:
        period_info = results.get('period_info', {})
        
        # Kiválasztott architektúrák megjelenítése
        selected_arch = period_info.get('selected_architectures', 'Összes')
        if isinstance(selected_arch, list):
            st.info(f"🎯 Kiválasztott architektúrák: {', '.join(selected_arch)}")
        else:
            st.info(f"🎯 Megjelenített architektúrák: {selected_arch}")
        
        # Időszak információk
        st.subheader("📅 Elemzési időszakok")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Aktuális időszak",
                     f"{period_info.get('current_start', '')} - {period_info.get('current_end', '')}")
        
        with col2:
            st.metric("Referencia időszak",
                     f"{period_info.get('reference_start', '')} - {period_info.get('reference_end', '')}")
        
        # ACV elemzés
        st.subheader("💰 ACV Analysis")
        acv_current = results.get('acv_current', {})
        acv_reference = results.get('acv_reference', {})
        
        if acv_current and acv_reference:
            display_comparison_table(st, acv_current, acv_reference, "ACV", "$")
        
        # TCV elemzés
        st.subheader("📊 TCV Analysis")
        tcv_current = results.get('tcv_current', {})
        tcv_reference = results.get('tcv_reference', {})
        
        if tcv_current and tcv_reference:
            display_comparison_table(st, tcv_current, tcv_reference, "TCV", "$")
            
    except Exception as e:
        st.error(f"Eredmény megjelenítési hiba: {e}")

def display_comparison_table(st, current_data, reference_data, metric_name, currency):
    """Összehasonlító táblázat megjelenítése - SZÍNES T-SHIRT SIZING-gel"""
    try:
        architectures = set(current_data.keys()).union(set(reference_data.keys()))
        table_data = []
        
        for arch in sorted(architectures):
            current_val = current_data.get(arch, 0)
            reference_val = reference_data.get(arch, 0)
            
            # BIZTONSÁGOS numerikus konverzió
            try:
                current_val = float(current_val) if current_val != '' else 0
                reference_val = float(reference_val) if reference_val != '' else 0
            except (ValueError, TypeError):
                current_val = 0
                reference_val = 0
            
            # Változás számítás
            if reference_val != 0:
                change = ((current_val - reference_val) / reference_val) * 100
                change_str = f"{change:+.1f}%"
            else:
                change_str = "N/A"
            
            # Abszolút változás
            abs_change = current_val - reference_val
            
            # Táblázat sor összeállítása
            row_data = {
                'Architecture': arch,
                f'Aktuális {metric_name}': f"{currency}{current_val:,.0f}",
                f'Referencia {metric_name}': f"{currency}{reference_val:,.0f}",
                'Változás %': change_str,
                'Abszolút változás': f"{currency}{abs_change:+,.0f}"
            }
            
            # T-SHIRT SIZING CSAK TCV-NÉL
            if metric_name == "TCV":
                tshirt_size = get_tshirt_size(current_val)
                
                # Színkódok a méretekhez
                size_colors = {
                    'XS': '🔴',
                    'S': '🟠', 
                    'M': '🟡',
                    'L': '🟢',
                    'XL': '🔵'
                }
                colored_size = f"{size_colors.get(tshirt_size, '')} {tshirt_size}"
                
                # T-shirt size az elejére
                row_data = {
                    'Size': colored_size,
                    **row_data  # összes többi oszlop
                }
            
            table_data.append(row_data)
        
        df_display = pd.DataFrame(table_data)
        
        # T-SHIRT SIZING LEGEND MEGJELENÍTÉSE TCV-NÉL
        if metric_name == "TCV":
            st.markdown("""
**📏 T-Shirt Sizing Legend:**  
🔴 **XS**: ≤ 2M | 🟠 **S**: 2M - 10M | 🟡 **M**: 10M - 25M | 🟢 **L**: 25M - 100M | 🔵 **XL**: > 100M [USD values]
""")
        
        st.dataframe(df_display, use_container_width=True)
        
    except Exception as e:
        st.error(f"Táblázat megjelenítési hiba: {e}")

if __name__ == "__main__":
    main()
