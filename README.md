# Apteka z Lekami 💊

Aplikacja: https://apteka-t9gi.vercel.app/

Aplikacja do nauki testów automatycznych w **Playwright + pytest**.
Panel apteki: dashboard sprzedaży z wykresami, magazyn leków (CRUD), kasa
z obsługą recept i ostrzeżeniami o interakcjach, historia sprzedaży, REST API.

Stack: Python, Flask, SQLite, Chart.js. Wszystko działa lokalnie, bez internetu.

## Uruchomienie

```bash
python -m venv venv
```

Aktywacja środowiska wirtualnego:

```bash
source venv/bin/activate          # Linux / macOS
```

```powershell
.\venv\Scripts\Activate.ps1       # Windows (PowerShell)
```

Potem:

```bash
python -m pip install -r requirements-dev.txt
python -m playwright install chromium

python run.py                     # http://127.0.0.1:5000
```

W PowerShell nie używaj `source` — to polecenie powłoki Unix.
Jeśli `pip` nie jest rozpoznawany, użyj `python -m pip` (jak wyżej).

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

Zadania są podzielone na etapy:

1. **Etap 1: testy UI „na surowo”**, tak jak na saucedemo: `page`, lokatory, `expect`.
2. **Etap 2: refaktoryzacja.** Te same testy przepisujesz na gotowe Page Objecty i fixtury.
3. **Etap 3: trudniejsze testy UI**: tabele, sortowanie, `parametrize`, dialogi.
4. **Etap 4 (później): testy API i techniki zaawansowane.**

> Gotowe testy w `tests/test_*.py` częściowo rozwiązują te zadania. Najpierw spróbuj sam, dopiero potem porównaj.

### Jak zacząć

Swoje testy trzymaj w osobnym folderze, np. `tests/moje/test_leki.py` i `tests/moje/test_kasa.py`.
Uruchamianie:

```bash
python -m pytest tests/moje --headed            # wszystkie Twoje testy
python -m pytest tests/moje/test_kasa.py -v     # jeden plik
```

Dobrze wiedzieć:

- **Aplikacji nie musisz uruchamiać ręcznie.** Testy robią to same.
- **Baza jest resetowana przed każdym testem**, więc zawsze startujesz z tymi samymi danymi (tabela niżej).
  Lek dodany w jednym teście nie istnieje w następnym.
- `page.goto("/kasa")` wystarczy. Adres serwera jest dopisywany automatycznie.

Szablon pliku z logowaniem, jak na saucedemo:

```python
from playwright.sync_api import Page, expect


def login(page: Page, username="farmaceuta", password="farmaceuta123"):
    page.goto("/login")
    page.get_by_label("Login").fill(username)
    page.get_by_label("Hasło").fill(password)
    page.get_by_role("button", name="Zaloguj się").click()
    expect(page.get_by_role("heading", name="Pulpit")).to_be_visible()


def test_moj_pierwszy_test(page: Page):
    login(page)
    page.goto("/leki/")
    expect(page.get_by_role("heading", name="Leki")).to_be_visible()
```

### Ściąga

```python
page.get_by_label("Kategoria").select_option("Alergia")        # dropdown po tekście opcji
page.get_by_label("Lek", exact=True).select_option("30")       # dropdown po wartości (ID leku)
page.get_by_label("Lek wydawany na receptę").check()           # checkbox
page.get_by_label("Gotówka").check()                           # radio
page.get_by_label("Data ważności").fill("2030-12-31")          # pole daty: zawsze RRRR-MM-DD
page.get_by_role("button", name="Dodaj lek").click()
page.get_by_role("link", name="Apap", exact=True).click()
page.get_by_test_id("cart-total")                              # elementy z atrybutem data-testid

expect(locator).to_have_text("22,98 zł")
expect(locator).to_contain_text("Amotaks")
expect(locator).to_have_count(3)
expect(locator).to_be_visible()
expect(page).to_have_url("/leki/")
```

**Nie wiesz, jak złapać element?** Uruchom nagrywarkę. Sama podpowiada lokatory, gdy klikasz po stronie:

```bash
python run.py                                         # w jednym terminalu
python -m playwright codegen http://127.0.0.1:5000    # w drugim
```

Możesz też w przeglądarce zrobić prawy klik → **Zbadaj** i poszukać `data-testid`, `id` albo tekstu etykiety `<label>`.

### Dane startowe

