"""Génère le logo, les icônes et l'image de partage (Open Graph) du site.

Usage : python site/make_images.py   (nécessite Pillow ; police Bahnschrift de Windows pour l'image de partage)
"""
import pathlib
from PIL import Image, ImageDraw, ImageFont

SITE = pathlib.Path(__file__).resolve().parent
NAVY, PAPER, INK, MUTED = "#161d30", "#0e1321", "#e6eaf4", "#98a3bd"
AID, WORK, GAIN, LINE = "#eaa845", "#86a2ff", "#5ccb9b", "#29324d"

# ---------- logo vectoriel : deux jauges (sans emploi / salarié) ----------
LOGO_SVG = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="salaire-ou-aides.fr">
<rect width="64" height="64" rx="14" fill="{NAVY}"/>
<rect x="15" y="30" width="13" height="20" rx="3" fill="{AID}"/>
<rect x="36" y="14" width="13" height="36" rx="3" fill="{WORK}"/>
</svg>
"""
(SITE / "favicon.svg").write_text(LOGO_SVG, encoding="utf-8")

def mark(size):
    s = size / 64
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=14 * s, fill=NAVY)
    d.rounded_rectangle([15 * s, 30 * s, 28 * s, 50 * s], radius=3 * s, fill=AID)
    d.rounded_rectangle([36 * s, 14 * s, 49 * s, 50 * s], radius=3 * s, fill=WORK)
    return im

for size, name in ((32, "favicon-32.png"), (180, "apple-touch-icon.png"), (512, "icon-512.png")):
    big = mark(size * 4).resize((size, size), Image.LANCZOS)
    big.save(SITE / name)

# ---------- image de partage 1200 × 630 ----------
W, H = 1200, 630
img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

def font(size, variation=None, path="C:/Windows/Fonts/bahnschrift.ttf"):
    f = ImageFont.truetype(path, size)
    if variation:
        try:
            f.set_variation_by_name(variation)
        except Exception:
            pass
    return f

f_title = font(78, "Bold Condensed")
f_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 30)
f_brand = font(30, "SemiBold")
f_num = font(150, "Bold Condensed")
f_unit = font(44, "Bold Condensed")
f_small = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 26)
f_mono = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 22)

# marque
img.paste(mark(256).resize((56, 56), Image.LANCZOS), (64, 56), mark(256).resize((56, 56), Image.LANCZOS))
d.text((136, 66), "salaire-ou-aides.fr", font=f_brand, fill=INK)

# titre et sous-titre
d.text((64, 160), "Ce que rapporte", font=f_title, fill=INK)
d.text((64, 244), "vraiment le travail", font=f_title, fill=INK)
d.text((64, 352), "Vivre des aides ou travailler :", font=f_sub, fill=MUTED)
d.text((64, 392), "le calcul, foyer par foyer, tout compris.", font=f_sub, fill=MUTED)

# carte chiffre clé
x0, y0, x1, y1 = 720, 150, 1136, 470
d.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=NAVY, outline=LINE, width=2)
d.text((x0 + 36, y0 + 24), "3,4 €", font=f_num, fill=WORK)
d.text((x0 + 40, y0 + 190), "restent en plus sur 10 €", font=f_small, fill=INK)
d.text((x0 + 40, y0 + 222), "de salaire, au SMIC", font=f_small, fill=MUTED)
for i in range(10):
    cx, cy, r = x0 + 52 + i * 34, y0 + 284, 12
    if i < 3:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GAIN)
    else:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=LINE, width=3)

# pied
d.line([64, 540, W - 64, 540], fill=LINE, width=2)
d.text((64, 560), "BARÈMES 2026  ·  CALCULS OPENFISCA  ·  10 FOYERS TYPES + VOTRE PROFIL", font=f_mono, fill=MUTED)

img.save(SITE / "og.png", optimize=True)
print("images générées dans", SITE)
