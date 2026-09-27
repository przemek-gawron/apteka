# Apteka Pod Wagą 💊

Aplikacja do nauki testów automatycznych w **Playwright + pytest**.
Panel apteki: dashboard sprzedaży z wykresami, magazyn leków (CRUD), kasa
z obsługą recept i ostrzeżeniami o interakcjach, historia sprzedaży, REST API.

Stack: Python, Flask, SQLite, Chart.js. Wszystko działa lokalnie, bez internetu.

## Uruchomienie

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium

python run.py                     # http://127.0.0.1:5000
```

Konta:

| login        | hasło           | rola                                  |
|--------------|-----------------|---------------------------------------|
| `kierownik`  | `kierownik123`  | wszystko                              |
| `farmaceuta` | `farmaceuta123` | wszystko poza usuwaniem leków         |

Reset danych: `RESET_DB=1 python run.py`

## Testy

```bash
python -m pytest              # headless
python -m pytest --headed     # z widoczną przeglądarką
python -m pytest --headed --slowmo 500 tests/test_pos.py
python -m pytest -k interaction
```

**Nie musisz ręcznie uruchamiać aplikacji** — `tests/conftest.py` startuje ją
na porcie 5055 z osobną bazą i trybem `APP_ENV=test`. Przed każdym testem baza
jest resetowana (`POST /api/test/reset`), więc testy są od siebie niezależne.

Po nieudanym teście w `test-results/` jest trace. Otwórz go:

```bash
python -m playwright show-trace test-results/<folder-testu>/trace.zip
```

### Struktura

```
tests/
├── conftest.py        # start serwera, reset bazy, logowanie przez API (storage_state)
├── pages/             # Page Object Model
├── test_login.py      # parametryzacja
├── test_drugs.py      # formularze, walidacja, dialog confirm()
├── test_pos.py        # kasa, recepty, interakcje, test UI + weryfikacja przez API
├── test_api.py        # testy REST API
└── test_dashboard.py  # czekanie na dane, mockowanie odpowiedzi (page.route)
```

### Przydatne fixtury

| fixtura           | co daje                                     |
|-------------------|---------------------------------------------|
| `page`            | niezalogowana strona                        |
| `farmaceuta_page` | strona zalogowana jako farmaceuta           |
| `kierownik_page`  | strona zalogowana jako kierownik            |
| `api`             | klient REST API zalogowany jako kierownik   |

## Co jest w aplikacji

- **Pulpit** (`/`): KPI dnia, wykres obrotu (7/30/90 dni), top 5 leków, kategorie,
  tabele „do zamówienia” i „terminy ważności”. Wykresy ładują dane z API
  z celowym opóźnieniem, więc widać spinner.
- **Leki** (`/leki/`): wyszukiwanie po nazwie/substancji, filtry (kategoria,
  Rx/OTC, status), sortowanie kolumn, paginacja, szczegóły, edycja, dostawa,
  usuwanie z oknem `confirm()`.
- **Kasa** (`/kasa`): koszyk; lek Rx wymaga 4-cyfrowego kodu recepty; nie da się
  sprzedać więcej niż jest na stanie ani leku przeterminowanego; przy interakcji
  pojawia się okno ostrzeżenia; płatność kartą lub gotówką (z resztą).
- **Sprzedaż** (`/sprzedaze`): historia z filtrem dat i płatności, paginacja,
  eksport CSV, paragon.

### Reguły biznesowe (przydatne do testów)

- Niski stan = `stan <= stan minimalny`
- „Kończy się ważność” = ważny jeszcze ≤ 30 dni
- Nowy lek nie może mieć daty ważności w przeszłości; nazwa unikalna (bez względu na wielkość liter)
- Cena: > 0 i ≤ 1000 zł, format `12,50` lub `12.50`
- Dostawa: 1–1000 szt.
- Przykładowe interakcje: Warfin + Ibuprom / Acard / Klacid / Ketonal,
  Atoris + Klacid, Sertagen + Tramal, Polpril + Ibuprom, Euthyrox + Magne B6,
  Bisocard + Sudafed, Metformax + Acard
- Dane startowe: Smecta jest przeterminowana; Ketonal, Sudafed, Claritine i Warfin mają niski stan

### REST API

Logowanie cookie: `POST /api/login` `{"username": "...", "password": "..."}`

| metoda | ścieżka | opis |
|---|---|---|
| GET | `/api/me` | zalogowany użytkownik |
| GET | `/api/drugs?q=&category=&rx=rx\|otc&status=` | lista leków |
| GET/PUT/PATCH/DELETE | `/api/drugs/<id>` | jeden lek (DELETE tylko kierownik → inaczej 403) |
| POST | `/api/drugs` | dodanie (201 albo 400 z `errors`) |
| GET | `/api/interactions?drug_ids=14,2` | interakcje między lekami |
| POST | `/api/sales` | sprzedaż; przy interakcji 409, chyba że `"confirm_interactions": true` |
| GET | `/api/sales/<id>` | paragon |
| GET | `/api/stats/summary`, `/revenue?days=`, `/top-drugs?days=&limit=`, `/categories?days=` | statystyki |
| POST | `/api/test/reset` | reset bazy (tylko `APP_ENV=test`) |

## Zadania do samodzielnego napisania

Gotowe testy to tylko przykłady. Poniżej są zadania, mniej więcej od najłatwiejszych.

**Podstawy**
1. Menu: kliknij każdą pozycję i sprawdź nagłówek strony.
2. Farmaceuta wchodzi na `/leki/1/usun` przez GET → co się dzieje? A przez POST z API?
3. Filtr „Na receptę (Rx)”: każdy wiersz ma badge `Rx`.
4. Filtr „Przeterminowane” pokazuje dokładnie 1 lek (Smecta).
5. Kliknięcie KPI „Niski stan” na pulpicie prowadzi do przefiltrowanej listy, a liczba wierszy = liczba z KPI.

**Formularze**
6. Edycja leku: zmień cenę i sprawdź ją na liście i w API.
7. Walidacja ceny: `parametrize` z przypadkami `0`, `-1`, `abc`, `12,345`, `1000,01`.
8. Data ważności w przeszłości → błąd.
9. Dostawa: `+50` zwiększa stan; `0` i `abc` dają błąd.

**Tabele**
10. Sortowanie po cenie rosnąco i malejąco (wzorem `test_saucedemo_sort.py`).
11. Paginacja: 32 leki → strona 1 ma 10 wierszy, strona 4 ma 2; „Poprzednia” jest nieaktywna na stronie 1.
12. Historia sprzedaży: filtr „od > do” pokazuje błąd; filtr „Gotówka” pokazuje tylko gotówkę.

**Kasa**
13. Ilość większa niż stan → komunikat z liczbą dostępnych sztuk.
14. Smecta (przeterminowana) → sprzedaż zablokowana.
15. Kod recepty `12a4` lub `123` → błąd.
16. Gotówka: za mała kwota → błąd; podgląd „Reszta:” aktualizuje się podczas wpisywania.
17. Anulowanie okna interakcji nie dodaje leku do koszyka.
18. Usuwanie pozycji z koszyka i przycisk „Wyczyść”; licznik w menu (`cart-count`).

**Zaawansowane**
19. Pobranie CSV: `with page.expect_download() as d:` → sprawdź nagłówek i liczbę wierszy.
20. Mock API: `page.route` zwraca własne dane top 5 → lista pokazuje Twoje nazwy.
21. Wydłuż odpowiedź API (route + opóźnienie) i sprawdź, że spinner jest widoczny w trakcie.
22. Przygotuj dane przez API (`POST /api/sales`), a sprawdź wynik w UI (historia, KPI na pulpicie).
23. Zmiana zakresu wykresu na 7 dni: `page.expect_response("**/api/stats/revenue?days=7")`.
24. Test na widoku mobilnym (`--device "iPhone 13"` albo `browser_context_args`).
25. Uruchom testy równolegle (`pip install pytest-xdist`, `-n 4`). Co się psuje przy wspólnej bazie i resecie? Jak to naprawić?

## CI (GitHub Actions)

`.github/workflows/e2e.yml` uruchamia testy przy każdym PR i pushu na `main`.
Po błędzie trace’y są w zakładce **Actions → run → Artifacts**.

Ćwiczenie: utwórz branch, zepsuj coś w aplikacji (np. usuń `stock - ?`
w `services.create_sale`), otwórz PR i zobacz, który test to złapie.
