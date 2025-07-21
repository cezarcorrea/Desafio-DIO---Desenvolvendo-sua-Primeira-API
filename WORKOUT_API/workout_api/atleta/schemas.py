from typing import Annotated, Optional 
from pydantic import BaseModel, Field, PositiveFloat, UUID4 
from datetime import datetime 


from workout_api.categorias.schemas import CategoriaIn as CategoriaAtleta 
from workout_api.centro_treinamento.schemas import CentroTreinamentoAtleta 

from workout_api.contrib.schemas import BaseSchema, OutMixin 

# --- Schema Base para Atleta (Usado para definir a estrutura principal) ---
class Atleta(BaseSchema):
    cpf: Annotated[str, Field(description='CPF do atleta', example='12345678900', max_length=11)]
    nome: Annotated[str, Field(description='Nome do atleta', example='Joao', max_length=50)]
    idade: Annotated[int, Field(description='Idade do atleta', example=25)]
    peso: Annotated[PositiveFloat, Field(description='Peso do atleta', example=75.5)]
    altura: Annotated[PositiveFloat, Field(description='Altura do atleta', example=1.70)]
    sexo: Annotated[str, Field(description='Sexo do atleta', example='M', max_length=1)]
    
    # Campos aninhados para Categoria e Centro de Treinamento
    categoria: Annotated[CategoriaAtleta, Field(description='Categoria do atleta')]
    centro_treinamento: Annotated[CentroTreinamentoAtleta, Field(description='Centro de treinamento do atleta')]

# --- Schema de Entrada (para requisições POST) ---
class AtletaIn(Atleta):
    pass

# --- Schema de Saída (para respostas GET, POST, PATCH) ---
class AtletaOut(AtletaIn, OutMixin):
    id: Annotated[UUID4, Field(description='Identificador do atleta')] 
    created_at: Annotated[datetime, Field(description='Data de criação do atleta')] 
    pass

# --- Schema de Atualização (para requisições PATCH) ---
class AtletaUpdate(BaseSchema):
    # Todos os campos são opcionais para permitir atualizações parciais
    nome: Annotated[Optional[str], Field(None, description='Nome do atleta', example='Joao', max_length=50)]
    idade: Annotated[Optional[int], Field(None, description='Idade do atleta', example=25)]
    peso: Annotated[Optional[PositiveFloat], Field(None, description='Peso do atleta', example=75.5)]
    altura: Annotated[Optional[PositiveFloat], Field(None, description='Altura do atleta', example=1.70)]
    sexo: Annotated[Optional[str], Field(None, description='Sexo do atleta', example='M', max_length=1)]
    
    # Campos para atualização de categoria e centro de treinamento (opcionais e aninhados)
    # Isso permite enviar APENAS a nova categoria ou centro de treinamento se desejar atualizá-los.
    categoria: Annotated[Optional[CategoriaAtleta], Field(None, description='Nova Categoria do atleta')]
    centro_treinamento: Annotated[Optional[CentroTreinamentoAtleta], Field(None, description='Novo Centro de treinamento do atleta')]