| ID | Lek | Cena | Stan | Uwagi |
|---:|---|---:|---:|---|
| 1 | Apap | 12,99 zł | 120 | OTC |
| 2 | Ibuprom | 15,49 zł | 95 | OTC |
| 8 | Amotaks | 17,20 zł | 40 | **Rx**, antybiotyk |
| 14 | Warfin | 16,75 zł | 5 | **Rx**, niski stan |
| 21 | Smecta | 17,50 zł | 30 | **przeterminowana** |
| 23 | Zyrtec | 16,90 zł | 60 | OTC |
| 28 | Sudafed | 19,99 zł | 3 | OTC, niski stan |
| 29 | Otrivin | 16,50 zł | 70 | OTC |
| 30 | Rutinoscorbin | 11,49 zł | 150 | OTC |

Leków jest łącznie 32. ID widać w adresie strony leku (`/leki/30`).

---

### Etap 1: testy UI bez Page Objectów

Każde zadanie to osobny test. Zaloguj się funkcją `login(page)` z szablonu.

**1. Logowanie kierownika**
Zaloguj się jako `kierownik` / `kierownik123`.
✔ Na dole menu widać „Anna Nowak” (`user-name`) i rolę „kierownik” (`user-role`).

**2. Nawigacja po menu**
Kliknij kolejno linki „Leki”, „Kasa”, „Sprzedaż”, „Pulpit”.
✔ Po każdym kliknięciu nagłówek strony (`heading`) to odpowiednio: „Leki”, „Kasa”, „Historia sprzedaży”, „Pulpit”.
*Podpowiedź: na pulpicie jest też przycisk „Nowa sprzedaż”, więc użyj `get_by_role("link", name="Sprzedaż", exact=True)`.
Bez `exact=True` Playwright znajdzie 2 elementy i zgłosi błąd „strict mode violation”.*

**3. Wyszukiwanie leku**
Na liście leków wpisz „para” w pole „Szukaj” i kliknij „Filtruj”.
✔ Tekst `drugs-count` to „Znaleziono: 3” (Apap, Gripex Max, Theraflu Extra; szukanie działa też po substancji czynnej).

**4. Filtr kategorii (dropdown)**
Na liście leków wybierz kategorię „Antybiotyki” i kliknij „Filtruj”.
✔ Są 3 wiersze (`drug-row`), a nazwy (`.drug-name`) to „Amotaks”, „Augmentin”, „Klacid”.

**5. Dodanie leku (formularz z dropdownami)**
Kliknij „+ Dodaj lek” i wypełnij formularz:
Nazwa „No-Spa”, substancja „drotaweryna”, postać **tabletki**, dawka „40 mg”,
kategoria **Układ pokarmowy**, cena „14,99”, stan „30”, minimum „10”, data ważności „2030-12-31”.
Kliknij „Dodaj lek”.
✔ Komunikat (`flash-success`) to „Dodano lek No-Spa.”
✔ Cena na stronie leku (`detail-price`) to „14,99 zł”.
➕ Bonus: przejdź na listę, wyszukaj „No-Spa” i sprawdź, że jest dokładnie 1 wynik.

**6. Dodanie leku na receptę**
Tak jak w zadaniu 5, ale zaznacz checkbox „Lek wydawany na receptę”, a postać ustaw na **syrop**.
✔ Na stronie leku widać badge „Rx”.

**7. Walidacja formularza**
Otwórz formularz nowego leku i od razu kliknij „Dodaj lek”.
✔ Widać ramkę błędów (`form-errors`).
✔ `error-name` to „Nazwa jest wymagana.”
Potem wpisz cenę „abc” i zapisz ponownie.
✔ `error-price` to „Niepoprawna cena (np. 12,50).”

**8. Edycja ceny**
Wejdź na `/leki/1` (Apap), kliknij „Edytuj” i zmień cenę na „13,49”. Zapisz.
✔ `flash-success` to „Zapisano zmiany: Apap.”
✔ `detail-price` to „13,49 zł”.

**9. Przyjęcie dostawy**
Wejdź na `/leki/28` (Sudafed, stan 3). W polu „Ilość” wpisz „50” i kliknij „Przyjmij”.
✔ `detail-stock` to „53 szt.”

**10. Sprzedaż kartą**
W kasie wybierz lek Rutinoscorbin (wartość `30`), wpisz ilość „2” i kliknij „Dodaj do koszyka”.
✔ `cart-total` to „22,98 zł”.
Zaznacz „Karta” i kliknij „Zakończ sprzedaż”.
✔ Na paragonie `receipt-total` to „22,98 zł”, a `receipt-payment` to „Karta”.
➕ Bonus: wejdź na `/leki/30` i sprawdź, że stan spadł do „148 szt.”

