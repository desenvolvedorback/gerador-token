const jwt = require('jsonwebtoken');
const crypto = require('crypto');

// Dados cruciais do sistema criptografados em AES-256-CBC
const DADOS_CRIPTOGRAFADOS = "b2E5MmRj..."; 
const IV = Buffer.from("1234567890123456"); // Vetor de inicialização fictício

function verificarEDesbloquear(tokenUsuario) {
    try {
        // 1. Valida o JWT
        const payload = jwt.verify(tokenUsuario, "SEGREDO_MESTRE_SUPER_SEGURO", { algorithms: ['HS256'] });

        if (payload.status !== 'active') {
            console.log("[-] ERRO: Licença não está ativa.");
            process.exit(1);
        }

        // 2. ANTI-TAMPER: Deriva a chave de descriptografia a partir do token
        // Se o cracker remover o validador do JWT, ele não terá a chave para rodar o decrypter abaixo
        const chaveDerivada = crypto.createHash('sha256').update(tokenUsuario).digest();
        const decipher = crypto.createDecipheriv('aes-256-cbc', chaveDerivada, IV);
        
        let dadosPuros = decipher.update(DADOS_CRIPTOGRAFADOS, 'hex', 'utf8');
        dadosPuros += decipher.final('utf8');
        
        return dadosPuros;

    } catch (err) {
        console.log("[-] ERRO CRÍTICO: Assinatura inválida ou código incompleto.");
        process.exit(1);
    }
}

// Execução
const readline = require('readline').createInterface({ input: process.stdin, output: process.stdout });
readline.question('Insira seu token: ', (token) => {
    const variavelSaaS = verificarEDesbloquear(token.trim());
    console.log("[+] Sistema iniciado com sucesso!");
    readline.close();
});
