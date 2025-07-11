"""Add Lesson model

Revision ID: 3030ac7e066e
Revises: 00bb246bbf28
Create Date: 2025-07-02 18:17:27.382619

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3030ac7e066e'
down_revision = '00bb246bbf28'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('lessons',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('level', sa.String(length=20), nullable=False),
    sa.Column('lesson_type', sa.String(length=50), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('audio_url', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('lessons')
    # ### end Alembic commands ###
