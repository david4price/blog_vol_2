"""about author and some removed

Revision ID: 5a02b30f8b22
Revises: 968802395da0
Create Date: 2022-10-12 20:45:11.181086

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5a02b30f8b22'
down_revision = '968802395da0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('about_author', sa.Text(length=500), nullable=True))
    op.drop_column('users', 'favorite_music')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('favorite_music', mysql.VARCHAR(length=100), nullable=True))
    op.drop_column('users', 'about_author')
    # ### end Alembic commands ###
