# DossierMedicale/utils/pdf_generator.py
from io import BytesIO
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os

def generate_fields_list(serializer_data, dossier_type):
    """
    Generate the fields list for the PDF based on the dossier type.

    Args:
        serializer_data: The serialized data from the serializer.
        dossier_type: String indicating the type ('etudiant', 'enseignant', 'ats').

    Returns:
        List of (label, value) tuples for the PDF.
    """
    common_fields = [
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
    elif dossier_type == "ats":
        type_specific_fields = [
            ("Grade", serializer_data.get("grade", "N/A")),
            ("Service", serializer_data.get("service", "N/A")),
        ]
    else:
        type_specific_fields = []

    remaining_fields = [
        ("Numéro de dossier", serializer_data.get("numero_dossier", "N/A")),
        ("Numéro sécurité sociale", serializer_data.get("numero_securite_sociale", "N/A")),
        ("Groupe sanguin", serializer_data.get("groupe_sanguin", "N/A")),
        ("Sexe", serializer_data.get("sexe", "N/A")),
        ("Taille (cm)", str(serializer_data.get("taille", "N/A"))),
        ("Poids (kg)", str(serializer_data.get("poids", "N/A"))),
        ("Fréquence cardiaque (bpm)", str(serializer_data.get("frequence_cardiaque", "N/A"))),
        ("Pression artérielle", serializer_data.get("pression_arterielle", "N/A")),
        ("IMC", str(serializer_data.get("imc", "N/A"))),
        ("Interprétation IMC", serializer_data.get("categorie_imc", "N/A")),
        ("Fumeur", "Oui" if serializer_data.get("fumeur", False) else "Non"),
        (
            "Cigarettes/jour",
            str(serializer_data.get("nombre_cigarettes", "N/A"))
            if serializer_data.get("fumeur", False)
            else "N/A"
        ),
        ("Chiqueur", "Oui" if serializer_data.get("chiqueur", False) else "Non"),
        (
            "Boîtes chique/jour",
            str(serializer_data.get("nombre_boites_chique", "N/A"))
            if serializer_data.get("chiqueur", False)
            else "N/A"
        ),
        ("Prise autre", "Oui" if serializer_data.get("prise_autre", False) else "Non"),
        (
            "Boîtes autre/jour",
            str(serializer_data.get("nombre_boites_autre", "N/A"))
            if serializer_data.get("prise_autre", False)
            else "N/A"
        ),
        ("Ancien fumeur", "Oui" if serializer_data.get("ancien_fumeur", False) else "Non"),
        (
            "Boîtes fumeur/jour",
            str(serializer_data.get("nombre_boites_fumeur", "N/A"))
            if serializer_data.get("ancien_fumeur", False)
            else "N/A"
        ),
        ("Âge première prise", str(serializer_data.get("age_premiere_prise", "N/A"))),
        ("Affections congénitales", serializer_data.get("affections_congenitales", "N/A")),
        ("Maladies générales", serializer_data.get("maladies_generales", "N/A")),
        ("Interventions chirurgicales", serializer_data.get("interventions_chirurgicales", "N/A")),
        ("Réactions allergiques", serializer_data.get("reactions_allergiques", "N/A")),
    ]

    return common_fields + type_specific_fields + remaining_fields

def generate_medical_pdf(dossier, serializer_data, dossier_type, document_model):
    """
    Generate a medical PDF for a dossier with the given fields.

    Args:
        dossier: The DossierMedical instance (e.g., DossierMedicalEtudiant).
        serializer_data: The serialized data from the serializer.
        dossier_type: String indicating the type ('etudiant', 'enseignant', 'ats').
        document_model: The Document model to save the PDF.

    Returns:
        Document instance with the generated PDF.
    """
    fields = generate_fields_list(serializer_data, dossier_type)

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50
    line_height = 25
    page_number = 1
    max_width = 350

    def draw_header():
        nonlocal y
        pdf.setFillColorRGB(0.29, 0.63, 0.66)
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawCentredString(width / 2, height - 30, "FICHE MÉDICALE")
        pdf.setFont("Helvetica", 12)
        pdf.drawCentredString(width / 2, height - 50, f"{dossier.nom} {dossier.prenom}")
        pdf.drawCentredString(width / 2, height - 70, "République Algérienne Démocratique et Populaire")
        pdf.drawCentredString(width / 2, height - 90, "École Nationale Supérieure d'Informatique")

        # Add profile picture if it exists and the file is accessible
        if dossier.photo and dossier.photo != "profile_pics/image.jpg" and os.path.exists(dossier.photo.path):
            try:
                img = ImageReader(dossier.photo.path)
                img_width, img_height = 80, 80
                img_x = width - img_width - 50
                img_y = height - img_height - 30
                pdf.drawImage(img, img_x, img_y, width=img_width, height=img_height)
            except Exception as e:
                print(f"Error loading image: {e}")

        pdf.setStrokeColorRGB(0.47, 0.84, 0.75)
        pdf.setLineWidth(2)
        pdf.line(50, height - 100, width - 50, height - 100)
        y = height - 120

    def check_page_space(required_space):
        nonlocal y, page_number
        if y < required_space:
            pdf.setFont("Helvetica", 10)
            pdf.drawRightString(width - 50, 30, f"Page {page_number}")
            pdf.showPage()
            page_number += 1
            y = height - 50
            draw_header()

    def wrap_text(text, max_width, font_name, font_size):
        pdf.setFont(font_name, font_size)
        lines = []
        words = str(text).split()
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if pdf.stringWidth(test_line, font_name, font_size) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    draw_header()
    pdf.setFillColorRGB(0, 0, 0)
    pdf.setFont("Helvetica-Bold", 12)

    sections = [
        ("Informations Personnelles", fields[:15]),
        ("Données Biométriques", fields[15:21]),
        ("Consommation de Tabac", fields[21:30]),
        ("Antécédents Médicaux", fields[30:])
    ]

    for section_title, section_fields in sections:
        check_page_space(50)
        pdf.setFillColorRGB(0.18, 0.31, 0.47)
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y, section_title)
        pdf.setFillColorRGB(0, 0, 0)
        y -= 10
        pdf.line(50, y, width - 50, y)
        y -= line_height
        pdf.setFont("Helvetica-Bold", 12)
        for label, value in section_fields:
            check_page_space(line_height * 2)
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(50, y, f"{label}:")
            pdf.setFont("Helvetica", 12)
            value_lines = wrap_text(value, max_width, "Helvetica", 12)
            for i, line in enumerate(value_lines):
                if i > 0:
                    y -= line_height
                    check_page_space(line_height)
                pdf.drawString(200, y, line)
            y -= line_height
        y -= 20

    pdf.setFont("Helvetica", 10)
    pdf.drawRightString(width - 50, 30, f"Page {page_number}")
    pdf.save()
    pdf_data = buffer.getvalue()
    buffer.close()

    if dossier.dossier_documents.exists():
        document = dossier.dossier_documents.first()
        document.file.save(document.title, ContentFile(pdf_data))
    else:
        document = document_model(
            title=f"Dossier_{dossier.nom}_{dossier.prenom}_{dossier.numero_dossier}.pdf",
            dossier_medical=dossier
        )
        document.file.save(document.title, ContentFile(pdf_data))
        document.save()
        dossier.dossier_documents.add(document)

    return document