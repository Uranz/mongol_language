"""Add lessonProgress model

Revision ID: 801d92a5c9e4
Revises: 3030ac7e066e
Create Date: 2025-07-02 18:23:22.381089

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '801d92a5c9e4'
down_revision = '3030ac7e066e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('lesson_progress',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('lesson_id', sa.Integer(), nullable=False),
    sa.Column('is_completed', sa.Boolean(), nullable=False),
    sa.Column('score', sa.Integer(), nullable=False),
    sa.Column('time_spent', sa.Integer(), nullable=True),
    sa.Column('last_accessed', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('lesson_progress')
    # ### end Alembic commands ###
