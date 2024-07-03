document.getElementById('account_sacar').addEventListener('submit',  async (e) =>{
    e.preventDefault();
    const dados = document.getElementById('account-select').value;
    const cpf = dados.cpf
    const tipo = dados.tipo
    const valor = document.querySelector('#sacar input[name="amount"]').value;
    const url = `/account/sacar/${cpf}/${tipo}/${valor}`;
    this.action = url;
    this.method = 'post';
    this.submit();
});

document.getElementById('depositar').addEventListener('submit', async (e) => {
e.preventDefault();
const dados = document.getElementById('account-select').value;
console.log(dados.cpf);
        // Adicione aqui a lógica para construir a URL e fazer a requisição
});