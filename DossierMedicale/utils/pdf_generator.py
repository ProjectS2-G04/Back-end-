import os
from io import BytesIO

from django.core.files.base import ContentFile
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle


def generate_fields_list(serializer_data, dossier_type):
    """
    Generate the fields list for the PDF based on the dossier type.

    Args:
        serializer_data: The serialized data from the serializer.
        dossier_type: String indicating the type ('etudiant', 'enseignant', 'fonctionnaires').

    Returns:
        List of (label, value) tuples for the PDF.
    """
    # Core personal fields with "Numéro de dossier" as the first element
    personal_fields = [
        ("Numéro de dossier", serializer_data.get("numero_dossier", "N/A")),
        ("Nom", serializer_data.get("nom", "N/A")),
        ("Prénom", serializer_data.get("prenom", "N/A")),
        ("Date de naissance", serializer_data.get("date_naissance", "N/A")),
        ("Lieu de naissance", serializer_data.get("lieu_naissance", "N/A")),
        ("Adresse", serializer_data.get("adresse", "N/A")),
        ("Numéro de téléphone", serializer_data.get("numero_telephone", "N/A")),
        ("Email", serializer_data.get("email", "N/A")),
        ("Situation familiale", serializer_data.get("situation_familiale", "N/A")),
        ("Admis(e)", serializer_data.get("admission_etablissement", "N/A")),
    ]

    # Type-specific fields based on dossier type
    type_specific_fields = []
    if dossier_type == "etudiant":
        type_specific_fields = [
            ("Filière", serializer_data.get("Filiere", "Informatique")),
            ("Niveau", serializer_data.get("Niveau", "N/A")),
        ]
    elif dossier_type == "enseignant":
        type_specific_fields = [
            ("Grade", serializer_data.get("grade", "N/A")),
            ("Spécialité", serializer_data.get("specialite", "N/A")),
        ]
    elif dossier_type == "fonctionnaires":
        type_specific_fields = [
            ("Grade", serializer_data.get("grade", "N/A")),
            ("Service", serializer_data.get("service", "N/A")),
        ]

    # Remaining fields for biometric, tobacco, and medical history
    remaining_fields = [
        (
            "Numéro sécurité sociale",
            serializer_data.get("numero_securite_sociale", "N/A"),
        ),
        ("Groupe sanguin", serializer_data.get("groupe_sanguin", "N/A")),
        ("Sexe", serializer_data.get("sexe", "N/A")),
        ("Taille (cm)", str(serializer_data.get("taille", "N/A"))),
        ("Poids (kg)", str(serializer_data.get("poids", "N/A"))),
        (
            "Fréquence cardiaque (bpm)",
            str(serializer_data.get("frequence_cardiaque", "N/A")),
        ),
        ("Pression artérielle", serializer_data.get("pression_arterielle", "N/A")),
        ("IMC", str(serializer_data.get("imc", "N/A"))),
        ("Interprétation IMC", serializer_data.get("categorie_imc", "N/A")),
        ("Fumeur", "Oui" if serializer_data.get("fumeur", False) else "Non"),
        (
            "Cigarettes/jour",
            (
                str(serializer_data.get("nombre_cigarettes", "N/A"))
                if serializer_data.get("fumeur", False)
                else "N/A"
            ),
        ),
        ("Chiqueur", "Oui" if serializer_data.get("chiqueur", False) else "Non"),
        (
            "Boîtes chique/jour",
            (
                str(serializer_data.get("nombre_boites_chique", "N/A"))
                if serializer_data.get("chiqueur", False)
                else "N/A"
            ),
        ),
        ("Prise autre", "Oui" if serializer_data.get("prise_autre", False) else "Non"),
        (
            "Boîtes autre/jour",
            (
                str(serializer_data.get("nombre_boites_autre", "N/A"))
                if serializer_data.get("prise_autre", False)
                else "N/A"
            ),
        ),
        (
            "Ancien fumeur",
            "Oui" if serializer_data.get("ancien_fumeur", False) else "Non",
        ),
        (
            "Boîtes fumeur/jour",
            (
                str(serializer_data.get("nombre_boites_fumeur", "N/A"))
                if serializer_data.get("ancien_fumeur", False)
                else "N/A"
            ),
        ),
        ("Âge première prise", str(serializer_data.get("age_premiere_prise", "N/A"))),
        (
            "Affections congénitales",
            serializer_data.get("affections_congenitales", "N/A"),
        ),
        ("Maladies générales", serializer_data.get("maladies_generales", "N/A")),
        (
            "Interventions chirurgicales",
            serializer_data.get("interventions_chirurgicales", "N/A"),
        ),
        ("Réactions allergiques", serializer_data.get("reactions_allergiques", "N/A")),
    ]

    return personal_fields + type_specific_fields + remaining_fields


