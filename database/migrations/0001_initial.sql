BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version text PRIMARY KEY,
    applied_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE app_users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email text NOT NULL UNIQUE,
    password_hash text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    disabled_at timestamptz
);

CREATE TABLE sessions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
    token_hash text NOT NULL UNIQUE,
    expires_at timestamptz NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    last_seen_at timestamptz NOT NULL DEFAULT now(),
    user_agent text,
    ip_hash text
);

CREATE TABLE works (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    canonical_title text NOT NULL,
    slug text NOT NULL UNIQUE,
    abstract text,
    year integer CHECK (year IS NULL OR year BETWEEN 1800 AND 2200),
    venue text,
    status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'merged', 'archived')),
    merged_into_id uuid REFERENCES works(id),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE research_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    work_id uuid REFERENCES works(id) ON DELETE SET NULL,
    item_type text NOT NULL CHECK (
        item_type IN ('paper', 'blog', 'article', 'project', 'repository', 'dataset', 'benchmark', 'collection')
    ),
    title text NOT NULL,
    canonical_url text NOT NULL,
    abstract text,
    authors jsonb NOT NULL DEFAULT '[]'::jsonb,
    year integer CHECK (year IS NULL OR year BETWEEN 1800 AND 2200),
    venue text,
    source_kind text NOT NULL DEFAULT 'web',
    confidence numeric(4,3) NOT NULL DEFAULT 0 CHECK (confidence BETWEEN 0 AND 1),
    reading_status text NOT NULL DEFAULT 'unread' CHECK (reading_status IN ('unread', 'read')),
    lifecycle_status text NOT NULL DEFAULT 'candidate' CHECK (
        lifecycle_status IN ('candidate', 'triaged', 'review', 'published', 'unresolved', 'failed_retryable', 'archived')
    ),
    added_context text,
    published_path text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (canonical_url)
);

CREATE TABLE source_identities (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    research_item_id uuid NOT NULL REFERENCES research_items(id) ON DELETE CASCADE,
    identity_type text NOT NULL CHECK (
        identity_type IN ('doi', 'arxiv', 'openreview', 'github', 'url', 'semantic_scholar')
    ),
    identity_value text NOT NULL,
    is_primary boolean NOT NULL DEFAULT false,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (identity_type, identity_value)
);

CREATE TABLE item_sources (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    research_item_id uuid NOT NULL REFERENCES research_items(id) ON DELETE CASCADE,
    url text NOT NULL,
    source_type text NOT NULL,
    is_official boolean NOT NULL DEFAULT false,
    discovered_by text NOT NULL DEFAULT 'user',
    fetched_at timestamptz,
    http_status integer,
    content_type text,
    error text,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (research_item_id, url)
);

CREATE TABLE document_versions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    research_item_id uuid NOT NULL REFERENCES research_items(id) ON DELETE CASCADE,
    source_url text NOT NULL,
    media_type text NOT NULL,
    sha256 text NOT NULL,
    storage_path text NOT NULL,
    byte_size bigint NOT NULL CHECK (byte_size >= 0),
    page_count integer CHECK (page_count IS NULL OR page_count >= 0),
    version_label text,
    fetched_at timestamptz NOT NULL DEFAULT now(),
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (research_item_id, sha256)
);

CREATE TABLE document_sections (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    document_version_id uuid NOT NULL REFERENCES document_versions(id) ON DELETE CASCADE,
    heading text,
    page_start integer CHECK (page_start IS NULL OR page_start >= 1),
    page_end integer CHECK (page_end IS NULL OR page_end >= 1),
    ordinal integer NOT NULL,
    content text NOT NULL,
    UNIQUE (document_version_id, ordinal)
);

CREATE TABLE document_chunks (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    document_version_id uuid NOT NULL REFERENCES document_versions(id) ON DELETE CASCADE,
    section_id uuid REFERENCES document_sections(id) ON DELETE SET NULL,
    ordinal integer NOT NULL,
    page integer CHECK (page IS NULL OR page >= 1),
    heading text,
    content text NOT NULL,
    bbox jsonb,
    token_count integer NOT NULL DEFAULT 0 CHECK (token_count >= 0),
    embedding vector(1536),
    embedding_model text,
    search_vector tsvector GENERATED ALWAYS AS (to_tsvector('simple', coalesce(heading, '') || ' ' || content)) STORED,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (document_version_id, ordinal)
);

CREATE INDEX document_chunks_search_idx ON document_chunks USING gin(search_vector);
CREATE INDEX document_chunks_embedding_idx ON document_chunks USING hnsw (embedding vector_cosine_ops);

