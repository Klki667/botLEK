from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler
import os

# ----------------- CONFIG -----------------
TOKEN = "8767474566:AAHcV_S4rlOzD8lldOV-iUV9F4wIJsE_zT4"
ADMIN_ID = 2139896036
MAX_MSG_LENGTH = 4000

# Fichiers à charger
files_to_load = ["fiches_258x (1).txt", "fiches_259x (1).txt", "fiches_259x (2).txt", "fiches_260x (2).txt"]

# Séparateur pour le nouveau format
SEPARATOR = "════════════════════════════════════════════════════════════"

# ----------------- INIT -----------------
banned_users = set()
all_users = set()
fiches = []

# Charger toutes les fiches
for file in files_to_load:
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            contenu = f.read()
        fiches += [fiche.strip() for fiche in contenu.split(SEPARATOR) if fiche.strip()]
    else:
        print(f"⚠️ Fichier introuvable : {file}")

# Créer un dictionnaire pour recherche rapide par numéro
fiche_dict = {}
for fiche in fiches:
    for line in fiche.splitlines():
        if "📱 Téléphone :" in line:
            numero = line.split(":")[1].strip()
            fiche_dict[numero] = fiche

print(f"✅ {len(fiches)} fiches chargées.")

# ----------------- FONCTIONS -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    welcome_message = (
        f"👋 Bonjour {user.first_name} !\n\n"
        "Bienvenue sur le bot.\n\n"
        "📌 Instructions :\n"
        "- Envoyez un numéro de téléphone pour recevoir la fiche correspondante.\n"
        "- Tapez /myinfo pour voir vos informations.\n"
        "- Tapez /stats pour voir le nombre total d'utilisateurs (admin uniquement).\n"
        "- Tapez /ban <user_id> pour bannir un utilisateur (admin uniquement)."
    )
    await update.message.reply_text(welcome_message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    text = update.message.text.strip()

    if user_id in banned_users:
        await update.message.reply_text("🚫 Vous êtes banni et ne pouvez pas utiliser le bot.")
        return

    # Nouvel utilisateur → alerte admin
    if user_id not in all_users:
        all_users.add(user_id)
        alert_message = (
            f"🚨 Nouvel utilisateur !\n"
            f"ID : {user.id}\n"
            f"Prénom : {user.first_name}\n"
            f"Nom : {user.last_name}\n"
            f"Username : @{user.username}\n"
            f"Message envoyé : {text}"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=alert_message)

    # ⚡ Nouvelle fonctionnalité : transmettre tous les messages à l’admin
    admin_forward = (
        f"💬 Message reçu :\n"
        f"ID : {user.id}\n"
        f"Prénom : {user.first_name}\n"
        f"Nom : {user.last_name}\n"
        f"Username : @{user.username}\n"
        f"Message : {text}"
    )
    # Découpage si trop long
    for i in range(0, len(admin_forward), MAX_MSG_LENGTH):
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_forward[i:i+MAX_MSG_LENGTH])

    # Recherche dans les fiches par numéro
    if text in fiche_dict:
        fiche = fiche_dict[text]
        for i in range(0, len(fiche), MAX_MSG_LENGTH):
            await update.message.reply_text(fiche[i:i+MAX_MSG_LENGTH])
    else:
        await update.message.reply_text("⚠️ Fiche introuvable. Vérifiez le numéro.")

# Bannir un utilisateur
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Accès refusé")
        return
    try:
        to_ban = int(context.args[0])
        banned_users.add(to_ban)
        await update.message.reply_text(f"Utilisateur {to_ban} banni ✅")
    except:
        await update.message.reply_text("Usage : /ban <user_id>")

# Stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Accès refusé")
        return
    await update.message.reply_text(f"📊 Nombre total d'utilisateurs : {len(all_users)}")

# Infos utilisateur
async def myinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    await update.message.reply_text(
        f"👤 Vos informations :\n"
        f"ID : {user.id}\n"
        f"Prénom : {user.first_name}\n"
        f"Nom : {user.last_name}\n"
        f"Username : @{user.username}"
    )

# ----------------- CONFIG BOT -----------------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("myinfo", myinfo))
app.add_handler(MessageHandler(filters.TEXT, handle_message))

print("Bot démarré...")
app.run_polling()