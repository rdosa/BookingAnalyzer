import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import os
from data_processor import BookingAnalyzer # Feltételezve, hogy a data_processor.py a gyökérkönyvtárban van

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
    
    # Fájlok ellenőrzése
    acv_exists, tcv_exists = check_csv_files()
    
    analyzer = None
    
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
                analyzer = BookingAnalyzer(acv_file_obj=acv_file, tcv_file_obj=tcv_file)
            except Exception as e:
                st.error(f"Hiba a feltöltött fájlokkal: {str(e)}")
    else:
        # Automatikus betöltés - CSENDES MÓD
        try:
            analyzer = BookingAnalyzer(acv_file_path='ACV.csv', tcv_file_path='TCV.csv')
        except Exception as e:
            st.error(f"Hiba történt az automatikus betöltéskor: {str(e)}")
            
            # Fallback manuális feltöltés
            st.markdown("---")
            st.subheader("🔄 Alternatív: Manuális feltöltés")
            col1, col2 = st.columns(2)
            with col1:
                acv_file = st.file_uploader("ACV CSV fájl feltöltése", type=['csv'])
            with col2:
                tcv_file = st.file_uploader("TCV CSV fájl feltöltése", type=['csv'])
            
            if acv_file and tcv_file:
                try:
                    analyzer = BookingAnalyzer(acv_file_obj=acv_file, tcv_file_obj=tcv_file)
                except Exception as e:
                    st.error(f"Hiba a feltöltött fájlokkal: {str(e)}")
    
    if analyzer:
        run_analysis(analyzer)


