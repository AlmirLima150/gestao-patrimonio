from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select, func 
from database import create_db_and_tables, get_session
from models import Categoria, Patrimonio, TermoConcessao, coordenador, ItemTermo
from typing import Annotated, Optional
from fpdf import FPDF
from fastapi.responses import FileResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Ligando a API: Criando tabelas no Postgres...")
    create_db_and_tables()
    
    yield
    
    print("Desligando a API: Limpando conexões...")

app = FastAPI(title="Sistema de Gestão de Patrimônios",
    description="""
    API para controle de empréstimo de patrimônios e geração de termos de concessão.
    
    Funcionalidades
    * Inventário: Cadastro e controle de estoque de patrimônios.
    * Termos: Emissão de termos de concessão para coordenadores.
    * Exportação: Geração de PDF para assinatura física.
    """,
    version="1.0.0",
    contact={
        "name": "Almir",
        "url": "https://github.com/AlmirLima150",
    },
    lifespan=lifespan)

SessionDep = Annotated[Session, Depends(get_session)]

## ROTAS DE CATEGORIA, QUE REPRESENTA AS CATEGORIAS DOS PATRIMÔNIOS E REALIZA O CONTROLE DE ESTOQUE DOS PATRIMÔNIOS CONCEDIDOS

@app.post("/categorias/", tags=["Gestão de Categorias"], response_model=Categoria)
def create_categoria(categoria: Categoria, session: SessionDep):
    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria

@app.get("/categorias/", tags=["Gestão de Categorias"], response_model=list[Categoria])
def listar_categorias(session: SessionDep):
    categorias = session.exec(select(Categoria)).all()
    return categorias

@app.delete(
    "/categorias/{categoria_id}",
    tags=["Gestão de Categorias"], 
    response_model=dict,
    responses={
        404: {
            "description": "Categoria não encontrada",
            "content": {
                "application/json": {
                    "example": {"detail": "Categoria não encontrada"}
                }
            }
        }
    }
)
def deletar_categoria(categoria_id: int, session: SessionDep):
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    session.delete(categoria)
    session.commit()
    return {"detail": "Categoria deletada com sucesso"}

@app.patch("/categorias/{categoria_id}", 
           tags=["Gestão de Categorias"],
           response_model=Categoria,
           responses={404: {"description": "Categoria não encontrada"} }
)
def atualizar_categoria(categoria_id: int, categoria_data: Categoria, session: SessionDep):
    db_categoria = session.get(Categoria, categoria_id)
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    dados_para_atualizar = categoria_data.model_dump(exclude_unset=True)
    
    for key, value in dados_para_atualizar.items():
        setattr(db_categoria, key, value)

    session.add(db_categoria)
    session.commit()
    session.refresh(db_categoria)
    return db_categoria

## ROTAS DE PATRIMONIO, QUE REPRESENTA OS BENS PATRIMONIAIS QUE SERÃO CONCEDIDOS ATRAVÉS DO TERMO DE CONCESSAO E REALIZA O CONTROLE DE ESTOQUE DOS PATRIMÔNIOS CONCEDIDOS

@app.post("/patrimonios/", tags=["Inventário e Patrimônio"], response_model=Patrimonio)
def create_patrimonio(patrimonio: Patrimonio, session: SessionDep):
    session.add(patrimonio)
    session.commit()
    session.refresh(patrimonio)
    return patrimonio

@app.get("/patrimonios/", tags=["Inventário e Patrimônio"], response_model=list[Patrimonio])
def listar_patrimonios(session: SessionDep):
    patrimonios = session.exec(select(Patrimonio)).all()
    return patrimonios

@app.delete(
    "/patrimonios/{patrimonio_id}",
    tags=["Inventário e Patrimônio"],
    response_model=dict,
    responses={
        404: {
            "description": "Patrimonio não encontrado",
            "content": {
                "application/json": {
                    "example": {"detail": "Patrimonio não encontrado"}
                }
            }
        }
    }
)
def deletar_patrimonio(patrimonio_id: int, session: SessionDep):
    patrimonio = session.get(Patrimonio, patrimonio_id)
    if not patrimonio:
        raise HTTPException(status_code=404)
    session.delete(patrimonio)
    session.commit()
    return {"detail": "Patrimonio deletado com sucesso"}