**11. Sprzedaż gotówką z resztą**
Sprzedaj 1 × Zyrtec (16,90 zł). Wybierz „Gotówka” i w polu „Otrzymano” wpisz „20”.
✔ Jeszcze przed kliknięciem podgląd `change-preview` pokazuje „Reszta: 3,10 zł”.
✔ Po zakończeniu sprzedaży `receipt-change` to „3,10 zł”.

**12. Lek na receptę bez kodu**
W kasie dodaj Amotaks (wartość `8`) bez kodu recepty.
✔ `pos-error` to „Amotaks: lek na receptę — podaj kod recepty.”
Potem wpisz kod „1234” i dodaj ponownie.
✔ Lek jest w koszyku (`cart-item-name`).
*Podpowiedź: pole „Kod recepty” pojawia się dopiero po wybraniu leku Rx.*

**13. Za mało towaru**
Spróbuj sprzedać 5 × Sudafed (wartość `28`, na stanie są 3 sztuki).
✔ `pos-error` to „Sudafed: niewystarczający stan magazynowy (dostępne: 3).”

**14. Usuwanie z koszyka**
Dodaj do koszyka Apap i Ibuprom. Kliknij „×” (`remove-item`) przy pierwszej pozycji.
✔ W koszyku zostaje 1 wiersz (`cart-row`) z Ibupromem.
Kliknij „Wyczyść”.
✔ Widać „Koszyk jest pusty.” (`cart-empty`).

**15. Usuwanie leku (okno potwierdzenia)**
Zaloguj się jako **kierownik**, wejdź na `/leki/29` (Otrivin) i kliknij „Usuń”.
Przeglądarka pokaże okno `confirm()`. Musisz je zaakceptować, **zanim** klikniesz:
```python
page.once("dialog", lambda dialog: dialog.accept())
```
✔ `flash-success` to „Usunięto lek Otrivin.”
➕ Bonus: zaloguj się jako farmaceuta i sprawdź, że przycisku „Usuń” nie ma (`to_have_count(0)`).

---

### Etap 2: przepisanie na Page Objecty i fixtury

Gdy etap 1 działa, przepisz te same testy krok po kroku. Po każdej zmianie odpal je ponownie.
Muszą dalej przechodzić, bo refaktoryzacja nie zmienia działania testu.

**Krok A: fixtura zamiast `login()`**

Fixtury `farmaceuta_page` i `kierownik_page` dają stronę, która jest **już zalogowana**
(logowanie przez API, bez klikania w formularz). Są szybsze i nie trzeba ich importować.

```python
# przed
def test_edycja_ceny(page: Page):
    login(page)
    page.goto("/leki/1")
    ...

# po
def test_edycja_ceny(farmaceuta_page: Page):
    farmaceuta_page.goto("/leki/1")
    ...
```

Funkcję `login()` zostaw tylko w teście logowania (zadanie 1), bo tam właśnie sprawdzasz formularz.

**Krok B: gotowe Page Objecty z `tests/pages/`**

```python
from pages import DrugFormPage, DrugsPage, LoginPage, PosPage
```

| Strona | Klasa | Co ma |
|---|---|---|
| Logowanie | `LoginPage` | `goto()`, `login(user, pass)`, `error` |
| Lista leków | `DrugsPage` | `goto()`, `search(tekst)`, `row(nazwa)`, `rows`, `names`, `count`, `empty`, `add_button` |
| Formularz leku | `DrugFormPage` | `goto_new()`, `fill(name=..., category=..., ...)`, `save()`, `error("price")`, `errors_alert` |
| Kasa | `PosPage` | `goto()`, `add("Apap", quantity=2, prescription_code="1234")`, `checkout("Gotówka", cash="20")`, `total`, `cart_rows`, `cart_names`, `error` |

Przykład dla zadania 11:

```python
# przed
def test_gotowka_reszta(page: Page):
    login(page)
    page.goto("/kasa")
    page.get_by_label("Lek", exact=True).select_option("23")
    page.get_by_label("Ilość").fill("1")
    page.get_by_role("button", name="Dodaj do koszyka").click()
    page.get_by_label("Gotówka").check()
    page.get_by_label("Otrzymano").fill("20")
    page.get_by_role("button", name="Zakończ sprzedaż").click()
    expect(page.get_by_test_id("receipt-change")).to_have_text("3,10 zł")

# po
from pages import PosPage

def test_gotowka_reszta(farmaceuta_page: Page):
    pos = PosPage(farmaceuta_page)
    pos.goto()
    pos.add("Zyrtec")
    pos.checkout("Gotówka", cash="20")
    expect(farmaceuta_page.get_by_test_id("receipt-change")).to_have_text("3,10 zł")
```

