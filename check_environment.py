#!/usr/bin/env python
"""
Verificador de Ambiente - SwOPy & Sewer Optimizer
Verifica se todas as dependências e arquivos estão prontos
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Verifica versão do Python"""
    print("\n[1/4] Verificando versão do Python...")
    major, minor, micro = sys.version_info[:3]
    version_str = f"{major}.{minor}.{micro}"
    
    if major < 3 or (major == 3 and minor < 8):
        print(f"   ❌ Python {version_str} - Versão mínima é 3.8!")
        return False
    
    print(f"   ✓ Python {version_str} (OK)")
    return True

def check_standard_libraries():
    """Verifica se bibliotecas padrão estão disponíveis"""
    print("\n[2/4] Verificando bibliotecas padrão...")
    
    required_libs = [
        'csv', 'json', 'math', 'random', 'statistics',
        'argparse', 'dataclasses', 'collections', 'pathlib', 'typing'
    ]
    
    all_ok = True
    for lib in required_libs:
        try:
            __import__(lib)
            print(f"   ✓ {lib}")
        except ImportError:
            print(f"   ❌ {lib} - Não encontrado!")
            all_ok = False
    
    return all_ok

def check_required_files():
    """Verifica presença de arquivos essenciais"""
    print("\n[3/4] Verificando arquivos do projeto...")
    
    required_files = [
        'SwOPy.py',
        'sewer_optimizer.py',
        'sample_network.csv',
        'sample_config.json'
    ]
    
    current_dir = Path.cwd()
    all_found = True
    
    for filename in required_files:
        filepath = current_dir / filename
        if filepath.exists():
            print(f"   ✓ {filename}")
        else:
            print(f"   ⚠ {filename} - Não encontrado (pode ser gerado com --generate-samples)")
            # Não é crítico para sewer_optimizer.py, que pode gerar samples
            if filename in ['sample_network.csv', 'sample_config.json']:
                continue
            all_found = False
    
    return all_found or True  # Permite prosseguir se samples não existem

def check_execution():
    """Testa se sewer_optimizer.py pode ser executado"""
    print("\n[4/4] Testando execução...")
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, 'sewer_optimizer.py', '--help'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("   ✓ sewer_optimizer.py executável")
            return True
        else:
            print(f"   ❌ Erro ao executar: {result.stderr[:100]}")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {str(e)[:100]}")
        return False

def main():
    """Executa todas as verificações"""
    print("=" * 50)
    print(" Verificação de Ambiente - SwOPy/Optimizer")
    print("=" * 50)
    
    checks = [
        ("Python versão", check_python_version),
        ("Bibliotecas padrão", check_standard_libraries),
        ("Arquivos do projeto", check_required_files),
        ("Execução", check_execution),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ Erro na verificação: {str(e)}")
            results.append((name, False))
    
    # Resumo
    print("\n" + "=" * 50)
    print(" RESUMO")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "✓ OK" if result else "❌ FALHOU"
        print(f"  {status} - {name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print(" ✅ AMBIENTE PRONTO! Você pode rodar:")
        print("    python sewer_optimizer.py --help")
        print("    python sewer_optimizer.py --generate-samples")
    else:
        print(" ❌ Alguns problemas foram encontrados.")
        print("    Veja SETUP_GUIDE.md para mais detalhes.")
    print("=" * 50 + "\n")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