@app.patch("/patrimonios/{patrimonio_id}",
           tags=["Inventário e Patrimônio"],
           response_model=Patrimonio,
           responses={404: {"description": "Patrimônio ou Categoria não encontrados"} }
)
def atualizar_patrimonio(patrimonio_id: int, patrimonio_data: Patrimonio, session: SessionDep):
    db_patrimonio = session.get(Patrimonio, patrimonio_id)
    if not db_patrimonio:
        raise HTTPException(status_code=404, detail="Patrimonio não encontrado")
    
    dados_para_atualizar = patrimonio_data.model_dump(exclude_unset=True)

    if "categoria_id" in dados_para_atualizar and dados_para_atualizar["categoria_id"] is not None:
        nova_categoria = session.get(Categoria, dados_para_atualizar["categoria_id"])
        if not nova_categoria:
            raise HTTPException(status_code=404, detail="Categoria informada não existe")
    
    for key, value in dados_para_atualizar.items():
        setattr(db_patrimonio, key, value)
    
    session.add(db_patrimonio)
    session.commit()
    session.refresh(db_patrimonio)
    return db_patrimonio

## ROTAS DE COORDENADOR, QUE REPRESENTA O USUÁRIO QUE REALIZA O EMPRÉSTIMO DOS PATRIMÔNIOS ATRAVÉS DO TERMO DE CONCESSAO, E REALIZA O CONTROLE DE ESTOQUE DOS PATRIMÔNIOS CONCEDIDOS 

@app.get("/coordenadores/", tags=["Gestão de Coordenadores"], response_model=list[coordenador])
def listar_coordenadores(session: SessionDep):
    coordenadores = session.exec(select(coordenador)).all()
    return coordenadores

@app.post("/coordenadores/", tags=["Gestão de Coordenadores"], response_model=coordenador)
def create_coordenador(coordenador_data: coordenador, session: SessionDep):
    session.add(coordenador_data)
    session.commit()
    session.refresh(coordenador_data)
    return coordenador_data

@app.delete(
    "/coordenadores/{coordenador_id}",
    tags=["Gestão de Coordenadores"],   
    response_model=dict,
    responses={
        404: {
            "description": "Coordenador não encontrado",
            "content": {
                "application/json": {
                    "example": {"detail": "Coordenador não encontrado"}
                }
            }
        }
    }
)
def deletar_coordenador(coordenador_id: int, session: SessionDep):
    db_coordenador = session.get(coordenador, coordenador_id)
    if not db_coordenador:
        raise HTTPException(status_code=404, detail="Coordenador não encontrado")
    session.delete(db_coordenador)
    session.commit()
    return {"detail": "Coordenador deletado com sucesso"}

@app.patch("/coordenadores/{coordenador_id}", 
            tags=["Gestão de Coordenadores"],
            response_model=coordenador,
            responses={404: {"description": "Coordenador não encontrado"} })
def atualizar_coordenador(coordenador_id: int, coordenador_data: coordenador, session: SessionDep):
    db_coordenador = session.get(coordenador, coordenador_id)
    if not db_coordenador:
        raise HTTPException(status_code=404, detail="Coordenador não encontrado")
    
    dados_para_atualizar = coordenador_data.model_dump(exclude_unset=True)
    
    for key, value in dados_para_atualizar.items():
        setattr(db_coordenador, key, value)
    
    session.add(db_coordenador)
    session.commit()
    session.refresh(db_coordenador)
    return db_coordenador

## ROTAS DE TERMO DE CONCESSAO, QUE REPRESENTA O EMPRÉSTIMO DOS PATRIMÔNIOS E REALIZA O CONTROLE DE ESTOQUE DOS PATRIMÔNIOS CONCEDIDOS

@app.post("/termos_concessao/",
          tags=["Gestão de Termos"], 
          response_model=None,
          responses={
              404: {
                  "description": "Coordenador ou Patrimonio não encontrado",
                  "content": {
                      "application/json": {
                          "example": {"detail": "Coordenador ou Patrimonio não encontrado"}
                      }
                  }
              },
                400: {
                    "description": "Estoque insuficiente para um ou mais patrimônios",
                    "content": {
                        "application/json": {
                            "example": {"detail": "Estoque insuficiente para um ou mais patrimônios"}
                        }
                    }
                }
          })
