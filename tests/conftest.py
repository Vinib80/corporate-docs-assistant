"""
conftest.py – configuração compartilhada de todos os testes.

Problema: embeddings.py e generation.py instanciam genai.Client() no nível
do módulo (fora de qualquer função), portanto o import já falha se
GOOGLE_API_KEY não estiver definida. Este conftest garante que a variável
existe ANTES que qualquer test file importe esses módulos.

Em tests de unidade/integração que mockam os módulos externos, o cliente
Gemini nunca é realmente chamado — mas o import precisa ter sucesso.
"""
import os

# Garante que GOOGLE_API_KEY existe para imports de módulo não falharem.
# O valor fictício é suficiente: nos testes que usam mock, o cliente nunca
# faz chamadas reais à API.
os.environ.setdefault("GOOGLE_API_KEY", "FAKE_KEY_FOR_TESTS")
