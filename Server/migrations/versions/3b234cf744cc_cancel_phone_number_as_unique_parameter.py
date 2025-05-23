"""cancel phone number as unique parameter

Revision ID: 3b234cf744cc
Revises: e3e8ceb21d43
Create Date: 2025-05-17 17:28:38.474701

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b234cf744cc'
down_revision = 'e3e8ceb21d43'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('phone_number',
               existing_type=sa.VARCHAR(length=15),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('phone_number',
               existing_type=sa.VARCHAR(length=15),
               nullable=False)

    # ### end Alembic commands ###
