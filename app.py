from flask import Flask, render_template, request, redirect, url_for
import datetime
from functools import reduce

from output import Output
from output_dao import OutputDAO

app = Flask(__name__)
dao = OutputDAO("database.db")
dao.create_table()

# ----------------------------
# Funktionale Bausteine
# ----------------------------

def berechne_summe(werte):
    return sum(werte)

def ausgabe_hinzu(ausgaben_tuple, neue_ausgabe):
    return ausgaben_tuple + (neue_ausgabe,)

def filter_positive_ausgaben(ausgaben):
    return list(filter(lambda x: x > 0, ausgaben))

def fuehre_berechnung_aus(ausgaben, funktion):
    return funktion(ausgaben)

def berechne_mit_regel(ausgaben, regel_funktion):
    gefiltert = list(filter(regel_funktion, ausgaben))
    return sum(gefiltert)

def nur_positive(betrag):
    return betrag > 0

def min_betrag_filter(min_betrag):
    def filter_funktion(betrag):
        return betrag >= min_betrag
    return filter_funktion

def berechne_summe_mit_filter(ausgaben, filter_funktion):
    return sum(filter(filter_funktion, ausgaben))

def reduce_ausgaben(ausgaben):
    return reduce(lambda a, b: a + b, ausgaben, 0)

def sortiere_outputs(outputs, asc=True):
    # Lambda steuert Programmfluss: Sortierung nach amount
    sortiert = sorted(outputs, key=lambda o: o.amount)
    return sortiert if asc else list(reversed(sortiert))

def berechne_gesamtbetrag_funktional(betraege, faktor):
    # filter + map + reduce kombiniert
    gueltige = filter(lambda x: x > 0, betraege)
    angepasst = map(lambda x: x * faktor, gueltige)
    return reduce(lambda a, b: a + b, angepasst, 0)

def berechne_summe_pro_kategorie(outputs):
    gefiltert = filter(lambda o: o.amount > 0, outputs)
    transformiert = map(lambda o: (o.category, o.amount), gefiltert)

    def reducer(ergebnis, eintrag):
        kategorie, betrag = eintrag
        ergebnis[kategorie] = ergebnis.get(kategorie, 0) + betrag
        return ergebnis

    return reduce(reducer, transformiert, {})

def berechne_gesamtbetrag_alt(ausgaben):
    gesamt = 0
    for wert in ausgaben:
        if wert > 0:
            gesamt += wert
    return gesamt

def berechne_gesamtbetrag_neu(ausgaben):
    return sum(filter(lambda x: x > 0, ausgaben))

# ----------------------------
# Helpers: Form parsing
# ----------------------------

def parse_output_from_form(form) -> Output | None:
    category = (form.get("category") or "").strip()
    description = (form.get("description") or "").strip()
    amount_s = (form.get("amount") or "").strip()
    date_s = (form.get("date") or "").strip()

    if category == "" or amount_s == "" or date_s == "":
        return None

    try:
        amount = float(amount_s)
        date_val = datetime.date.fromisoformat(date_s)
    except ValueError:
        return None

    return Output(
        id=None,
        amount=amount,
        category=category,
        date=date_val,
        description=description
    )

def outputs_to_amount_list(outputs):
    return list(map(lambda o: o.amount, outputs))

def amounts_to_immutable_tuple(amounts):
    tup = ()
    for a in amounts:
        tup = ausgabe_hinzu(tup, a)
    return tup

# ----------------------------
# Routes
# ----------------------------

@app.get("/")
def index():
    outputs = dao.get_all()
    return render_template("index.html", outputs=outputs)

@app.post("/add")
def add_output():
    output = parse_output_from_form(request.form)
    if output is not None:
        dao.add(output)
    return redirect(url_for("index"))

@app.post("/berechnen")
def berechnen():
    outputs = dao.get_all()

    faktor_s = (request.form.get("faktor") or "1.0").strip()
    min_betrag_s = (request.form.get("min_betrag") or "").strip()
    sortierung = request.form.get("sortierung", "asc")

    try:
        faktor = float(faktor_s)
    except ValueError:
        faktor = 1.0

    try:
        min_betrag = float(min_betrag_s) if min_betrag_s != "" else 0.0
    except ValueError:
        min_betrag = 0.0

    asc = (sortierung == "asc")
    outputs_sortiert = sortiere_outputs(outputs, asc=asc)

    betraege = outputs_to_amount_list(outputs)
    betraege_tuple = amounts_to_immutable_tuple(betraege)

    # B4E Aggregation
    summe_pro_kategorie = berechne_summe_pro_kategorie(outputs)

    # B2E Closure
    closure_filter = min_betrag_filter(min_betrag)
    summe_mit_min = berechne_summe_mit_filter(betraege, closure_filter)

    # B2F hoeherwertig
    summe_positive = berechne_mit_regel(betraege, nur_positive)

    # B2G Funktionen als Objekte
    berechnungs_funktion = berechne_summe
    summe_via_objekt = fuehre_berechnung_aus(filter_positive_ausgaben(betraege), berechnungs_funktion)

    # B3F reduce
    summe_reduce = reduce_ausgaben(filter_positive_ausgaben(betraege))

    # B4F kombiniert
    summe_funktional = berechne_gesamtbetrag_funktional(betraege, faktor)

    # C1E Refactoring Check
    alt = berechne_gesamtbetrag_alt(betraege)
    neu = berechne_gesamtbetrag_neu(betraege)
    refactoring_ok = (alt == neu)

    return render_template(
        "result.html",
        outputs_sortiert=outputs_sortiert,
        betraege_tuple=betraege_tuple,
        summe_pro_kategorie=summe_pro_kategorie,
        summe_positive=summe_positive,
        summe_via_objekt=summe_via_objekt,
        summe_reduce=summe_reduce,
        summe_mit_min=summe_mit_min,
        summe_funktional=summe_funktional,
        faktor=faktor,
        min_betrag=min_betrag,
        refactoring_ok=refactoring_ok
    )

if __name__ == "__main__":
    app.run(debug=True)
