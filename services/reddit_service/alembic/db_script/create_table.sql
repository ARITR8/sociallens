-- Create the table
CREATE TABLE reddit_posts (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    subreddit VARCHAR(100) NOT NULL,
    title TEXT NOT NULL,
    url VARCHAR(500) NOT NULL,
    author VARCHAR(100) NOT NULL,
    score INTEGER NOT NULL,
    comments INTEGER NOT NULL,
    normalized_score FLOAT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    fetched_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    top_comments JSONB,
    post_text TEXT
);

-- Create indexes
CREATE INDEX idx_reddit_posts_score_date ON reddit_posts (normalized_score, created_at);
CREATE INDEX idx_reddit_posts_subreddit_date ON reddit_posts (subreddit, created_at);
CREATE UNIQUE INDEX idx_reddit_posts_url ON reddit_posts (url);
CREATE INDEX idx_reddit_posts_source ON reddit_posts (source);
CREATE INDEX idx_reddit_posts_author ON reddit_posts (author);