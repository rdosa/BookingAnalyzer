import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar
import io

class BookingAnalyzer:
    """ACV/TCV Booking Value Analyzer"""
    
    def __init__(self, acv_file_path=None, tcv_file_path=None, acv_file_obj=None, tcv_file_obj=None):
        """BookingAnalyzer inicializálása
        Parameters:
        - acv_file_path: ACV CSV fájl elérési útja (string)
        - tcv_file_path: TCV CSV fájl elérési útja (string)
        - acv_file_obj: ACV fájl objektum (Streamlit upload)
        - tcv_file_obj: TCV fájl objektum (Streamlit upload)
        """
#        print("BookingAnalyzer inicializálása...")
        try:
            # ACV fájl betöltése
            if acv_file_path:
                self.acv_df = pd.read_csv(acv_file_path)
#                print(f"✅ ACV betöltve fájlból: {acv_file_path}")
            elif acv_file_obj:
                self.acv_df = pd.read_csv(acv_file_obj)
#                print("✅ ACV betöltve feltöltött fájlból")
            else:
                raise ValueError("❌ Nincs ACV fájl megadva")
            
            # TCV fájl betöltése
            if tcv_file_path:
                self.tcv_df = pd.read_csv(tcv_file_path)
#                print(f"✅ TCV betöltve fájlból: {tcv_file_path}")
            elif tcv_file_obj:
                self.tcv_df = pd.read_csv(tcv_file_obj)
#                print("✅ TCV betöltve feltöltött fájlból")
            else:
                raise ValueError("❌ Nincs TCV fájl megadva")
            
#            print(f"📊 ACV adatok: {len(self.acv_df)} sor")
#            print(f"📊 TCV adatok: {len(self.tcv_df)} sor")
            
            # Adatok feldolgozása
            self._process_data()
            
        except Exception as e:
            print(f"❌ Hiba az inicializáláskor: {e}")
            raise

    def _process_data(self):
        """Adatok feldolgozása és előkészítése"""
#        print("Adatok feldolgozása...")
        try:
            # Oszlopok listázása debug céljából
#            print(f"🔍 ACV oszlopok: {list(self.acv_df.columns)}")
#            print(f"🔍 TCV oszlopok: {list(self.tcv_df.columns)}")
            
            # Dátum oszlop keresése és egységesítése
            self._process_date_columns()
            
            # Architektúra oszlop egységesítése
            self._process_architecture_columns()
            
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
            