def run_analysis(analyzer):
    """Elemzés futtatása a megadott analyzer-rel"""
    
    # OLDALSÁV CÍME ÉS BEÁLLÍTÁSOK
    st.sidebar.title("📊 ACV/TCV Booking Value Elemző")
    # st.sidebar.markdown("12+12 hónapos gördülő elemzés architektúránként - **Predikciós funkcióval**")
    # st.sidebar.markdown("---")

    # Fájlok mentési dátumának kiírása
    st.sidebar.subheader("📄 Adatok frissessége:")
    st.sidebar.markdown(f"**ACV:** `{analyzer.acv_file_creation_date}`")
    st.sidebar.markdown(f"**TCV:** `{analyzer.tcv_file_creation_date}`")
    st.sidebar.markdown("---")
    
    # Felhasználói vezérlők
    st.sidebar.header("⚙️ Beállítások")
    
    # Hónap választása
    available_months = analyzer.get_available_months()
    
    # Alapértelmezett értékként az aktuális hónapot állítjuk be
    default_index = 0
    try:
        current_fiscal_month = analyzer.current_fiscal_month
        if current_fiscal_month in available_months:
            default_index = available_months.index(current_fiscal_month)
    except Exception as e:
        st.sidebar.warning(f"Nem sikerült beállítani az alapértelmezett hónapot: {e}")
        pass
    
    selected_month = st.sidebar.selectbox(
        "Válaszd ki a végpont hónapot:",
        available_months,
        index=default_index,
        help="Történeti elemzéshez múltbeli, predikciós elemzéshez jövőbeli hónapot válassz"
    )
    
    # Elemzési típus meghatározása
    analysis_type = analyzer.get_analysis_type(selected_month)

    # Jelzések az elemzési típus alapján
    if analysis_type == 'future_prediction':
        st.sidebar.warning("🔮 **PREDIKCIÓS MÓD**")
        st.sidebar.info("📈 A rendszer kiszámolja a szükséges booking target-eket.")
    elif analysis_type == 'current_month_prediction':
        st.sidebar.info("✨ **AKTUÁLIS STÁTUSZ** - predikcióval")
        st.sidebar.info("⚠️ A hónap még nem zárult le. A meglévő adatok kiegészülnek predikciós targetekkel.")
    else: # historical
        st.sidebar.success("📊 **TÖRTÉNETI ELEMZÉS** - Múltbeli adatok")
    
    # Architektúra szűrő - TÖBBSZÖRÖS VÁLASZTÁS
    available_architectures = analyzer.get_architectures()
    selected_architectures = st.sidebar.multiselect(
        "Architektúrák kiválasztása:",
        options=available_architectures,
        default=[],
        help="Hagyd üresen az összes architektúra megjelenítéséhez, vagy válassz ki egy vagy több architektúrát"
    )
    
    # Ha semmi nincs kiválasztva, akkor az összes architektúrát mutatjuk
    if not selected_architectures:
        st.sidebar.info("💡 Összes architektúra megjelenítve")
        arch_filter = None
    else:
        st.sidebar.success(f"✅ {len(selected_architectures)} architektúra kiválasztva")
        arch_filter = selected_architectures
    
    # Dashboard nézet választó - CSAK AKTUÁLIS/PREDIKCIÓS MÓDBAN
    st.sidebar.markdown("---")
    st.sidebar.header("📊 Megjelenítés")
    
    view_mode_options = ["📊 Főképernyő"]
    # Bővítés: Az aktuális hónap elemzésénél is elérhető a "Hasonló a történelmihez" nézet
    if analysis_type != 'historical': 
        view_mode_options.extend(["🔍 Részletes Index Elemzés", "📚 Útmutató"])
    
    # Ha az elemzési típus 'current_month_prediction', akkor adjunk hozzá egy extra nézetet
    if analysis_type == 'current_month_prediction':
        view_mode_options.insert(1, "📜 Aktuális Hónap - Összehasonlító") # Beszúrjuk a második helyre

    # Ellenőrizzük, hogy a session_state-ben tárolt view_mode még érvényes-e
    if 'view_mode' in st.session_state and st.session_state['view_mode'] not in view_mode_options:
        st.session_state['view_mode'] = "📊 Főképernyő" # Visszaállítjuk, ha már nem érvényes
        
    view_mode = st.sidebar.selectbox(
        "Dashboard nézet:",
        options=view_mode_options,
        index=view_mode_options.index(st.session_state.get('view_mode', "📊 Főképernyő")), # Beállítjuk a mentett értéket
        key="view_mode_selector", # Explicit kulcs hozzáadása
        help="Válaszd ki a megjelenítendő nézetet"
    )
    # A selectbox változását eltároljuk a session_state-ben, ha különbözik
    if st.session_state.get('view_mode', "📊 Főképernyő") != view_mode:
        st.session_state['view_mode'] = view_mode
        st.rerun() # Frissíteni kell, ha nézetet váltunk

    # Elemzés futtatása
    results = analyzer.get_rolling_analysis(selected_month, arch_filter)
    
    # Eredmények megjelenítése
    display_results(st, results, view_mode, analysis_type)

def display_results(st, results, view_mode, analysis_type):
    """Eredmények megjelenítése - normál, aktuális és predikciós módban"""
    try:
        period_info = results.get('period_info', {})
        
        if view_mode == "📚 Útmutató":
            display_guidance_page(st)
            return
        elif view_mode == "🔍 Részletes Index Elemzés":
            display_detailed_analysis_page(st, results, period_info, analysis_type)
            return
        elif view_mode == "📜 Aktuális Hónap - Összehasonlító" and analysis_type == 'current_month_prediction':
            display_current_month_detailed_results(st, results, period_info)
            return
        
        # Főképernyő megjelenítése (ez tartalmazza a predikciós főképernyőt is)
        if analysis_type == 'historical':
            display_historical_results(st, results, period_info)
        else: # current_month_prediction vagy future_prediction
            display_prediction_main_screen(st, results, period_info, analysis_type)

    except Exception as e:
        st.error(f"Eredmény megjelenítési hiba: {e}")

