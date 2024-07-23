package main

import (
    "bufio"
    "fmt"
    "net/http"
    "os"
    "strings"
    "sync"
)

var (
    targetURL  string
    userAgent  = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"
    wordlist   = "/home/matheus/Documentos/wordlist/dirb/lista.txt"
    extensions = []string{".php", ".bak", ".orig", ".inc", ".sql", ".txt", ".pdf", ".js"}
    wordQueue  = make(chan string)
    wg         sync.WaitGroup
    maxWorkers = 10 // Limite de 10 goroutines
    sem        = make(chan struct{}, maxWorkers)
)

func main() {
    fmt.Println("\033[1m\033[91m----------------------------------------\033[0m")
    fmt.Println("\t\tWebRecon\n\n")
    fmt.Println("\033[1m\033[91m----------------------------------------\033[0m")

    fmt.Print("Digite o host (ex: http://host): ")
    reader := bufio.NewReader(os.Stdin)
    targetURL, _ = reader.ReadString('\n')
    targetURL = strings.TrimSpace(targetURL)

    fmt.Println("Host:", targetURL)
    fmt.Println("Resultados:\n")

    // Iniciar as goroutines para o bruteforce
    for i := 0; i < maxWorkers; i++ {
        wg.Add(1)
        go dirBruter()
    }

    // Ler a lista de palavras e enviar para a fila de trabalho
    wordlistFile, err := os.Open(wordlist)
    if err != nil {
        fmt.Println("Erro ao abrir a wordlist:", err)
        return
    }
    defer wordlistFile.Close()

    scanner := bufio.NewScanner(wordlistFile)
    for scanner.Scan() {
        word := scanner.Text()
        wordQueue <- word
    }
    close(wordQueue)

    wg.Wait()
}

func dirBruter() {
    defer wg.Done()

    for word := range wordQueue {
        sem <- struct{}{} // Adquirir um "ticket" do semáforo
        go func(word string) {
            defer func() { <-sem }() // Liberar o "ticket" do semáforo no final

            attemptList := []string{}

            if !strings.Contains(word, ".") {
                attemptList = append(attemptList, "/"+word+"/")
            } else {
                attemptList = append(attemptList, "/"+word)
            }

            // Adicionar extensões se necessário
            for _, ext := range extensions {
                attemptList = append(attemptList, "/"+word+ext)
            }

            // Iterar sobre as tentativas
            for _, brute := range attemptList {
                fullURL := targetURL + brute

                req, err := http.NewRequest("GET", fullURL, nil)
                if err != nil {
                    fmt.Println("Erro ao criar requisição:", err)
                    continue
                }

                req.Header.Set("User-Agent", userAgent)

                client := &http.Client{}
                resp, err := client.Do(req)
                if err != nil {
                    fmt.Println("Erro ao enviar requisição:", err)
                    continue
                }
                defer resp.Body.Close()

                if resp.StatusCode != 404 {
                    fmt.Printf("[%d] => %s\n", resp.StatusCode, fullURL)
                }
            }
        }(word)
    }
}