CREATE TABLE topics (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    slug text NOT NULL UNIQUE,
    name text NOT NULL,
    parent_id uuid REFERENCES topics(id),
    description text,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE research_item_topics (
    research_item_id uuid NOT NULL REFERENCES research_items(id) ON DELETE CASCADE,
    topic_id uuid NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    source text NOT NULL CHECK (source IN ('manual', 'agent', 'migration', 'roadmap')),
    confidence numeric(4,3) NOT NULL DEFAULT 1 CHECK (confidence BETWEEN 0 AND 1),
    PRIMARY KEY (research_item_id, topic_id)
);

CREATE TABLE relations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_work_id uuid NOT NULL REFERENCES works(id) ON DELETE CASCADE,
    target_work_id uuid NOT NULL REFERENCES works(id) ON DELETE CASCADE,
    relation_type text NOT NULL CHECK (
        relation_type IN ('builds_on', 'extends', 'contrasts_with', 'evaluates', 'explains', 'implements', 'uses_dataset', 'critiques', 'reproduces')
    ),
    rationale text NOT NULL,
    evidence jsonb NOT NULL DEFAULT '[]'::jsonb,
    confidence numeric(4,3) NOT NULL DEFAULT 0 CHECK (confidence BETWEEN 0 AND 1),
    review_status text NOT NULL DEFAULT 'pending' CHECK (review_status IN ('pending', 'accepted', 'rejected')),
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (source_work_id, target_work_id, relation_type)
);

CREATE TABLE claims (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    research_item_id uuid REFERENCES research_items(id) ON DELETE CASCADE,
    relation_id uuid REFERENCES relations(id) ON DELETE CASCADE,
    claim_kind text NOT NULL CHECK (claim_kind IN ('fact', 'inference', 'personal')),
    text text NOT NULL,
    created_by text NOT NULL CHECK (created_by IN ('agent', 'user', 'migration')),
    review_status text NOT NULL DEFAULT 'pending' CHECK (review_status IN ('pending', 'accepted', 'edited', 'rejected')),
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK ((research_item_id IS NOT NULL)::int + (relation_id IS NOT NULL)::int = 1)
);

CREATE TABLE claim_evidence (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id uuid NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    document_version_id uuid NOT NULL REFERENCES document_versions(id) ON DELETE CASCADE,
    page integer CHECK (page IS NULL OR page >= 1),
    section text,
    figure text,
    table_name text,
    quote text CHECK (quote IS NULL OR length(quote) <= 500),
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (page IS NOT NULL OR section IS NOT NULL OR figure IS NOT NULL OR table_name IS NOT NULL)
);

CREATE TABLE roadmaps (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    slug text NOT NULL UNIQUE,
    title text NOT NULL,
    description text,
    status text NOT NULL DEFAULT 'seed' CHECK (status IN ('seed', 'current', 'stale', 'review')),
    published_path text,
    version integer NOT NULL DEFAULT 1,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE roadmap_nodes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    roadmap_id uuid NOT NULL REFERENCES roadmaps(id) ON DELETE CASCADE,
    parent_id uuid REFERENCES roadmap_nodes(id) ON DELETE SET NULL,
    work_id uuid REFERENCES works(id) ON DELETE SET NULL,
    node_type text NOT NULL CHECK (node_type IN ('branch', 'problem', 'concept', 'work', 'frontier', 'open_question')),
    slug text NOT NULL,
    title text NOT NULL,
    narrative text,
    ordinal integer NOT NULL DEFAULT 0,
    review_status text NOT NULL DEFAULT 'pending' CHECK (review_status IN ('pending', 'accepted', 'edited', 'rejected')),
    UNIQUE (roadmap_id, slug)
);

CREATE TABLE roadmap_edges (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    roadmap_id uuid NOT NULL REFERENCES roadmaps(id) ON DELETE CASCADE,
    source_node_id uuid NOT NULL REFERENCES roadmap_nodes(id) ON DELETE CASCADE,
    target_node_id uuid NOT NULL REFERENCES roadmap_nodes(id) ON DELETE CASCADE,
    edge_type text NOT NULL CHECK (edge_type IN ('prerequisite', 'evolves_to', 'alternative', 'supports', 'challenges', 'contains')),
    rationale text,
    evidence jsonb NOT NULL DEFAULT '[]'::jsonb,
    review_status text NOT NULL DEFAULT 'pending' CHECK (review_status IN ('pending', 'accepted', 'rejected')),
    UNIQUE (source_node_id, target_node_id, edge_type)
);

CREATE TABLE jobs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type text NOT NULL CHECK (job_type IN ('ingest_url', 'deep_read', 'research', 'publish_review', 'reindex_markdown', 'refresh_roadmap')),
    payload jsonb NOT NULL,
    status text NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'running', 'succeeded', 'failed', 'dead', 'cancelled')),
    priority integer NOT NULL DEFAULT 100,
    idempotency_key text UNIQUE,
    attempts integer NOT NULL DEFAULT 0,
    max_attempts integer NOT NULL DEFAULT 3,
    available_at timestamptz NOT NULL DEFAULT now(),
    leased_by text,
    lease_expires_at timestamptz,
    progress numeric(5,2) NOT NULL DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
    current_stage text,
    result jsonb,
    error jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    started_at timestamptz,
    finished_at timestamptz
);

CREATE INDEX jobs_claim_idx ON jobs (status, available_at, priority, created_at);

