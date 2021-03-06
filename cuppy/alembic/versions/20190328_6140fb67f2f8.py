"""joined_date

Revision ID: 6140fb67f2f8
Revises: 49dfda51cf38
Create Date: 2019-03-28 10:21:36.327338

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6140fb67f2f8'
down_revision = '49dfda51cf38'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('categories')
    op.drop_table('posts')
    op.add_column('users', sa.Column('joined_date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'joined_date')
    op.create_table('posts',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('category_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name='fk_posts_category_id_categories'),
    sa.ForeignKeyConstraint(['id'], ['documents.id'], name='fk_posts_id_documents'),
    sa.PrimaryKeyConstraint('id', name='pk_posts')
    )
    op.create_table('categories',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id', name='pk_categories')
    )
    # ### end Alembic commands ###
