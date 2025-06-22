-- 儲存唯一職位內容
CREATE TABLE jobs (
    job_id TEXT PRIMARY KEY,              -- 唯一 job ID（例如從 URL 或 DOM 抓出來）
    title TEXT NOT NULL,
    company TEXT,
    location TEXT,
    detail_url TEXT,
    description TEXT,
    requirements TEXT,
    created_at TIMESTAMP,                 -- 職位首次出現時間
    last_seen_at TIMESTAMP                -- 最後一次被爬到的時間（用於追蹤下架）
);

-- 每次抓取快照
CREATE TABLE job_snapshots (
    id SERIAL PRIMARY KEY,
    job_id TEXT REFERENCES jobs(job_id) ON DELETE CASCADE,
    snapshot_time TIMESTAMP NOT NULL DEFAULT now(),  -- 抓取時間
    salary TEXT,
    work_type TEXT,
    employment_type TEXT,
    tags TEXT[],                    -- e.g. ['remote', 'contract'] if available
    source_url TEXT,                -- 此次抓取的來源 URL
    raw_html TEXT                   -- 保留原始 HTML 可作為 fallback/debug
);