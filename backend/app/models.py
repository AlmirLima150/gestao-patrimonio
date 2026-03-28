from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=100)

    patrimonios: list["Patrimonio"] = Relationship(back_populates="categoria")

class Patrimonio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=100)
    descricao: str = Field(max_length=255)
    quantidade_total: int = Field(default=0)
    quantidade_disponivel: int = Field(default=0)
    item_unico: bool = Field(default=False)

    categoria_id: Optional[int] = Field(default=None,foreign_key="categoria.id")
    categoria: Optional[Categoria] = Relationship(back_populates="patrimonios")
    itens_termo: list["ItemTermo"] = Relationship(back_populates="patrimonio")

class TermoConcessao(SQLModel, table=True):  
    __tablename__ = "termo_concessao"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    coordenador_id: int = Field(foreign_key="coordenador.id", nullable=False)
    
    data_concessao: datetime = Field(default_factory=datetime.now)
    data_devolucao: Optional[datetime] = Field(default=None, sa_column_kwargs={"nullable": True})    
    status: str = Field(default="ATIVO", max_length=20)

    itens: list["ItemTermo"] = Relationship(back_populates="termo_concessao")
    coordenador: "coordenador" = Relationship(back_populates="termos_concessao")

class coordenador(SQLModel, table=True):
    __tablename__ = "coordenador"
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=100)
    email: str = Field(max_length=100)

    termos_concessao: list[TermoConcessao] = Relationship(back_populates="coordenador")

class ItemTermo(SQLModel, table=True):
    __tablename__ = "item_termo"
    id: Optional[int] = Field(default=None, primary_key=True)
    termo_concessao_id: int = Field(foreign_key="termo_concessao.id")
    patrimonio_id: int = Field(foreign_key="patrimonio.id")
    quantidade_concedida: int = Field(default=0)
    quantidade_devolvida: int = Field(default=0)

    termo_concessao: TermoConcessao = Relationship(back_populates="itens")
    patrimonio: Patrimonio = Relationship(back_populates="itens_termo")

