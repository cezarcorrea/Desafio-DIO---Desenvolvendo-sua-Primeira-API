from uuid import uuid4
from fastapi import APIRouter, Body, Depends, status, HTTPException
from fastapi_pagination import LimitOffsetPage, paginate, LimitOffsetParams 
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import UUID4

from workout_api.atleta.models import AtletaModel
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from workout_api.centro_treinamento.schemas import CentroTreinamentoIn, CentroTreinamentoOut, CentroTreinamentoUpdate
from workout_api.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


router = APIRouter()

#Cria os centros de treinamento no banco
@router.post(
    "/",
    summary="Criar um novo Centro de Treinamento",
    status_code=status.HTTP_201_CREATED,
    response_model=CentroTreinamentoOut,
)
async def post(
    db_session: DatabaseDependency, centro_treinamento_in: CentroTreinamentoIn = Body(...)
) -> CentroTreinamentoOut:
    try:
        centro_treinamento_id = uuid4()
        centro_treinamento_model = CentroTreinamentoModel(id=centro_treinamento_id, **centro_treinamento_in.model_dump())

        db_session.add(centro_treinamento_model)
        await db_session.commit()
        await db_session.refresh(
            centro_treinamento_model
        )  # Atualiza para obter valores padrão gerados pelo DB (ex: created_at)

        return CentroTreinamentoOut.model_validate(centro_treinamento_model)
    except Exception as e:
        # Tratamento de erro genérico para problemas inesperados durante a criação
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro ao inserir os dados no banco: {e}",
        )

#Realiza consulta geral no banco
@router.get(
    "/",
    summary="Consultar todos os Centros de Treinamento",
    status_code=status.HTTP_200_OK,
    response_model=LimitOffsetPage[CentroTreinamentoOut],
)
async def query_all_categories(db_session: DatabaseDependency, params: LimitOffsetParams = Depends()
) -> LimitOffsetPage[CentroTreinamentoOut]:
    query = select(CentroTreinamentoModel)

    return await paginate(db_session, query, params)
    
#Consulta centro de treinamento pelo ID
@router.get(
    "/{id}",
    summary="Consultar Centro de Treinamento por ID",
    status_code=status.HTTP_200_OK,
    response_model=CentroTreinamentoOut,
)
async def get_category_by_id(id: UUID4, db_session: DatabaseDependency) -> CentroTreinamentoOut:

    centro_treinamento: CentroTreinamentoModel | None = (
        (await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Centro de Treinamento não encontrado no id: {id}",
        )

    return CentroTreinamentoOut.model_validate(
        centro_treinamento
    )  

#Edita centros de treinamento por ID
@router.patch(
    "/{id}",
    summary="Editar o Centro de Treinamento pelo ID",
    status_code=status.HTTP_200_OK,
    response_model=CentroTreinamentoOut,
)
async def patch_centro_treinamento_by_id(
    id: UUID4, db_session: DatabaseDependency, centro_treinamento_up: CentroTreinamentoUpdate = Body(...)
) -> CentroTreinamentoOut:

    centro_treinamento: CentroTreinamentoModel | None = (
        await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))
    ).scalars().first()

    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Centro de treinamento não encontrado no id: {id}",
        )

    
    # Prepara os dados para atualização

    update_data = centro_treinamento_up.model_dump(exclude_unset=True)
    
    # Atualiza os campos do objeto SQLAlchemy
    for key, value in update_data.items():
        setattr(centro_treinamento, key, value)
    
    try:
        await db_session.commit()
        await db_session.refresh(centro_treinamento) # Atualiza o objeto com os dados do DB

        
        return CentroTreinamentoOut.model_validate(centro_treinamento) 
    except IntegrityError as e:
       
        if "centros_treinamento_nome_key" in str(e.orig): 
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe um centro de treinamento com o nome '{centro_treinamento_up.nome}'."
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Erro de integridade ao atualizar centro de treinamento: {e.orig}"
        )
    except SQLAlchemyError as e:
        # Captura outros erros do SQLAlchemy (conexão, etc.)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no banco de dados ao atualizar o centro de treinamento: {e}"
        )
    except Exception as e:
        # Captura qualquer outra exceção inesperada
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro inesperado ao atualizar o centro de treinamento: {e}"
        )

#Deleta centro de treinamento
@router.delete(
    "/{id}", 
    summary="Deletar um Centro de Treinamento pelo ID", 
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_centro_treinamento_by_id(id: UUID4, db_session: DatabaseDependency) -> None:
    # 1. Busca o centro de treinamento pelo ID
    centro_treinamento: CentroTreinamentoModel | None = (
        await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))
    ).scalars().first()

    # Verifica se o centro de treinamento existe
    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Centro de treinamento não encontrado no id: {id}",
        )

    # 2. Verifica se existem atletas vinculados a este centro de treinamento
    atletas_vinculados = (
        await db_session.execute(
            select(AtletaModel).filter_by(centro_treinamento_id=centro_treinamento.pk_id) 
        )
    ).scalars().all()

    # 3. Se houver atletas vinculados, retorna um erro 409 Conflict
    if atletas_vinculados:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Não é possível deletar o centro de treinamento '{centro_treinamento.nome}' "
                   f"pois existem {len(atletas_vinculados)} atleta(s) vinculado(s) a ele. "
                   "Por favor, mova todos os atletas para outro centro de treinamento antes de tentar deletar este."
        )

    # 4. Se não houver atletas, procede com a deleção
    try:
        await db_session.delete(centro_treinamento)
        await db_session.commit()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no banco de dados ao deletar o centro de treinamento: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro inesperado ao deletar o centro de treinamento: {e}"
        )