def display_current_month_detailed_results(st, results, period_info):
    """
    Az aktuális hónap elemzésének részletes (hasonló a történelmihez) megjelenítése.
    Ez a nézet az aktuális hónapban már meglévő adatokat hasonlítja össze a baseline-nal.
    """
    st.title("📜 AKTUÁLIS HÓNAP - Összehasonlító Elemzés")
    st.markdown("⚠️ Ebben a nézetben az aktuális oszlop a hónapban *már lekönyvelt* booking-okat mutatja.")
    st.markdown("---")

    # Időszak információk
    st.subheader("📅 Elemzési időszakok")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Aktuális 12 hónap",
                 f"{period_info.get('future_start_fiscal', '')} - {period_info.get('future_end_fiscal', '')}")
    with col2:
        st.metric("Referencia 12 hónap",
                 f"{period_info.get('baseline_start_fiscal', '')} - {period_info.get('baseline_end_fiscal', '')}")
    with col3:
        st.metric("Utolsó adatpont dátuma", period_info.get('last_data_point', ''))

    # ACV elemzés
    st.subheader("💰 ACV Analysis (Már meglévő vs. Baseline)")
    # Fontos: itt a 'acv_current'-et használjuk, ami az _get_current_month_analysis()-ből jön,
    # és tartalmazza a már meglévő adatokat az last_data_point_date-ig.
    acv_current = results.get('acv_current', {})
    acv_baseline = results.get('acv_baseline', {})

    if acv_current and acv_baseline:
        display_comparison_table(st, acv_current, acv_baseline, "ACV", "$")
    
    # TCV elemzés
    st.subheader("📊 TCV Analysis (Már meglévő vs. Baseline)")
    tcv_current = results.get('tcv_current', {})
    tcv_baseline = results.get('tcv_baseline', {})
    if tcv_current and tcv_baseline:
        display_comparison_table(st, tcv_current, tcv_baseline, "TCV", "$")

    # Visszagomb a predikciós nézetre
    st.markdown("---")
    if st.button("← Vissza az Aktuális Státusz (Predikciós) nézetre", key="back_to_prediction_current_month"):
        st.session_state['view_mode'] = "📊 Főképernyő" # A predikciós nézet a főképernyő 'current_month_prediction' esetén
        st.rerun()

def display_historical_results(st, results, period_info):
    """Történeti elemzés eredményeinek megjelenítése"""
    st.title("📊 TÖRTÉNETI ELEMZÉS")
    st.markdown("---")

    # Időszak információk
    st.subheader("📅 Elemzési időszakok")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Aktuális 12 hónap",
                 f"{period_info.get('current_start_fiscal', '')} - {period_info.get('current_end_fiscal', '')}")
    with col2:
        st.metric("Referencia 12 hónap",
                 f"{period_info.get('reference_start_fiscal', '')} - {period_info.get('reference_end_fiscal', '')}")
    
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

