"""Initial migration

Revision ID: 000c0b20aabb
Revises: 
Create Date: 2025-06-05 00:51:40.163060

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '000c0b20aabb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('configs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=64), nullable=False),
    sa.Column('value', sa.String(length=256), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key')
    )
    op.create_table('words',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('mongolian', sa.String(length=100), nullable=False),
    sa.Column('english', sa.String(length=200), nullable=False),
    sa.Column('part_of_speech', sa.String(length=50), nullable=True),
    sa.Column('example_sentence', sa.Text(), nullable=True),
    sa.Column('difficulty', sa.String(length=20), nullable=True),
    sa.Column('audio_url', sa.String(length=255), nullable=True),
    sa.Column('category', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('quizzes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('word_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('options', sa.Text(), nullable=False),
    sa.Column('correct_option', sa.String(length=200), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['word_id'], ['words.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('vocabulary')
    op.drop_table('config')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('config',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('key', sa.VARCHAR(length=64), nullable=False),
    sa.Column('value', sa.VARCHAR(length=256), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key')
    )
    op.create_table('vocabulary',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('mongolian_word', sa.VARCHAR(length=100), nullable=False),
    sa.Column('english_meaning', sa.VARCHAR(length=200), nullable=False),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.Column('updated_at', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('quizzes')
    op.drop_table('words')
    op.drop_table('configs')
    # ### end Alembic commands ###
