# Instrukcja Gumroad - GitMind Self-hosted

## Krok 1: Załóż produkt

1. Wejdź na https://app.gumroad.com/products/new
2. Wybierz "Single product" (nie "Subscription")

## Krok 2: Wypełnij szczegóły

### Basic Info:
- **Product name:** GitMind Self-hosted
- **Description:** (skopiuj z GUMROAD_PRODUCT.md)
- **Price:** $29

### Variants (opcjonalne):
Dodaj wariant "Z wsparciem" za $49:
- Kliknij "Add variant"
- Name: "Z priorytetowym wsparciem"
- Price: $49

## Krok 3: Upload content

1. Kliknij "Add content" (po lewej)
2. Wybierz "Link" lub "File"
3. Dla początku wybierz "Link" i wklej: `https://github.com/felanraf-gif/rafmos`
4. Opis: "Kod źródłowy + dokumentacja"

## Krok 4: Ustawienia

- **Free preview:** OFF
- **Comments:** ON (żeby ludzie mogli zadawać pytania)
- **Custom redirect URL:** (zostaw puste)

## Krok 5: Publish

1. Kliknij "Save draft" (żeby przetestować)
2. Lub "Publish" (żeby było live)

## Krok 6: Pobierz link

Po zapisaniu znajdziesz link w polu "Link" - będzie wyglądać tak:
```
https://gumroad.com/l/gitmind
```
(lub inny unikalny ID)

## Krok 7: Zaktualizuj landing page

W pliku `docs/buy-now.html` zamień linki:
```html
<a href="https://gumroad.com/l/gitmind" class="btn btn-primary">
```

Zamień na Twój prawdziwy link z Gumroad.

---

## Co jeszcze musisz przygotować?

### Opcja A: Link do GitHub (najprostsza)
- repository musi być publiczne LUB
- dodaj kupujących jako collaborators po zakupie

### Opcja B: ZIP z kodem
1. Spakuj cały projekt do ZIP
2. Upload w Gumroad jako "File"

### Opcja C: License key system (zaawansowane)
Wymaga dodatkowej integracji - pomiń na początek.

---

## Status?

Powiedz mi kiedy masz link do Gumroad, to zaktualizuję landing page.