Test czyta się teraz jak scenariusz, a gdy zmieni się HTML kasy, poprawiasz lokator w jednym miejscu (`PosPage`), a nie w każdym teście.

**Krok C: dopisz to, czego brakuje w POM**

Część zadań z etapu 1 nie ma jeszcze metod w Page Objectach. Dopisanie ich to dobre ćwiczenie:

- `DrugsPage.filter_category("Antybiotyki")` (zadanie 4)
- `PosPage.remove_item(0)` i `PosPage.clear_cart()` (zadanie 14)
- nowa klasa `DrugDetailPage` w `tests/pages/drug_detail_page.py`, z metodami `goto(drug_id)`, `restock(ilosc)`, `edit()`, `delete()` i lokatorami `price`, `stock`
  (zadania 8, 9 i 15). Pamiętaj, żeby dopisać ją do `tests/pages/__init__.py`.

---

### Etap 3: trudniejsze testy UI

16. **Sortowanie po cenie**, wzorem `test_saucedemo_sort.py`: kliknij nagłówek „Cena” i sprawdź, że ceny rosną. Kliknij jeszcze raz i sprawdź, że maleją.
    *Podpowiedź: tekst „12,99 zł” zamienisz na liczbę, usuwając „zł” i zamieniając przecinek na kropkę.*
17. **Paginacja**: 32 leki → strona 1 ma 10 wierszy, a strona 4 ma 2. `page-info` pokazuje „Strona 1 z 4”.
18. **`parametrize` walidacji ceny**: `0`, `-1`, `abc`, `12,345`, `1000,01`, każdy z oczekiwanym komunikatem.
19. **Data ważności w przeszłości** daje błąd `error-expiry_date`.
20. **Przeterminowana Smecta** (wartość `21`): sprzedaż zablokowana.
21. **Kod recepty** `12a4` i `123` (parametrize): „Kod recepty musi składać się z 4 cyfr.”
22. **Interakcja leków**: Warfin (kod 1234) + Ibuprom → okno `interaction-modal`. Kliknij „Anuluj” i sprawdź, że Ibupromu nie ma w koszyku.
23. **Licznik koszyka w menu** (`cart-count`) rośnie po dodaniu kolejnych pozycji.
24. **Kafelek „Niski stan” na pulpicie**: kliknięcie prowadzi do przefiltrowanej listy, a liczba wierszy = liczba z kafelka.
25. **Historia sprzedaży**: data „od” późniejsza niż „do” → `sales-filter-error`. Filtr „Gotówka” → każdy wiersz w kolumnie płatności ma „Gotówka”.

---

### Etap 4 (później): API i techniki zaawansowane

Gdy UI będzie szło płynnie. Przykłady są w `tests/test_api.py` i `tests/test_dashboard.py`.

26. Weryfikacja przez API: po sprzedaży w UI sprawdź stan leku przez `api.get("/api/drugs/30")` (fixtura `api`).
27. Farmaceuta usuwa lek przez `DELETE /api/drugs/1` → 403.
28. Przygotowanie danych przez API (`POST /api/sales`), a sprawdzenie wyniku w UI (historia, kafelki na pulpicie).
29. Pobranie CSV: `with page.expect_download() as d:` → sprawdź nagłówek i liczbę wierszy.
30. Mock API: `page.route` zwraca własne dane „top 5” → lista na pulpicie pokazuje Twoje nazwy.
31. Opóźnienie odpowiedzi w `page.route` → spinner jest widoczny w trakcie ładowania.
32. Zmiana zakresu wykresu na 7 dni: `page.expect_response("**/api/stats/revenue?days=7")`.
33. Test na widoku mobilnym (`--device "iPhone 13"`).
34. Testy równoległe (`pip install pytest-xdist`, `-n 4`). Co się psuje przy wspólnej bazie i jak to naprawić?

## CI (GitHub Actions)

`.github/workflows/e2e.yml` uruchamia testy przy każdym PR i pushu na `main`.
Po błędzie trace’y są w zakładce **Actions → run → Artifacts**.

Ćwiczenie: utwórz branch, zepsuj coś w aplikacji (np. usuń `stock - ?`
w `services.create_sale`), otwórz PR i zobacz, który test to złapie.
