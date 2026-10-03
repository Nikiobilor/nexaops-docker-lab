-- NexaOps Dashboard Database Schema
CREATE TABLE IF NOT EXISTS deployments (
    id          SERIAL PRIMARY KEY,
    service     VARCHAR(100) NOT NULL,
    version     VARCHAR(50)  NOT NULL,
    status      VARCHAR(20)  NOT NULL,
    deployed_by VARCHAR(100) NOT NULL,
    deployed_at TIMESTAMP    DEFAULT NOW()
);

INSERT INTO deployments (service, version, status, deployed_by) VALUES
    ('user-service',         '1.2.0', 'success', 'engineer-a'),
    ('notification-service', '2.1.1', 'success', 'engineer-b'),
    ('payment-service',      '3.0.1', 'failed',  'engineer-c'),
    ('api-gateway',          '4.5.0', 'success', 'engineer-a'),
    ('report-service',       '1.0.2', 'success', 'engineer-b');
