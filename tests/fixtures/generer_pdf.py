"""Génère un PDF de conditions générales fictives, mis en page comme un vrai contrat :
sommaire, en-têtes et pieds de page, lexique « Terme : définition », intertitres sans
numéro (« Ce que nous garantissons »), titres en capitales, mots coupés en fin de ligne.

Sert à tester le découpage sur autre chose que notre Markdown bien rangé.
Usage : python tests/fixtures/generer_pdf.py
"""

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

PAGES = [
    [
        "SOMMAIRE",
        "Lexique ........................................ 3",
        "1. Les biens assurés ............................ 4",
        "2. Les événements garantis ...................... 4",
        "2.1 Incendie .................................... 4",
        "2.2 Vol et vandalisme ........................... 5",
        "3. Exclusions générales ......................... 6",
        "4. En cas de sinistre ........................... 6",
    ],
    [
        "LEXIQUE",
        "Dépendances : locaux clos et couverts, à usage exclusif de l'assuré,",
        "situés à la même adresse que l'habitation (cave, garage, box).",
        "Effraction : forcement, dégradation ou destruction d'un dispositif de",
        "fermeture.",
        "Incendie : combustion avec flammes en dehors d'un foyer normal.",
        "Mobilier de jardin : tables, chaises, parasols et objets de décoration",
        "situés à l'extérieur des bâtiments.",
        "Parties communes : locaux à usage collectif de l'immeuble, notamment le",
        "hall, les couloirs et le local à vélos.",
    ],
    [
        "1. Les biens assurés",
        "Ce que nous garantissons",
        "Le mobilier vous appartenant, situé dans les bâtiments assurés, y compris les",
        "vélos. Le mobilier de jardin est garanti à concurrence de 1 500 € par sinistre.",
        "2. Les événements garantis",
        "2.1 Incendie",
        "Ce que nous garantissons",
        "Nous garantissons les dommages matériels causés aux biens assurés par l'incen-",
        "die, l'explosion et la foudre, tels que définis au lexique.",
        "Ce que nous ne garantissons pas",
        "Les brûlures et dommages causés par la chaleur, une bougie ou un objet incan-",
        "descent, sans incendie. Les dommages subis par le mobilier de jardin du fait",
        "des intempéries ou de la chaleur.",
    ],
    [
        "2.2 Vol et vandalisme",
        "Ce que nous garantissons",
        "Nous garantissons le vol des biens assurés commis dans les bâtiments assurés",
        "ou les dépendances, avec effraction, escalade ou violences, dans les conditions",
        "de l'article 4.2.",
        "Ce que nous ne garantissons pas",
        "Le vol commis dans les parties communes de l'immeuble. Le vol commis sans",
        "effraction lorsque les locaux n'étaient pas fermés à clé.",
        "MESURES DE PRÉVENTION",
        "Vous devez fermer à clé les portes des bâtiments et des dépendances en votre",
        "absence. À défaut, l'indemnité est réduite de moitié.",
    ],
    [
        "3. Exclusions générales",
        "Nous ne garantissons jamais les dommages intentionnels, l'usure et le défaut",
        "d'entretien.",
        "4. En cas de sinistre",
        "4.1 Délais",
        "Vous devez déclarer le sinistre dans les 5 jours ouvrés, 2 jours en cas de vol.",
        "4.2 Plainte",
        "En cas de vol, vous devez déposer plainte dans les 48 heures.",
    ],
]


def generer(sortie: Path) -> None:
    c = canvas.Canvas(str(sortie), pagesize=A4)
    largeur, hauteur = A4
    for num, lignes in enumerate(PAGES, start=2):
        c.setFont("Helvetica", 8)
        c.drawString(50, hauteur - 30, "Assur'Test Habitation - Conditions générales - Réf. AT-2026")
        c.drawString(50, 30, f"Page {num} / {len(PAGES) + 1}")
        y = hauteur - 70
        for ligne in lignes:
            titre = ligne.isupper() or ligne[:2].strip(".").isdigit() or ligne.startswith("Ce que")
            c.setFont("Helvetica-Bold" if titre else "Helvetica", 11 if titre else 10)
            c.drawString(50, y, ligne)
            y -= 16
        c.showPage()
    c.save()


if __name__ == "__main__":
    generer(Path(__file__).with_name("cg_style_reel.pdf"))
