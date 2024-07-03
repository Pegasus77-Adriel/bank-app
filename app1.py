from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import socket
from threading import Lock

app = Flask(__name__)
HOST = socket.gethostbyname(socket.gethostname())

# Configurando o banco de dados
def init_db():
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, cpf TEXT UNIQUE, password TEXT, conta TEXT, saldo REAL, banco TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para criação de conta
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    conta = data['conta']
    name = data['name']
    cpf = data['cpf']
    banco = "Nubank"
    password = generate_password_hash(data['password'])
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()

    try:
        c.execute("INSERT INTO users (name, cpf, password, conta, saldo, banco) VALUES (?, ?, ?, ?, ?, ?)", 
                  (name, cpf, password, conta, 0.00, banco))
        conn.commit()
        message = 'Conta criada com sucesso'
    except sqlite3.IntegrityError:
        message = 'Usuário já existe'
    finally:
        conn.close()

    return jsonify({'message': message})

# Rota para login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    conta = data['conta']
    cpf = data['cpf']
    password = data['password']
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    c.execute("SELECT id, password FROM users WHERE cpf = ? AND conta = ?", (cpf, conta))
    user = c.fetchone()
    conn.close()
    if user and check_password_hash(user[1], password):
        return jsonify({'message': 'Login bem-sucedido', 'redirect': url_for('account', cpf=cpf)})
    else:
        return jsonify({'message': 'Credenciais inválidas'})

@app.route('/account/<cpf>')
def account(cpf):
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()
    c.execute("SELECT name, saldo FROM users WHERE cpf = ?", (cpf,))
    user = c.fetchone()
    conn.close()
    
    if user:
        user_data = {'name': user[0], 'saldo': user[1]}
        
        # Faz uma requisição interna para a rota /account/contas/<cpf>
        accounts_response = requests.get(f'http://{HOST}:59998/account/contas/{cpf}')
        
        if accounts_response.status_code == 200:
            accounts_data = accounts_response.json()
        else:
            accounts_data = []

        return render_template('account.html', user=user_data, accounts=accounts_data)
    else:
        return redirect(url_for('index'))  # Redireciona para a página inicial se o usuário não for encontrado

@app.route('/account/contas/<cpf>')
def account_contas(cpf):
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()

    # Execute a query to find all accounts containing the sequence of CPF
    c.execute("SELECT * FROM users WHERE cpf LIKE ?", ('%' + cpf + '%',))
    accounts = c.fetchall()

    # Format the results into a list of dictionaries
    accounts_list = []
    for account in accounts:
        account_dict = {
            "id": account[0],  # Assuming the first column is 'id'
            "nome": account[1],  # Assuming the second column is 'nome'
            "cpf": account[2],  # Assuming the third column is 'cpf'
            "saldo": account[5],  # Assuming the fifth column is 'saldo'
            "tipo": account[4],  # Assuming the fifth column is 'saldo'
            "conta": account[6],
        }
        accounts_list.append(account_dict)

    conn.close()

    # Return the list of accounts as a JSON
    return jsonify(accounts_list)

# Adiciona um bloqueio (lock) para operações críticas
lock = Lock()

@app.route('/account/sacar/<cpf>/<tipo>/<valor>', methods=['POST'])
def account_sacar(cpf, tipo, valor):
    with lock:
        try:
            # Converte o valor para um número
            valor = float(valor)
        except ValueError:
            return jsonify({'error': 'Valor inválido'}), 400

        conn = sqlite3.connect('bank.db')
        try:
            c = conn.cursor()
            conn.execute('BEGIN')  # Inicia a transação

            # Verifica se o usuário existe e obtém o saldo atual
            c.execute("SELECT saldo FROM users WHERE cpf = ?", (cpf,))
            user = c.fetchone()

            if not user:
                print("usuário não encontrado")
                conn.execute('ROLLBACK')
                conn.close()
                return jsonify({'error': 'Usuário não encontrado'}), 404

            saldo_atual = user[0]

            # Verifica se o saldo é suficiente para a operação
            if saldo_atual < valor:
                conn.execute('ROLLBACK')
                conn.close()
                return jsonify({'message': 'Saldo insuficiente'}), 400

            # Calcula o novo saldo
            novo_saldo = saldo_atual - valor

            # Atualiza o saldo na tabela
            c.execute("UPDATE users SET saldo = ? WHERE cpf = ?", (novo_saldo, cpf))
            conn.commit()  # Confirma a transação
        except Exception as e:
            conn.execute('ROLLBACK')  # Reverte a transação em caso de erro
            conn.close()
            return jsonify({'error': str(e)}), 500

        conn.close()
        return jsonify({'message': 'Saque realizado com sucesso', 'novo_saldo': novo_saldo})

@app.route('/account/depositar/<cpf>/<tipo>/<valor>', methods=['POST'])
def account_depositar(cpf, tipo, valor):
    with lock:
        try:
            # Converte o valor para um número
            valor = float(valor)
        except ValueError:
            return jsonify({'error': 'Valor inválido'}), 400

        conn = sqlite3.connect('bank.db')
        try:
            c = conn.cursor()
            conn.execute('BEGIN')  # Inicia a transação

            # Verifica se o usuário existe e obtém o saldo atual
            c.execute("SELECT saldo FROM users WHERE cpf = ?", (cpf,))
            user = c.fetchone()

            if not user:
                conn.execute('ROLLBACK')
                conn.close()
                return jsonify({'error': 'Usuário não encontrado'}), 404

            saldo_atual = user[0]

            # Calcula o novo saldo
            novo_saldo = saldo_atual + valor

            # Atualiza o saldo na tabela
            c.execute("UPDATE users SET saldo = ? WHERE cpf = ?", (novo_saldo, cpf))
            conn.commit()  # Confirma a transação
        except Exception as e:
            conn.execute('ROLLBACK')  # Reverte a transação em caso de erro
            conn.close()
            return jsonify({'error': str(e)}), 500

        conn.close()
        return jsonify({'message': 'Depósito realizado com sucesso', 'novo_saldo': novo_saldo})

if __name__ == '__main__':
    app.run(HOST, port=59998, debug=True)