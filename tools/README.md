# Ferramentas de Automação (`tools/`)

Este diretório contém ferramentas auxiliares de compilação e geração de ativos gráficos do projeto.

---

## 1. Compilador de Diagramas (`build_diagrams.py` / `build_diagrams.sh`)

Script automatizado para compilar arquivos de especificação Mermaid (`.mmd`) presentes em `doc/assets/diagrams/` gerando os formatos:
* **Vetor Scalable (`.svg`)**: com estilos CSS incorporados.
* **Imagem Rasterizada Retina 2x (`.png`)**: em alta resolução com fundo escuro e efeito de iluminação neon.

### Pré-requisitos
* Node.js / NPM
* `@mermaid-js/mermaid-cli` instalado globalmente:
  ```bash
  npm install -g @mermaid-js/mermaid-cli
  ```

### Uso Rápido
Executando a partir da raiz do repositório:
```bash
./tools/build_diagrams.sh
```
Ou diretamente com Python:
```bash
python3 tools/build_diagrams.py
```

### Opções Disponíveis
```bash
python3 tools/build_diagrams.py --help
```
* `--diagrams-dir`: Diretório contendo os arquivos `.mmd` (padrão: `doc/assets/diagrams`).
* `--theme`: Caminho para a folha de estilo CSS (padrão: `doc/assets/themes/cyberpunk.css`).
* `--bg-color`: Cor hexadecimal de fundo (padrão: `#030a16`).
* `--scale`: Fator de escala da imagem PNG (padrão: `2`).
