from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Chave secreta da sessão
app.secret_key = "my_top_secret_123"

# Configuração do banco
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///diary.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
# ======================
# MODELOS
# ======================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    user_email = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Card {self.id}>"
# ======================
# LOGIN
# ======================
@app.route("/", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email,
            password=password
        ).first()

        if user:
            session["user_email"] = user.email
            return redirect("/index")

        error = "Usuário ou senha incorretos"

    return render_template("login.html", error=error)
# ======================
# REGISTRO
# ======================
@app.route("/reg", methods=["GET", "POST"])
def reg():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Verifica se já existe
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return render_template(
                "registration.html",
                error="E-mail já cadastrado."
            )
        user = User(
            email=email,
            password=password
        )
        db.session.add(user)
        db.session.commit()

        return redirect("/")

    return render_template("registration.html")
# ======================
# HOME
# ======================
@app.route("/index")
def index():
    email = session.get("user_email")

    if not email:
        return redirect("/")

    cards = Card.query.filter_by(user_email=email).all()

    return render_template(
        "index.html",
        cards=cards
    )
# ======================
# VER CARD
# ======================
@app.route("/card/<int:id>")
def card(id):
    card = Card.query.get_or_404(id)
    return render_template(
        "card.html",
        card=card
    )
# ======================
# CRIAR CARD
# ======================
@app.route("/create")
def create():
    if "user_email" not in session:
        return redirect("/")

    return render_template("create_card.html")

@app.route("/form_create", methods=["GET", "POST"])
def form_create():

    if "user_email" not in session:
        return redirect("/")

    if request.method == "POST":

        title = request.form["title"]
        subtitle = request.form["subtitle"]
        text = request.form["text"]

        card = Card(
            title=title,
            subtitle=subtitle,
            text=text,
            user_email=session["user_email"]
        )
        db.session.add(card)
        db.session.commit()

        return redirect("/index")

    return render_template("create_card.html")
# ======================
# LOGOUT
# ======================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
# ======================
# INICIAR APP
# ======================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
