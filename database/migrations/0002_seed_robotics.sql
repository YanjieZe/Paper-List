BEGIN;

INSERT INTO roadmaps (slug, title, description, status, published_path)
VALUES (
    'robotics',
    'Robotics',
    'The root research map spanning perception, learning, planning, control, embodiment, and evaluation.',
    'seed',
    'knowledge/roadmaps/robotics.md'
)
ON CONFLICT (slug) DO NOTHING;

WITH root AS (SELECT id FROM roadmaps WHERE slug = 'robotics')
INSERT INTO roadmap_nodes (roadmap_id, node_type, slug, title, ordinal, review_status)
SELECT root.id, 'branch', seed.slug, seed.title, seed.ordinal, 'accepted'
FROM root
CROSS JOIN (VALUES
    ('sensing-perception', 'Sensing & Perception', 10),
    ('representation-world-models', 'Representation & World Models', 20),
    ('planning-reasoning', 'Planning & Reasoning', 30),
    ('learning-foundation-models', 'Learning & Foundation Models', 40),
    ('control-dynamics', 'Control & Dynamics', 50),
    ('manipulation-dexterity', 'Manipulation & Dexterity', 60),
    ('locomotion-humanoids', 'Locomotion & Humanoids', 70),
    ('navigation-mobile-manipulation', 'Navigation & Mobile Manipulation', 80),
    ('hardware-embodiment', 'Hardware & Embodiment', 90),
    ('data-simulation-evaluation', 'Data, Simulation, Benchmarks & Evaluation', 100)
) AS seed(slug, title, ordinal)
ON CONFLICT (roadmap_id, slug) DO NOTHING;

INSERT INTO app_settings (key, value) VALUES
    ('model_roles', '{"fast":{"model":"gpt-5.6-luna","reasoning":"low"},"standard":{"model":"gpt-5.6-terra","reasoning":"medium"},"deep":{"model":"gpt-5.6-sol","reasoning":"high"},"embedding":{"model":"text-embedding-3-large"}}'),
    ('cost_budgets_usd', '{"triage":0.10,"standard":1.00,"deep":5.00,"research":10.00,"roadmap":20.00}')
ON CONFLICT (key) DO NOTHING;

COMMIT;
