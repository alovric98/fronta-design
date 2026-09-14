# SEO paket za frontadesign.hr — gotov za ugradnju

Ovo je dorađena i proširena verzija SEO plana (nadovezuje se na `seo-brief-fronta-design.md` od prije, ali ovaj put s gotovim, copy-paste tekstom i kodom umjesto checkliste). Temelji se na stvarnom trenutnom sadržaju `index.html`.

## ⚠️ 0. KRITIČNO — napravi ovo prvo, prije svega ostalog

U trenutnom `index.html`, redak 20, stoji:

```html
<meta name="robots" content="noindex">
```

Ovo eksplicitno govori Googleu "nemoj me indeksirati". Dok god ovo stoji, apsolutno ništa iz ostatka ovog dokumenta neće imati efekta — stranica se neće pojaviti na Googleu bez obzira na title, meta description ili schema. Ovo je vjerojatno bilo namjerno dok je stranica bila u izradi.

**Zamijeniti s:**
```html
<meta name="robots" content="index, follow">
```
(ili taj red jednostavno obrisati — `index, follow` je default ponašanje ako meta robots uopće ne postoji).

## 1. Meta tagovi u `<head>`

Postojeći title je već dobar, zadržati:
```html
<title>Fronta Design — namještaj po mjeri, Slavonski Brod</title>
```

Dodati (trenutno nedostaje, kako i piše u dev TODO komentaru na vrhu fajla):
```html
<meta name="description" content="Izrada i montaža namještaja po mjeri u Slavonskom Brodu i okolici — kuhinje, ugradbeni ormari, komode i radne sobe. Besplatna izmjera na adresi, izrada i montaža bez podizvođača.">
<link rel="canonical" href="https://frontadesign.hr/">
```

## 2. Open Graph / Twitter Card (za dijeljenje linka na Facebooku, WhatsAppu i sl.)

Koristi postojeću hero sliku dok klijent ne pošalje namjensku OG sliku:

```html
<meta property="og:type" content="website">
<meta property="og:title" content="Fronta Design — namještaj po mjeri, Slavonski Brod">
<meta property="og:description" content="Izrada i montaža namještaja po mjeri u Slavonskom Brodu i okolici — kuhinje, ugradbeni ormari, komode i radne sobe.">
<meta property="og:image" content="https://frontadesign.hr/images/hero-ladicar-wide.jpg">
<meta property="og:url" content="https://frontadesign.hr/">
<meta property="og:locale" content="hr_HR">
<meta name="twitter:card" content="summary_large_image">
```

## 3. H1/H2 — sadržaj je već dobar, ne prepisivati

Postojeći H1 ("Izrada i montaža namještaja po mjeri.") i H2 naslovi sekcija su već prirodno napisani i sadrže ključne riječi bez keyword-stuffinga — nema potrebe za prepisivanjem. Jedina sitna dopuna: u karticama u sekciji Projekti (`<h3>Kuhinje po mjeri</h3>`, `<h3>Ormari po mjeri</h3>`, itd.) po želji dodati "— Slavonski Brod" ako klijent želi jače lokalno signaliziranje, npr:

```html
<h3>Kuhinje po mjeri — Slavonski Brod</h3>
```

Nije obavezno, tekst ispod kartica (dl.meta-row) već navodi "Lokacija: Slavonski Brod" za svaki projekt, što je dovoljno.

## 4. Alt tekstovi — dorada postojećih

Postojeći alt tekstovi su OK, ali generički. Doraditi na specifičnije (pomaže i Google Images rangiranju):

| Trenutni alt | Novi alt |
|---|---|
| `alt="Namještaj izrađen po mjeri"` (hero) | `alt="Namještaj po mjeri izrađen za dom u Slavonskom Brodu"` |
| `alt="Kuhinja po mjeri"` | `alt="Kuhinja po mjeri, izrada i montaža — Slavonski Brod"` |
| `alt="Ormar po mjeri"` | `alt="Ugradbeni ormar po mjeri — Slavonski Brod"` |
| `alt="Komoda po mjeri"` | `alt="Komoda i ladičar izrađeni po mjeri — Slavonski Brod"` |
| `alt="Radni stol po mjeri"` | `alt="Namještaj za radnu sobu po mjeri — Slavonski Brod"` |

**Napomena implementatoru:** galerija unutar modala/lightboxa (klik na "Galerija →") generira se dinamički u `js/main.js`, koji nisam pregledao u ovom paketu — provjeri tamo da svaka slika u galeriji dobiva smislen `alt`, ne prazan string ili samo broj.

## 5. JSON-LD structured data (lokalni biznis)

