# 🔧 Guia de Instalação - SwOPy & Sewer Optimizer

## ✅ O que você precisa fazer:

### 1️⃣ **Instalar Python 3.8+**

#### Opção A: Instalador oficial (Recomendado)
1. Acesse: https://www.python.org/downloads/
2. Clique em **"Download Python 3.11"** (ou versão mais recente)
3. Execute o instalador
4. **⚠️ IMPORTANTE**: Marque a opção **"Add Python to PATH"** antes de clicar em Install
5. Conclua a instalação

#### Opção B: Microsoft Store (Mais fácil)
1. Abra **Microsoft Store** no Windows
2. Pesquise por **"Python 3.11"**
3. Clique em **Instalar**

### 2️⃣ **Verificar a Instalação**

Abra o PowerShell/CMD e execute:
```powershell
python --version
```

Deve retornar algo como: `Python 3.11.x`

### 3️⃣ **Dependências do Projeto**

✨ **Boa notícia**: Este projeto usa **APENAS bibliotecas padrão do Python**!

Nenhuma instalação adicional é necessária. O projeto usa apenas:
- `csv`, `json` - para leitura/escrita de dados
- `math`, `random` - para cálculos matemáticos
- `statistics` - para estatísticas
- `argparse` - para linha de comando
- `dataclasses` - para estrutura de dados
- Tudo isso já vem com Python!

### 4️⃣ **Rodar o Projeto**

#### Gerar arquivos de exemplo:
```powershell
python sewer_optimizer.py --generate-samples
```

#### Executar com dados de exemplo:
```powershell
python sewer_optimizer.py --network sample_network.csv --config sample_config.json
```

#### Executar SwOPy (versão original):
```powershell
python SwOPy.py
```

---

## 📋 Verificação Rápida

Se tudo estiver instalado, você deve conseguir executar:
```powershell
python --version
cd "c:\Users\User\Documents\Otimização Gamero\Otimizacao-Gamero"
python sewer_optimizer.py --help
```

---

## ❓ Problemas Comuns?

### "Python não foi encontrado"
- Feche e reabra o PowerShell após instalar Python
- Verifique se marcou **"Add Python to PATH"** durante a instalação
- Se não marcou, desinstale e reinstale marcando esta opção

### Erro de encoding UTF-8
- O projeto trata isso automaticamente (veja a linha 38 em `sewer_optimizer.py`)
- Se ainda tiver problemas, use: `chcp 65001` antes de rodar

### Arquivos CSV ou JSON não encontrados
- Certifique-se de estar no diretório correto:
  ```powershell
  cd "c:\Users\User\Documents\Otimização Gamero\Otimizacao-Gamero"
  ```
- Ou use caminhos absolutos

---

## 🎯 Próximos Passos

1. ✅ Instale Python seguindo as instruções acima
2. ✅ Abra o PowerShell e execute: `python --version`
3. ✅ Execute: `python sewer_optimizer.py --help`
4. ✅ Rode o projeto com: `python sewer_optimizer.py --network sample_network.csv --config sample_config.json`

Pronto! 🚀
