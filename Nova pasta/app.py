from flask import Flask, redirect, render_template, request, url_for
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from database import Base, SessionLocal, engine
from models import Book, User

app = Flask(__name__)
Base.metadata.create_all(engine)


@app.get("/")
def index():
    with SessionLocal() as session:
        usuarios = session.scalars(
            select(User).options(selectinload(User.books)).order_by(User.nome)
        ).all()
        livros = session.scalars(
            select(Book).options(selectinload(Book.user)).order_by(Book.titulo)
        ).all()

    return render_template("index.html", usuarios=usuarios, livros=livros)


@app.route("/usuarios/novo", methods=["GET", "POST"])
def novo_usuario():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()

        if nome and email:
            usuario = User(nome=nome, email=email)
            try:
                with SessionLocal() as session:
                    session.add(usuario)
                    session.commit()
                return redirect(url_for("index"))
            except IntegrityError:
                return render_template("user_form.html", error="Este e-mail já está cadastrado.")

    return render_template("user_form.html")


@app.route("/livros/novo", methods=["GET", "POST"])
def novo_livro():
    with SessionLocal() as session:
        usuarios = session.scalars(select(User).order_by(User.nome)).all()

        if request.method == "POST":
            titulo = request.form.get("titulo", "").strip()
            usuario_id = request.form.get("usuario_id", type=int)

            if titulo and usuario_id is not None:
                livro = Book(titulo=titulo, user_id=usuario_id)
                session.add(livro)
                session.commit()
                return redirect(url_for("index"))

    return render_template("book_form.html", usuarios=usuarios)


if __name__ == "__main__":
    app.run(debug=True)