def display_prediction_main_screen(st, results, period_info, analysis_type):
    """Predikciós (vagy aktuális hónap) elemzés főképernyőjének megjelenítése"""
    if analysis_type == 'current_month_prediction':
        st.title("✨ AKTUÁLIS STÁTUSZ - predikcióval")
        # Eltávolítva: st.info(f"Adatok a {period_info.get('last_data_point', 'ismeretlen')} dátumig vannak feldolgozva.")
    else: # future_prediction
        st.title("🔮 PREDIKCIÓS MÓD")
        # Eltávolítva: st.info(f"Jelenlegi adatok a {period_info.get('last_data_point', 'ismeretlen')} dátumig állnak rendelkezésre. A hiányzó időszakra vonatkozó booking még nem történt meg.")
    
    st.markdown("---")

    st.subheader("📅 Elemzési időszakok")
    col1, col2 = st.columns(2)
    with col1:
        if analysis_type == 'current_month_prediction':
             st.metric("Aktuális 12 hónap (részben meglévő)",
                      f"{period_info.get('future_start_fiscal', '')} - {period_info.get('future_end_fiscal', '')}")
        else: # future_prediction
            st.metric("Predikciós 12 hónap",
                     f"{period_info.get('future_start_fiscal', '')} - {period_info.get('future_end_fiscal', '')}")
    with col2:
        st.metric("Baseline 12 hónap",
                 f"{period_info.get('baseline_start_fiscal', '')} - {period_info.get('baseline_end_fiscal', '')}")
    
    # ACV predikciós elemzés - EGYSZERŰSÍTETT
    st.subheader("💰 ACV Index-alapú Elemzés")
    acv_existing = results.get('acv_current', {})
    acv_baseline = results.get('acv_baseline', {})
    acv_index_targets = results.get('acv_index_targets', {})
    acv_needed_by_index = results.get('acv_needed_by_index', {})
    
    if acv_existing and acv_baseline:
        display_simplified_prediction_table(st, acv_existing, acv_baseline,
                                           acv_index_targets, acv_needed_by_index, "ACV", "$")
    
    # TCV predikciós elemzés - EGYSZERŰSÍTETT
    st.subheader("📊 TCV Index-alapú Elemzés")
    tcv_existing = results.get('tcv_current', {})
    tcv_baseline = results.get('tcv_baseline', {})
    tcv_index_targets = results.get('tcv_index_targets', {})
    tcv_needed_by_index = results.get('tcv_needed_by_index', {})
    
    if tcv_existing and tcv_baseline:
        display_simplified_prediction_table(st, tcv_existing, tcv_baseline,
                                           tcv_index_targets, tcv_needed_by_index, "TCV", "$")
    
    # NAVIGÁCIÓS LINKEK
    st.markdown("---")
    st.markdown("### 🔗 További részletek")
    
    # A gombok elhelyezéséhez használjunk oszlopokat
    cols = st.columns(3 if analysis_type == 'current_month_prediction' else 2) # Három oszlop, ha aktuális hónap
    
    with cols[0]:
        if st.button("🔍 Részletes Index Elemzés", key="detail_button_main"):
            st.session_state['view_mode'] = "🔍 Részletes Index Elemzés" # Módváltás
            st.rerun()

    # Új gomb csak akkor, ha az elemzés típusa 'current_month_prediction'
    if analysis_type == 'current_month_prediction':
        with cols[1]:
            if st.button("📜 Aktuális Hónap - Összehasonlító", key="current_month_comparison_button"):
                st.session_state['view_mode'] = "📜 Aktuális Hónap - Összehasonlító"
                st.rerun()
        with cols[2]: # A harmadik oszlopba kerül az útmutató gomb
            if st.button("📚 Index Útmutató", key="guidance_button_main"):
                st.session_state['view_mode'] = "📚 Útmutató" # Módváltás
                st.rerun()
    else: # Ha nem current_month_prediction, akkor csak két oszlop marad
        with cols[1]:
            if st.button("📚 Index Útmutató", key="guidance_button_main"):
                st.session_state['view_mode'] = "📚 Útmutató" # Módváltás
                st.rerun()

