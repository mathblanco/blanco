import subprocess
import socket
import shlex

def print_banner():
	print('\033[1m' + '\033[5m' + '\033[94m' + '-------------------------------------' + '\033[0m')
	print('\033[1m' + '\033[5m' + '\033[94m' + '\t Smart Recon' + '\033[0m')
	print('\033[1m' + '\033[5m' + '\033[94m' + '-------------------------------------' + '\033[0m')

def run_nmap(domain):
    if not domain:
        print("Domínio inválido.")
        return

    print("\n--- Executando Nmap ---\n")
    nmap_command = f"nmap -sV -Pn {domain}"
    print(f"Comando Nmap: {nmap_command}")  # Comando para depuração
    result = subprocess.run(shlex.split(nmap_command), capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Erro ao executar Nmap: {result.stderr}")
    else:
        print(result.stdout)

def check_http_methods(domain):
    print("\n--- Identificando Métodos HTTP Aceitos ---\n")
    curl_command = f"curl -X OPTIONS -i http://{domain}"
    result = subprocess.run(shlex.split(curl_command), capture_output=True, text=True)
    print(result.stdout)

def run_dirb(domain):
    print("\n--- Executando Dirb ---")
    
    protocol = input("Escolha o protocolo (http ou https): ").strip().lower()
    if protocol not in ['http', 'https']:
        print("Protocolo inválido. Usando http por padrão.")
        protocol = 'http'
    
    extensions = input("Digite as extensões a serem procuradas (ex: .php,.txt,.pdf) ou pressione Enter para ignorar: ").strip()
    delay = input("Digite o delay em milissegundos (ou pressione Enter para nenhum): ").strip()
    
    dirb_command = f"dirb {protocol}://{domain}/ /usr/share/dirb/wordlists/big.txt -r"
    
    if extensions:
        dirb_command += f" -X {extensions}"
    if delay:
        dirb_command += f" -z {delay}ms"
    
    print(f"Comando Dirb: {dirb_command}")  # Para depuração
    
    try:
        subprocess.run(shlex.split(dirb_command))
    except Exception as e:
        print(f"Erro ao executar o comando: {str(e)}")

def enumerate_subdomains(domain):
    wordlist = "/usr/share/dirb/wordlists/small.txt"
    print("\n--- Enumeração de Subdomínios ---")
    subdomains = []
    with open(wordlist, 'r') as f:
        for line in f:
            subdomain = line.strip()
            if subdomain:  # Verifica se o subdomínio não está vazio
                DNS = f"{subdomain}.{domain}"
                if len(DNS) <= 253:  # Verifica se o nome completo do domínio não é muito longo
                    try:
                        ip = socket.gethostbyname(DNS)
                        subdomains.append({DNS: ip})
                        print(f"{DNS}: {ip}")
                    except socket.gaierror:
                        pass
                else:
                    print(f"Subdomínio ignorado (muito longo): {DNS}")
            else:
                print("Subdomínio vazio ignorado.")


def run_dns(domain):
    print("\n--- DNS ---")
    while True:
        print('\033[1m' + '\033[92m' + "1. Consultar Name Server" + '\033[0m')
        print('\033[1m' + '\033[92m' + "2. Consultar SPF" + '\033[0m')
        print('\033[1m' + '\033[92m' + "3. Voltar ao menu principal" + '\033[0m')
        
        choice = input("Escolha uma opção: ")
        
        if choice == '1':
            print(f"\n--- Name Server para {domain} ---")
            ns_command = f"host -t ns {domain}"
            result = subprocess.run(shlex.split(ns_command), capture_output=True, text=True)
            print(result.stdout)
        elif choice == '2':
            print(f"\n--- SPF para {domain} ---")
            spf_command = f"host -t txt {domain}"
            result = subprocess.run(shlex.split(spf_command), capture_output=True, text=True)
            print(result.stdout)
        elif choice == '3':
            break
        else:
            print("Opção inválida. Tente novamente.")

def main():
    print_banner()
    
    print('\nEntre com o domínio alvo')
    print('\nex: businesscorp.com.br')
    domain = input("Domínio: ")

    while True:
        print('\n\033[1m' + '\033[92m' + '--- Menu ---' + '\033[0m')  # Menu em verde
        print('\033[1m' + '\033[92m' + '1. Executar Nmap' + '\033[0m')
        print('\033[1m' + '\033[92m' + '2. Identificar Métodos HTTP Aceitos' + '\033[0m')
        print('\033[1m' + '\033[92m' + '3. Executar Dirb' + '\033[0m')
        print('\033[1m' + '\033[92m' + '4. Enumerar Subdomínios' + '\033[0m')
        print('\033[1m' + '\033[92m' + '5. Executar DNS' + '\033[0m')
        print('\033[1m' + '\033[92m' + '6. Trocar de host' + '\033[0m')
        print('\033[1m' + '\033[92m' + '7. Sair' + '\033[0m')
        
        choice = input("Escolha uma opção: ")

        if choice == '1':
            run_nmap(domain)
        elif choice == '2':
            check_http_methods(domain)
        elif choice == '3':
            run_dirb(domain)
        elif choice == '4':
            enumerate_subdomains(domain)
        elif choice == '5':
            run_dns(domain)
        elif choice == '6':
            domain = input("Digite o novo domínio alvo: ")
        elif choice == '7':
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()

