from uuid import uuid4
from fastapi import APIRouter, Body, Depends, status, HTTPException
from fastapi_pagination import LimitOffsetPage, paginate, LimitOffsetParams 
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import UUID4

from workout_api.atleta.models import AtletaModel
from workout_api.categorias.models import CategoriaModel
from workout_api.categorias.schemas import CategoriaIn, CategoriaOut, CategoriaUpdate
from workout_api.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError


router = APIRouter()

#Cria nova categoria no banco de dados
@router.post(
    "/",
    summary="Criar uma nova Categoria",
    status_code=status.HTTP_201_CREATED,
    response_model=CategoriaOut,
)
async def post(
    db_session: DatabaseDependency, categoria_in: CategoriaIn = Body(...)
) -> CategoriaOut:
    try:
        categoria_id = uuid4()
        categoria_model = CategoriaModel(id=categoria_id, **categoria_in.model_dump())

        db_session.add(categoria_model)
        await db_session.commit()
        await db_session.refresh(
            categoria_model
        )  # Atualiza para obter valores padrão gerados pelo DB (ex: created_at)

        return CategoriaOut.model_validate(categoria_model)
    except Exception as e:
        # Tratamento de erro genérico 
        #  para problemas inesperados durante a criação
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro ao inserir os dados no banco: {e}",
        )

#Aplica consulta no banco de dados para as categorias
@router.get(
    "/",
    summary="Consultar todas as Categorias",
    status_code=status.HTTP_200_OK,
    response_model=LimitOffsetPage[CategoriaOut],
)
async def query_all_categories(db_session: DatabaseDependency, params: LimitOffsetParams = Depends()
) -> LimitOffsetPage[CategoriaOut]:
    query = select(CategoriaModel)

    return await paginate(db_session, query, params)

#realiza consulta especifica pelo ID
@router.get(
    "/{id}",
    summary="Consultar Categoria por ID",
    status_code=status.HTTP_200_OK,
    response_model=CategoriaOut,
)
async def get_category_by_id(id: UUID4, db_session: DatabaseDependency) -> CategoriaOut:

    categoria: CategoriaModel | None = (
        (await db_session.execute(select(CategoriaModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria não encontrada no id: {id}",
        )

    return CategoriaOut.model_validate(categoria) 

#Realiza edição de uma categoria pelo ID
@router.patch(
    "/{id}",
    summary="Editar uma Categoria pelo ID",
    status_code=status.HTTP_200_OK,
    response_model=CategoriaOut,
)
async def patch_categoria_by_id(
    id: UUID4, db_session: DatabaseDependency, categoria_up: CategoriaUpdate = Body(...)
) -> CategoriaOut:

    categoria: CategoriaModel | None = (
        await db_session.execute(select(CategoriaModel).filter_by(id=id))
    ).scalars().first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria não encontrado no id: {id}",
        )

    
    categoria_update_data = categoria_up.model_dump(exclude_unset=True)
    for key, value in categoria_update_data.items():
        
        if key == "categoria" and isinstance(value, dict) and "nome" in value:
            
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Alteração de categoria por nome não implementada diretamente aqui.")
        
        else:
            setattr(categoria, key, value)

    await db_session.commit()
    await db_session.refresh(categoria)

    return CategoriaOut.model_validate(categoria)

#Deleta categorias por ID
@router.delete(
    "/{id}", 
    summary="Deletar uma Categoria pelo ID", 
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_categoria_by_id(id: UUID4, db_session: DatabaseDependency) -> None:
    # 1. Busca a categoria pelo ID
    categoria: CategoriaModel | None = (
        await db_session.execute(select(CategoriaModel).filter_by(id=id))
    ).scalars().first()

    # Verifica se a categoria existe
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria não encontrada no id: {id}",
        )

    # 2. Verifica se existem atletas vinculados a esta categoria
    atletas_vinculados = (
        await db_session.execute(
            select(AtletaModel).filter_by(categoria_id=categoria.pk_id) # Usamos pk_id da categoria para a consulta
        )
    ).scalars().all()

    # 3. Se houver atletas vinculados, retorna um erro 409 Conflict
    if atletas_vinculados:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Não é possível deletar a categoria '{categoria.nome}' "
                   f"pois existem {len(atletas_vinculados)} atleta(s) vinculado(s) a ela. "
                   "Por favor, mova todos os atletas para outra categoria antes de tentar deletar esta."
        )

    # 4. Se não houver atletas, procede com a deleção
    try:
        await db_session.delete(categoria)
        await db_session.commit()
    except SQLAlchemyError as e:
        # Captura erros relacionados ao SQLAlchemy (ex: problemas de conexão, deadlock)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no banco de dados ao deletar a categoria: {e}"
        )
    except Exception as e:
        # Captura qualquer outra exceção inesperada
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro inesperado ao deletar a categoria: {e}"
        )