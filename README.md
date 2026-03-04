## Magyar változat

# 📊 ACV/TCV Booking Value Elemző

Ez a Streamlit alapú webalkalmazás egy interaktív eszköz, amely az ACV (Annual Contract Value) és TCV (Total Contract Value) adatok elemzésére szolgál, 12+12 hónapos gördülő nézetben, architektúrákra bontva. 
Képes múltbeli adatok elemzésére, az aktuális hónap státuszának prediktív megjelenítésére, valamint jövőbeli booking targetek meghatározására index-alapú megközelítéssel.

## ✨ Főbb funkciók

*   **Rugalmas adatintegráció**: CSV fájlokból olvassa be az ACV és TCV adatokat, akár lokálisan tárolt fájlokból, akár felhasználói feltöltésből.
*   **Architektúra-mapping**: Testreszabható mapping logikával egységesíti az architektúra neveket a konzisztens elemzés érdekében.
*   **12+12 hónapos gördülő elemzés**: Képes összehasonlítani az aktuális 12 hónapos teljesítményt az előző 12 hónapos referencia időszakkal.
*   **Predikciós képességek**:
    *   **Aktuális Hónap Státusz**: Kombinálja a már meglévő adatokat a hónapra vonatkozó index-alapú predikcióval.
    *   **Jövőbeli Hónapok Predikciója**: Meghatározza, mennyi bookingra van szükség a jövőbeli 12 hónapos periódusokban az `Index 0-10` célok eléréséhez.
*   **Index-alapú célkitűzés**: Kiszámolja a szükséges booking mennyiséget az 0-tól 10-ig terjedő indexszintek eléréséhez, ahol az `Index N` N% növekedést jelent a baseline-hoz képest. Az `Index 10` >9%-os növekedést jelöl.
*   **T-Shirt Sizing (csak TCV-hez)**: Vizuálisan segíti a TCV értékek kategorizálását (XS, S, M, L, XL), ami rávilágít a bookingok méretére és jelentőségére.
*   **Interaktív Dashboard**: Streamlit segítségével könnyen kezelhető felületet biztosít a hónap, architektúra és elemzési nézet kiválasztásához.

## 🚀 Helyi futtatás

A projekt futtatásához a következőkre van szükséged:

*   Python 3.8+
*   pip (Python csomagkezelő)

### 1. Klonozd a repository-t

```bash
git clone [A Te GitHub Repository URL-ed]
cd [a te-repository-neved]
```

### 2. Telepítsd a függőségeket

```bash
pip install -r requirements.txt
```
**Megjegyzés**: Ha nincs `requirements.txt` fájlod, akkor hozd létre a következő tartalommal:
```
streamlit
pandas
numpy
plotly
```
Majd futtasd a `pip install -r requirements.txt` parancsot.

### 3. Helyezd el az adatfájlokat

Helyezd el az `ACV.csv` és `TCV.csv` fájlokat a projekt gyökérkönyvtárába. **Fontos**: Ezeknek a fájloknak egy adott formátumot kell követniük, mely tartalmazza 
az `Architecture`, `Fiscal Year`, `Fiscal Quarter`, `FISCAL_MONTH_NAME` (vagy `Date`), valamint egy numerikus érték oszlopot (pl. `A` vagy `B`). Az alkalmazás 
megpróbálja automatikusan felismerni a megfelelő oszlopokat, de a konzisztencia kulcsfontosságú.

### 4. Futtasd az alkalmazást

```bash
streamlit run app.py
```

A böngésződ automatikusan megnyitja az alkalmazást (`http://localhost:8501`).

## 📁 Projekt struktúra

```
.
├── app.py                  # A Streamlit webalkalmazás fő kódja
├── data_processor.py       # A booking adatok feldolgozásáért és elemzéséért felelős osztály (BookingAnalyzer)
├── ACV.csv                 # ACV adatokat tartalmazó fájl (lokálisan tárolva, nem része a repository-nak)
├── TCV.csv                 # TCV adatokat tartalmazó fájl (lokálisan tárolva, nem része a repository-nak)
└── requirements.txt        # Python függőségek listája
```

