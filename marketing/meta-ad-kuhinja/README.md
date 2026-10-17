# Meta oglas – kuhinja "od nule" (hook video)

`kuhinja-hook-9x16.mp4` – 13 s, 1080×1920 (9:16), 30 fps, H.264, za Reels/Stories.

| Vrijeme | Što se vidi | Tekst gore |
|---|---|---|
| 0–1,3 s | Prostor se iscrta kao tamni tehnički crtež | Od skice |
| 1,3–5,1 s | Elementi se ugrađuju redom: donji elementi, visoki element s pećnicom, radna ploča, gornji elementi, šank, police, barske stolice | do montaže |
| 5,1–7,2 s | Zidovi, pod i detalji se "upale", pali se LED rasvjeta | *do zadnjeg detalja.* |
| 8–13 s | Gotova kuhinja stoji mirno | Želiš iskoristiti svaki kutak svog doma na najbolji način? *Onda si na pravom mjestu.* |

Ova mapa nije povezana sa stranicom (ništa je ne učitava).

## Ponovno renderiranje

```
pip install numpy pillow opencv-python-headless
python3 render.py                    # -> kuhinja-hook-9x16.mp4
python3 render.py --preview 2.5 9    # PNG kadrovi za zadane sekunde
```

- `kuhinja-izvor.jpg` – izvorna fotografija
- `elements.py` – maske elemenata (poligoni u pikselima fotografije) i redoslijed/smjer ugradnje
- `render.py` – animacija, tekstovi i tajming (`T_DRAW`, `T_WIPE`, `T_LIGHT`, `BUILD_TIMES`, `FINAL_TIMES`)
- `fonts/` – Newsreader (font sa stranice, OFL licenca); Inter se uzima iz sustava
