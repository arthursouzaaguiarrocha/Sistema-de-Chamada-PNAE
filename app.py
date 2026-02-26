from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
import mysql.connector
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
import io
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = "pnae_secret_key"

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="sistema_pnae"
    )

# ---------- DECORATORS ----------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "usuario" not in session:
            flash("Faça login para continuar.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "usuario" not in session:
            flash("Faça login para continuar.")
            return redirect(url_for("login"))
        if not session.get("is_admin"):
            flash("Acesso restrito ao coordenador.")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated

# ---------- HELPER: GERAR PDF EM MEMÓRIA ----------
def build_pdf(alunos_dados, verificados_ids, nome_responsavel, turma=""):
    """
    alunos_dados: lista de dicts {id, nome, serie}
    verificados_ids: set/list de str com ids marcados
    Retorna bytes do PDF
    """
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    hora_hoje = datetime.now().strftime("%H:%M")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle('Titulo', parent=styles['Title'],
        fontSize=16, textColor=colors.HexColor('#1a5c35'),
        alignment=TA_CENTER, spaceAfter=4)
    sub_style = ParagraphStyle('Sub', parent=styles['Normal'],
        fontSize=10, alignment=TA_CENTER, textColor=colors.grey, spaceAfter=16)

    story = []
    story.append(Paragraph("CONTROLE DE LANCHE - PNAE", titulo_style))
    sub_txt = f"Data: {data_hoje} &nbsp;|&nbsp; Horário: {hora_hoje} &nbsp;|&nbsp; Bolsista: {nome_responsavel}"
    if turma:
        sub_txt += f" &nbsp;|&nbsp; Turma: {turma}"
    story.append(Paragraph(sub_txt, sub_style))
    story.append(Spacer(1, 0.3*cm))

    dados_tab = [["#", "Nome do Aluno", "Série", "Recebeu Lanche?"]]
    for i, al in enumerate(alunos_dados, start=1):
        recebeu = "SIM" if str(al["id"]) in verificados_ids else "NAO"
        dados_tab.append([str(i), al["nome"], al["serie"], recebeu])

    tabela = Table(dados_tab, colWidths=[1*cm, 8*cm, 4*cm, 4.5*cm])
    tabela.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,0), colors.HexColor('#1a5c35')),
        ('TEXTCOLOR',     (0,0),(-1,0), colors.white),
        ('FONTNAME',      (0,0),(-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0),(-1,0), 11),
        ('ALIGN',         (0,0),(-1,0), 'CENTER'),
        ('BOTTOMPADDING', (0,0),(-1,0), 10),
        ('TOPPADDING',    (0,0),(-1,0), 10),
        ('FONTNAME',      (0,1),(-1,-1), 'Helvetica'),
        ('FONTSIZE',      (0,1),(-1,-1), 10),
        ('ALIGN',         (0,1),(0,-1),  'CENTER'),
        ('ALIGN',         (3,1),(3,-1),  'CENTER'),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [colors.white, colors.HexColor('#f0f7f3')]),
        ('BOTTOMPADDING', (0,1),(-1,-1), 8),
        ('TOPPADDING',    (0,1),(-1,-1), 8),
        ('GRID',          (0,0),(-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('BOX',           (0,0),(-1,-1), 1,   colors.HexColor('#1a5c35')),
        ('TEXTCOLOR',     (3,1),(3,-1),  colors.HexColor('#1a5c35')),
    ]))
    story.append(tabela)
    story.append(Spacer(1, 1*cm))

    total         = len(alunos_dados)
    receberam     = sum(1 for al in alunos_dados if str(al["id"]) in verificados_ids)
    nao_receberam = total - receberam

    resumo_style = ParagraphStyle('Resumo', parent=styles['Normal'], fontSize=10, textColor=colors.grey)
    story.append(Paragraph(
        f"<b>Total:</b> {total} &nbsp;|&nbsp; <b>Receberam:</b> {receberam} &nbsp;|&nbsp; <b>Não receberam:</b> {nao_receberam}",
        resumo_style))

    doc.build(story)
    return buffer.getvalue()



# AUTENTICAÇÃO


@app.route("/")
def login():
    return render_template("Login.html")

@app.route("/login", methods=['POST'])
def fazer_login():
    email = request.form["email"]
    senha = request.form["senha"]
    conn = conectar()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM usuarios WHERE email=%s AND senha=%s", (email, senha))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user:
        session["usuario"] = email
        session["nome"]     = user["nome"]
        session["is_admin"] = bool(user["is_admin"])
        return redirect(url_for("index"))
    flash("E-mail ou senha inválidos!")
    return redirect(url_for("login"))

