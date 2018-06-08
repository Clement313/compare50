"""empty message

Revision ID: 4a04947c2455
Revises: 
Create Date: 2018-04-21 04:57:26.538207

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a04947c2455'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('upload',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('uuid', sa.CHAR(length=36), nullable=False),
    sa.Column('created', sa.TIMESTAMP(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('uuid')
    )
    op.create_table('hash',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('upload_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['upload_id'], ['upload.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pass',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('config', sa.VARCHAR(length=255), nullable=False),
    sa.Column('upload_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['upload_id'], ['upload.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('submission',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('upload_id', sa.INTEGER(), nullable=False),
    sa.Column('path', sa.VARCHAR(length=255), nullable=False),
    sa.ForeignKeyConstraint(['upload_id'], ['upload.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('file',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('submission_id', sa.INTEGER(), nullable=False),
    sa.Column('path', sa.VARCHAR(length=255), nullable=False),
    sa.ForeignKeyConstraint(['submission_id'], ['submission.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fragment',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('hash_id', sa.INTEGER(), nullable=False),
    sa.Column('file_id', sa.INTEGER(), nullable=False),
    sa.Column('start', sa.INTEGER(), nullable=False),
    sa.Column('end', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['file_id'], ['file.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['hash_id'], ['hash.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('fragment')
    op.drop_table('file')
    op.drop_table('submission')
    op.drop_table('pass')
    op.drop_table('hash')
    op.drop_table('upload')
    # ### end Alembic commands ###