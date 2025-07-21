from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi_pagination import LimitOffsetPage, paginate, LimitOffsetParams 
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import UUID4
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError # Importa IntegrityError para tratamento de erros específico

from workout_api.centro_treinamento.models import CentroTreinamentoModel
from workout_api.categorias.models import CategoriaModel
from workout_api.atleta.models import AtletaModel
from workout_api.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdate 
from workout_api.contrib.dependencies import DatabaseDependency


router = APIRouter()

#Cria dados de novos atletas
@router.post(
    "/",
    summary="Criar novo Atleta",
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut,
)
async def post(db_session: DatabaseDependency, atleta_in: AtletaIn = Body(...)) -> AtletaOut:
    # 1. Obtenha os nomes da categoria e centro de treinamento da entrada
    categoria_nome = atleta_in.categoria.nome
    centro_treinamento_nome = atleta_in.centro_treinamento.nome

    # 2. Busque a categoria pelo nome
    categoria = (
        await db_session.execute(
            select(CategoriaModel).filter_by(nome=categoria_nome)
        )
    ).scalars().first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A categoria '{categoria_nome}' não foi encontrada.",
        )

    # 3. Busque o centro de treinamento pelo nome
    centro_treinamento = (
        await db_session.execute(
            select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_nome)
        )
    ).scalars().first()

    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"O centro de treinamento '{centro_treinamento_nome}' não foi encontrado.",
        )
    
    # 4. Verifique se o CPF já existe
    atleta_existente = (
        await db_session.execute(
            select(AtletaModel).filter_by(cpf=atleta_in.cpf)
        )
    ).scalars().first()

    if atleta_existente:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, # Ou HTTP_409_CONFLICT
            detail=f"Já existe um atleta cadastrado com o CPF: {atleta_in.cpf}"
        )

    try:
        # 5. Crie a instância do modelo Atleta
        atleta_model = AtletaModel(
            id=uuid4(),
            created_at=datetime.now(),
            # Exclui os objetos aninhados do dump
            **atleta_in.model_dump(exclude={"categoria", "centro_treinamento"})
        )
        
        # Atribui os IDs das chaves estrangeiras (pk_id do SQLAlchemy)
        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro_treinamento.pk_id

        db_session.add(atleta_model)
        await db_session.commit()
        await db_session.refresh(atleta_model) # REFRESH: Garante que o modelo tem os dados mais recentes do DB

        # 6. Retorne o AtletaOut validando a instância do modelo, que agora tem todos os dados
        return AtletaOut.model_validate(atleta_model)

    except IntegrityError: # Captura erros de integridade (como CPF único)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=f"Já existe um atleta cadastrado com o CPF: {atleta_in.cpf}"
        )
    except Exception as e: # Captura outros erros inesperados
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro interno inesperado ao criar o atleta: {e}",
        )

#Consulta Geral do Banco de dados
@router.get(
    "/",
    summary="Consultar todos os Atletas",
    status_code=status.HTTP_200_OK,
    response_model=LimitOffsetPage[AtletaOut],
)
async def query_all_atletas(db_session: DatabaseDependency, params: LimitOffsetParams = Depends()
) -> LimitOffsetPage[AtletaOut]:
    query = select(AtletaModel)

    return await paginate(db_session, query, params)

#Consulta Atleta, retorna Erro se não encontrado
@router.get(
    "/{id}",
    summary="Consultar Atleta pelo ID",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def get_atleta_by_id(id: UUID4, db_session: DatabaseDependency) -> AtletaOut:
    atleta: AtletaModel | None = ( 
        await db_session.execute(select(AtletaModel).filter_by(id=id))
    ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado no id: {id}",
        )

    
    return AtletaOut.model_validate(atleta)

#Atualiza dados existentes no Banco, E retorna erro caso não encontrado
@router.patch(
    "/{id}",
    summary="Editar um Atleta pelo ID",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def patch_atleta_by_id( 
    id: UUID4, db_session: DatabaseDependency, atleta_up: AtletaUpdate = Body(...)
) -> AtletaOut:

    atleta: AtletaModel | None = ( 
        await db_session.execute(select(AtletaModel).filter_by(id=id))
    ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado no id: {id}",
        )

    update_data = atleta_up.model_dump(exclude_unset=True) 
    
    # Lida com a atualização de categoria
    if "categoria" in update_data:
        categoria_data = update_data.pop("categoria")
        categoria_nome = categoria_data.get("nome") 
        
        # Verifica se o nome foi realmente fornecido dentro do objeto categoria
        if not categoria_nome:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome da categoria não fornecido para alteração."
            )
        
        #Verifica se a categoria existe, se não retorna o Erro
        categoria = (
            await db_session.execute(
                select(CategoriaModel).filter_by(nome=categoria_nome)
            )
        ).scalars().first()
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A nova categoria '{categoria_nome}' não foi encontrada.",
            )
        atleta.categoria_id = categoria.pk_id # Atualiza a chave estrangeira
    
    # Lida com a atualização de centro_treinamento
    if "centro_treinamento" in update_data:
        centro_treinamento_data = update_data.pop("centro_treinamento")
        centro_treinamento_nome = centro_treinamento_data.get("nome")
        
        #Boloco de validação de Erro
        if not centro_treinamento_nome:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome do centro de treinamento não fornecido para alteração."
            )

        centro_treinamento = (
            await db_session.execute(
                select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_nome)
            )
        ).scalars().first()
        if not centro_treinamento:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"O novo centro de treinamento '{centro_treinamento_nome}' não foi encontrado.",
            )
        atleta.centro_treinamento_id = centro_treinamento.pk_id # Atualiza a chave estrangeira

    # Atualiza os campos primitivos restantes
    for key, value in update_data.items(): 
        setattr(atleta, key, value)
    
    #Bloco de validação de Erro
    try:
        await db_session.commit()
        await db_session.refresh(atleta) 

        return AtletaOut.model_validate(atleta)
    except IntegrityError as e:
         raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=f"Já existe um atleta cadastrado com o CPF informado." 
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro inesperado ao editar o atleta: {e}",
        )

#Deleta atleta do banco pleo ID Informado
@router.delete(
    "/{id}", summary="Deletar um Atleta pelo ID", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_atleta_by_id(id: UUID4, db_session: DatabaseDependency) -> None: 
    atleta: AtletaModel | None = ( 
        await db_session.execute(select(AtletaModel).filter_by(id=id))
    ).scalars().first()
    
    #Retorna erro se não for encontrado atleta Com ID informado
    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado no id: {id}",
        )

    await db_session.delete(atleta)
    await db_session.commit()