def create_termo_concessao(termo_data: TermoConcessao, session: SessionDep):
    # 1. Validação do Coordenador
    # Use o nome exato da sua classe (coordenador ou Coordenador)
    db_coordenador = session.get(coordenador, termo_data.coordenador_id)
    if not db_coordenador:
        raise HTTPException(status_code=404, detail="Coordenador não encontrado")
    
    # 2. Criação do Termo (Garantindo que itens venha vazio)
    # Ignoramos qualquer 'itens' que venha no JSON de entrada para evitar o erro 500
    novo_termo = TermoConcessao(
        coordenador_id=termo_data.coordenador_id,
        data_concessao=termo_data.data_concessao,
        status="ATIVO",
        data_devolucao=None # Garantimos que comece nulo
    )
    
    try:
        session.add(novo_termo)
        session.commit()
        session.refresh(novo_termo)
        return novo_termo
    except Exception as e:
        session.rollback()
        # Se der erro aqui, é a restrição NOT NULL da data_devolucao no banco
        raise HTTPException(status_code=400, detail=f"Erro de integridade: {str(e)}")
    
@app.get("/termos_concessao/", tags=["Gestão de Termos"], response_model=list[TermoConcessao])
def listar_termos(session: SessionDep, status: Optional[str] = None):
    statement = select(TermoConcessao)
    
    if status:
        statement = statement.where(TermoConcessao.status == status)
        
    termos = session.exec(statement).all()
    return termos

@app.delete("/termos_concessao/{termo_id}", 
            tags=["Gestão de Termos"],
            response_model=None,
            responses={404: {"description": "Termo de Concessão não encontrado"}}
)
def delete_termo(termo_id: int, session: SessionDep):
    termo = session.get(TermoConcessao, termo_id)
    if not termo:
        raise HTTPException(status_code=404, detail="Termo de Concessão não encontrado")
    session.delete(termo)
    session.commit()
    return {"detail": "Termo de Concessão deletado com sucesso"}

@app.patch("/item_termo/{item_id}/devolucao", 
           tags=["Gestão de Termos"],
           response_model=ItemTermo,
           responses={
               404: {
                   "description": "Registro de item ou patrimônio associado não encontrado",
                   "content": {
                       "application/json": {
                           "example": {"detail": "Registro de item ou patrimônio associado não encontrado"}
                       }
                   }
               },
               400: {
                   "description": "Quantidade devolvida excede a quantidade concedida",
                   "content": {
                       "application/json": {
                           "example": {"detail": "Quantidade devolvida excede a quantidade concedida"}
                       }
                   }
               }
           })
def devolver_item(item_id: int, quantidade_devolvida_agora: int, session: SessionDep):

    item_db = session.get(ItemTermo, item_id)
    if not item_db:
        raise HTTPException(status_code=404, detail="Registro de item não encontrado")
    
    patrimonio = session.get(Patrimonio, item_db.patrimonio_id)
    if not patrimonio:
        raise HTTPException(status_code=404, detail="Patrimonio associado ao item não encontrado")
    
    total_apos_devolucao = item_db.quantidade_devolvida + quantidade_devolvida_agora
    if total_apos_devolucao > item_db.quantidade_concedida:
        raise HTTPException(
            status_code=400, 
            detail=f"Quantidade excede o total concedido ({item_db.quantidade_concedida})"
        )

    item_db.quantidade_devolvida = total_apos_devolucao
    patrimonio.quantidade_disponivel += quantidade_devolvida_agora

    session.add(item_db)
    session.add(patrimonio)

    termo = session.get(TermoConcessao, item_db.termo_concessao_id)

    statement = select(ItemTermo).where(ItemTermo.termo_concessao_id == termo.id)
    todos_itens = session.exec(statement).all()

    totalmente_devolvido = all(i.quantidade_concedida == i.quantidade_devolvida for i in todos_itens)

    if totalmente_devolvido:
        termo.status = "DEVOLVIDO"
        termo.data_devolucao = func.now()  
        session.add(termo)

    session.commit()
    session.refresh(item_db)
    return item_db

## ROTAS DE ITEM DE TERMO, QUE REPRESENTA OS ITENS CONCEDIDOS EM CADA TERMO DE CONCESSAO E REALIZA O CONTROLE DE ESTOQUE DOS PATRIMONIOS

@app.post("/item_termo/", 
          response_model=ItemTermo,
            tags=["Gestão de Termos"],
          responses={
              404: {
                  "description": "Termo de Concessão ou Patrimonio não encontrado",
                  "content": {
                      "application/json": {
                          "example": {"detail": "Termo de Concessão ou Patrimonio não encontrado"}
                      }
                  }
              },
              400: {
                  "description": "Quantidade concedida excede a quantidade disponível do patrimônio",
                  "content": {
                      "application/json": {
                          "example": {"detail": "Quantidade concedida excede a quantidade disponível do patrimônio"}
                      }
                  }
              },
              500: {
                  "description": "Erro ao processar o item de concessão",
                  "content": {
                      "application/json": {
                          "example": {"detail": "Erro ao processar o item de concessão: [detalhes do erro]"}
                      }
                  }
              }
          })
