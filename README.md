## **README - Script para obter resultados de scan Bright**  

### **Descrição**  
Este script permite autenticar na plataforma **Bright**, escolher um projeto para obter informações sobre vulnerabilidades e salvar os dados do último scan do projeto em arquivos **JSON** e **CSV**. 

---

### **Pré-requisitos**  
- Python 3.8+ instalado  
- **pip** atualizado  
- Instalar as dependências necessárias  

---

### **Instalação e Configuração**  

1. **Clone o repositório ou copie o script para o VS Code.**  

2. **Preencha o arquivo `.env` com as suas credencias do Bright:**  
   ```plaintext
   EMAIL=seu_email@example.com
   PASSWORD=sua_senha

3. **Instale as dependências necessárias executando:**  
   ```bash
   pip install -r requirements.txt
   ```

---

### **Como Executar o Script**  
1. Certifique-se de que o `.env` está configurado corretamente.  
2. Execute o script com o seguinte comando:  
   ```bash
   python brightsec_script.py
   ```  
3. Insira o nome do projeto quando solicitado.  

---

### **Saída do Script**  
Após a execução, serão gerados os seguintes arquivos na raiz do projeto:  
- `vulnerabilidades_<nome_do_projeto>.json`  
- `vulnerabilidades_<nome_do_projeto>.csv`  

---

### **Possíveis Problemas**  
- **Erro de autenticação:** Verifique as credenciais no `.env`.  
- **Falha ao instalar dependências:** Certifique-se de que o `pip` está atualizado.  

