#!/bin/bash

# Script para gerar SECRET_KEY segura para produção

echo "🔐 Gerando SECRET_KEY segura..."
echo ""

# Gerar chave usando Python
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

echo "✅ SECRET_KEY gerada com sucesso!"
echo ""
echo "Adicione esta linha ao seu arquivo .env de produção:"
echo ""
echo "SECRET_KEY=${SECRET_KEY}"
echo ""
echo "⚠️  IMPORTANTE:"
echo "  - Nunca compartilhe esta chave"
echo "  - Nunca faça commit desta chave no git"
echo "  - Use diferentes chaves para dev/staging/production"
echo ""
