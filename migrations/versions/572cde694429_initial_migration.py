"""Initial migration.

Revision ID: 572cde694429
Revises: 5573b876a458
Create Date: 2023-02-27 22:34:49.530311

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '572cde694429'
down_revision = '5573b876a458'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('register', schema=None) as batch_op:
        batch_op.drop_column('public')
        batch_op.drop_column('private')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('register', schema=None) as batch_op:
        batch_op.add_column(sa.Column('private', sa.VARCHAR(length=200), nullable=True))
        batch_op.add_column(sa.Column('public', sa.VARCHAR(length=200), nullable=True))

    # ### end Alembic commands ###