def display_simplified_prediction_table(st, existing_data, baseline_data, index_targets, needed_by_index, metric_name, currency):
    """Egyszerűsített predikciós táblázat a főképernyőhöz"""
    try:
        architectures = set(existing_data.keys()).union(set(baseline_data.keys()))
        
        # Csak architektúra szintű összefoglaló táblázat
        summary_data = []
        for arch in sorted(architectures):
            if arch == 'Összes':
                continue
                
            existing_val = float(existing_data.get(arch, 0) if existing_data.get(arch) is not None else 0)
            baseline_val = float(baseline_data.get(arch, 0) if baseline_data.get(arch) is not None else 0)
            
            # Jelenlegi index számítása
            current_index_display_numeric = 0
            if baseline_val != 0:
                current_growth = ((existing_val - baseline_val) / abs(baseline_val)) * 100
                # Az index 0-tól 9-ig a százalékos növekedést jelenti, 10 pedig >9%
                if current_growth >= 10:
                    current_index_display_numeric = 10
                elif current_growth > 0: # 0.01% - 9.99% között
                    current_index_display_numeric = int(current_growth) 
                else:
                    current_index_display_numeric = 0 # Negatív vagy 0 növekedés
            
            current_index_display = f"📊 {current_index_display_numeric}"
            
            # Kulcs értékek (5% és 10%+ növekedéshez szükséges értékek)
            needed_for_5 = needed_by_index.get(arch, {}).get(5, 0)
            needed_for_10 = needed_by_index.get(arch, {}).get(10, 0)
            
            row_data = {
                'Architecture': arch,
                f'Meglévő {metric_name}': f"{currency}{existing_val:,.0f}",
                f'Baseline {metric_name}': f"{currency}{baseline_val:,.0f}",
                'Jelenlegi Index': current_index_display,
                f'Index 5-höz szükséges': f"{currency}{needed_for_5:,.0f}",
                f'Index 10-hez szükséges': f"{currency}{needed_for_10:,.0f}"
            }
            
            # T-SHIRT SIZING CSAK TCV-NÉL
            if metric_name == "TCV":
                tshirt_size = get_tshirt_size(existing_val)
                size_colors = {'XS': '🔴', 'S': '🟠', 'M': '🟡', 'L': '🟢', 'XL': '🔵'}
                colored_size = f"{size_colors.get(tshirt_size, '')} {tshirt_size}"
                row_data = {'Size': colored_size, **row_data}
            
            summary_data.append(row_data)
        
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(df_summary, use_container_width=True)
        
        # T-SHIRT SIZING LEGEND CSAK TCV-NÉL
        if metric_name == "TCV":
            st.markdown("""**📏 T-Shirt Sizing:** 🔴 XS: ≤2M | 🟠 S: 2-10M | 🟡 M: 10-25M | 🟢 L: 25-100M | 🔵 XL: >100M [USD]""")
    
    except Exception as e:
        st.error(f"Egyszerűsített táblázat hiba: {e}")

def display_detailed_analysis_page(st, results, period_info, analysis_type):
    """Részletes index elemzés oldal"""
    
    if analysis_type == 'current_month_prediction':
        st.title("🔍 Részletes Index Elemzés - Aktuális Státusz")
        # Eltávolítva: st.info(f"Adatok a {period_info.get('last_data_point', 'ismeretlen')} dátumig vannak feldolgozva.")
    else: # future_prediction
        st.title("🔍 Részletes Index Elemzés - Predikciós Mód")
        # Eltávolítva: st.info(f"Jelenlegi adatok a {period_info.get('last_data_point', 'ismeretlen')} dátumig állnak rendelkezésre.")

    st.markdown("---")
    
    # Visszagomb (a főképernyőre navigál)
    if st.button("← Vissza a főképernyőre", key="back_button_detail"):
        st.session_state['view_mode'] = "📊 Főképernyő"
        st.rerun()
    
    st.markdown("---")
    
    # ACV részletes elemzés
    st.subheader("💰 ACV Részletes Index Elemzés")
    acv_data = results.get('acv_current', {})
    acv_baseline = results.get('acv_baseline', {})
    acv_targets = results.get('acv_index_targets', {})
    acv_needed = results.get('acv_needed_by_index', {})
    
    if acv_data:
        display_detailed_metrics_page(st, acv_data, acv_baseline, acv_targets, acv_needed, "ACV", "$")
    
    st.markdown("---")
    
    # TCV részletes elemzés
    st.subheader("📊 TCV Részletes Index Elemzés")
    tcv_data = results.get('tcv_current', {})
    tcv_baseline = results.get('tcv_baseline', {})
    tcv_targets = results.get('tcv_index_targets', {})
    tcv_needed = results.get('tcv_needed_by_index', {})
    
    if tcv_data:
        display_detailed_metrics_page(st, tcv_data, tcv_baseline, tcv_targets, tcv_needed, "TCV", "$")

