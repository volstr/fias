"""First

Revision ID: 011e038fb4ce
Revises: 
Create Date: 2022-07-10 21:39:59.938515

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '011e038fb4ce'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('apartment_type',
    sa.Column('update_date', sa.Date(), nullable=False, comment='Дата внесения (обновления) записи'),
    sa.Column('start_date', sa.Date(), nullable=False, comment='Начало действия записи'),
    sa.Column('end_date', sa.Date(), nullable=False, comment='Окончание действия записи'),
    sa.Column('is_active', sa.Boolean(), nullable=False, comment='Статус активности'),
    sa.Column('id', sa.Integer(), nullable=False, comment='id'),
    sa.Column('name', sa.String(length=250), nullable=False, comment='Полное наименование типа объекта'),
    sa.Column('short_name', sa.String(length=50), nullable=True, comment='Краткое наименование типа объекта'),
    sa.Column('description', sa.String(length=250), nullable=True, comment='Описание'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_apartment_type_name'), 'apartment_type', ['name'], unique=False)
    op.create_table('hierarchy_adm',
    sa.Column('update_date', sa.Date(), nullable=False, comment='Дата внесения (обновления) записи'),
    sa.Column('start_date', sa.Date(), nullable=False, comment='Начало действия записи'),
    sa.Column('end_date', sa.Date(), nullable=False, comment='Окончание действия записи'),
    sa.Column('is_active', sa.Boolean(), nullable=False, comment='Статус активности'),
    sa.Column('id', sa.BigInteger(), nullable=False, comment='id'),
    sa.Column('object_id', sa.BigInteger(), nullable=False, comment='Глобальный уникальный идентификатор адресного объекта {address_objects | houses | apartments -> object_id}'),
    sa.Column('parent_object_id', sa.BigInteger(), nullable=True, comment='Идентификатор родительского объекта {address_objects | houses | apartments -> object_id}'),
    sa.Column('region_code', sa.Integer(), nullable=True, comment='Код региона'),
    sa.Column('area_code', sa.Integer(), nullable=True, comment='Код района'),
    sa.Column('city_code', sa.Integer(), nullable=True, comment='Код города'),
    sa.Column('place_code', sa.Integer(), nullable=True, comment='Код населенного пункта'),
    sa.Column('plan_code', sa.Integer(), nullable=True, comment='Код ЭПС'),
    sa.Column('street_code', sa.Integer(), nullable=True, comment='Код улицы'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hierarchy_adm_object_id'), 'hierarchy_adm', ['object_id'], unique=False)
    op.create_index(op.f('ix_hierarchy_adm_parent_object_id'), 'hierarchy_adm', ['parent_object_id'], unique=False)
    op.create_table('hierarchy_mun',
    sa.Column('update_date', sa.Date(), nullable=False, comment='Дата внесения (обновления) записи'),
    sa.Column('start_date', sa.Date(), nullable=False, comment='Начало действия записи'),
    sa.Column('end_date', sa.Date(), nullable=False, comment='Окончание действия записи'),
    sa.Column('is_active', sa.Boolean(), nullable=False, comment='Статус активности'),
    sa.Column('id', sa.BigInteger(), nullable=False, comment='id'),
    sa.Column('object_id', sa.BigInteger(), nullable=False, comment='Глобальный уникальный идентификатор адресного объекта {address_objects | houses | apartments -> object_id}'),
    sa.Column('parent_object_id', sa.BigInteger(), nullable=True, comment='Идентификатор родительского объекта {address_objects | houses | apartments -> object_id}'),
    sa.Column('oktmo', sa.String(length=50), nullable=False, comment='Код ОКТМО'),
    sa.Column('path', sa.String(length=250), nullable=True, comment='Материализованный путь к объекту (полная иерархия)'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hierarchy_mun_object_id'), 'hierarchy_mun', ['object_id'], unique=False)
    op.create_index(op.f('ix_hierarchy_mun_parent_object_id'), 'hierarchy_mun', ['parent_object_id'], unique=False)
    op.create_table('house_types',
    sa.Column('update_date', sa.Date(), nullable=False, comment='Дата внесения (обновления) записи'),
    sa.Column('start_date', sa.Date(), nullable=False, comment='Начало действия записи'),
    sa.Column('end_date', sa.Date(), nullable=False, comment='Окончание действия записи'),
    sa.Column('is_active', sa.Boolean(), nullable=False, comment='Статус активности'),
    sa.Column('id', sa.Integer(), nullable=False, comment='id'),
    sa.Column('name', sa.String(length=250), nullable=False, comment='Полное наименование типа объекта'),
    sa.Column('short_name', sa.String(length=50), nullable=True, comment='Краткое наименование типа объекта'),
    sa.Column('description', sa.String(length=250), nullable=True, comment='Описание'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_house_types_name'), 'house_types', ['name'], unique=False)
    op.create_table('levels',
    sa.Column('update_date', sa.Date(), nullable=False, comment='Дата внесения (обновления) записи'),
    sa.Column('start_date', sa.Date(), nullable=False, comment='Начало действия записи'),
    sa.Column('end_date', sa.Date(), nullable=False, comment='Окончание действия записи'),
    sa.Column('is_active', sa.Boolean(), nullable=False, comment='Статус активности'),
    sa.Column('id', sa.Integer(), nullable=False, comment='id'),
    sa.Column('name', sa.String(length=250), nullable=False, comment='Наименование'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_levels_name'), 'levels', ['name'], unique=False)
    op.create_table('param_types',
    sa.Column('update_date', sa.Date(), nullable=False, comment='Дата внесения (обновления) записи'),
    sa.Column('start_date', sa.Date(), nullable=False, comment='Начало действия записи'),
    sa.Column('end_date', sa.Date(), nullable=False, comment='Окончание действия записи'),
    sa.Column('is_active', sa.Boolean(), nullable=False, comment='Статус активности'),
    sa.Column('id', sa.Integer(), nullable=False, comment='id'),
    sa.Column('name', sa.String(length=250), nullable=False, comment='Полное наименование типа объекта'),
    sa.Column('short_name', sa.String(length=50), nullable=True, comment='Краткое наименование типа объекта'),
    sa.Column('description', sa.String(length=250), nullable=True, comment='Описание'),
    sa.Column('code', sa.String(length=50), nullable=False, comment='Кодовое обозначение'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_param_types_name'), 'param_types', ['name'], unique=False)
    op.create_table('updates',
    sa.Column('id', sa.Integer(), nullable=False, comment='id'),
    sa.Column('update_date', sa.DateTime(), nullable=False, comment='Дата и время выполнения обновления'),
    sa.Column('state', sa.String(length=16), nullable=False, comment='Состояние обновления'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('address_object_params',
    sa.Column('id', sa.BigInteger(), nullable=False, comment='id'),
    sa.Column('object_id', sa.BigInteger(), nullable=False, comment='Глобальный уникальный идентификатор адресного объекта {address_objects}'),
    sa.Column('param_type_id', sa.Integer(), nullable=False),
    sa.Column('value', sa.String(length=128), nullable=False, comment='Значение параметра'),
    sa.Column('update_date', sa.Date(), nullable=False, comment='Дата внесения (обновления) записи'),
    sa.Column('start_date', sa.Date(), nullable=False, comment='Начало действия записи'),
    sa.Column('end_date', sa.Date(), nullable=False, comment='Окончание действия записи'),
    sa.ForeignKeyConstraint(['param_type_id'], ['param_types.id'], name='fk_address_object_params_param_types_id_param_type_id'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_address_object_params_object_id'), 'address_object_params', ['object_id'], unique=False)
    op.create_index(op.f('ix_address_object_params_value'), 'address_object_params', ['value'], unique=False)
    op.create_table('address_objects',
    sa.Column('update_date', sa.Date(), nullable=False, comment='Дата внесения (обновления) записи'),
    sa.Column('start_date', sa.Date(), nullable=False, comment='Начало действия записи'),
    sa.Column('end_date', sa.Date(), nullable=False, comment='Окончание действия записи'),
    sa.Column('is_active', sa.Boolean(), nullable=False, comment='Статус активности'),
    sa.Column('id', sa.BigInteger(), nullable=False, comment='id'),
    sa.Column('object_id', sa.BigInteger(), nullable=False, comment='Глобальный уникальный идентификатор адресного объекта'),
    sa.Column('object_guid', sa.String(length=36), nullable=False, comment='Глобальный уникальный идентификатор адресного объекта. Соответствует коду ФИАС'),
    sa.Column('name', sa.String(length=250), nullable=False, comment='Наименование'),
    sa.Column('type_name', sa.String(length=50), nullable=False, comment='Краткое наименование типа объекта'),
    sa.Column('level_id', sa.Integer(), nullable=False),
    sa.Column('is_actual', sa.Boolean(), nullable=False, comment='Статус актуальности адресного объекта ФИАС'),
    sa.ForeignKeyConstraint(['level_id'], ['levels.id'], name='fk_address_objects_levels_id_level_id'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_address_objects_name'), 'address_objects', ['name'], unique=False)
    op.create_index(op.f('ix_address_objects_object_guid'), 'address_objects', ['object_guid'], unique=False)
    op.create_index(op.f('ix_address_objects_object_id'), 'address_objects', ['object_id'], unique=False)
    op.create_table('address_types',
    sa.Column('update_date', sa.Date(), nullable=False, comment='Дата внесения (обновления) записи'),
    sa.Column('start_date', sa.Date(), nullable=False, comment='Начало действия записи'),
    sa.Column('end_date', sa.Date(), nullable=False, comment='Окончание действия записи'),
    sa.Column('is_active', sa.Boolean(), nullable=False, comment='Статус активности'),
    sa.Column('id', sa.Integer(), nullable=False, comment='id'),
    sa.Column('name', sa.String(length=250), nullable=False, comment='Полное наименование типа объекта'),
    sa.Column('short_name', sa.String(length=50), nullable=True, comment='Краткое наименование типа объекта'),
    sa.Column('description', sa.String(length=250), nullable=True, comment='Описание'),
    sa.Column('level_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['level_id'], ['levels.id'], name='fk_address_types_levels_id_level_id'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_address_types_name'), 'address_types', ['name'], unique=False)
    op.create_table('apartments',
    sa.Column('update_date', sa.Date(), nullable=False, comment='Дата внесения (обновления) записи'),
    sa.Column('start_date', sa.Date(), nullable=False, comment='Начало действия записи'),
    sa.Column('end_date', sa.Date(), nullable=False, comment='Окончание действия записи'),
    sa.Column('is_active', sa.Boolean(), nullable=False, comment='Статус активности'),
    sa.Column('id', sa.BigInteger(), nullable=False, comment='id'),
    sa.Column('object_id', sa.BigInteger(), nullable=False, comment='Глобальный уникальный идентификатор адресного объекта'),
    sa.Column('object_guid', sa.String(length=36), nullable=False, comment='Глобальный уникальный идентификатор адресного объекта. Соответствует коду ФИАС'),
    sa.Column('number', sa.String(length=50), nullable=False, comment='Номер помещения'),
    sa.Column('apartment_type_id', sa.Integer(), nullable=False),
    sa.Column('is_actual', sa.Boolean(), nullable=False, comment='Статус актуальности адресного объекта ФИАС'),
    sa.ForeignKeyConstraint(['apartment_type_id'], ['apartment_type.id'], name='fk_apartments_apartment_type_id_apartment_type_id'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_apartments_number'), 'apartments', ['number'], unique=False)
    op.create_index(op.f('ix_apartments_object_guid'), 'apartments', ['object_guid'], unique=False)
    op.create_index(op.f('ix_apartments_object_id'), 'apartments', ['object_id'], unique=False)
    op.create_table('houses',
    sa.Column('update_date', sa.Date(), nullable=False, comment='Дата внесения (обновления) записи'),
    sa.Column('start_date', sa.Date(), nullable=False, comment='Начало действия записи'),
    sa.Column('end_date', sa.Date(), nullable=False, comment='Окончание действия записи'),
    sa.Column('is_active', sa.Boolean(), nullable=False, comment='Статус активности'),
    sa.Column('id', sa.BigInteger(), nullable=False, comment='id'),
    sa.Column('object_id', sa.BigInteger(), nullable=False, comment='Глобальный уникальный идентификатор адресного объекта'),
    sa.Column('object_guid', sa.String(length=36), nullable=False, comment='Глобальный уникальный идентификатор адресного объекта. Соответствует коду ФИАС'),
    sa.Column('house_num', sa.String(length=50), nullable=True, comment='Основной номер дома'),
    sa.Column('add_num1', sa.String(length=50), nullable=True, comment='Дополнительный номер дома 1'),
    sa.Column('add_num2', sa.String(length=50), nullable=True, comment='Дополнительный номер дома 2'),
    sa.Column('house_type', sa.Integer(), nullable=True),
    sa.Column('add_type1', sa.Integer(), nullable=True),
    sa.Column('add_type2', sa.Integer(), nullable=True),
    sa.Column('is_actual', sa.Boolean(), nullable=False, comment='Статус актуальности адресного объекта ФИАС'),
    sa.ForeignKeyConstraint(['add_type1'], ['house_types.id'], name='fk_houses_house_types_id_add_type1'),
    sa.ForeignKeyConstraint(['add_type2'], ['house_types.id'], name='fk_houses_house_types_id_add_type2'),
    sa.ForeignKeyConstraint(['house_type'], ['house_types.id'], name='fk_houses_house_types_id_house_type'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_houses_add_num1'), 'houses', ['add_num1'], unique=False)
    op.create_index(op.f('ix_houses_add_num2'), 'houses', ['add_num2'], unique=False)
    op.create_index(op.f('ix_houses_house_num'), 'houses', ['house_num'], unique=False)
    op.create_index(op.f('ix_houses_object_guid'), 'houses', ['object_guid'], unique=False)
    op.create_index(op.f('ix_houses_object_id'), 'houses', ['object_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_houses_object_id'), table_name='houses')
    op.drop_index(op.f('ix_houses_object_guid'), table_name='houses')
    op.drop_index(op.f('ix_houses_house_num'), table_name='houses')
    op.drop_index(op.f('ix_houses_add_num2'), table_name='houses')
    op.drop_index(op.f('ix_houses_add_num1'), table_name='houses')
    op.drop_table('houses')
    op.drop_index(op.f('ix_apartments_object_id'), table_name='apartments')
    op.drop_index(op.f('ix_apartments_object_guid'), table_name='apartments')
    op.drop_index(op.f('ix_apartments_number'), table_name='apartments')
    op.drop_table('apartments')
    op.drop_index(op.f('ix_address_types_name'), table_name='address_types')
    op.drop_table('address_types')
    op.drop_index(op.f('ix_address_objects_object_id'), table_name='address_objects')
    op.drop_index(op.f('ix_address_objects_object_guid'), table_name='address_objects')
    op.drop_index(op.f('ix_address_objects_name'), table_name='address_objects')
    op.drop_table('address_objects')
    op.drop_index(op.f('ix_address_object_params_value'), table_name='address_object_params')
    op.drop_index(op.f('ix_address_object_params_object_id'), table_name='address_object_params')
    op.drop_table('address_object_params')
    op.drop_table('updates')
    op.drop_index(op.f('ix_param_types_name'), table_name='param_types')
    op.drop_table('param_types')
    op.drop_index(op.f('ix_levels_name'), table_name='levels')
    op.drop_table('levels')
    op.drop_index(op.f('ix_house_types_name'), table_name='house_types')
    op.drop_table('house_types')
    op.drop_index(op.f('ix_hierarchy_mun_parent_object_id'), table_name='hierarchy_mun')
    op.drop_index(op.f('ix_hierarchy_mun_object_id'), table_name='hierarchy_mun')
    op.drop_table('hierarchy_mun')
    op.drop_index(op.f('ix_hierarchy_adm_parent_object_id'), table_name='hierarchy_adm')
    op.drop_index(op.f('ix_hierarchy_adm_object_id'), table_name='hierarchy_adm')
    op.drop_table('hierarchy_adm')
    op.drop_index(op.f('ix_apartment_type_name'), table_name='apartment_type')
    op.drop_table('apartment_type')
    # ### end Alembic commands ###
