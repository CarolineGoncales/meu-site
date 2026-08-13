# Publicação na Render

## Backend

Configure o serviço para usar `backend_estude` como diretório de trabalho e execute:

```text
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Variáveis necessárias:

```text
DATABASE_URL=<URL interna do PostgreSQL da Render>
MERCADO_PAGO_ACCESS_TOKEN=<token privado do Mercado Pago>
MERCADO_PAGO_PUBLIC_KEY=<chave pública do Mercado Pago>
```

Após o deploy, cadastre no painel do Mercado Pago a URL:

```text
https://cpg-estude-backend.onrender.com/webhook
```

Habilite o tópico de assinatura `subscription_preapproval`.

## Checklist de publicação

1. Faça commit de todos os arquivos modificados, incluindo `material-progresso.js`.
2. Confirme que a Render concluiu o deploy sem falhas de dependência.
3. Faça um cadastro de teste e inicie uma assinatura de teste no Mercado Pago.
4. Após a notificação do webhook, confirme que o login é liberado.
5. Conclua uma apostila Python ou IA, recarregue a página e confirme que ela continua marcada como concluída.
6. Ao completar seis apostilas de uma trilha, confirme a liberação e o download do certificado.

As trilhas Cloud & DevOps e Analista de Projetos permanecem somente como grade de conteúdos em breve; elas não liberam materiais, progresso ou certificados enquanto não houver apostilas publicadas.