def create_item_termo(item_data: ItemTermo, session: SessionDep):
    termo_concessao = session.get(TermoConcessao, item_data.termo_concessao_id)
    if not termo_concessao:
        raise HTTPException(status_code=404, detail="Termo de Concessão não encontrado")
    
    patrimonio = session.get(Patrimonio, item_data.patrimonio_id)
    if not patrimonio:
        raise HTTPException(status_code=404, detail="Patrimonio não encontrado")
    
    item_data.quantidade_devolvida = 0
    
    if item_data.quantidade_concedida > patrimonio.quantidade_disponivel:
        raise HTTPException(status_code=400, detail=f"Estoque insuficiente. Disponível: {patrimonio.quantidade_disponivel}")
    
    patrimonio.quantidade_disponivel -= item_data.quantidade_concedida

    session.add(patrimonio)
    session.add(item_data)
    try:
        session.commit()
        session.refresh(item_data)
        return item_data
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao processar item: {str(e)}")

@app.get("/termos/{termo_id}/detalhes", 
         response_model=None,
        tags=["Gestão de Termos"],
         responses={
             404: {
                 "description": "Termo de Concessão não encontrado",
                 "content": {
                     "application/json": {
                         "example": {"detail": "Termo de Concessão não encontrado"}
                     }
                 }
             }
         })
def obter_termo_completo(termo_id: int, session: SessionDep):

    termo = session.get(TermoConcessao, termo_id)
    if not termo:
        raise HTTPException(status_code=404, detail="Termo não encontrado")
    
    return {
        "id": termo.id,
        "data_concessao": termo.data_concessao,
        "data_devolucao": termo.data_devolucao,
        "status": termo.status,
        "coordenador": termo.coordenador.nome,
        "itens": [
            {
                "patrimonio": item.patrimonio.nome,
                "quantidade_concedida": item.quantidade_concedida,
                "quantidade_devolvida": item.quantidade_devolvida
            } for item in termo.itens
        ]
    }

## LOGICA PARA CRIAR O PDF DO TERMO DE CONCESSAO, QUE REPRESENTA O DOCUMENTO GERADO PARA REGISTRAR O EMPRÉSTIMO DOS PATRIMÔNIOS

@app.get("/termos/{termo_id}/pdf",
         tags=["Documentos e Exportação"], 
         response_model=None, 
         responses={
             404: {
                 "description": "Termo de Concessão não encontrado",
                 "content": {
                     "application/json": {
                         "example": {"detail": "Termo de Concessão não encontrado"}
                     }
                 }
             },
             500: {
                 "description": "Erro ao gerar PDF",
                 "content": {
                     "application/json": {
                         "example": {"detail": "Erro ao gerar PDF: [detalhes do erro]"}
                     }
                 }
             }
         })
def gerar_pdf_termo(termo_id: int, session: SessionDep):

    termo = session.get(TermoConcessao, termo_id)
    if not termo:
        raise HTTPException(status_code=404, detail="Termo não encontrado")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    
    pdf.cell(0, 10, "TERMO DE CONCESSÃO DE EQUIPAMENTOS", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, f"Termo Nº: {termo.id}", ln=True)
    pdf.cell(0, 10, f"Coordenador Responsável: {termo.coordenador.nome}", ln=True)
    pdf.cell(0, 10, f"Data de Emissão: {termo.data_concessao.strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.cell(0, 10, f"Status Atual: {termo.status}", ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(100, 10, "Patrimônio/Equipamento", border=1, align="C")
    pdf.cell(40, 10, "Qtd Concedida", border=1, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 12)
    for item in termo.itens:
        pdf.cell(100, 10, f" {item.patrimonio.nome}", border=1)
        pdf.cell(40, 10, f" {item.quantidade_concedida}", border=1, align="C")
        pdf.ln()

    pdf.ln(20)
    pdf.cell(0, 10, "________________________________________________", ln=True, align="C")
    pdf.cell(0, 10, f"Assinatura: {termo.coordenador.nome}", ln=True, align="C")

    nome_arquivo = f"termo_{termo.id}.pdf"
    caminho_arquivo = f"/tmp/{nome_arquivo}" 
    pdf.output(caminho_arquivo)

    return FileResponse(
        path=caminho_arquivo, 
        filename=nome_arquivo, 
        media_type="application/pdf"
    )