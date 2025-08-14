"""
Génère un QR code pour accéder facilement à DietTracker
"""
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

def generate_diettracker_qr():
    # URL de l'application
    url = "https://diettracker.netlify.app"
    
    # Créer le QR code avec des paramètres personnalisés
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    
    qr.add_data(url)
    qr.make(fit=True)
    
    # Créer l'image avec des couleurs personnalisées
    img_qr = qr.make_image(fill_color="darkgreen", back_color="white")
    
    # Créer une image plus grande avec titre
    width, height = img_qr.size
    new_height = height + 100
    
    # Nouvelle image avec fond blanc
    img_final = Image.new('RGB', (width, new_height), 'white')
    
    # Coller le QR code
    img_final.paste(img_qr, (0, 50))
    
    # Ajouter du texte
    draw = ImageDraw.Draw(img_final)
    
    # Texte centré en haut
    text_top = "🥗 DietTracker"
    text_bottom = "Scannez pour accéder"
    
    # Police par défaut (vous pouvez personnaliser si nécessaire)
    try:
        # Essayer une police système
        from PIL import ImageFont
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        # Utiliser la police par défaut si pas trouvée
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Calculer la position du texte
    bbox = draw.textbbox((0, 0), text_top, font=font_large)
    text_width = bbox[2] - bbox[0]
    text_x = (width - text_width) // 2
    
    # Dessiner le texte
    draw.text((text_x, 10), text_top, fill='darkgreen', font=font_large)
    
    # Texte du bas
    bbox_bottom = draw.textbbox((0, 0), text_bottom, font=font_small)
    text_width_bottom = bbox_bottom[2] - bbox_bottom[0]
    text_x_bottom = (width - text_width_bottom) // 2
    draw.text((text_x_bottom, height + 60), text_bottom, fill='gray', font=font_small)
    
    # Sauvegarder l'image
    output_path = "/mnt/d/vibeCode/GitRepo/sportProject/docs/diettracker_qr_code.png"
    img_final.save(output_path)
    
    # Aussi sauvegarder une version simple sans texte
    simple_path = "/mnt/d/vibeCode/GitRepo/sportProject/docs/diettracker_qr_simple.png"
    img_qr.save(simple_path)
    
    print(f"✅ QR Code généré avec succès !")
    print(f"📍 Fichier principal : {output_path}")
    print(f"📍 Version simple : {simple_path}")
    print(f"🔗 URL encodée : {url}")
    print("\n📱 Instructions :")
    print("1. Ouvrez l'appareil photo de votre téléphone")
    print("2. Pointez vers le QR code")
    print("3. Cliquez sur la notification pour ouvrir DietTracker")
    print("4. Ajoutez à l'écran d'accueil pour un accès rapide")
    
    return output_path, simple_path

if __name__ == "__main__":
    # Installer qrcode et pillow si nécessaire
    try:
        import qrcode
        from PIL import Image
    except ImportError:
        print("Installation des dépendances...")
        import subprocess
        subprocess.run(["pip", "install", "qrcode[pil]"])
        import qrcode
        from PIL import Image
    
    generate_diettracker_qr()