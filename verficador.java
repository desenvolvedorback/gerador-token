import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.interfaces.DecodedJWT;
import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.Scanner;

public class VerificadorSaaS {

    // Simulação de string crucial encriptada (Hexadecimal)
    private static final String DADOS_MUTADOS = "4f61b36a..."; 

    public static String verificarEDesbloquear(String tokenUsuario) {
        try {
            // 1. Validação JWT
            Algorithm algorithm = Algorithm.HMAC256("SEGREDO_MESTRE_SUPER_SEGURO");
            DecodedJWT jwt = JWT.require(algorithm).build().verify(tokenUsuario);

            if (!"active".equals(jwt.getClaim("status").asString())) {
                System.out.println("[-] ERRO: Status da licença inválido.");
                System.exit(1);
            }

            // 2. ANTI-TAMPER: Derivação de chave AES-128 via SHA-256 do token
            byte[] key = tokenUsuario.getBytes(StandardCharsets.UTF_8);
            MessageDigest sha = MessageDigest.getInstance("SHA-256");
            key = sha.digest(key);
            key = Arrays.copyOf(key, 16); // Usa os primeiros 128 bits
            
            SecretKeySpec secretKey = new SecretKeySpec(key, "AES");
            Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
            cipher.init(Cipher.DECRYPT_MODE, secretKey);
            
            // Converte o Hex do dado para Bytes e Descriptografa
            byte[] dadosHex = javax.xml.bind.DatatypeConverter.parseHexBinary(DADOS_MUTADOS);
            return new String(cipher.doFinal(dadosHex), StandardCharsets.UTF_8);

        } catch (Exception e) {
            System.out.println("[-] ERRO CATASTRÓFICO: Integridade violada ou código incompleto!");
            System.exit(1);
        }
        return null;
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.print("Insira seu token de ativação: ");
        String token = scanner.nextLine().trim();

        // Se alterarem essa linha ou removerem, as funções abaixo não recebem os dados puros e quebram
        String credencialSaaS = verificarEDesbloquear(token);

        System.out.println("[+] Inicializando core do software de forma segura...");
    }
}
