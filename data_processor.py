import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar
import io
import os # Hozzáadva a fájl dátumának lekéréséhez

class BookingAnalyzer:
    """ACV/TCV Booking Value Analyzer with Prediction Capability"""
    
    def __init__(self, acv_file_path=None, tcv_file_path=None, acv_file_obj=None, tcv_file_obj=None):
        """BookingAnalyzer inicializálása"""
        print("BookingAnalyzer inicializálása...")
        try:
            # ACV fájl betöltése
            if acv_file_path:
                self.acv_df = pd.read_csv(acv_file_path)
                self.acv_file_creation_date = datetime.fromtimestamp(os.path.getmtime(acv_file_path)).strftime('%Y-%m-%d')
                print(f"✅ ACV betöltve fájlból: {acv_file_path}")
            elif acv_file_obj:
                # Memóriában lévő fájl esetén nincs mód a creation date lekérésére, 
                # ezért az aktuális dátumot használjuk fallbackként.
                self.acv_df = pd.read_csv(acv_file_obj)
                self.acv_file_creation_date = datetime.now().strftime('%Y-%m-%d') 
                print("✅ ACV betöltve feltöltött fájlból")
            else:
                raise ValueError("❌ Nincs ACV fájl megadva")
            
            # TCV fájl betöltése
            if tcv_file_path:
                self.tcv_df = pd.read_csv(tcv_file_path)
                self.tcv_file_creation_date = datetime.fromtimestamp(os.path.getmtime(tcv_file_path)).strftime('%Y-%m-%d')
                print(f"✅ TCV betöltve fájlból: {tcv_file_path}")
            elif tcv_file_obj:
                # Memóriában lévő fájl esetén nincs mód a creation date lekérésére, 
                # ezért az aktuális dátumot használjuk fallbackként.
                self.tcv_df = pd.read_csv(tcv_file_obj)
                self.tcv_file_creation_date = datetime.now().strftime('%Y-%m-%d')
                print("✅ TCV betöltve feltöltött fájlból")
            else:
                raise ValueError("❌ Nincs TCV fájl megadva")
            
            # OSZLOPOK DIAGNOSZTIZÁLÁSA
            print(f"📊 ACV oszlopok: {list(self.acv_df.columns)}")
            print(f"📊 TCV oszlopok: {list(self.tcv_df.columns)}")
            
            # ARCHITEKTÚRA MAPPING DEFINIÁLÁSA
            self.architecture_mapping = {
                'ENTERPRISE NETWORKING': 'NETWORKING*',
                'IOT': 'NETWORKING*',
                'DATA CENTER GROUP': 'CLOUD & AI',
                'SERVICES': 'SERVICES*',
                'OTHER': 'SERVICES*',
            }
            print(f"🏗️ Architektúra mapping: {self.architecture_mapping}")
            
            # Adatok feldolgozása
            self._process_data()
            
            # Aktuális dátum meghatározása a legutóbbi adatok alapján
            # Módosítás: _determine_current_period-ot hívjuk, de már nem az üzenethez
            self._determine_current_period()
            
        except Exception as e:
            print(f"❌ Hiba az inicializáláskor: {e}")
            raise

    def _determine_current_period(self):
        """Aktuális időszak meghatározása az adatok alapján"""
        try:
            # A legutóbbi dátumok keresése
            acv_latest = self.acv_df['Date'].max()
            tcv_latest = self.tcv_df['Date'].max()
            
            # A legfrissebb dátum használata
            latest_date = max(acv_latest, tcv_latest)
            self.current_fiscal_month = self._to_fiscal_month(latest_date)
            # A legutolsó nap, amire van adat
            self.last_data_point_date = latest_date
            print(f"📅 Aktuális fiscal month: {self.current_fiscal_month} (utolsó adatpont: {self.last_data_point_date.strftime('%Y-%m-%d')})")
        except Exception as e:
            print(f"❌ Aktuális időszak meghatározási hiba: {e}")
            self.current_fiscal_month = "Jul FY2025"
            self.last_data_point_date = datetime.now() # Fallback

    def _process_data(self):
        """Adatok feldolgozása és előkészítése"""
        print("Adatok feldolgozása...")
        try:
            # Dátum oszlop keresése és egységesítése
            self._process_date_columns()
            
            # Architektúra oszlop egységesítése
            self._process_architecture_columns()
            
            # ARCHITEKTÚRA MAPPING ALKALMAZÁSA
            self._apply_architecture_mapping()
            
            # VALUE OSZLOPOK AZONOSÍTÁSA
            self._identify_value_columns()
            
            # FiscalMonth generálása (ha szükséges)
            if 'FiscalMonth' not in self.acv_df.columns:
                if 'FISCAL_MONTH_NAME' in self.acv_df.columns:
                    self.acv_df['FiscalMonth'] = self.acv_df['FISCAL_MONTH_NAME']
                else:
                    self.acv_df['FiscalMonth'] = self.acv_df['Date'].apply(self._to_fiscal_month)
            
            if 'FiscalMonth' not in self.tcv_df.columns:
                if 'FISCAL_MONTH_NAME' in self.tcv_df.columns:
                    self.tcv_df['FiscalMonth'] = self.tcv_df['FISCAL_MONTH_NAME']
                else:
                    self.tcv_df['FiscalMonth'] = self.tcv_df['Date'].apply(self._to_fiscal_month)
            
            print("✅ Adatok feldolgozva")
        except Exception as e:
            print(f"❌ Adatfeldolgozási hiba: {e}")
            raise

    def _apply_architecture_mapping(self):
        """Architektúra mapping alkalmazása"""
        try:
            print("🔄 Architektúra mapping alkalmazása...")
            
            # ACV architektúra mapping
            original_acv_arch = self.acv_df['Architecture'].value_counts()
            print(f"📊 Eredeti ACV architektúrák: {dict(original_acv_arch)}")
            self.acv_df['Architecture'] = self.acv_df['Architecture'].map(lambda x: self.architecture_mapping.get(x, x))
            
            # TCV architektúra mapping
            original_tcv_arch = self.tcv_df['Architecture'].value_counts()
            print(f"📊 Eredeti TCV architektúrák: {dict(original_tcv_arch)}")
            self.tcv_df['Architecture'] = self.tcv_df['Architecture'].map(lambda x: self.architecture_mapping.get(x, x))
            
            # Mapping utáni állapot
            mapped_acv_arch = self.acv_df['Architecture'].value_counts()
            mapped_tcv_arch = self.tcv_df['Architecture'].value_counts()
            print(f"✅ Mapped ACV architektúrák: {dict(mapped_acv_arch)}")
            print(f"✅ Mapped TCV architektúrák: {dict(mapped_tcv_arch)}")
        except Exception as e:
            print(f"❌ Architektúra mapping hiba: {e}")
            raise

    def _identify_value_columns(self):
        """Érték oszlopok azonosítása"""
        try:
            # ACV érték oszlop keresése
            acv_value_candidates = []
            for col in self.acv_df.columns:
                # Numerikus oszlopokat keresünk (kivéve year, quarter stb.)
                if (self.acv_df[col].dtype in ['int64', 'float64'] or
                    (self.acv_df[col].dtype == 'object' and
                     self.acv_df[col].astype(str).str.contains(r'^[\d\.,\-\$\s]*$', na=False).any())):
                    if col.lower() not in ['fiscal year', 'year', 'quarter', 'month']:
                        acv_value_candidates.append(col)
            
            # A legvalószínűbb érték oszlop kiválasztása ACV-hez
            if acv_value_candidates:
                # Próbáljuk az 'A' oszlopot először (a minta alapján)
                if 'A' in acv_value_candidates:
                    self.acv_value_column = 'A'
                else:
                    self.acv_value_column = acv_value_candidates[0]
                print(f"💰 ACV érték oszlop: {self.acv_value_column}")
            else:
                self.acv_value_column = None
                print("❌ ACV érték oszlop nem található!")
            
            # TCV érték oszlop keresése
            tcv_value_candidates = []
            for col in self.tcv_df.columns:
                if (self.tcv_df[col].dtype in ['int64', 'float64'] or
                    (self.tcv_df[col].dtype == 'object' and
                     self.tcv_df[col].astype(str).str.contains(r'^[\d\.,\-\$\s]*$', na=False).any())):
                    if col.lower() not in ['fiscal year', 'year', 'quarter', 'month']:
                        tcv_value_candidates.append(col)
            
            # A legvalószínűbb érték oszlop kiválasztása TCV-hez
            if tcv_value_candidates:
                # Próbáljuk az 'A' oszlopot először (a minta alapján)
                if 'A' in tcv_value_candidates:
                    self.tcv_value_column = 'A'
                else:
                    self.tcv_value_column = tcv_value_candidates[0]
                print(f"💰 TCV érték oszlop: {self.tcv_value_column}")
            else:
                self.tcv_value_column = None
                print("❌ TCV érték oszlop nem található!")
        except Exception as e:
            print(f"❌ Érték oszlop azonosítási hiba: {e}")
            self.acv_value_column = None
            self.tcv_value_column = None

    def _process_date_columns(self):
        """Dátum oszlopok feldolgozása"""
        try:
            # ACV dátum kezelés
            if 'FISCAL_MONTH_NAME' in self.acv_df.columns:
                self.acv_df['Date'] = self.acv_df['FISCAL_MONTH_NAME'].apply(self._convert_fiscal_month)
            elif 'Date' in self.acv_df.columns:
                self.acv_df['Date'] = pd.to_datetime(self.acv_df['Date'])
            else:
                date_candidates = [col for col in self.acv_df.columns if
                                 'date' in col.lower() or 'datum' in col.lower() or 'time' in col.lower()]
                if date_candidates:
                    self.acv_df['Date'] = pd.to_datetime(self.acv_df[date_candidates[0]])
                    print(f"🗓️ ACV dátum oszlop: {date_candidates[0]}")
                else:
                    print("⚠️ ACV dátum oszlop nem található!")
            
            # TCV dátum kezelés
            if 'FISCAL_MONTH_NAME' in self.tcv_df.columns:
                self.tcv_df['Date'] = self.tcv_df['FISCAL_MONTH_NAME'].apply(self._convert_fiscal_month)
            elif 'Date' in self.tcv_df.columns:
                self.tcv_df['Date'] = pd.to_datetime(self.tcv_df['Date'])
            else:
                date_candidates = [col for col in self.tcv_df.columns if
                                 'date' in col.lower() or 'datum' in col.lower() or 'time' in col.lower()]
                if date_candidates:
                    self.tcv_df['Date'] = pd.to_datetime(self.tcv_df[date_candidates[0]])
                    print(f"🗓️ TCV dátum oszlop: {date_candidates[0]}")
                else:
                    print("⚠️ TCV dátum oszlop nem található!")
            
            # Rendezés dátum szerint
            self.acv_df = self.acv_df.sort_values('Date')
            self.tcv_df = self.tcv_df.sort_values('Date')
            
        except Exception as e:
            print(f"❌ Dátum feldolgozási hiba: {e}")
            raise

    def _process_architecture_columns(self):
        """Architektúra oszlopok feldolgozása"""
        try:
            # ACV architektúra oszlop keresése
            if 'Architecture' not in self.acv_df.columns:
                arch_candidates = [col for col in self.acv_df.columns if 'arch' in col.lower()]
                if arch_candidates:
                    self.acv_df['Architecture'] = self.acv_df[arch_candidates[0]]
                    print(f"🏗️ ACV architektúra oszlop: {arch_candidates[0]} -> Architecture")
                else:
                    self.acv_df['Architecture'] = 'Unknown'
                    print("⚠️ ACV architektúra oszlop nem található, 'Unknown' használata")
            
            # TCV architektúra oszlop keresése
            if 'Architecture' not in self.tcv_df.columns:
                arch_candidates = [col for col in self.tcv_df.columns if 'arch' in col.lower()]
                if arch_candidates:
                    self.tcv_df['Architecture'] = self.tcv_df[arch_candidates[0]]
                    print(f"🏗️ TCV architektúra oszlop: {arch_candidates[0]} -> Architecture")
                else:
                    self.tcv_df['Architecture'] = 'Unknown'
                    print("⚠️ TCV architektúra oszlop nem található, 'Unknown' használata")
        except Exception as e:
            print(f"❌ Architektúra feldolgozási hiba: {e}")
            raise

    def _to_fiscal_month(self, date):
        """Dátum konvertálása fiscal month formátumra"""
        try:
            if pd.isna(date):
                return None
            
            if date.month >= 8:  # Aug - Dec
                fiscal_year = date.year + 1
            else:  # Jan - Jul
                fiscal_year = date.year
                
            month_name = date.strftime('%b')
            return f"{month_name} FY{fiscal_year}"
        except Exception as e:
            print(f"Fiscal month konverziós hiba: {e}")
            return None

    def _convert_fiscal_month(self, fiscal_month):
        """Fiscal month konvertálása dátummá"""
        try:
            if pd.isna(fiscal_month):
                # Visszatérhet valamilyen alapértelmezett dátummal, vagy hibát dobhat
                # Most az aktuális dátummal térünk vissza, hogy ne törjön el a kód
                return datetime(datetime.now().year, datetime.now().month, 1)
                
            parts = str(fiscal_month).strip().split(' ')
            if len(parts) != 2:
                raise ValueError(f"Hibás formátum: {fiscal_month}")
                
            month_name = parts[0]
            fiscal_year_str = parts[1]
            
            if not fiscal_year_str.startswith('FY'):
                raise ValueError(f"Hibás fiscal year formátum: {fiscal_year_str}")
                
            fiscal_year = int(fiscal_year_str[2:])
            
            month_mapping = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
                'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
                'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }
            
            month_num = month_mapping.get(month_name)
            if month_num is None:
                raise ValueError(f"Ismeretlen hónap: {month_name}")
            
            # JAVÍTOTT FISCAL YEAR SZÁMÍTÁS
            # Ha a hónap augusztus vagy később van, akkor az előző naptári évhez tartozik
            # Ha a hónap július vagy korábban van, akkor az adott fiscal year-hez tartozik
            if month_num >= 8:  # Aug - Dec
                calendar_year = fiscal_year - 1
            else:  # Jan - Jul
                calendar_year = fiscal_year
                
            result = datetime(calendar_year, month_num, 1)
            return result
        except Exception as e:
            print(f"Dátum konverziós hiba: {fiscal_month} -> {e}")
            # Visszatérhet valamilyen alapértelmezett dátummal, vagy hibát dobhat
            return datetime(datetime.now().year, datetime.now().month, 1)

    def get_available_months(self):
        """Elérhető hónapok listája - beleértve a jövőbeli hónapokat is predikciós célokra"""
        try:
            # Meglévő hónapok az adatokból
            if 'FISCAL_MONTH_NAME' in self.acv_df.columns:
                acv_months = set(self.acv_df['FISCAL_MONTH_NAME'].dropna())
            else:
                acv_months = set(self.acv_df['FiscalMonth'].dropna())

            if 'FISCAL_MONTH_NAME' in self.tcv_df.columns:
                tcv_months = set(self.tcv_df['FISCAL_MONTH_NAME'].dropna())
            else:
                tcv_months = set(self.tcv_df['FiscalMonth'].dropna())

            existing_months = list(acv_months.union(tcv_months))

            # Jövőbeli hónapok generálása (következő 4 hónap)
            future_months = []
            if hasattr(self, 'current_fiscal_month') and self.current_fiscal_month:
                current_month = self.current_fiscal_month
            else:
                # Fallback: legutóbbi hónap az adatokból
                current_month = max(existing_months, key=lambda x: self._convert_fiscal_month(x))

            print(f"🔍 Current month a future generáláshoz: {current_month}")
            
            # Következő 4 hónap generálása a current_fiscal_month-tól kezdve
            for i in range(1, 4 + 1): # current_fiscal_month + 1-től +4-ig
                future_month = self._add_fiscal_months(current_month, i)
                future_months.append(future_month)
                print(f"  + {i} hónap: {future_month}")

            # Összes hónap kombinálása
            all_months = set(existing_months + future_months) # Használunk set-et az ismétlődések elkerülésére
            
            # Rendezés dátum szerint (legújabb elől)
            month_dates = [(month, self._convert_fiscal_month(month)) for month in all_months]
            month_dates.sort(key=lambda x: x[1], reverse=True)

            result = [month for month, date in month_dates]
            print(f"📅 Elérhető hónapok (beleértve jövőbeli): {len(result)} hónap")
            return result

        except Exception as e:
            print(f"Hónapok lekérési hiba: {e}")
            return ['Jul FY2025']

    def _add_fiscal_months(self, fiscal_month, months_to_add):
        """JAVÍTOTT Fiscal month előreszámítás"""
        try:
            # Fiscal year kezdés: August
            fiscal_months_order = ['Aug', 'Sep', 'Oct', 'Nov', 'Dec',
                                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']
            
            parts = str(fiscal_month).strip().split(' ')
            month_name = parts[0]
            fiscal_year = int(parts[1][2:])
            
            current_position = fiscal_months_order.index(month_name)
            
            # JAVÍTOTT SZÁMÍTÁS
            total_months = current_position + months_to_add
            years_forward = total_months // 12
            target_position = total_months % 12
            
            target_fiscal_year = fiscal_year + years_forward
            target_month_name = fiscal_months_order[target_position]
            
            result = f"{target_month_name} FY{target_fiscal_year}"
            # print(f"    DEBUG: {fiscal_month} + {months_to_add} = {result}") # Túl sok output lehet
            return result
            
        except Exception as e:
            print(f"Hónap előreszámítási hiba: {e}")
            return "Jul FY2025"

    def _subtract_fiscal_months(self, fiscal_month, months_to_subtract):
        """Fiscal month visszaszámítás"""
        try:
            fiscal_months_order = ['Aug', 'Sep', 'Oct', 'Nov', 'Dec',
                                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']
            
            parts = str(fiscal_month).strip().split(' ')
            month_name = parts[0]
            fiscal_year = int(parts[1][2:])
            
            current_position = fiscal_months_order.index(month_name)
            target_position = current_position - months_to_subtract
            
            years_back = 0
            while target_position < 0:
                target_position += 12
                years_back += 1
                
            target_fiscal_year = fiscal_year - years_back
            target_month_name = fiscal_months_order[target_position]
            
            return f"{target_month_name} FY{target_fiscal_year}"
            
        except Exception as e:
            print(f"Hónap visszaszámítási hiba: {e}")
            return "Jul FY2024"

    def get_architectures(self):
        """Elérhető architektúrák - MAPPED VERZIÓ"""
        try:
            acv_arch = set(self.acv_df['Architecture'].dropna())
            tcv_arch = set(self.tcv_df['Architecture'].dropna())
            return sorted(list(acv_arch.union(tcv_arch)))
        except Exception as e:
            print(f"Architektúrák lekérési hiba: {e}")
            return ['Unknown']

    def get_analysis_type(self, end_month):
        """Meghatározza az elemzés típusát: 'historical', 'current_month_prediction', 'future_prediction'."""
        end_date = self._convert_fiscal_month(end_month)
        current_fiscal_month_date = self._convert_fiscal_month(self.current_fiscal_month)

        if end_date > current_fiscal_month_date:
            return 'future_prediction'
        elif end_date == current_fiscal_month_date:
            return 'current_month_prediction'
        else:
            return 'historical'

    def get_rolling_analysis(self, end_month, architecture=None):
        """12+12 hónapos gördülő elemzés - normál, aktuális és predikciós módban"""
        try:
            analysis_type = self.get_analysis_type(end_month)
            
            if analysis_type == 'future_prediction':
                return self._get_prediction_analysis(end_month, architecture)
            elif analysis_type == 'current_month_prediction':
                return self._get_current_month_analysis(end_month, architecture)
            else: # historical
                return self._get_historical_analysis(end_month, architecture)
        except Exception as e:
            print(f"Elemzési hiba: {e}")
            return {
                'acv_current': {}, 'acv_reference': {},
                'tcv_current': {}, 'tcv_reference': {}, 
                'period_info': {}
            }

    def _get_historical_analysis(self, end_month, architecture=None):
        """Történeti elemzés (eredeti logika)"""
        try:
            end_date = self._convert_fiscal_month(end_month)
            current_start_month = self._subtract_fiscal_months(end_month, 11)
            reference_start_month = self._subtract_fiscal_months(end_month, 23)
            
            current_start_date = self._convert_fiscal_month(current_start_month)
            reference_start_date = self._convert_fiscal_month(reference_start_month)
            # A referencia időszak záró hónapja 1 hónappal korábbi, mint az aktuális időszak kezdő hónapja
            reference_end_month_str = self._subtract_fiscal_months(current_start_month, 1)


            # Szűrési feltételek
            acv_current_mask = (self.acv_df['Date'] >= current_start_date) & (self.acv_df['Date'] <= end_date)
            acv_reference_mask = (self.acv_df['Date'] >= reference_start_date) & (self.acv_df['Date'] < current_start_date)
            tcv_current_mask = (self.tcv_df['Date'] >= current_start_date) & (self.tcv_df['Date'] <= end_date)
            tcv_reference_mask = (self.tcv_df['Date'] >= reference_start_date) & (self.tcv_df['Date'] < current_start_date)

            # Architektúra szűrés
            if architecture:
                if isinstance(architecture, list):
                    acv_current_mask &= (self.acv_df['Architecture'].isin(architecture))
                    acv_reference_mask &= (self.acv_df['Architecture'].isin(architecture))
                    tcv_current_mask &= (self.tcv_df['Architecture'].isin(architecture))
                    tcv_reference_mask &= (self.tcv_df['Architecture'].isin(architecture))
                else:
                    acv_current_mask &= (self.acv_df['Architecture'] == architecture)
                    acv_reference_mask &= (self.acv_df['Architecture'] == architecture)
                    tcv_current_mask &= (self.tcv_df['Architecture'] == architecture)
                    tcv_reference_mask &= (self.tcv_df['Architecture'] == architecture)

            # Összesítések az azonosított érték oszlopokkal
            acv_current = self._aggregate_data(self.acv_df[acv_current_mask], self.acv_value_column)
            acv_reference = self._aggregate_data(self.acv_df[acv_reference_mask], self.acv_value_column)
            tcv_current = self._aggregate_data(self.tcv_df[tcv_current_mask], self.tcv_value_column)
            tcv_reference = self._aggregate_data(self.tcv_df[tcv_reference_mask], self.tcv_value_column)

            return {
                'acv_current': acv_current,
                'acv_reference': acv_reference,
                'tcv_current': tcv_current,
                'tcv_reference': tcv_reference,
                'analysis_type': 'historical', # Új mező
                'period_info': {
                    'current_start': current_start_date.strftime('%Y-%m'),
                    'current_end': end_date.strftime('%Y-%m'),
                    'reference_start': reference_start_date.strftime('%Y-%m'),
                    'reference_end': self._convert_fiscal_month(reference_end_month_str).strftime('%Y-%m'), # Itt is dátum formátum
                    'current_start_fiscal': current_start_month,
                    'current_end_fiscal': end_month,
                    'reference_start_fiscal': reference_start_month, # Fiscal month string
                    'reference_end_fiscal': reference_end_month_str, # Fiscal month string
                    'selected_architectures': architecture if architecture else 'Összes'
                }
            }
        except Exception as e:
            print(f"Történeti elemzési hiba: {e}")
            return {
                'acv_current': {}, 'acv_reference': {},
                'tcv_current': {}, 'tcv_reference': {}, 
                'period_info': {}
            }

    def _get_current_month_analysis(self, end_month, architecture=None):
        """AKTUÁLIS HÓNAP elemzése: kombinálja a már meglévő (történeti) adatokat a predikciós logikával"""
        try:
            print(f"✨ AKTUÁLIS STÁTUSZ - predikcióval: {end_month}")
            
            # Az `end_month` az a hónap, amit a felhasználó kiválasztott, azaz a `current_fiscal_month`
            end_date_full_month = self._convert_fiscal_month(end_month) 
            
            # A 12 hónapos periódus `current_period_start_month`-tól `end_month`-ig tart
            current_period_start_month = self._subtract_fiscal_months(end_month, 11) 
            current_period_start_date = self._convert_fiscal_month(current_period_start_month)

            # A Baseline időszak ugyanaz, mint a jövőbeli predikció esetén: 12 hónappal korábbi
            baseline_start_month = self._subtract_fiscal_months(current_period_start_month, 12)
            baseline_end_month = self._subtract_fiscal_months(end_month, 12)
            
            baseline_start_date = self._convert_fiscal_month(baseline_start_month)
            baseline_end_date = self._convert_fiscal_month(baseline_end_month)
            
            # --- Adatok szűrése és aggregálása ---

            # ACV/TCV EXISTING: már meglévő booking-ok az aktuális 12 hónapos periódusban,
            # DE CSAK az utolsó adatpont dátumáig bezárólag!
            # Azaz a már lekönyvelt adatok az aktuális hónapban (is).
            acv_existing_mask = (self.acv_df['Date'] >= current_period_start_date) & (self.acv_df['Date'] <= self.last_data_point_date)
            tcv_existing_mask = (self.tcv_df['Date'] >= current_period_start_date) & (self.tcv_df['Date'] <= self.last_data_point_date)
            
            # ACV/TCV BASELINE: egy évvel korábbi, teljes 12 hónapos időszak
            acv_baseline_mask = (self.acv_df['Date'] >= baseline_start_date) & (self.acv_df['Date'] <= baseline_end_date)
            tcv_baseline_mask = (self.tcv_df['Date'] >= baseline_start_date) & (self.tcv_df['Date'] <= baseline_end_date)
            
            # Architektúra szűrés
            if architecture:
                if isinstance(architecture, list):
                    acv_existing_mask &= (self.acv_df['Architecture'].isin(architecture))
                    acv_baseline_mask &= (self.acv_df['Architecture'].isin(architecture))
                    tcv_existing_mask &= (self.tcv_df['Architecture'].isin(architecture))
                    tcv_baseline_mask &= (self.tcv_df['Architecture'].isin(architecture))
                else:
                    acv_existing_mask &= (self.acv_df['Architecture'] == architecture)
                    acv_baseline_mask &= (self.acv_df['Architecture'] == architecture)
                    tcv_existing_mask &= (self.tcv_df['Architecture'] == architecture)
                    tcv_baseline_mask &= (self.tcv_df['Architecture'] == architecture)

            # Aggregálás
            acv_existing = self._aggregate_data(self.acv_df[acv_existing_mask], self.acv_value_column)
            acv_baseline = self._aggregate_data(self.acv_df[acv_baseline_mask], self.acv_value_column)
            tcv_existing = self._aggregate_data(self.tcv_df[tcv_existing_mask], self.tcv_value_column)
            tcv_baseline = self._aggregate_data(self.tcv_df[tcv_baseline_mask], self.tcv_value_column)

            # Index-alapú target-ek számítása
            acv_index_targets = self._calculate_index_targets(acv_baseline)
            tcv_index_targets = self._calculate_index_targets(tcv_baseline)

            # Szükséges booking-ok számítása minden index szinthez (a meglévő adatok és a targetek alapján)
            acv_needed_by_index = self._calculate_needed_by_index(acv_existing, acv_index_targets)
            tcv_needed_by_index = self._calculate_needed_by_index(tcv_existing, tcv_index_targets)

            return {
                'acv_current': acv_existing,  # Már meglévő booking az aktuális hónapig
                'acv_baseline': acv_baseline,  # Baseline (egy évvel korábbi)
                'acv_index_targets': acv_index_targets,  # Target-ek index szintenként
                'acv_needed_by_index': acv_needed_by_index,  # Szükséges booking index-enként
                'tcv_current': tcv_existing,
                'tcv_baseline': tcv_baseline,
                'tcv_index_targets': tcv_index_targets,
                'tcv_needed_by_index': tcv_needed_by_index,
                'analysis_type': 'current_month_prediction', # Új mező
                'period_info': {
                    'future_start': current_period_start_date.strftime('%Y-%m'),
                    'future_end': end_date_full_month.strftime('%Y-%m') + " (aktuális hónap vége)", # pontosabb leírás
                    'baseline_start': baseline_start_date.strftime('%Y-%m'),
                    'baseline_end': baseline_end_date.strftime('%Y-%m'),
                    'future_start_fiscal': current_period_start_month,
                    'future_end_fiscal': end_month,
                    'baseline_start_fiscal': baseline_start_month,
                    'baseline_end_fiscal': baseline_end_month,
                    'selected_architectures': architecture if architecture else 'Összes',
                    'last_data_point': self.last_data_point_date.strftime('%Y-%m-%d') # Fontos infó
                }
            }

        except Exception as e:
            print(f"Aktuális hónap elemzési hiba: {e}")
            return {'acv_current': {}, 'acv_baseline': {}, 'tcv_current': {}, 'tcv_baseline': {}, 'period_info': {}}

    def _get_prediction_analysis(self, end_month, architecture=None):
        """Predikciós elemzés INDEX-ALAPÚ TARGET-EKKEL"""
        try:
            print(f"🔮 Predikciós elemzés index-alapú target-ekkel: {end_month}")
            end_date = self._convert_fiscal_month(end_month)
            future_start_month = self._subtract_fiscal_months(end_month, 11)
            future_start_date = self._convert_fiscal_month(future_start_month)

            # Az aktuális időszakban már meglévő booking-ok (a current_fiscal_month-ig)
            current_date = self._convert_fiscal_month(self.current_fiscal_month)
            
            # Baseline időszak (egy évvel korábbi ugyanezen időszak)
            baseline_start_month = self._subtract_fiscal_months(future_start_month, 12)
            baseline_end_month = self._subtract_fiscal_months(end_month, 12)
            baseline_start_date = self._convert_fiscal_month(baseline_start_month)
            baseline_end_date = self._convert_fiscal_month(baseline_end_month)

            # Jövőbeli időszakban már meglévő booking-ok (a kiválasztott jövőbeli időszakban, de csak a mai napig)
            acv_future_mask = (self.acv_df['Date'] >= future_start_date) & (self.acv_df['Date'] <= self.last_data_point_date)
            tcv_future_mask = (self.tcv_df['Date'] >= future_start_date) & (self.tcv_df['Date'] <= self.last_data_point_date)

            # Baseline időszak (referencia)
            acv_baseline_mask = (self.acv_df['Date'] >= baseline_start_date) & (self.acv_df['Date'] <= baseline_end_date)
            tcv_baseline_mask = (self.tcv_df['Date'] >= baseline_start_date) & (self.tcv_df['Date'] <= baseline_end_date)

            # Architektúra szűrés
            if architecture:
                if isinstance(architecture, list):
                    acv_future_mask &= (self.acv_df['Architecture'].isin(architecture))
                    acv_baseline_mask &= (self.acv_df['Architecture'].isin(architecture))
                    tcv_future_mask &= (self.tcv_df['Architecture'].isin(architecture))
                    tcv_baseline_mask &= (self.tcv_df['Architecture'].isin(architecture))
                else:
                    acv_future_mask &= (self.acv_df['Architecture'] == architecture)
                    acv_baseline_mask &= (self.acv_df['Architecture'] == architecture)
                    tcv_future_mask &= (self.tcv_df['Architecture'] == architecture)
                    tcv_baseline_mask &= (self.tcv_df['Architecture'] == architecture)

            # Aggregálás
            acv_existing = self._aggregate_data(self.acv_df[acv_future_mask], self.acv_value_column)
            acv_baseline = self._aggregate_data(self.acv_df[acv_baseline_mask], self.acv_value_column)
            tcv_existing = self._aggregate_data(self.tcv_df[tcv_future_mask], self.tcv_value_column)
            tcv_baseline = self._aggregate_data(self.tcv_df[tcv_baseline_mask], self.tcv_value_column)

            # Index-alapú target-ek számítása
            acv_index_targets = self._calculate_index_targets(acv_baseline)
            tcv_index_targets = self._calculate_index_targets(tcv_baseline)

            # Szükséges booking-ok számítása minden index szinthez
            acv_needed_by_index = self._calculate_needed_by_index(acv_existing, acv_index_targets)
            tcv_needed_by_index = self._calculate_needed_by_index(tcv_existing, tcv_index_targets)

            return {
                'acv_current': acv_existing,  # Már meglévő booking
                'acv_baseline': acv_baseline,  # Baseline (egy évvel korábbi)
                'acv_index_targets': acv_index_targets,  # Target-ek index szintenként
                'acv_needed_by_index': acv_needed_by_index,  # Szükséges booking index-enként
                'tcv_current': tcv_existing,
                'tcv_baseline': tcv_baseline,
                'tcv_index_targets': tcv_index_targets,
                'tcv_needed_by_index': tcv_needed_by_index,
                'analysis_type': 'future_prediction', # Új mező
                'period_info': {
                    'future_start': future_start_date.strftime('%Y-%m'),
                    'future_end': end_date.strftime('%Y-%m'),
                    'baseline_start': baseline_start_date.strftime('%Y-%m'),
                    'baseline_end': baseline_end_date.strftime('%Y-%m'),
                    'future_start_fiscal': future_start_month,
                    'future_end_fiscal': end_month,
                    'baseline_start_fiscal': baseline_start_month,
                    'baseline_end_fiscal': baseline_end_month,
                    'selected_architectures': architecture if architecture else 'Összes',
                    'last_data_point': self.last_data_point_date.strftime('%Y-%m-%d') # Fontos infó
                }
            }

        except Exception as e:
            print(f"Predikciós elemzési hiba: {e}")
            return {'acv_current': {}, 'acv_baseline': {}, 'tcv_current': {}, 'tcv_baseline': {}, 'period_info': {}}

    def _calculate_index_targets(self, baseline_data):
        """Index-alapú target-ek számítása minden architektúrához - JAVÍTOTT SZÁZALÉKOS NÖVEKEDÉS"""
        try:
            index_targets = {}
            for arch, baseline_value in baseline_data.items():
                baseline_value = float(baseline_value) if baseline_value is not None else 0
                arch_targets = {}
                
                # Index 0-10 target-ek számítása
                for index in range(11):  # 0-10
                    if baseline_value != 0:
                        if index == 10:
                            # Index 10: >9% növekedés, vegyük 10%-nak
                            growth_rate = 0.10
                        else:
                            # Index 0-9: pontosan az index százaléka
                            growth_rate = index / 100
                        
                        target_value = baseline_value * (1 + growth_rate)
                    else:
                        # Ha a baseline 0, a target is 0, kivéve ha az index 0.
                        # De egy 0 baseline esetén a 0-nál nagyobb target irreális.
                        # Most maradunk a 0-nál.
                        target_value = 0 
                    
                    arch_targets[index] = target_value
                
                index_targets[arch] = arch_targets
                
            return index_targets
            
        except Exception as e:
            print(f"Index target számítási hiba: {e}")
            return {}

    def _calculate_needed_by_index(self, existing_data, index_targets):
        """Szükséges booking számítása minden index szinthez"""
        try:
            needed_by_index = {}
            
            for arch in index_targets.keys():
                existing_value = float(existing_data.get(arch, 0))
                arch_needed = {}
                
                for index, target_value in index_targets[arch].items():
                    needed = max(0, target_value - existing_value)
                    arch_needed[index] = needed
                
                needed_by_index[arch] = arch_needed
                
            return needed_by_index
        
        except Exception as e:
            print(f"Szükséges booking index számítási hiba: {e}")
            return {}

    def _aggregate_data(self, df, value_column):
        """Adatok összesítése architektúra szerint - ÖSSZEVONT ARCHITEKTÚRÁKKAL"""
        try:
            if df.empty or value_column is None:
                print("❌ Üres DataFrame vagy hiányzó érték oszlop")
                return {}
            
            df = df.copy()
            
            # Ha az érték oszlop nem létezik
            if value_column not in df.columns:
                print(f"❌ Érték oszlop nem található: {value_column}")
                return {}
            
            # STRING ÉRTÉKEK TISZTÍTÁSA
            if df[value_column].dtype == 'object':
                df[value_column] = df[value_column].astype(str).str.replace('$', '', regex=False)
                df[value_column] = df[value_column].str.replace(',', '', regex=False)
                df[value_column] = df[value_column].str.replace(' ', '', regex=False)
                df[value_column] = df[value_column].replace('', '0')
                df[value_column] = pd.to_numeric(df[value_column], errors='coerce').fillna(0)
            
            # Összesítés architektúra szerint (NETWORKING* és SERVICES már összevonva a mappingben)
            aggregated = df.groupby('Architecture')[value_column].sum().to_dict()
            aggregated['Összes'] = df[value_column].sum()
            
            print(f"✅ Aggregálva: {len(aggregated)} architektúra")
            for arch, value in aggregated.items():
                print(f"   📊 {arch}: {value:,.0f}")
            
            return aggregated
        except Exception as e:
            print(f"Aggregálási hiba: {e}")
            return {}

if __name__ == "__main__":
    print("✅ data_processor.py sikeresen betöltve!")
    print("✅ BookingAnalyzer osztály elérhető predikciós funkcionalitással!")