def display_detailed_metrics_page(st, existing_data, baseline_data, index_targets, needed_by_index, metric_name, currency):
    """Részletes metrika elemzés - teljesítmény oszlop nélkül"""
    architectures = set(existing_data.keys()).union(set(baseline_data.keys()))
    
    # Architektúra választó
    selected_arch = st.selectbox(
        f"Válassz architektúrát a {metric_name} részletes nézethez:",
        options=[arch for arch in sorted(architectures) if arch != 'Összes'],
        key=f"detail_page_select_{metric_name}" # Egyedi kulcs
    )
    
    if selected_arch and selected_arch in index_targets:
        existing_val = float(existing_data.get(selected_arch, 0) if existing_data.get(selected_arch) is not None else 0)
        baseline_val = float(baseline_data.get(selected_arch, 0) if baseline_data.get(selected_arch) is not None else 0)
        
        st.markdown(f"#### 🏗️ {selected_arch} - Részletes Index Analízis")
        
        # Alap információk
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"Jelenlegi {metric_name}", f"{currency}{existing_val:,.0f}")
        with col2:
            st.metric(f"Baseline {metric_name}", f"{currency}{baseline_val:,.0f}")
        with col3:
            current_performance_str = "N/A"
            if baseline_val != 0:
                current_performance = ((existing_val - baseline_val) / abs(baseline_val)) * 100
                current_performance_str = f"{current_performance:+.1f}%"
            st.metric("Jelenlegi teljesítmény", current_performance_str)
        
        # Index táblázat
        index_data = []
        arch_targets = index_targets.get(selected_arch, {})
        arch_needed = needed_by_index.get(selected_arch, {})
        
        for index in range(11):  # 0-10
            target_val = arch_targets.get(index, 0)
            needed_val = arch_needed.get(index, 0)
            
            # Státusz meghatározása
            if existing_val >= target_val:
                status = "✅ Elérve"
            elif needed_val <= (target_val * 0.1) and target_val > 0:  # 10%-on belül
                status = "🟡 Közel"
            else:
                status = "🔴 Távolibb"

            # Növekedési ráta kijelzése
            growth_display = f"{index}%" if index < 10 else ">9%"
            
            index_data.append({
                'Index': f"📊 {index}",
                'Státusz': status,
                f'Target {metric_name}': f"{currency}{target_val:,.0f}",
                f'Szükséges további': f"{currency}{needed_val:,.0f}",
                'Növekedés baseline-hoz': growth_display
            })
        
        df_index = pd.DataFrame(index_data)
        st.dataframe(df_index, use_container_width=True)

