document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        const amountInput = form.querySelector('input[name="amount"]');
        if (amountInput && amountInput.value <= 0) {
            e.preventDefault();
            alert('O valor deve ser maior que zero.');
        }
    });
});

document.getElementById('signup-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const conta = document.getElementById('tipoConta').value;
    const name = document.getElementById('name').value;
    const cpf1 = document.getElementById('cpf').value.replace(/\D/g, ''); // Remove a formatação
    const cpf2 = document.getElementById('cpf2').value.replace(/\D/g, ''); // Remove a formatação
    const password = document.getElementById('password').value;

    // Validação do CPF
    if (cpf1.length !== 11) {
        alert('O CPF deve ter exatamente 11 dígitos.');
        return;
    }

    // Validação do CPF Conjunto, se preenchido
    if (cpf2 && cpf2.length !== 11) {
        alert('O CPF conjunto deve ter exatamente 11 dígitos.');
        return;
    }

    let cpf; 

    if (conta === "conjunta") {
        cpf = cpf1 + (cpf2 ? cpf2 : ''); // Concatenação correta dos CPFs
    } else {
        cpf = cpf1;
    }
    try {
        const response = await fetch('/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ conta, name, cpf, password })
        });

        const result = await response.json();
        alert(result.message);
    } catch (error) {
        console.error('Erro ao enviar formulário:', error);
        alert('Ocorreu um erro ao enviar o formulário. Por favor, tente novamente.');
    }
});

document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const conta = document.getElementById('tipoContaLogin').value;
    const cpf1 = document.getElementById('login-cpf').value.replace(/\D/g, ''); // Remove a formatação
    const cpf2 = document.getElementById('login-cpf2').value.replace(/\D/g, ''); // Remove a formatação
    const password = document.getElementById('login-password').value;

    let cpf; 

    if (conta === "conjunta") {
        cpf = cpf1 + (cpf2 ? cpf2 : ''); // Concatenação correta dos CPFs
    } else {
        cpf = cpf1;
    }

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {

                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ conta, cpf, password })
        });

        const result = await response.json();
        alert(result.message);

        if (result.message === 'Login bem-sucedido') {
            window.location.href = result.redirect;
        }
    } catch (error) {
        console.error('Erro ao enviar formulário:', error);
        alert('Ocorreu um erro ao enviar o formulário. Por favor, tente novamente.');
    }
});

document.getElementById('name').addEventListener('input', function (event) {
    const input = event.target;
    input.value = input.value.replace(/[^a-zA-ZÀ-ÿ\s]/g, '');
});

document.getElementById('tipoConta').addEventListener('change', function() {
    const tipoConta = this.value;
    document.getElementById('cpfConjunto1').style.display = tipoConta === 'conjunta' ? 'block' : 'none';
});

document.getElementById('tipoContaLogin').addEventListener('change', function() {
    const tipoContaLogin = this.value;
    document.getElementById('cpfConjuntoLogin').style.display = tipoContaLogin === 'conjunta' ? 'block' : 'none';
});

function formatCPF(e) {
    var value = e.target.value;

    // Remove tudo que não for dígito
    value = value.replace(/\D/g, '');

    // Limita o valor a 11 dígitos
    if (value.length > 11) {
        value = value.slice(0, 11);
    }

    // Adiciona a formatação de CPF
    if (value.length > 6) {
        value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    } else if (value.length > 3) {
        value = value.replace(/(\d{3})(\d{3})(\d{1,3})/, '$1.$2.$3');
    } else if (value.length > 0) {
        value = value.replace(/(\d{3})(\d{1,3})/, '$1.$2');
    }

    e.target.value = value;
}

// Seleciona todos os campos com a classe 'cpf'
var cpfFields = document.querySelectorAll('.cpf');

// Seleciona todos os campos com o nome 'target_cpf'
var targetCpfFields = document.querySelectorAll('[name="target_cpf"]');

// Adiciona o event listener a cada campo com a classe 'cpf'
cpfFields.forEach(function(field) {
    field.addEventListener('input', formatCPF);
});

// Adiciona o event listener a cada campo com o nome 'target_cpf'
targetCpfFields.forEach(function(field) {
    field.addEventListener('input', formatCPF);
});