## ⚠️ Adatbiztonság és adatvédelem

Ez a repository kizárólag a booking elemző alkalmazás logikáját és a felhasználói felületet tartalmazza. A bizalmas üzleti adatok (mint az `ACV.csv` és `TCV.csv` fájlok) 
**nincsenek** benne a repository-ban. A felhasználónak kell lokálisan biztosítania ezeket az adatokat. Az alkalmazás futtatása során az adatok csak a helyi környezetedben 
kerülnek feldolgozásra, és nem kerülnek külső szerverre vagy adatbázisba feltöltésre.

---

## English Version

# 📊 ACV/TCV Booking Value Analyzer

This Streamlit-based web application is an interactive tool designed for analyzing ACV (Annual Contract Value) and TCV (Total Contract Value) data. It provides a 12+12 month rolling view, 
broken down by architecture, and offers capabilities for historical data analysis, predictive visualization of the current month's status, and setting future booking targets using an index-based approach.

## ✨ Key Features

*   **Flexible Data Integration**: Reads ACV and TCV data from CSV files, either from locally stored files or user uploads.
*   **Architecture Mapping**: Uses customizable mapping logic to standardize architecture names for consistent analysis.
*   **12+12 Month Rolling Analysis**: Compares the current 12-month performance against a previous 12-month reference period.
*   **Prediction Capabilities**:
    *   **Current Month Status**: Combines existing data with index-based predictions for the ongoing month.
    *   **Future Month Prediction**: Determines the required bookings in future 12-month periods to achieve `Index 0-10` targets.
*   **Index-Based Targeting**: Calculates the necessary booking volume to reach index levels from 0 to 10, where `Index N` signifies an N% growth compared to the baseline. `Index 10` represents >9% growth.
*   **T-Shirt Sizing (TCV only)**: Visually aids in categorizing TCV values (XS, S, M, L, XL), highlighting the size and significance of bookings.
*   **Interactive Dashboard**: Provides an easy-to-use interface via Streamlit for selecting months, architectures, and analysis views.

## 🚀 How to Run Locally

To run this project, you will need:

*   Python 3.8+
*   pip (Python package manager)

### 1. Clone the repository

```bash
git clone [Your GitHub Repository URL]
cd [your-repository-name]
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```
**Note**: If you don't have a `requirements.txt` file, create one with the following content:
```
streamlit
pandas
numpy
plotly
```
Then run the `pip install -r requirements.txt` command.

### 3. Place your data files

Place your `ACV.csv` and `TCV.csv` files in the root directory of the project. **Important**: These files must follow a specific format, 
including `Architecture`, `Fiscal Year`, `Fiscal Quarter`, `FISCAL_MONTH_NAME` (or `Date`), and a numeric value column (e.g., `A` or `B`). The application attempts 
to automatically identify the correct columns, but consistency is key.

### 4. Run the application

```bash
streamlit run app.py
```

Your browser will automatically open the application at (`http://localhost:8501`).

## 📁 Project Structure

```
.
├── app.py                  # Main Streamlit web application code
├── data_processor.py       # Class responsible for processing and analyzing booking data (BookingAnalyzer)
├── ACV.csv                 # ACV data file (stored locally, not part of the repository)
├── TCV.csv                 # TCV data file (stored locally, not part of the repository)
└── requirements.txt        # List of Python dependencies
```

## ⚠️ Data Security and Privacy

This repository contains only the logic and user interface of the booking analysis application. Confidential business data (such as `ACV.csv` and `TCV.csv` files) 
**are not included** in this repository. The user must provide these data locally. During the application's runtime, data is processed only in your local environment 
and is not uploaded to any external servers or databases.
