# Maestro Dashboard

Maestro Dashboard je vizualizační nástroj postavený na frameworku **Streamlit**, který slouží k přehlednému zobrazení výsledků automatizovaných testů (Maestro). Aplikace parsuje XML reporty a logy, poskytuje statistiky úspěšnosti, interaktivní grafy a detailní náhledy chyb pro platformy Android a iOS.

## Hlavní funkce
* **Podpora více platforem:** Přepínání mezi výsledky pro Android a iOS.
  
* **Interaktivní kalendář:** Filtrace testovacích běhů podle data pomocí vizuálního kalendáře.
  
* **Globální přehled:** Souhrnné statistiky (Total, Passed, Failed, Success Rate) pro celou historii testování.
  
* **Detailní analýza běhu:**
  * Koláčové grafy poměru úspěšnosti.
  * Sloupcové grafy průměrné doby trvání jednotlivých testů.
    
* **Inspekce chyb:**
  * Barevné zvýraznění chybových hlášek v logách (Error, Fatal, Exception).
  * Zobrazení screenshotů selhání u neúspěšných testů.
  * Přístup k celému obsahu `console_output.log`.

## Struktura projektu
Aplikace je rozdělena do logických modulů pro oddělení logiky načítání dat, vykreslování a samotného rozhraní.

```text
├── app.py                 # Hlavní spouštěcí soubor aplikace
├── src/
│   ├── components.py      # UI komponenty (metriky, grafy, log viewer)
│   └── data_provider.py   # Načítání a parsování XML/log souborů
├── logs/                  # Adresář pro vstupní data (viz níže)
│   ├── logs_android/
│   └── logs_ios/
└── requirements.txt       # Seznam závislostí
```

## Požadavky
* Python 3.9+
* Knihovny uvedené v requirements.txt (zejména Streamlit, Pandas, Plotly, Pillow, Streamlit Calendar).

## Instalace a spuštění
* **1. Klonování repozitáře:**

```text
git clone <url-repozitare>
cd maestro-dashboard
```

* **2. Vytvoření virtuálního prostředí (doporučeno):**

```text
python -m venv venv

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

* **3. Instalace závislostí:**

```text
pip install streamlit pandas plotly streamlit-calendar
```

* **4. Spuštění aplikace:**

```text
streamlit run app.py
```

## Organizace dat (Složka logs)
Aby aplikace správně načetla data, je nutné dodržet přesnou strukturu složek uvnitř adresáře `logs`. Aplikace očekává XML reporty (JUnit format) a případné screenshoty/logy.
Struktura musí vypadat následovně:
```text
logs/
├── logs_android/                     # Data pro Android sekci
│   └── <timestamp_nebo_id_behu>/     # Složka konkrétního běhu (např. 2026-02-13_06-09-21)
│       ├── report_1.xml              # Výsledek testu (JUnit XML)
│       ├── fail_1.png                # Screenshot chyby (volitelné, musí odpovídat ID testu)
│       └── console_output.log        # Textový log testu
│
└── logs_ios/                         # Data pro iOS sekci
    └── <timestamp_nebo_id_behu>/
        ├── report_1.xml
        └── ...
```

## Formát souborů

* **XML Reporty**: Aplikace parsuje standardní JUnit XML výstup. Klíčové atributy jsou `testcase name`, `time` a element `failure` pro detekci chyb.

* **Screenshoty**: Pokud test selže, aplikace hledá obrázek ve formátu `fail_{ID}.png`, kde `{ID}` odpovídá číslu v názvu XML souboru (např. pro `report_123.xml` hledá `fail_123.png`).

* **Logy**: Pro zobrazení detailního výpisu se očekává soubor pojmenovaný `console_output.log`.


## Logika aplikace
* **Načítání dat**: Skript data_provider.py skenuje složky logs_android nebo logs_ios na základě výběru uživatele.

* **Kalendář:** Z názvů složek (očekává se datum ve formátu YYYY-MM-DD na začátku názvu složky) se generují události do kalendáře.

* **Visualizace:**

  * `render_metrics`: Počítá success rate a průměrné časy.
  * `highlight_logs`: Prochází text logu a aplikuje HTML stylování na řádky obsahující klíčová slova jako "ERROR" nebo "FAIL".


## Řešení problémů
* **Chyba: Žádná data nebyla nalezena**

  * Ověřte, že ve složce projektu existuje složka `logs`.
  * Ověřte, že podadresáře jsou pojmenovány přesně `logs_android` a `logs_ios`.
  * Zkontrolujte, zda XML soubory nejsou poškozené.

* **Chyba: Nezobrazují se screenshoty**

  * Ujistěte se, že název screenshotu odpovídá konvenci `fail_{test_id}.png`. ID testu je odvozeno z názvu XML souboru (např. `report_5.xml` -> ID `5`).