Ubaciti prije `</head>` (podaci potvrđeni s korisnikom — adresa i telefon isti kao na Google Business Profileu):

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "HomeAndConstructionBusiness",
  "name": "Fronta Design",
  "legalName": "Fronta design j.d.o.o.",
  "image": "https://frontadesign.hr/images/hero-ladicar-wide.jpg",
  "url": "https://frontadesign.hr/",
  "telephone": "+385976113362",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Ulica Tadije Smičiklasa 47",
    "addressLocality": "Slavonski Brod",
    "postalCode": "35000",
    "addressCountry": "HR"
  },
  "areaServed": "Slavonski Brod i okolica",
  "priceRange": "$$",
  "makesOffer": [
    { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Kuhinje po mjeri" } },
    { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Ugradbeni ormari po mjeri" } },
    { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Komode i ladičari po mjeri" } },
    { "@type": "Offer", "itemOffered": { "@type": "Service", "name": "Namještaj za radne sobe po mjeri" } }
  ]
}
</script>
```

**Namjerno izostavljeno:** `aggregateRating` (ocjena 5.0 s Google Business Profila). Google Rich Results pravila zahtijevaju da broj recenzija (`reviewCount`) bude točan i provjerljiv na stranici — ako se doda netočan/izmišljen broj, Google to tretira kao spam schema i može kazniti cijelu domenu. Kad budeš znao točan broj recenzija, dodaj:
```json
"aggregateRating": {
  "@type": "AggregateRating",
  "ratingValue": "5.0",
  "reviewCount": "BROJ_RECENZIJA_OVDJE"
}
```

## 6. `robots.txt` (novi fajl, root repozitorija)

```
User-agent: *
Allow: /

Sitemap: https://frontadesign.hr/sitemap.xml
```

## 7. `sitemap.xml` (novi fajl, root repozitorija)

Stranica je trenutno one-page (sve sekcije su anchor linkovi #pocetna, #projekti, #o-nama, #kontakt unutar iste stranice), pa sitemap ima samo jedan URL:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://frontadesign.hr/</loc>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
```

## 8. Sitni popravci prije launcha (nisu striktno SEO, ali utječu na povjerenje/UX i vezani su uz iste TODO stavke u kodu)

- Facebook link je trenutno placeholder (`href="https://www.facebook.com"`) na dva mjesta (kontakt sekcija i footer) — zamijeniti stvarnim URL-om Fronta Design Facebook stranice kad ga klijent pošalje.
- Link "Politika privatnosti" u footeru trenutno vodi na `#kontakt` — za punu GDPR usklađenost trebala bi postojati stvarna stranica s politikom privatnosti. Ovo nije nužno za SEO rangiranje, ali vrijedi spomenuti klijentu.

## 9. Poruka za klijenta (spremna za slanje)

---

Pozdrav,

Web stranica je sada tehnički spremna za Google pretragu. Da bi sve povezali, trebam od vas dvije stvari:

**1. Poveži Google Business Profile sa stranicom**
- Uđite na business.google.com i otvorite svoj profil (Fronta Design).
- Kliknite "Uredi profil" → "Kontakt" → polje "Web-mjesto".
- Upišite: `https://frontadesign.hr`
- Spremite.

**2. Dodajte me u Google Search Console** (alat kojim pratim i prijavljujem stranicu Googleu)
- Idite na search.google.com/search-console
- Ako property za frontadesign.hr već postoji (možda je netko ranije započeo verifikaciju) → Postavke → "Korisnici i dozvole" → "Dodaj korisnika"
- Ako ne postoji, recite mi pa ga postavljam ja i dodajem vas kao vlasnika.
- Dodajte moju mail adresu s razinom pristupa "Vlasnik" (Owner).

Nakon toga stranica bi trebala početi ulaziti u Google pretragu unutar nekoliko dana do par tjedana.

---

## 10. Bonus — Lighthouse provjera performansi (jedini dio inspiriran videom koji se stvarno isplati ovdje)

Nakon što se sve gore ugradi i deploya, otvori frontadesign.hr u Chromeu → DevTools (F12) → tab **Lighthouse** → pokreni izvještaj za Performance, Accessibility, Best Practices i SEO (Mobile + Desktop).

Ako izvještaj pokaže greške (npr. prevelike slike, blokirajući render CSS/JS, nedostaje `alt`), kopiraj konkretne stavke iz izvještaja i proslijedi implementatoru da ih popravi jednu po jednu — ne treba stroga cifra 100/100 na svemu, ali vrijedi riješiti sve što je označeno crveno/narančasto (posebno "Largest Contentful Paint" ako su slike neoptimizirane, spomenuto je već u prvom SEO briefu kao WebP + lazy loading).

Napomena: ostatak pristupa iz videa (Semrush keyword research, programmatic "grad+usluga" stranice, blog automatizacija, Pexels API) namjerno je izostavljen iz ovog paketa — za frontadesign.hr (jednostranačna stranica, poslovanje isključivo u Slavonskom Brodu) taj pristup nosi veći rizik (thin/duplicate content penalizacija) nego korist, i predstavlja odvojen, veći i kontinuiran projekt, a ne dio jednokratnog 150€ paketa.

## Verifikacija nakon ugradnje (checklist za tebe/implementatora)

- [ ] `noindex` uklonjen ili promijenjen u `index, follow` — provjeri view-source uživo nakon deploya.
- [ ] JSON-LD prolazi bez grešaka na search.google.com/test/rich-results (zalijepi frontadesign.hr URL).
- [ ] `frontadesign.hr/robots.txt` i `frontadesign.hr/sitemap.xml` su dostupni nakon deploya.
- [ ] Svaka `<img>` na stranici ima neprazan, opisan `alt` (uključujući modal/lightbox galeriju u JS-u).
- [ ] Nakon dodavanja u Search Console: poslati sitemap.xml i ručno zatražiti indeksiranje početne stranice ("Request Indexing").
- [ ] Lighthouse izvještaj (Performance/Accessibility/Best Practices/SEO) pokrenut, crvene/narančaste stavke riješene.
