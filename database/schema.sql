-- =============================================================================
-- Student Registration System - PostgreSQL schema
--
-- HOW TO USE:
-- 1. Create the database (run this from psql, connected as a superuser,
--    e.g. `psql -U postgres`):
--
--      CREATE DATABASE student_registration;
--
-- 2. Connect to it:
--
--      \c student_registration
--
-- 3. Run this whole file:
--
--      \i database/schema.sql
--
--    Or, from the command line in one step:
--
--      psql -U postgres -d student_registration -f database/schema.sql
--
-- Note: the FastAPI app also creates this table automatically on startup
-- (via SQLAlchemy) if it does not already exist, so running this script
-- manually is optional but recommended for clarity/evaluation purposes.
-- =============================================================================

CREATE TABLE IF NOT EXISTS students (
    id              SERIAL PRIMARY KEY,
    first_name      VARCHAR(100)  NOT NULL,
    last_name       VARCHAR(100)  NOT NULL,
    email           VARCHAR(255)  NOT NULL UNIQUE,
    mobile          VARCHAR(10)   NOT NULL UNIQUE,
    date_of_birth   DATE          NOT NULL,
    gender          VARCHAR(10)   NOT NULL,
    course          VARCHAR(10)   NOT NULL,
    address         VARCHAR(500)  NOT NULL,
    city            VARCHAR(100)  NOT NULL,
    state           VARCHAR(100)  NOT NULL,
    pincode         VARCHAR(6)    NOT NULL,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- Helpful indexes for lookups used during duplicate checks.
CREATE INDEX IF NOT EXISTS idx_students_email  ON students (email);
CREATE INDEX IF NOT EXISTS idx_students_mobile ON students (mobile);
