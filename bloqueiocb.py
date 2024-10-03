import os
import subprocess

def executar_comando(comando):
    """Função para executar comandos no shell."""
    try:
        print(f"Executando: {comando}")
        subprocess.run(comando, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar: {comando}")
        print(e)

def baixar_lista_de_sites():
    """Baixa a lista de sites para bloqueio."""
    url_lista = "https://raw.githubusercontent.com/Badcebola/blockcebola/refs/heads/main/Sites-bloqueios"
    arquivo_destino = "/etc/unbound/bloqueiodesites/sites"
    
    # Baixar a lista de sites usando curl
    executar_comando(f"curl -s {url_lista} -o {arquivo_destino}")
    print("Lista de sites baixada com sucesso.")

def criar_arquivo_bloqueio():
    """Cria o arquivo de configuração de bloqueio de sites."""
    arquivo_sites = "/etc/unbound/bloqueiodesites/sites"
    arquivo_config = "/etc/unbound/bloqueiodesites/bloqueio.conf"

    print("Recriando o arquivo de configuração de bloqueio...")
    with open(arquivo_config, 'w') as conf_file:
        with open(arquivo_sites, 'r') as sites_file:
            for dominio in sites_file:
                dominio = dominio.strip()  # Remove espaços ou quebras de linha
                conf_file.write(f'local-zone: "{dominio}" redirect\n')
                conf_file.write(f'local-data: "{dominio} A 127.0.0.1"\n')
                conf_file.write(f'local-data: "{dominio} AAAA ::1"\n')
                conf_file.write("\n")
    print(f"Arquivo de configuração criado: {arquivo_config}")

def adicionar_bloqueio_no_unbound():
    """Adiciona o arquivo de bloqueio nas configurações do Unbound."""
    unbound_conf_path = "/etc/unbound/unbound.conf"
    bloqueio_conf_entry = 'include: "/etc/unbound/bloqueiodesites/bloqueio.conf"'
    bloqueio_conf_server_block = f"server:\n    {bloqueio_conf_entry}\n"

    # Ler o conteúdo do arquivo unbound.conf
    with open(unbound_conf_path, "r") as unbound_conf:
        conteudo = unbound_conf.read()

    # Verifica se o bloco de configuração completo já existe
    if bloqueio_conf_entry in conteudo:
        print("A configuração de bloqueio já existe no Unbound.")
    else:
        # Adicionar a configuração ao final do arquivo
        with open(unbound_conf_path, "a") as unbound_conf:
            unbound_conf.write(f"\n{bloqueio_conf_server_block}")
        print("Configuração de bloqueio adicionada ao Unbound.")

    # Reinicia o serviço do Unbound
    executar_comando("systemctl restart unbound")

def configurar_apache():
    """Instala e configura o Apache, PHP e o site bloqueadonobrasil se o Apache não estiver instalado."""
    # Verifica se o Apache já está instalado
    try:
        subprocess.run("apache2 -v", shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Apache já está instalado. Pulando a instalação.")
    except subprocess.CalledProcessError:
        print("Apache não encontrado. Instalando Apache e pacotes necessários...")
        
        # Instalar Apache e PHP
        executar_comando("apt install apache2 -y")

        # Reiniciar o Apache para garantir que as mudanças tenham efeito
        executar_comando("systemctl restart apache2")

    # Verifica se o diretório bloqueadonobrasil já existe
    if not os.path.exists("/var/www/bloqueadonobrasil"):
        executar_comando("cd /var/www/ && wget https://github.com/Badcebola/blockcebola/raw/refs/heads/main/bloqueadonobrasil.tar.gz")
        executar_comando("cd /var/www/ && tar -vxzf bloqueadonobrasil.tar.gz")
        executar_comando("rm /var/www/bloqueadonobrasil.tar.gz")
    else:
        print("O diretório /var/www/bloqueadonobrasil já existe. Pulando a descompressão.")

    # Modificar o DocumentRoot no arquivo de configuração do Apache
    config_file = "/etc/apache2/sites-available/000-default.conf"
    with open(config_file, 'r') as file:
        conteudo = file.read()

    novo_documentroot = "DocumentRoot /var/www/bloqueadonobrasil"
    if "DocumentRoot /var/www/bloqueadonobrasil" in conteudo:
        print("DocumentRoot já está configurado para /var/www/bloqueadonobrasil. Pulando atualização.")
    else:
        print("Atualizando o DocumentRoot para /var/www/bloqueadonobrasil...")
        conteudo = conteudo.replace("DocumentRoot /var/www/html", novo_documentroot)
    
        with open(config_file, 'w') as file:
            file.write(conteudo)
        
        # Reiniciar o Apache para aplicar as mudanças
        executar_comando("systemctl restart apache2")
        print("DocumentRoot atualizado para /var/www/bloqueadonobrasil.")

def adicionar_crontab():
    """Adiciona uma entrada no crontab para executar o script de minuto em minuto."""
    cron_job = "0 0 * * * cd /etc/unbound && /usr/bin/python3 bloqueiocb.py"
    
    # Verifica se a tarefa já existe no crontab
    try:
        crontab_result = subprocess.run("crontab -l", shell=True, check=True, capture_output=True, text=True)
        if cron_job not in crontab_result.stdout:
            # Adiciona a nova entrada no crontab
            executar_comando(f'(crontab -l ; echo "{cron_job}") | crontab -')
            print("Tarefa adicionada ao crontab com sucesso.")
        else:
            print("A tarefa já existe no crontab.")
    except subprocess.CalledProcessError:
        # Se o crontab não existe ainda, cria-o
        executar_comando(f'echo "{cron_job}" | crontab -')
        print("Crontab criado e tarefa adicionada com sucesso.")

if __name__ == "__main__":
    # Criar o diretório se ele não existir
    if not os.path.exists("/etc/unbound/bloqueiodesites"):
        executar_comando("mkdir -p /etc/unbound/bloqueiodesites")
        print("Diretório /etc/unbound/bloqueiodesites criado com sucesso.")
    
    if os.path.exists("/etc/unbound/bloqueiodesites"):
        baixar_lista_de_sites()
        criar_arquivo_bloqueio()
        adicionar_bloqueio_no_unbound()
        configurar_apache()
        adicionar_crontab()
        print("Processo de bloqueio de sites e configuração do Apache finalizado com sucesso.")
    else:
        print("Erro ao criar o diretório /etc/unbound/bloqueiodesites.")
