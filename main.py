from flask import Flask, render_template, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)
DATABASE = "links.db"

# Lista de links iniciais
LINKS = [
    "https://www.tecconcursos.com.br/questoes/cadernos/71567640",
    "https://www.tecconcursos.com.br/questoes/cadernos/71126507",
    "https://www.tecconcursos.com.br/questoes/cadernos/71567654",
    "https://www.tecconcursos.com.br/questoes/cadernos/71145453",
    "https://www.tecconcursos.com.br/questoes/cadernos/71567719",
    "https://www.tecconcursos.com.br/questoes/cadernos/71145441",
    "https://www.tecconcursos.com.br/questoes/cadernos/71145457",
    "https://www.tecconcursos.com.br/questoes/cadernos/71145424",
    "https://www.tecconcursos.com.br/questoes/cadernos/71145434",
    "https://www.tecconcursos.com.br/questoes/cadernos/71567723",
    "https://www.tecconcursos.com.br/questoes/cadernos/71567635",
    "https://www.tecconcursos.com.br/questoes/cadernos/71567622",
    "https://www.tecconcursos.com.br/questoes/cadernos/71567631",
    "https://www.tecconcursos.com.br/questoes/cadernos/71145055",
    "https://www.tecconcursos.com.br/questoes/cadernos/71145465",
    # Novo link adicionado
]


# Criar conexão com o banco de dados
def get_db():
  db = sqlite3.connect(DATABASE)
  db.row_factory = sqlite3.Row
  return db


# Inicializar banco de dados
def init_db():
  with get_db() as db:
    cursor = db.cursor()

    # Cria as tabelas se não existirem
    cursor.execute('''CREATE TABLE IF NOT EXISTS links (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            url TEXT NOT NULL UNIQUE)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS state (
                            id INTEGER PRIMARY KEY,
                            current_index INTEGER)''')

    # Inicializa a tabela de estado se estiver vazia
    cursor.execute("SELECT COUNT(*) FROM state")
    if cursor.fetchone()[0] == 0:
      cursor.execute("INSERT INTO state (id, current_index) VALUES (1, 0)")
      db.commit()

    # Obtém os links atuais no banco de dados
    cursor.execute("SELECT url FROM links")
    db_links = [row["url"] for row in cursor.fetchall()]

    # Adiciona novos links que estão na lista LINKS mas não no banco de dados
    for link in LINKS:
      if link not in db_links:
        cursor.execute("INSERT INTO links (url) VALUES (?)", (link, ))
        print(f"Link adicionado: {link}")

    # Remove links que estão no banco de dados mas não estão na lista LINKS
    for db_link in db_links:
      if db_link not in LINKS:
        cursor.execute("DELETE FROM links WHERE url = ?", (db_link, ))
        print(f"Link removido: {db_link}")

    db.commit()


@app.route('/')
def index():
  db = get_db()
  cursor = db.cursor()
  cursor.execute("SELECT current_index FROM state WHERE id = 1")
  current_index = cursor.fetchone()[0]
  cursor.execute("SELECT url FROM links ORDER BY id")
  links = cursor.fetchall()
  current_link = links[current_index][0]
  return render_template('index.html', link=current_link)


@app.route('/next')
def next_link():
  db = get_db()
  cursor = db.cursor()
  cursor.execute("SELECT COUNT(*) FROM links")
  total_links = cursor.fetchone()[0]
  cursor.execute("SELECT current_index FROM state WHERE id = 1")
  current_index = cursor.fetchone()[0]
  new_index = (current_index + 1) % total_links
  cursor.execute("UPDATE state SET current_index = ? WHERE id = 1",
                 (new_index, ))
  db.commit()

  # Retorna o próximo link como JSON
  cursor.execute("SELECT url FROM links ORDER BY id")
  links = cursor.fetchall()
  next_link = links[new_index][0]
  return jsonify({"next_link": next_link})


if __name__ == '__main__':
    with app.app_context():
        init_db()
    port = int(os.environ.get("PORT", 5000))  # Pega a porta do Render
    app.run(host='0.0.0.0', port=port)