CREATE TABLE job_events (
    id bigserial PRIMARY KEY,
    job_id uuid NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    event_type text NOT NULL,
    stage text,
    progress numeric(5,2) CHECK (progress IS NULL OR progress BETWEEN 0 AND 100),
    message text,
    data jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX job_events_stream_idx ON job_events (job_id, id);

CREATE TABLE agent_runs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id uuid REFERENCES jobs(id) ON DELETE SET NULL,
    agent_name text NOT NULL,
    model text NOT NULL,
    reasoning_effort text NOT NULL,
    prompt_version text NOT NULL,
    schema_version integer NOT NULL,
    status text NOT NULL CHECK (status IN ('running', 'succeeded', 'failed', 'budget_exceeded')),
    input_summary text,
    input_tokens integer NOT NULL DEFAULT 0,
    output_tokens integer NOT NULL DEFAULT 0,
    cached_tokens integer NOT NULL DEFAULT 0,
    tool_cost_usd numeric(12,6) NOT NULL DEFAULT 0,
    total_cost_usd numeric(12,6) NOT NULL DEFAULT 0,
    max_cost_usd numeric(12,6) NOT NULL,
    started_at timestamptz NOT NULL DEFAULT now(),
    finished_at timestamptz,
    error jsonb
);

CREATE TABLE artifacts (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_run_id uuid NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
    artifact_type text NOT NULL,
    schema_version integer NOT NULL,
    content jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE review_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    research_item_id uuid REFERENCES research_items(id) ON DELETE CASCADE,
    roadmap_id uuid REFERENCES roadmaps(id) ON DELETE CASCADE,
    artifact_id uuid REFERENCES artifacts(id) ON DELETE SET NULL,
    review_type text NOT NULL CHECK (review_type IN ('reading_note', 'roadmap', 'relation', 'migration_conflict', 'git_conflict')),
    status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_review', 'approved', 'rejected', 'published', 'conflict')),
    base_git_sha text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CHECK ((research_item_id IS NOT NULL)::int + (roadmap_id IS NOT NULL)::int >= 1 OR review_type IN ('migration_conflict', 'git_conflict'))
);

CREATE TABLE review_sections (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    review_item_id uuid NOT NULL REFERENCES review_items(id) ON DELETE CASCADE,
    section_key text NOT NULL,
    title text NOT NULL,
    generated_markdown text NOT NULL,
    edited_markdown text,
    claims jsonb NOT NULL DEFAULT '[]'::jsonb,
    required boolean NOT NULL DEFAULT true,
    status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'edited', 'rejected')),
    ordinal integer NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (review_item_id, section_key)
);

CREATE TABLE merge_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    target_work_id uuid NOT NULL REFERENCES works(id),
    source_work_id uuid NOT NULL REFERENCES works(id),
    reason text NOT NULL,
    confidence numeric(4,3) NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    evidence jsonb NOT NULL DEFAULT '[]'::jsonb,
    before_snapshot jsonb NOT NULL,
    after_snapshot jsonb NOT NULL,
    undone_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE research_profiles (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL UNIQUE REFERENCES app_users(id) ON DELETE CASCADE,
    markdown text NOT NULL DEFAULT '',
    structured_profile jsonb NOT NULL DEFAULT '{}'::jsonb,
    version integer NOT NULL DEFAULT 1,
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE conversations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    title text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE conversation_messages (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id uuid NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role text NOT NULL CHECK (role IN ('user', 'assistant', 'tool')),
    content jsonb NOT NULL,
    promoted_to_knowledge boolean NOT NULL DEFAULT false,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE notifications (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    kind text NOT NULL,
    title text NOT NULL,
    message text NOT NULL,
    href text,
    read_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE git_exports (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    review_item_id uuid NOT NULL REFERENCES review_items(id) ON DELETE RESTRICT,
    path text NOT NULL,
    base_sha text NOT NULL,
    commit_sha text,
    push_status text NOT NULL CHECK (push_status IN ('pending', 'pushed', 'conflict', 'failed')),
    error text,
    created_at timestamptz NOT NULL DEFAULT now(),
    finished_at timestamptz
);

CREATE TABLE migration_records (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_file text NOT NULL,
    line_number integer NOT NULL CHECK (line_number >= 1),
    occurrence_index integer NOT NULL DEFAULT 0 CHECK (occurrence_index >= 0),
    raw_text text NOT NULL,
    raw_url text NOT NULL,
    normalized_url text NOT NULL,
    detected_type text NOT NULL,
    status text NOT NULL CHECK (status IN ('discovered', 'imported', 'merged', 'unresolved', 'failed_retryable')),
    research_item_id uuid REFERENCES research_items(id) ON DELETE SET NULL,
    error text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (source_file, line_number, occurrence_index)
);

CREATE TABLE app_settings (
    key text PRIMARY KEY,
    value jsonb NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER works_updated_at BEFORE UPDATE ON works FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER research_items_updated_at BEFORE UPDATE ON research_items FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER roadmaps_updated_at BEFORE UPDATE ON roadmaps FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER review_items_updated_at BEFORE UPDATE ON review_items FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER migration_records_updated_at BEFORE UPDATE ON migration_records FOR EACH ROW EXECUTE FUNCTION set_updated_at();

COMMIT;
