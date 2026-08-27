from fastapi import APIRouter, Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Assinante

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================================================
# WEBHOOK PAGBANK (ASSINATURAS / RECORRÊNCIA)
# =========================================================
@router.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    try:
        dados = await request.json()
    except Exception:
        # Retorna erro HTTP 400 se o JSON estiver corrompido
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Payload inválido"
        )

    print("========================================")
    print("WEBHOOK PAGBANK RECEBIDO")
    print("DADOS COMPLETOS:", dados)
    print("========================================")

    # Captura o tipo de evento enviado na raiz do JSON pelo PagBank
    evento = dados.get("event") 
    
    # Tratamento para garantir compatibilidade caso os dados venham na raiz ou no nó 'resource'
    resource = dados.get("resource") if isinstance(dados.get("resource"), dict) else dados

    # 1. Localiza o ID da Assinatura
    assinatura_id = resource.get("id") or dados.get("subscription_id")

    # 2. Localiza o Status da Assinatura (O PagBank envia em CAIXA ALTA, ex: ACTIVE)
    status_assinatura = resource.get("status")
    if isinstance(status_assinatura, str):
        status_assinatura = status_assinatura.upper()

    # 3. Localiza o E-mail do Cliente (Formato padrão PagBank: customer -> email)
    customer = resource.get("customer") or {}
    email = None
    if isinstance(customer, dict):
        email = customer.get("email")
    
    # Fallbacks de segurança para capturar o e-mail em diferentes variações do payload
    if not email:
        email = resource.get("email") or dados.get("email")

    print(f"EVENTO MAPEADO: {evento}")
    print(f"ID DA ASSINATURA: {assinatura_id}")
    print(f"STATUS ENVIADO: {status_assinatura}")
    print(f"EMAIL EXTRAÍDO: {email}")

    # Se não achar o e-mail, responde 200 para o PagBank não repetir a requisição
    if not email:
        print("AVISO: E-mail não encontrado no payload do webhook.")
        return {"status": "ignorado", "motivo": "email_nao_encontrado"}

    email = email.strip().lower()

    # Procura o assinante no Banco de Dados
    usuario = db.query(Assinante).filter(Assinante.email == email).first()
    if not usuario:
        print(f"ALUNO NÃO ENCONTRADO NO BANCO: {email}")
        return {"status": "ignorado", "motivo": "usuario_nao_encontrado", "email": email}

    # Salva ou atualiza o ID da assinatura do PagBank no cadastro do usuário
    if assinatura_id:
        usuario.assinatura_id = str(assinatura_id)

    # =====================================================
    # PROCESSAMENTO DE COBRANÇAS DE CARTÃO DE CRÉDITO
    # =====================================================
    
    # 🟢 SUCESSO COMPLETO (Nova assinatura ou renovação mensal aprovada)
    eventos_aprovados = ("subscription.activated", "subscription.recurrence", "subscription.initial")
    if evento in eventos_aprovados or status_assinatura == "ACTIVE":
        usuario.status = "ativo"
        usuario.status_pagamento = "active"
        
        # Mapeamento das datas de vigência
        usuario.ultimo_pagamento = resource.get("updated_at") or resource.get("created_at")
        usuario.proximo_pagamento = resource.get("next_invoice_at")
        
        db.commit()
        print(f"✅ CARTÃO APROVADO: Acesso liberado/mantido para {usuario.email}")
        return {"status": "sucesso", "acao": "liberado"}

    # 🟠 CARTÃO RECUSADO / FALTA DE LIMITE (Assinatura Suspensa)
    elif evento == "subscription.suspended" or status_assinatura == "SUSPENDED":
        usuario.status = "pendente"
        usuario.status_pagamento = "suspended"
        
        db.commit()
        print(f"⚠️ CARTÃO RECUSADO NA RENOVAÇÃO: Acesso bloqueado para {usuario.email}")
        return {"status": "sucesso", "acao": "suspenso_por_recusa"}

    # 🔴 ASSINATURA CANCELADA OU EXPIRADA (Cancelamento manual ou fim do contrato)
    elif evento in ("subscription.canceled", "subscription.expired") or status_assinatura in ("CANCELED", "EXPIRED"):
        usuario.status = "pendente"
        usuario.status_pagamento = "canceled"
        
        db.commit()
        print(f"🚫 ASSINATURA ENCERRADA: Acesso bloqueado para {usuario.email}")
        return {"status": "sucesso", "acao": "cancelado"}

    # Eventos informativos não monitorados (ex: plan.created)
    print(f"ℹ️ EVENTO IGNORADO/NÃO TRATADO: {evento}")
    return {"status": "sucesso", "motivo": "evento_nao_utilizado"}
