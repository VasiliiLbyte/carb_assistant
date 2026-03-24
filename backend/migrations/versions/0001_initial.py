"""initial schema"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def _uuid_col(name: str, nullable: bool = False):
    return sa.Column(name, postgresql.UUID(as_uuid=True), primary_key=(name == 'id'), nullable=nullable)


def upgrade() -> None:
    op.create_table(
        'users',
        _uuid_col('id'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='viewer'),
        sa.Column('skills', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('notification_settings', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('workload_profile', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_role', 'users', ['role'])

    op.create_table(
        'projects',
        _uuid_col('id'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('project_type', sa.String(length=100), nullable=False, server_default='general'),
        sa.Column('stage', sa.String(length=100), nullable=False, server_default='planned'),
        sa.Column('custom_fields', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
    )
    op.create_index('ix_projects_name', 'projects', ['name'])
    op.create_index('ix_projects_project_type', 'projects', ['project_type'])
    op.create_index('ix_projects_stage', 'projects', ['stage'])

    op.create_table(
        'tasks',
        _uuid_col('id'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=4000), nullable=False, server_default=''),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='to-do'),
        sa.Column('priority', sa.String(length=50), nullable=False, server_default='medium'),
        sa.Column('estimated_hours', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('due_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('dependency_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='SET NULL'), nullable=True),
        sa.Column('assignee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
    )
    op.create_index('ix_tasks_title', 'tasks', ['title'])
    op.create_index('ix_tasks_status', 'tasks', ['status'])
    op.create_index('ix_tasks_priority', 'tasks', ['priority'])
    op.create_index('ix_tasks_due_at', 'tasks', ['due_at'])
    op.create_index('ix_tasks_project_id', 'tasks', ['project_id'])
    op.create_index('ix_tasks_assignee_id', 'tasks', ['assignee_id'])

    op.create_table(
        'documents',
        _uuid_col('id'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('object_key', sa.String(length=500), nullable=False),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='SET NULL'), nullable=True),
    )
    op.create_index('ix_documents_name', 'documents', ['name'])
    op.create_index('ix_documents_object_key', 'documents', ['object_key'], unique=True)
    op.create_index('ix_documents_project_id', 'documents', ['project_id'])

    op.create_table(
        'document_versions',
        _uuid_col('id'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('object_key', sa.String(length=500), nullable=False),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
    )
    op.create_index('ix_document_versions_document_id', 'document_versions', ['document_id'])
    op.create_index('ix_document_versions_object_key', 'document_versions', ['object_key'])

    op.create_table(
        'risks',
        _uuid_col('id'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('probability', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('impact', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('mitigation_plan', sa.String(length=2000), nullable=False, server_default=''),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='open'),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='SET NULL'), nullable=True),
    )
    op.create_index('ix_risks_title', 'risks', ['title'])
    op.create_index('ix_risks_status', 'risks', ['status'])
    op.create_index('ix_risks_project_id', 'risks', ['project_id'])

    op.create_table(
        'proactive_rules',
        _uuid_col('id'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('trigger_type', sa.String(length=100), nullable=False),
        sa.Column('action_type', sa.String(length=100), nullable=False, server_default='send_message'),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('buttons', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
    )
    op.create_index('ix_proactive_rules_name', 'proactive_rules', ['name'], unique=True)
    op.create_index('ix_proactive_rules_trigger_type', 'proactive_rules', ['trigger_type'])
    op.create_index('ix_proactive_rules_enabled', 'proactive_rules', ['enabled'])

    op.create_table(
        'message_history',
        _uuid_col('id'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('channel', sa.String(length=50), nullable=False),
        sa.Column('recipient', sa.String(length=255), nullable=False),
        sa.Column('direction', sa.String(length=10), nullable=False, server_default='out'),
        sa.Column('message_text', sa.String(length=4000), nullable=False),
        sa.Column('external_message_id', sa.String(length=255), nullable=True),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('proactive_rule_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('proactive_rules.id', ondelete='SET NULL'), nullable=True),
    )
    op.create_index('ix_message_history_channel', 'message_history', ['channel'])
    op.create_index('ix_message_history_recipient', 'message_history', ['recipient'])
    op.create_index('ix_message_history_direction', 'message_history', ['direction'])
    op.create_index('ix_message_history_external_message_id', 'message_history', ['external_message_id'])

    op.create_table(
        'ai_recommendations',
        _uuid_col('id'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('recommendation_type', sa.String(length=100), nullable=False),
        sa.Column('rationale', sa.String(length=2000), nullable=False, server_default=''),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='proposed'),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tasks.id', ondelete='SET NULL'), nullable=True),
    )
    op.create_index('ix_ai_recommendations_recommendation_type', 'ai_recommendations', ['recommendation_type'])
    op.create_index('ix_ai_recommendations_status', 'ai_recommendations', ['status'])
    op.create_index('ix_ai_recommendations_task_id', 'ai_recommendations', ['task_id'])

    op.create_table(
        'memory_entries',
        _uuid_col('id'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('scope_type', sa.String(length=50), nullable=False),
        sa.Column('scope_id', sa.String(length=100), nullable=False),
        sa.Column('memory_type', sa.String(length=50), nullable=False, server_default='short_term'),
        sa.Column('content', sa.String(length=4000), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
    )
    op.create_index('ix_memory_entries_scope_type', 'memory_entries', ['scope_type'])
    op.create_index('ix_memory_entries_scope_id', 'memory_entries', ['scope_id'])
    op.create_index('ix_memory_entries_memory_type', 'memory_entries', ['memory_type'])
    op.create_index('ix_memory_entries_expires_at', 'memory_entries', ['expires_at'])

    op.create_table(
        'knowledge_documents',
        _uuid_col('id'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('source_type', sa.String(length=50), nullable=False, server_default='document'),
        sa.Column('source_id', sa.String(length=100), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
    )
    op.create_index('ix_knowledge_documents_title', 'knowledge_documents', ['title'])
    op.create_index('ix_knowledge_documents_source_type', 'knowledge_documents', ['source_type'])
    op.create_index('ix_knowledge_documents_source_id', 'knowledge_documents', ['source_id'])

    op.create_table(
        'knowledge_chunks',
        _uuid_col('id'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('knowledge_document_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('knowledge_documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('chunk_text', sa.String(length=4000), nullable=False),
        sa.Column('embedding_ref', sa.String(length=255), nullable=True),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
    )
    op.create_index('ix_knowledge_chunks_knowledge_document_id', 'knowledge_chunks', ['knowledge_document_id'])
    op.create_index('ix_knowledge_chunks_embedding_ref', 'knowledge_chunks', ['embedding_ref'])


def downgrade() -> None:
    for table in [
        'knowledge_chunks',
        'knowledge_documents',
        'memory_entries',
        'ai_recommendations',
        'message_history',
        'proactive_rules',
        'risks',
        'document_versions',
        'documents',
        'tasks',
        'projects',
        'users',
    ]:
        op.drop_table(table)
