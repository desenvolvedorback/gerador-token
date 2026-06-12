# gerador-token
Um gerador de token local que permite vc ter total controle das aplicações.

Resumo da Ópera de Segurança
Ao espalhar essa lógica de Criptografia Simétrica Baseada no Token dentro das suas aplicações, você impossibilita o "Cracking de bypass simples" (onde o usuário apenas altera um pulo de linha no código).

Se você for distribuir esses scripts compilados/empacotados, lembre-se do toque de mestre final:

Python: Compile usando PyArmor para gerar os arquivos .pye ofuscados.

JavaScript: Utilize o javascript-obfuscator antes de mandar o arquivo pro servidor.

Java: Passe um ProGuard no seu JAR para embaralhar os métodos e classes.

A Arquitetura da Barreira Inviolável
Na sua máquina (Dev): Você escreve seu código normal. Antes de subir para a nuvem, você roda um mini-script que pega o seu código limpo e o transforma em uma massa de bytes criptografada.


depois de passar do compilador.py passe nesse script no terminal:

pyarmor pack -e " --onefile" projeto_blindado.py
