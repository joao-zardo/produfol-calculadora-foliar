from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import db, Usuario, Produto, Produtor, Recomendacao
from app.services import calcular_dosagem, gerar_resumo_whatsapp

bp = Blueprint("main", __name__)


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "usuario_id" not in session:
            flash("Faça login para acessar o sistema.", "warning")
            return redirect(url_for("main.login"))
        usuario = db.session.get(Usuario, session["usuario_id"])
        if not usuario or not usuario.ativo:
            session.clear()
            return redirect(url_for("main.login"))
        return view(**kwargs)
    return wrapped_view


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        tentativas = session.get("tentativas_login", 0)
        if tentativas >= 5:
            flash("Muitas tentativas inválidas. Aguarde alguns minutos e tente novamente.", "danger")
            return render_template("login.html"), 429

        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.ativo and usuario.verificar_senha(senha):
            session.clear()
            session["usuario_id"] = usuario.id
            session["usuario_nome"] = usuario.nome
            return redirect(url_for("main.index"))

        session["tentativas_login"] = tentativas + 1
        flash("E-mail ou senha inválidos. Verifique seus dados e tente novamente.", "danger")

    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@bp.route("/")
@login_required
def index():
    return render_template("index.html")


@bp.route("/nova-recomendacao", methods=["GET", "POST"])
@login_required
def nova_recomendacao():
    produtores = Produtor.query.filter_by(ativo=True).order_by(Produtor.nome).all()
    produtos = Produto.query.filter_by(ativo=True).order_by(Produto.nome).all()

    if request.method == "POST":
        try:
            id_produtor = int(request.form.get("id_produtor", 0))
            id_produto = int(request.form.get("id_produto", 0))
            cultura = request.form.get("cultura", "").strip()
            area_hectares = float(request.form.get("area_hectares", 0))

            produtor = db.session.get(Produtor, id_produtor)
            produto = db.session.get(Produto, id_produto)
            if not produtor or not produto or not cultura:
                raise ValueError("Selecione produtor, fertilizante e cultura válidos.")

            resultado = calcular_dosagem(area_hectares, produto.dose_padrao_ha, produto.volume_embalagem)

            rec = Recomendacao(
                id_usuario=session["usuario_id"],
                id_produto=produto.id,
                id_produtor=produtor.id,
                cultura=cultura,
                area_hectares=area_hectares,
                volume_total=resultado["volume_total"],
                qtd_embalagens=resultado["qtd_embalagens"],
            )
            db.session.add(rec)
            db.session.commit()

            return redirect(url_for("main.resultado", rec_id=rec.id))
        except ValueError as err:
            flash(str(err), "danger")

    return render_template("calculadora.html", produtores=produtores, produtos=produtos)


@bp.route("/resultado/<int:rec_id>")
@login_required
def resultado(rec_id):
    rec = db.session.get(Recomendacao, rec_id)
    if not rec:
        return redirect(url_for("main.index"))

    resumo = gerar_resumo_whatsapp(
        produtor_nome=rec.produtor.nome,
        cultura=rec.cultura,
        area_hectares=rec.area_hectares,
        produto_nome=rec.produto.nome,
        dose_padrao_ha=rec.produto.dose_padrao_ha,
        volume_total=rec.volume_total,
        qtd_embalagens=rec.qtd_embalagens,
        volume_embalagem=rec.produto.volume_embalagem,
    )
    return render_template("resultado.html", rec=rec, resumo=resumo)


@bp.route("/produtos", methods=["GET", "POST"])
@login_required
def produtos():
    if request.method == "POST":
        try:
            nome = request.form.get("nome", "").strip()
            dose = float(request.form.get("dose_padrao_ha", 0))
            embalagem = float(request.form.get("volume_embalagem", 0))
            culturas = request.form.get("culturas_indicadas", "Soja, Milho").strip()
            if not nome or dose <= 0 or embalagem <= 0:
                raise ValueError("Preencha o nome do produto e valores maiores que zero.")
            db.session.add(Produto(nome=nome, dose_padrao_ha=dose, volume_embalagem=embalagem, culturas_indicadas=culturas))
            db.session.commit()
            flash("Fertilizante cadastrado com sucesso!", "success")
        except Exception as err:
            db.session.rollback()
            flash(f"Erro ao cadastrar fertilizante: {err}", "danger")
    lista = Produto.query.order_by(Produto.nome).all()
    return render_template("cadastros.html", modo="produtos", produtos=lista)


@bp.route("/produtores", methods=["GET", "POST"])
@login_required
def produtores():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        municipio = request.form.get("municipio", "").strip()
        telefone = request.form.get("telefone", "").strip()
        propriedade = request.form.get("propriedade", "").strip()
        if not nome or not municipio:
            flash("Nome e município do produtor são obrigatórios.", "danger")
        else:
            db.session.add(Produtor(nome=nome, municipio=municipio, telefone=telefone, propriedade=propriedade))
            db.session.commit()
            flash("Produtor rural cadastrado com sucesso!", "success")
    lista = Produtor.query.order_by(Produtor.nome).all()
    return render_template("cadastros.html", modo="produtores", produtores=lista)


@bp.route("/historico")
@login_required
def historico():
    busca = request.args.get("q", "").strip()
    query = Recomendacao.query.join(Produtor).order_by(Recomendacao.data_criacao.desc())
    if busca:
        query = query.filter(Produtor.nome.ilike(f"%{busca}%"))
    lista = query.all()
    return render_template("cadastros.html", modo="historico", recomendacoes=lista, busca=busca)