def display_guidance_page(st):
    """Index útmutató oldal"""
    st.title("📚 Index Rendszer Útmutató")
    st.markdown("---")
    
    # Visszagomb (a főképernyőre navigál)
    if st.button("← Vissza a főképernyőre", key="back_button_guidance"):
        st.session_state['view_mode'] = "📊 Főképernyő"
        st.rerun()

    st.markdown("---")
    
    st.markdown("""
## 📋 Index Magyarázat

- **Index 0**: Baseline szint (egy évvel ezelőtti teljesítmény, 0% növekedés)
- **Index 1**: 1% növekedés a baseline-hoz képest
- **Index 2**: 2% növekedés a baseline-hoz képest
- **Index 5**: 5% növekedés a baseline-hoz képest
- **Index 9**: 9% növekedés a baseline-hoz képest
- **Index 10**: >9% növekedés a baseline-hoz képest (10%-ként számítva)

## 🎯 Metrika Számítás

**📈 Teljesítmény számítás**: `(Aktuális - Baseline) / |Baseline| × 100%`

**📊 Target számítás**: `Baseline × (1 + Index%)`

## 📏 T-Shirt Sizing (csak TCV-nél)

- 🔴 **XS**: ≤ 2M USD
- 🟠 **S**: 2M - 10M USD
- 🟡 **M**: 10M - 25M USD
- 🟢 **L**: 25M - 100M USD
- 🔵 **XL**: > 100M USD

## 🔮 Predikciós Mód Működése

A predikciós mód segít felmérni, mennyi bookingra van még szükség egy adott jövőbeli (vagy még nem lezárt aktuális) 12 hónapos periódusban a kitűzött index-targetek eléréséhez.

1.  **Baseline időszak**: Az egy évvel korábbi ugyanazon 12 hónapos időszak. Ez szolgál referenciaként, 0%-os növekedési célként.
2.  **Jövőbeli (Target) időszak**: A kiválasztott végpontig tartó 12 hónap. Ha az aktuális hónapot választod, akkor ez a még nem lezárt aktuális 12 hónapos periódusra vonatkozik.
3.  **Meglévő booking**: Az `ACV.csv` és `TCV.csv` fájlokban szereplő, már lekönyvelt booking-ok a Jövőbeli (Target) időszakban, **de csak az utolsó adatpont dátumáig bezárólag**.
4.  **Index target-ek**: A baseline teljesítménye alapján számított növekedési célok az egyes indexszintekre (0% - >9%).
5.  **Szükséges booking**: Ez az az összeg (ACV vagy TCV), ami még hiányzik az egyes index-targetek eléréséhez a Jövőbeli (Target) időszakban, figyelembe véve a már meglévő booking-okat.

## 📊 Dashboard Használata

-   **Főképernyő**: Összefoglaló táblázatok minden architektúrához, kiemelve a jelenlegi indexet és a kulcsfontosságú targetekhez (5% és 10%+) szükséges összeget.
-   **Részletes Index Elemzés**: Architektúránként részletes bontás index szintenként, megmutatva a targeteket, a szükséges bookingokat és az aktuális státuszt.
-   **Útmutató**: Ez az oldal - technikai részletek és magyarázatok a rendszer működéséről.
""")

def display_comparison_table(st, current_data, reference_data, metric_name, currency):
    """Történeti összehasonlító táblázat megjelenítése - SZÍNES T-SHIRT SIZING-gel"""
    try:
        architectures = set(current_data.keys()).union(set(reference_data.keys()))
        table_data = []
        
        for arch in sorted(architectures):
            if arch == 'Összes':
                continue  

            current_val = current_data.get(arch, 0)
            reference_val = reference_data.get(arch, 0)
            
            # BIZTONSÁGOS numerikus konverzió
            try:
                current_val = float(current_val) if current_val is not None else 0
                reference_val = float(reference_val) if reference_val is not None else 0
            except (ValueError, TypeError):
                current_val = 0
                reference_val = 0
            
            # Változás számítás
            change_str = "N/A"
            if reference_val != 0:
                change = ((current_val - reference_val) / abs(reference_val)) * 100
                change_str = f"{change:+.1f}%"
            
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
                    'XS': '🔴', 'S': '🟠', 'M': '🟡', 'L': '🟢', 'XL': '🔵'
                }
                colored_size = f"{size_colors.get(tshirt_size, '')} {tshirt_size}"
                # T-shirt size az elejére
                row_data = {'Size': colored_size, **row_data}
            
            table_data.append(row_data)
        
        df_display = pd.DataFrame(table_data)
        
        # T-SHIRT SIZING LEGEND MEGJELENÍTÉSE TCV-NÉL
        if metric_name == "TCV":
            st.markdown("""**📏 T-Shirt Sizing Legend:**
🔴 **XS**: ≤ 2M | 🟠 **S**: 2M - 10M | 🟡 **M**: 10M - 25M | 🟢 **L**: 25M - 100M | 🔵 **XL**: > 100M [USD values]""")
        
        st.dataframe(df_display, use_container_width=True)
        
    except Exception as e:
        st.error(f"Táblázat megjelenítési hiba: {e}")

if __name__ == "__main__":
    if 'view_mode' not in st.session_state:
        st.session_state['view_mode'] = "📊 Főképernyő"
    main()
