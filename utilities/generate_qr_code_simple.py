"""
Génère un QR code simple pour DietTracker
"""
import qrcode

# URL de votre application
url = "https://diettracker-front.netlify.app"

# Créer le QR code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=15,
    border=2,
)

qr.add_data(url)
qr.make(fit=True)

# Créer l'image
img = qr.make_image(fill_color="darkgreen", back_color="white")

# Sauvegarder
output_path = "/mnt/d/vibeCode/GitRepo/sportProject/docs/diettracker_qr.png"
img.save(output_path)

print("=" * 50)
print("✅ QR CODE CRÉÉ AVEC SUCCÈS !")
print("=" * 50)
print(f"📍 Fichier : docs/diettracker_qr.png")
print(f"🔗 URL : {url}")
print("\n📱 COMMENT L'UTILISER :")
print("1. Ouvrez le fichier : docs/diettracker_qr.png")
print("2. Scannez avec l'appareil photo de votre téléphone")
print("3. Cliquez sur la notification pour ouvrir DietTracker")
print("4. Ajoutez à l'écran d'accueil (Partager → Sur l'écran d'accueil)")
print("=" * 50)