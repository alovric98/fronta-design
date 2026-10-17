# Meta oglas – kuhinja "od nule" (hook video)

`kuhinja-hook-9x16.mp4` – 13 s, 1080×1920 (9:16), 30 fps, H.264, za Reels/Stories.

| Vrijeme | Što se vidi | Tekst gore |
|---|---|---|
| 0–1,3 s | Prostor se iscrta kao tamni tehnički crtež | Od skice |
| 1,3–5,1 s | Elementi se ugrađuju redom: donji elementi, visoki element s pećnicom, radna ploča, gornji elementi, šank, police, barske stolice | do montaže |
| 5,1–7,2 s | Zidovi, pod i detalji se "upale", pali se LED rasvjeta | *do zadnjeg detalja.* |
| 8–13 s | Gotova kuhinja stoji mirno | Želiš iskoristiti svaki kutak svog doma na najbolji način? *Onda si na pravom mjestu.* |

Ova mapa nije povezana sa stranicom (ništa je ne učitava).

## Kako je složeno

Animacija je HTML + CSS + GSAP, a u MP4 je renderira [HyperFrames](https://hyperframes.heygen.com):

- `hyperframes/index.html` – cijeli motion design: raspored, tekstovi, tajming (GSAP timeline na dnu datoteke). Za promjenu teksta, boja ili tempa mijenja se samo ova datoteka.
- `hyperframes/assets/layers/` – slojevi izrezani iz fotografije (crtež, svaki element posebno, prostor, svjetlo ugašeno/upaljeno).
- `hyperframes/assets/fonts/` – Newsreader i Inter (fontovi sa stranice, OFL licenca); `assets/vendor/gsap.min.js` – GSAP 3.14.2.
- `layers.py` + `elements.py` – izrezuju slojeve iz `kuhinja-izvor.jpg`. `elements.py` drži poligone elemenata u pikselima fotografije. Ponovo pokrenuti samo kad se mijenja fotografija ili maske.

## Naredbe

```
cd hyperframes
npm run dev       # preview u pregledniku (HyperFrames Studio)
npm run check     # lint + provjera layouta i kontrasta
npm run render    # -> ../kuhinja-hook-9x16.mp4
npm run layers    # ponovno izrezivanje slojeva (treba: pip install numpy pillow opencv-python-headless)
```

Za render treba Node 22+, FFmpeg i Chrome Headless Shell (`npx hyperframes browser ensure`,
ili postojeći preglednik preko varijable `HYPERFRAMES_BROWSER_PATH`).