@app.route("/cadastro", methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome  = request.form["nome"].strip()
        email = request.form["email"].strip()
        senha = request.form["senha"]
        conf  = request.form["confirmar_senha"]
        if senha != conf:
            flash("As senhas não coincidem!")
            return redirect(url_for("cadastro"))
        conn = conectar()
        cur  = conn.cursor()
        try:
            cur.execute("INSERT INTO usuarios (nome, email, senha, is_admin) VALUES (%s,%s,%s,0)",
                        (nome, email, senha))
            conn.commit()
            flash("Conta criada! Faça login.")
        except mysql.connector.IntegrityError:
            flash("E-mail já cadastrado!")
        finally:
            cur.close()
            conn.close()
        return redirect(url_for("login"))
    return render_template("cadastro.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ÁREA DO BOLSISTA

@app.route("/index")
@login_required
def index():
    conn = conectar()
    cur  = conn.cursor(dictionary=True)
    cur.execute("SELECT id, nome, serie FROM alunos ORDER BY serie, nome")
    alunos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", alunos=alunos,
                           nome_usuario=session.get("nome",""),
                           is_admin=session.get("is_admin", False))

@app.route("/aluno/add", methods=['POST'])
@login_required
def add_aluno():
    nome  = request.form["nome"]
    serie = request.form["serie"]
    conn = conectar(); cur = conn.cursor()
    cur.execute("INSERT INTO alunos (nome, serie) VALUES (%s,%s)", (nome, serie))
    conn.commit(); cur.close(); conn.close()
    flash("Aluno cadastrado!")
    return redirect(url_for("index"))

@app.route("/aluno/editar/<int:id>", methods=['GET', 'POST'])
@login_required
def editar_aluno(id):
    conn = conectar(); cur = conn.cursor(dictionary=True)
    if request.method == 'POST':
        cur.execute("UPDATE alunos SET nome=%s, serie=%s WHERE id=%s",
                    (request.form["nome"], request.form["serie"], id))
        conn.commit(); cur.close(); conn.close()
        flash("Aluno atualizado!")
        return redirect(url_for("index"))
    cur.execute("SELECT * FROM alunos WHERE id=%s", (id,))
    aluno = cur.fetchone(); cur.close(); conn.close()
    return render_template("editar.html", aluno=aluno)

@app.route("/aluno/delete/<int:id>")
@login_required
def delete_aluno(id):
    conn = conectar(); cur = conn.cursor()
    cur.execute("DELETE FROM alunos WHERE id=%s", (id,))
    conn.commit(); cur.close(); conn.close()
    flash("Aluno removido!")
    return redirect(url_for("index"))

# Baixar PDF (bolsista só baixa, não envia)
@app.route("/gerar-pdf", methods=['POST'])
@login_required
def gerar_pdf():
    alunos_dados = []
    ids      = request.form.getlist("aluno_id")
    nomes    = request.form.getlist("aluno_nome")
    series   = request.form.getlist("aluno_serie")
    verif    = request.form.getlist("verificado")

    for aid, nome, serie in zip(ids, nomes, series):
        alunos_dados.append({"id": aid, "nome": nome, "serie": serie})

    pdf_bytes = build_pdf(alunos_dados, verif, session.get("nome",""))
    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        f'attachment; filename=chamada_{datetime.now().strftime("%d-%m-%Y")}.pdf'
    return response

# Enviar chamada para o coordenador (salva no banco)
@app.route("/enviar-chamada", methods=['POST'])
@login_required
def enviar_chamada():
    ids    = request.form.getlist("aluno_id")
    nomes  = request.form.getlist("aluno_nome")
    series = request.form.getlist("aluno_serie")
    verif  = request.form.getlist("verificado")

    if not ids:
        flash("Nenhum aluno na lista para enviar.")
        return redirect(url_for("index"))

    alunos_dados = [{"id": a, "nome": n, "serie": s}
                    for a, n, s in zip(ids, nomes, series)]

    total     = len(alunos_dados)
    receberam = len(verif)

    # Gera PDF e salva como BLOB
    pdf_bytes = build_pdf(alunos_dados, verif, session.get("nome",""))

    conn = conectar(); cur = conn.cursor()
    cur.execute("""
        INSERT INTO chamadas (bolsista_email, bolsista_nome, data_chamada, total_alunos, receberam, pdf_arquivo)
        VALUES (%s, %s, NOW(), %s, %s, %s)
    """, (session["usuario"], session.get("nome",""), total, receberam, pdf_bytes))
    conn.commit(); cur.close(); conn.close()

    flash("✅ Chamada enviada com sucesso para o coordenador!")
    return redirect(url_for("index"))

# ÁREA DO COORDENADOR (ADMIN)

@app.route("/admin")
@admin_required
def admin_dashboard():
    conn = conectar()
    cur  = conn.cursor(dictionary=True)

    cur.execute("SELECT COUNT(*) AS t FROM alunos")
    total_alunos = cur.fetchone()["t"]

    cur.execute("SELECT COUNT(*) AS t FROM usuarios WHERE is_admin=0")
    total_bolsistas = cur.fetchone()["t"]

    # Chamadas de hoje
    cur.execute("SELECT COUNT(*) AS t FROM chamadas WHERE DATE(data_chamada)=CURDATE()")
    chamadas_hoje = cur.fetchone()["t"]

    # Total de chamadas
    cur.execute("SELECT COUNT(*) AS t FROM chamadas")
    total_chamadas = cur.fetchone()["t"]

    # Alunos por série
    cur.execute("SELECT serie, COUNT(*) AS qtd FROM alunos GROUP BY serie ORDER BY serie")
    alunos_por_serie = cur.fetchall()

    # Chamadas recentes (últimas 50)
    cur.execute("""
        SELECT id, bolsista_nome, bolsista_email,
               DATE_FORMAT(data_chamada,'%d/%m/%Y') AS data_fmt,
               TIME_FORMAT(data_chamada,'%H:%i') AS hora_fmt,
               total_alunos, receberam
        FROM chamadas
        ORDER BY data_chamada DESC
        LIMIT 50
    """)
    chamadas = cur.fetchall()

    # Bolsistas que enviaram hoje
    cur.execute("""
        SELECT DISTINCT bolsista_nome, bolsista_email
        FROM chamadas WHERE DATE(data_chamada)=CURDATE()
    """)
    enviaram_hoje = cur.fetchall()

    # Todos bolsistas
    cur.execute("SELECT nome, email FROM usuarios WHERE is_admin=0 ORDER BY nome")
    todos_bolsistas = cur.fetchall()

    # Usuários
    cur.execute("SELECT email, nome, is_admin FROM usuarios ORDER BY nome")
    usuarios = cur.fetchall()

    cur.close(); conn.close()

    # Bolsistas que NÃO enviaram hoje
    emails_enviaram = {u["bolsista_email"] for u in enviaram_hoje}
    nao_enviaram    = [b for b in todos_bolsistas if b["email"] not in emails_enviaram]

    return render_template("admin_dashboard.html",
        total_alunos=total_alunos,
        total_bolsistas=total_bolsistas,
        chamadas_hoje=chamadas_hoje,
        total_chamadas=total_chamadas,
        alunos_por_serie=alunos_por_serie,
        chamadas=chamadas,
        enviaram_hoje=enviaram_hoje,
        nao_enviaram=nao_enviaram,
        usuarios=usuarios,
        nome_usuario=session.get("nome","")
    )

# Baixar PDF de uma chamada
@app.route("/admin/download-pdf/<int:chamada_id>")
@admin_required
def download_pdf_chamada(chamada_id):
    conn = conectar(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT pdf_arquivo, bolsista_nome, data_chamada FROM chamadas WHERE id=%s", (chamada_id,))
    row = cur.fetchone(); cur.close(); conn.close()
    if not row:
        flash("Chamada não encontrada.")
        return redirect(url_for("admin_dashboard"))
    data_str = row["data_chamada"].strftime("%d-%m-%Y")
    response = make_response(bytes(row["pdf_arquivo"]))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
        f'attachment; filename=chamada_{row["bolsista_nome"].replace(" ","_")}_{data_str}.pdf'
    return response

# Excluir chamada
@app.route("/admin/excluir-chamada/<int:chamada_id>")
@admin_required
def excluir_chamada(chamada_id):
    conn = conectar(); cur = conn.cursor()
    cur.execute("DELETE FROM chamadas WHERE id=%s", (chamada_id,))
    conn.commit(); cur.close(); conn.close()
    flash("Chamada removida.")
    return redirect(url_for("admin_dashboard"))

# Promover/rebaixar usuário
@app.route("/admin/toggle/<email>")
@admin_required
def toggle_admin(email):
    if email == session["usuario"]:
        flash("Você não pode alterar sua própria permissão.")
        return redirect(url_for("admin_dashboard"))
    conn = conectar(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT is_admin FROM usuarios WHERE email=%s", (email,))
    user = cur.fetchone()
    if user:
        novo = 0 if user["is_admin"] else 1
        cur.execute("UPDATE usuarios SET is_admin=%s WHERE email=%s", (novo, email))
        conn.commit()
        flash("Permissão atualizada!")
    cur.close(); conn.close()
    return redirect(url_for("admin_dashboard"))

# Excluir usuário
@app.route("/admin/excluir-usuario/<email>")
@admin_required
def excluir_usuario(email):
    if email == session["usuario"]:
        flash("Você não pode excluir sua própria conta.")
        return redirect(url_for("admin_dashboard"))
    conn = conectar(); cur = conn.cursor()
    cur.execute("DELETE FROM usuarios WHERE email=%s", (email,))
    conn.commit(); cur.close(); conn.close()
    flash("Usuário excluído.")
    return redirect(url_for("admin_dashboard"))


# Adicionar usuário pelo coordenador
@app.route("/admin/add-usuario", methods=['POST'])
@admin_required
def admin_add_usuario():
    nome     = request.form["nome"].strip()
    email    = request.form["email"].strip()
    senha    = request.form["senha"]
    is_admin = int(request.form.get("is_admin", 0))

    conn = conectar(); cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO usuarios (nome, email, senha, is_admin) VALUES (%s,%s,%s,%s)",
            (nome, email, senha, is_admin)
        )
        conn.commit()
        tipo = "coordenador" if is_admin else "bolsista"
        flash(f"✅ {nome} adicionado(a) como {tipo} com sucesso!")
    except mysql.connector.IntegrityError:
        flash(f"⚠️ O e-mail {email} já está cadastrado.")
    finally:
        cur.close(); conn.close()

    return redirect(url_for("admin_dashboard") + "#usuarios")

if __name__ == "__main__":
    app.run(debug=True)
