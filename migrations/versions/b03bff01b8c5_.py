"""empty message

Revision ID: b03bff01b8c5
Revises: 52bfc57cb523
Create Date: 2019-09-27 21:09:25.994059

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b03bff01b8c5'
down_revision = '52bfc57cb523'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('recipe', sa.Column('recipe_image', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('recipe', 'recipe_image')
    # ### end Alembic commands ###
