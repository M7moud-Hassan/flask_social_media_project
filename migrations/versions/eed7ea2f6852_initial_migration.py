"""Initial migration.

Revision ID: eed7ea2f6852
Revises: 572cde694429
Create Date: 2023-03-01 11:33:05.068993

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eed7ea2f6852'
down_revision = '572cde694429'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chat',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('register_id', sa.Integer(), nullable=False),
    sa.Column('friend', sa.Integer(), nullable=False),
    sa.Column('msg', sa.String(length=500), nullable=True),
    sa.ForeignKeyConstraint(['register_id'], ['register.id'], name=op.f('fk_chat_register_id_register')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_chat'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('chat')
    # ### end Alembic commands ###
