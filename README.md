# SwOPy & Sewer Optimizer 🚿

Ferramentas computacionais em Python para otimização de redes coletoras de esgoto usando Algoritmos Genéticos.

## 📁 Arquivos do Projeto

- **SwOPy.py** - Versão original com rede fixa de 18 trechos e 19 nós (base da dissertação Gameiro 2003)
- **sewer_optimizer.py** - Versão 2.0 com suporte a redes dinâmicas via CSV e saída em Excel
- **sample_network.csv** - Exemplo de topologia de rede
- **sample_config.json** - Configuração de parâmetros e custos
- **requirements.txt** - Dependências do projeto (apenas stdlib)

## ⚡ Início Rápido

### Pré-requisitos

- **Python 3.8+** (Obrigatório)

### Instalação

1. **Instale Python** (se ainda não tiver):
   - Acesse: https://www.python.org/downloads/
   - Baixe Python 3.11 ou superior
   - Execute o instalador com **"Add Python to PATH"** marcado

2. **Verifique a instalação**:
   ```powershell
   python --version
   ```

3. **Pronto!** Não há dependências externas para instalar.

### Executar o Projeto

#### Versão 2.0 (Recomendado - Redes Dinâmicas)

Gerar arquivos de exemplo:
```powershell
python sewer_optimizer.py --generate-samples
```

Executar com dados de exemplo:
```powershell
python sewer_optimizer.py --network sample_network.csv --config sample_config.json
```

Ver todas as opções:
```powershell
python sewer_optimizer.py --help
```

#### Versão Original (SwOPy - Rede Fixa)

```powershell
python SwOPy.py
```

## 🔍 Verificar Configuração

Execute o script de verificação:
```powershell
verificar_ambiente.bat
```

Ou manualmente:
```powershell
python --version
python sewer_optimizer.py --help
```

## 📊 Saídas

O projeto gera:
- **CSV**: Resultados tabulares com dimensões e custos
- **Excel (.xlsx)**: Planilha completa com análise hidráulica (sewer_optimizer.py)
- **JSON**: Configuração e parâmetros

## 🧬 Algoritmo Genético

Parâmetros configuráveis:
- População inicial
- Número de gerações
- Taxa de cruzamento (Pc)
- Taxa de mutação (Pm)
- Estratégia de elitismo

## 📖 Documentação Adicional

- **SETUP_GUIDE.md** - Guia completo de instalação e solução de problemas
- **requirements.txt** - Comentários sobre dependências

## ⚙️ Requisitos Técnicos

### Bibliotecas Utilizadas (Todas Padrão do Python)

- `csv` - Leitura/escrita de redes e resultados
- `json` - Configuração e parâmetros
- `math` - Cálculos hidráulicos
- `random` - Geração de números aleatórios (AG)
- `statistics` - Estatísticas (média, desvio padrão)
- `argparse` - Interface CLI
- `dataclasses` - Estrutura de dados
- `collections` - defaultdict, deque
- `pathlib` - Manipulação de caminhos
- `typing` - Type hints

## 🛠️ Solução de Problemas

### Python não encontrado
- Reinstale Python com **"Add Python to PATH"** marcado
- Feche e reabra o PowerShell

### Erro de codificação UTF-8 (Windows)
- Execute: `chcp 65001` antes de rodar
- O projeto trata automaticamente (ver linha 38 em sewer_optimizer.py)

### Arquivo não encontrado
- Certifique-se que está no diretório correto:
  ```powershell
  cd "c:\Users\User\Documents\Otimização Gamero\Otimizacao-Gamero"
  ```

## 📝 Exemplo Completo

```powershell
# 1. Verificar Python
python --version

# 2. Ir para o diretório do projeto
cd "c:\Users\User\Documents\Otimização Gamero\Otimizacao-Gamero"

# 3. Gerar arquivos de exemplo
python sewer_optimizer.py --generate-samples

# 4. Executar otimização
python sewer_optimizer.py --network sample_network.csv --config sample_config.json

# 5. Verifique os resultados (arquivos .csv e .xlsx gerados)
```

## 📧 Informações

- **Base**: Dissertação "Dimensionamento Otimizado de Redes de Esgotos Usando Algoritmos Genéticos" - Gameiro (2003)
- **Versão Original**: SwOPy.py (rede fixa)
- **Versão 2.0**: sewer_optimizer.py (redes dinâmicas, topologia via CSV)

---

**Última atualização**: Junho 2026