def generate_medical_pdf(dossier, serializer_data, dossier_type, document_model):
    """
    Generate a professional medical PDF for a dossier.

    Args:
        dossier: The DossierMedical instance (e.g., DossierMedicalEtudiant).
        serializer_data: The serialized data from the serializer.
        dossier_type: String indicating the type ('etudiant', 'enseignant', 'fonctionnaires').
        document_model: The Document model to save the PDF.

    Returns:
        Document instance with the generated PDF.
    """
    fields = generate_fields_list(serializer_data, dossier_type)

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 50
    y = height - margin
    page_number = 1

    def draw_header():
        nonlocal y
        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawCentredString(width / 2, height - 40, "DOSSIER MÉDICAL")
        pdf.setFont("Helvetica", 12)
        pdf.drawCentredString(
            width / 2, height - 70, "École Nationale Supérieure d'Informatique"
        )
        pdf.setLineWidth(1)
        pdf.line(margin, height - 80, width - margin, height - 80)
        y -= 60

        # Only show profile picture on the first page
        if (
            page_number == 1
            and dossier.photo
            and dossier.photo != "profile_pics/image.jpg"
            and os.path.exists(dossier.photo.path)
        ):
            try:
                img = ImageReader(dossier.photo.path)
                img_width = 50  # Set desired width
                img_height = 50  # Set desired height
                img_x = width - margin - img_width - 10  # Right-aligned with margin
                img_y = height - 100  # Position below header
                pdf.drawImage(
                    img, img_x, img_y, width=img_width, height=img_height, mask="auto"
                )
            except Exception as e:
                print(f"Error loading image: {e}")

    def draw_footer():
        pdf.setFont("Helvetica", 10)
        pdf.drawString(margin, 30, f"Page {page_number}")
        pdf.drawRightString(
            width - margin, 30, "École Nationale Supérieure d'Informatique"
        )
        pdf.setLineWidth(0.5)
        pdf.line(margin, 40, width - margin, 40)

    def create_table(section_fields):
        # Modify the label formatting to exclude colons
        data = [
            [Paragraph(label, styles["Field_Bold"]), Paragraph(value, styles["Field"])]
            for label, value in section_fields
        ]
        table = Table(data, colWidths=[180, 300])
        table.setStyle(
            TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), "Helvetica", 10),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                    ("ALIGN", (1, 0), (1, -1), "LEFT"),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),  # Header row
                    ("BACKGROUND", (0, 1), (-1, -1), colors.lightblue),  # Data rows
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        return table

    def check_page_space(required_space):
        nonlocal y, page_number
        # Reserve space for footer (50 units) plus extra padding
        if y < margin + required_space + 50:
            draw_footer()
            pdf.showPage()
            page_number += 1
            y = height - margin
            draw_header()

    # Set styles for table and paragraphs
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(name="Field", fontSize=10, leading=12, textColor=colors.black)
    )
    styles.add(
        ParagraphStyle(
            name="Field_Bold",
            fontSize=10,
            leading=12,
            textColor=colors.black,
            alignment=1,
        )
    )

    draw_header()
    sections = [
        ("Informations Personnelles", fields[:12]),  # 10 personal + 2 type-specific
        ("Données Biométriques", fields[12:18]),  # 6 fields
        ("Consommation de Tabac", fields[18:27]),  # 9 fields
        ("Antécédents Médicaux", fields[27:]),  # 4 fields
    ]

    for section_title, section_fields in sections:
        check_page_space(100)
        pdf.setFont("Helvetica-Bold", 14)
        pdf.setFillColor(colors.black)
        pdf.drawString(margin, y, section_title)
        y -= 20

        table = create_table(section_fields)
        table_width, table_height = table.wrap(width - 2 * margin, height)

        # Ensure section header and table fit on the same page
        if y < table_height + 40 + 50:  # 40 for header/spacing, 50 for footer
            check_page_space(table_height + 40)

        table.drawOn(pdf, margin, y - table_height)
        y -= table_height + 40  # Increased spacing to avoid touching footer

    draw_footer()
    pdf.save()
    pdf_data = buffer.getvalue()
    buffer.close()

    # Save or update the document in the database
    if dossier.dossier_documents.exists():
        document = dossier.dossier_documents.first()
        document.file.save(document.title, ContentFile(pdf_data))
    else:
        document = document_model(
            title=f"Dossier_{dossier.nom}_{dossier.prenom}_{dossier.numero_dossier}.pdf",
            dossier_medical=dossier,
        )
        document.file.save(document.title, ContentFile(pdf_data))
        document.save()
        dossier.dossier_documents.add(document)

    return document
