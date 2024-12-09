from flask import Flask, render_template, request, redirect, url_for, flash
import random
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Liste initiale des participants
participants = ["Noé", "Théo", "Antoine", "PE", "Maxime"]

# Fichier de stockage des listes dynamiques (utiliser /tmp pour Vercel)
RESULTS_FILE = "/tmp/results.txt"
PASSWORD = "admin123"  # Mot de passe pour réinitialiser

def initialize_lists():
    """Initialise les listes de participants dans results.txt."""
    with open(RESULTS_FILE, "w") as f:
        f.write(",".join(participants) + "\n")  # Liste pour "bêtise"
        f.write(",".join(participants) + "\n")  # Liste pour "sérieux"

def load_lists():
    """Charge les listes de participants disponibles à partir du fichier."""
    if not os.path.exists(RESULTS_FILE):
        initialize_lists()
    with open(RESULTS_FILE, "r") as f:
        lines = f.readlines()
    bêtise_list = lines[0].strip().split(",") if lines else []
    sérieux_list = lines[1].strip().split(",") if len(lines) > 1 else []
    return bêtise_list, sérieux_list

def load_results():
    """Charge les résultats des participants ayant déjà tiré."""
    if not os.path.exists(RESULTS_FILE):
        initialize_lists()
    with open(RESULTS_FILE, "r") as f:
        lines = f.readlines()
    results = {}
    for line in lines:
        if line.startswith("RESULT:"):
            parts = line.strip().split(":")[1].split(",")
            participant, bêtise, sérieux = parts
            results[participant] = {"bêtise": bêtise, "sérieux": sérieux}
    return results

def save_lists(bêtise_list, sérieux_list):
    """Sauvegarde les listes mises à jour dans results.txt."""
    with open(RESULTS_FILE, "r") as f:
        lines = f.readlines()
    results_lines = [line for line in lines if line.startswith("RESULT:")]
    with open(RESULTS_FILE, "w") as f:
        f.write(",".join(bêtise_list) + "\n")
        f.write(",".join(sérieux_list) + "\n")
        f.writelines(results_lines)

def save_result(participant, bêtise, sérieux):
    """Sauvegarde les résultats individuels dans results.txt."""
    with open(RESULTS_FILE, "a") as f:
        f.write(f"RESULT:{participant},{bêtise},{sérieux}\n")

@app.route("/")
def index():
    bêtise_list, sérieux_list = load_lists()
    results = load_results()
    return render_template(
        "index.html",
        participants=participants,
        results=results,
        bêtise_list=bêtise_list,
        sérieux_list=sérieux_list,
    )

@app.route("/results/<participant>")
def results(participant):
    bêtise_list, sérieux_list = load_lists()
    results = load_results()
    if participant in results:
        flash(f"{participant} a déjà effectué son tirage !", "error")
        return redirect(url_for("index"))

    bêtise_choices = [p for p in bêtise_list if p != participant]
    sérieux_choices = [p for p in sérieux_list if p != participant]
    if not bêtise_choices or not sérieux_choices:
        flash("Pas assez de participants disponibles pour effectuer le tirage.", "error")
        return redirect(url_for("index"))

    bêtise = random.choice(bêtise_choices)
    sérieux = random.choice(sérieux_choices)
    bêtise_list.remove(bêtise)
    sérieux_list.remove(sérieux)
    save_lists(bêtise_list, sérieux_list)
    save_result(participant, bêtise, sérieux)

    return render_template("results.html", participant=participant, bêtise=bêtise, sérieux=sérieux)

@app.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "POST":
        password = request.form.get("password")
        if password == PASSWORD:
            initialize_lists()
            flash("Les résultats ont été réinitialisés !", "success")
            return redirect(url_for("index"))
        else:
            flash("Mot de passe incorrect !", "error")
    return render_template("reset.html")

app = app