#            print("✅ Adatok feldolgozva")
            
        except Exception as e:
            print(f"❌ Adatfeldolgozási hiba: {e}")
            raise

    def _process_date_columns(self):
        """Dátum oszlopok feldolgozása"""
        try:
            # ACV dátum kezelés
            if 'FISCAL_MONTH_NAME' in self.acv_df.columns:
                # Ha van FISCAL_MONTH_NAME, azt használjuk
                self.acv_df['Date'] = self.acv_df['FISCAL_MONTH_NAME'].apply(self._convert_fiscal_month)
            elif 'Date' in self.acv_df.columns:
                # Ha van Date oszlop, azt konvertáljuk
                self.acv_df['Date'] = pd.to_datetime(self.acv_df['Date'])
            else:
                # Keresés dátum jellegű oszlopokra
                date_candidates = [col for col in self.acv_df.columns if 
                                 'date' in col.lower() or 'datum' in col.lower() or 'time' in col.lower()]
                if date_candidates:
                    self.acv_df['Date'] = pd.to_datetime(self.acv_df[date_candidates[0]])
                    print(f"🗓️ ACV dátum oszlop: {date_candidates[0]}")
                else:
                    print("⚠️ ACV dátum oszlop nem található!")
            
            # TCV dátum kezelés
            if 'FISCAL_MONTH_NAME' in self.tcv_df.columns:
                # Ha van FISCAL_MONTH_NAME, azt használjuk
                self.tcv_df['Date'] = self.tcv_df['FISCAL_MONTH_NAME'].apply(self._convert_fiscal_month)
            elif 'Date' in self.tcv_df.columns:
                # Ha van Date oszlop, azt konvertáljuk
                self.tcv_df['Date'] = pd.to_datetime(self.tcv_df['Date'])
            else:
                # Keresés dátum jellegű oszlopokra
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
                    # Ha nincs, alapértelmezett értéket adunk
                    self.acv_df['Architecture'] = 'Unknown'
                    print("⚠️ ACV architektúra oszlop nem található, 'Unknown' használata")
            
            # TCV architektúra oszlop keresése
            if 'Architecture' not in self.tcv_df.columns:
                arch_candidates = [col for col in self.tcv_df.columns if 'arch' in col.lower()]
                if arch_candidates:
                    self.tcv_df['Architecture'] = self.tcv_df[arch_candidates[0]]
                    print(f"🏗️ TCV architektúra oszlop: {arch_candidates[0]} -> Architecture")
                else:
                    # Ha nincs, alapértelmezett értéket adunk
                    self.tcv_df['Architecture'] = 'Unknown'
                    print("⚠️ TCV architektúra oszlop nem található, 'Unknown' használata")
                    
        except Exception as e:
            print(f"❌ Architektúra feldolgozási hiba: {e}")
            raise

    def _to_fiscal_month(self, date):
        """Dátum konvertálása fiscal month formátumra (pl. Jun FY2025)"""
        try:
            if pd.isna(date):
                return None
            
            # Ha a hónap július vagy után, akkor a következő fiscal year
            if date.month >= 7:
                fiscal_year = date.year + 1
            else:
                fiscal_year = date.year
                
            month_name = date.strftime('%b')
            return f"{month_name} FY{fiscal_year}"
            
        except Exception as e:
            print(f"Fiscal month konverziós hiba: {e}")
            return None

    def _convert_fiscal_month(self, fiscal_month):
        """Fiscal month konvertálása dátummá - TELJES DEBUG"""
        try:
            if pd.isna(fiscal_month):
                return datetime(2024, 1, 1)
                
            parts = str(fiscal_month).strip().split(' ')
            if len(parts) != 2:
                raise ValueError(f"Hibás formátum: {fiscal_month}")
            
            month_name = parts[0]
            fiscal_year_str = parts[1]
            
            if not fiscal_year_str.startswith('FY'):
                raise ValueError(f"Hibás fiscal year formátum: {fiscal_year_str}")
            
            fiscal_year = int(fiscal_year_str[2:])  # FY2025 -> 2025
            
            # Hónap név -> szám
            month_mapping = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
                'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
                'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }
            
            month_num = month_mapping.get(month_name)
            if month_num is None:
                raise ValueError(f"Ismeretlen hónap: {month_name}")
            
            # FY2025 logika: 2024 Aug - 2025 Jul
            if month_num >= 8:  # Aug, Sep, Oct, Nov, Dec
                calendar_year = fiscal_year - 1
            else:  # Jan-Jul
                calendar_year = fiscal_year
            
            result = datetime(calendar_year, month_num, 1)
            return result
            
        except Exception as e:
            print(f"Dátum konverziós hiba: {fiscal_month} -> {e}")
            return datetime(2024, 1, 1)

    def get_available_months(self):
        """Elérhető hónapok listája"""
        try:
            # FISCAL_MONTH_NAME oszlop használata ha elérhető
            if 'FISCAL_MONTH_NAME' in self.acv_df.columns:
                acv_months = set(self.acv_df['FISCAL_MONTH_NAME'].dropna())
            else:
                acv_months = set(self.acv_df['FiscalMonth'].dropna())
                
            if 'FISCAL_MONTH_NAME' in self.tcv_df.columns:
                tcv_months = set(self.tcv_df['FISCAL_MONTH_NAME'].dropna())
            else:
                tcv_months = set(self.tcv_df['FiscalMonth'].dropna())
            
            all_months = list(acv_months.union(tcv_months))
            
            # Explicit rendezés dátum szerint
            month_dates = [(month, self._convert_fiscal_month(month)) for month in all_months]
            month_dates.sort(key=lambda x: x[1], reverse=True)  # Legújabb elől
            result = [month for month, date in month_dates]
            
            return result
            
        except Exception as e:
            print(f"Hónapok lekérési hiba: {e}")
            return ['Jul FY2025']

    def _subtract_fiscal_months(self, fiscal_month, months_to_subtract):
        """Fiscal month visszaszámítás"""
        try:
            # Fiscal months sorrendje
            fiscal_months_order = [
                'Aug', 'Sep', 'Oct', 'Nov', 'Dec',  # FY első fele
                'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'  # FY második fele
            ]
            
            parts = str(fiscal_month).strip().split(' ')
            month_name = parts[0]
            fiscal_year = int(parts[1][2:])
            
            # Jelenlegi pozíció
            current_position = fiscal_months_order.index(month_name)
            
            # Visszaszámítás
            target_position = current_position - months_to_subtract
            
            # Év korrekció
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
        """Elérhető architektúrák"""
        try:
            acv_arch = set(self.acv_df['Architecture'].dropna())
            tcv_arch = set(self.tcv_df['Architecture'].dropna())
            return sorted(list(acv_arch.union(tcv_arch)))
        except Exception as e:
            print(f"Architektúrák lekérési hiba: {e}")
            return ['Unknown']

    def get_rolling_analysis(self, end_month, architecture=None):
        """12+12 hónapos gördülő elemzés"""
        try:
            end_date = self._convert_fiscal_month(end_month)
            
            # Rolling logika: 11 hónappal korábban kezdjük (hogy 12 hónapos legyen)
            current_start_month = self._subtract_fiscal_months(end_month, 11)
            reference_start_month = self._subtract_fiscal_months(end_month, 23)
            
            current_start_date = self._convert_fiscal_month(current_start_month)
            reference_start_date = self._convert_fiscal_month(reference_start_month)
            
            # Referencia időszak vége
            reference_end_month = self._subtract_fiscal_months(current_start_month, 1)
            reference_end_date_display = self._convert_fiscal_month(reference_end_month)
            
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
            
            # Összesítések
            acv_current = self._aggregate_data(self.acv_df[acv_current_mask], 'Sum of ACV_BOOKINGS_AMT_USD')
            acv_reference = self._aggregate_data(self.acv_df[acv_reference_mask], 'Sum of ACV_BOOKINGS_AMT_USD')
            tcv_current = self._aggregate_data(self.tcv_df[tcv_current_mask], 'Sum of Bookings')
            tcv_reference = self._aggregate_data(self.tcv_df[tcv_reference_mask], 'Sum of Bookings')
            
            return {
                'acv_current': acv_current,
                'acv_reference': acv_reference,
                'tcv_current': tcv_current,
                'tcv_reference': tcv_reference,
                'period_info': {
                    'current_start': current_start_date.strftime('%Y-%m'),
                    'current_end': end_date.strftime('%Y-%m'),
                    'reference_start': reference_start_date.strftime('%Y-%m'),
                    'reference_end': reference_end_date_display.strftime('%Y-%m'),
                    'current_start_fiscal': current_start_month,
                    'current_end_fiscal': end_month,
                    'selected_architectures': architecture if architecture else 'Összes'
                }
            }
            
        except Exception as e:
            print(f"Elemzési hiba: {e}")
            return {
                'acv_current': {}, 'acv_reference': {},
                'tcv_current': {}, 'tcv_reference': {},
                'period_info': {}
            }

    def _aggregate_data(self, df, value_column):
        """Adatok összesítése architektúra szerint - RUGALMAS OSZLOP KERESÉS"""
        try:
            if df.empty:
                return {}
            
            # Másolat készítése
            df = df.copy()
            
            # Oszlop keresése ha nem található
            if value_column not in df.columns:
                value_candidates = [col for col in df.columns if 
                                 'booking' in col.lower() or 'amount' in col.lower() or 
                                 'value' in col.lower() or 'sum' in col.lower()]
                if value_candidates:
                    value_column = value_candidates[0]
                    print(f"💰 Érték oszlop használata: {value_column}")
                else:
                    print(f"❌ Érték oszlop nem található: {value_column}")
                    return {}
            
            # STRING ÉRTÉKEK TISZTÍTÁSA
            if df[value_column].dtype == 'object':  # Ha string típusú
                # Dollár jel és vessző eltávolítása
                df[value_column] = df[value_column].astype(str).str.replace('$', '', regex=False)
                df[value_column] = df[value_column].str.replace(',', '', regex=False)
                df[value_column] = df[value_column].str.replace(' ', '', regex=False)
                # Üres stringek kezelése
                df[value_column] = df[value_column].replace('', '0')
                # Numerikus konverzió
                df[value_column] = pd.to_numeric(df[value_column], errors='coerce').fillna(0)
            
            # Összesítés architektúra szerint
            aggregated = df.groupby('Architecture')[value_column].sum().to_dict()
            
            # Összes összesítése
            aggregated['Összes'] = df[value_column].sum()
            
            return aggregated
            
        except Exception as e:
            print(f"Aggregálási hiba: {e}")
            return {}

# Teszt a fájl végén
if __name__ == "__main__":
    print("✅ data_processor.py sikeresen betöltve!")
    print("✅ BookingAnalyzer osztály elérhető!")
