-- Voice Agent System Database Migration
-- Simplified schema with voice_sessions and outbound_calls only
-- Tool execution is tracked within session analytics

-- Create voice session status enum
CREATE TYPE voice_session_status AS ENUM (
    'initializing',
    'active',
    'paused',
    'ended',
    'failed',
    'timeout'
);

-- Create agent type enum
CREATE TYPE agent_type AS ENUM (
    'personal_assistant',
    'outbound_caller',
    'emergency_response'
);

-- Create call status enum
CREATE TYPE call_status AS ENUM (
    'scheduled',
    'queued',
    'dialing',
    'ringing',
    'connected',
    'in_progress',
    'completed',
    'failed',
    'no_answer',
    'busy',
    'voicemail',
    'cancelled'
);

-- Create call purpose enum
CREATE TYPE call_purpose AS ENUM (
    'lead_generation',
    'customer_follow_up',
    'appointment_scheduling',
    'payment_reminder',
    'service_reminder',
    'quote_follow_up',
    'satisfaction_survey',
    'general_inquiry',
    'emergency_notification'
);

-- Create call outcome enum
CREATE TYPE call_outcome AS ENUM (
    'successful',
    'partial_success',
    'no_response',
    'callback_requested',
    'not_interested',
    'wrong_number',
    'do_not_call',
    'rescheduled',
    'voicemail_left',
    'technical_issue'
);

-- Create voice sessions table
CREATE TABLE voice_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL,
    user_id TEXT NOT NULL,
    agent_type agent_type NOT NULL,
    status voice_session_status NOT NULL DEFAULT 'initializing',
    
    -- LiveKit configuration
    livekit_room_name TEXT NOT NULL,
    livekit_room_token TEXT,
    session_timeout_minutes INTEGER NOT NULL DEFAULT 60,
    
    -- Session lifecycle
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    last_activity TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Context data (JSONB for flexibility)
    context_data JSONB NOT NULL DEFAULT '{
        "current_location": null,
        "current_job_id": null,
        "current_contact_id": null,
        "current_project_id": null,
        "session_metadata": {},
        "conversation_state": {}
    }',
    
    -- Analytics and tool execution tracking
    analytics_data JSONB NOT NULL DEFAULT '{
        "total_interactions": 0,
        "successful_actions": 0,
        "failed_actions": 0,
        "average_response_time_ms": null,
        "total_duration_seconds": null,
        "interruption_count": 0,
        "sentiment_score": null,
        "confidence_score": null,
        "tools_used": [],
        "tool_execution_log": []
    }',
    
    -- Conversation data
    conversation_transcript TEXT,
    audio_recording_url TEXT,
    
    -- Session settings
    voice_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    background_mode BOOLEAN NOT NULL DEFAULT FALSE,
    emergency_mode BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Metadata
    session_notes TEXT,
    error_log TEXT[] DEFAULT '{}',
    custom_settings JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT voice_sessions_business_id_fkey FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE,
    CONSTRAINT voice_sessions_timeout_positive CHECK (session_timeout_minutes > 0),
    CONSTRAINT voice_sessions_ended_after_started CHECK (ended_at IS NULL OR ended_at >= started_at),
    CONSTRAINT voice_sessions_last_activity_after_started CHECK (last_activity >= started_at)
);

-- Create outbound calls table
CREATE TABLE outbound_calls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL,
    campaign_id UUID,
    purpose call_purpose NOT NULL,
    status call_status NOT NULL DEFAULT 'scheduled',
    
    -- Recipient information (JSONB for flexibility)
    recipient_data JSONB NOT NULL DEFAULT '{
        "contact_id": null,
        "name": "",
        "phone_number": "",
        "email": null,
        "preferred_contact_time": null,
        "time_zone": "UTC",
        "language": "en",
        "do_not_call": false
    }',
    
    -- Call script (JSONB for flexibility)
    script_data JSONB NOT NULL DEFAULT '{
        "opening_script": "",
        "main_script": "",
        "closing_script": "",
        "objection_handling": {},
        "questions": [],
        "call_to_action": "",
        "max_duration_minutes": 10
    }',
    
    -- Call configuration
    priority INTEGER NOT NULL DEFAULT 1,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    retry_interval_minutes INTEGER NOT NULL DEFAULT 60,
    
    -- Scheduling
    scheduled_time TIMESTAMPTZ,
    actual_start_time TIMESTAMPTZ,
    actual_end_time TIMESTAMPTZ,
    
    -- Execution tracking
    current_attempt INTEGER NOT NULL DEFAULT 0,
    session_id UUID,
    livekit_room_name TEXT,
    
    -- Call outcome
    outcome call_outcome,
    outcome_notes TEXT,
    follow_up_required BOOLEAN NOT NULL DEFAULT FALSE,
    follow_up_date TIMESTAMPTZ,
    
    -- Analytics (JSONB for flexibility)
    analytics_data JSONB NOT NULL DEFAULT '{
        "dial_attempts": 0,
        "connection_duration_seconds": null,
        "talk_time_seconds": null,
        "hold_time_seconds": null,
        "sentiment_score": null,
        "engagement_score": null,
        "interruption_count": 0,
        "objections_raised": 0,
        "questions_asked": 0,
        "questions_answered": 0
    }',
    
    -- Audio and conversation
    conversation_transcript TEXT,
    audio_recording_url TEXT,
    
    -- Metadata
    created_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_modified TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT NOT NULL DEFAULT 'system',
    tags TEXT[] DEFAULT '{}',
    custom_fields JSONB DEFAULT '{}',
    
    -- Constraints
    CONSTRAINT outbound_calls_business_id_fkey FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE,
    CONSTRAINT outbound_calls_session_id_fkey FOREIGN KEY (session_id) REFERENCES voice_sessions(id) ON DELETE SET NULL,
    CONSTRAINT outbound_calls_priority_range CHECK (priority >= 1 AND priority <= 5),
    CONSTRAINT outbound_calls_max_attempts_positive CHECK (max_attempts > 0),
    CONSTRAINT outbound_calls_retry_interval_non_negative CHECK (retry_interval_minutes >= 0),
    CONSTRAINT outbound_calls_current_attempt_non_negative CHECK (current_attempt >= 0),
    CONSTRAINT outbound_calls_actual_end_after_start CHECK (actual_end_time IS NULL OR actual_start_time IS NULL OR actual_end_time >= actual_start_time),
    CONSTRAINT outbound_calls_follow_up_date_future CHECK (follow_up_date IS NULL OR follow_up_date > created_date)
);

-- Create indexes for performance optimization

-- Voice sessions indexes
CREATE INDEX idx_voice_sessions_business_id ON voice_sessions(business_id);
CREATE INDEX idx_voice_sessions_user_id ON voice_sessions(user_id);
CREATE INDEX idx_voice_sessions_status ON voice_sessions(status);
CREATE INDEX idx_voice_sessions_agent_type ON voice_sessions(agent_type);
CREATE INDEX idx_voice_sessions_started_at ON voice_sessions(started_at);
CREATE INDEX idx_voice_sessions_last_activity ON voice_sessions(last_activity);
CREATE INDEX idx_voice_sessions_business_status ON voice_sessions(business_id, status);
CREATE INDEX idx_voice_sessions_business_user ON voice_sessions(business_id, user_id);
CREATE INDEX idx_voice_sessions_emergency_mode ON voice_sessions(business_id, emergency_mode) WHERE emergency_mode = true;

-- Outbound calls indexes
CREATE INDEX idx_outbound_calls_business_id ON outbound_calls(business_id);
CREATE INDEX idx_outbound_calls_campaign_id ON outbound_calls(campaign_id);
CREATE INDEX idx_outbound_calls_status ON outbound_calls(status);
CREATE INDEX idx_outbound_calls_purpose ON outbound_calls(purpose);
CREATE INDEX idx_outbound_calls_priority ON outbound_calls(priority);
CREATE INDEX idx_outbound_calls_scheduled_time ON outbound_calls(scheduled_time);
CREATE INDEX idx_outbound_calls_session_id ON outbound_calls(session_id);
CREATE INDEX idx_outbound_calls_business_status ON outbound_calls(business_id, status);
CREATE INDEX idx_outbound_calls_business_purpose ON outbound_calls(business_id, purpose);
CREATE INDEX idx_outbound_calls_follow_up_required ON outbound_calls(business_id, follow_up_required, follow_up_date) WHERE follow_up_required = true;
CREATE INDEX idx_outbound_calls_high_priority ON outbound_calls(business_id, priority, scheduled_time) WHERE priority >= 4;

-- Create triggers for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_voice_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_voice_sessions_updated_at
    BEFORE UPDATE ON voice_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_voice_updated_at_column();

-- Create trigger for outbound calls last_modified
CREATE OR REPLACE FUNCTION update_outbound_calls_last_modified()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_modified = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_outbound_calls_last_modified
    BEFORE UPDATE ON outbound_calls
    FOR EACH ROW
    EXECUTE FUNCTION update_outbound_calls_last_modified();

-- Create trigger for voice session analytics and activity updates
CREATE OR REPLACE FUNCTION update_voice_session_activity()
RETURNS TRIGGER AS $$
BEGIN
    -- Update last_activity when analytics data changes (indicating tool usage)
    IF NEW.analytics_data IS DISTINCT FROM OLD.analytics_data THEN
        NEW.last_activity = NOW();
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_voice_session_activity_trigger
    BEFORE UPDATE ON voice_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_voice_session_activity();

-- Enable RLS on all tables
ALTER TABLE voice_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE outbound_calls ENABLE ROW LEVEL SECURITY;

-- Voice sessions RLS policies
CREATE POLICY voice_sessions_business_isolation ON voice_sessions
    FOR ALL
    USING (business_id = current_setting('app.current_business_id')::UUID);

-- Outbound calls RLS policies
CREATE POLICY outbound_calls_business_isolation ON outbound_calls
    FOR ALL
    USING (business_id = current_setting('app.current_business_id')::UUID);

-- Utility functions for voice agent operations

-- Function to get active voice sessions for a business
CREATE OR REPLACE FUNCTION get_active_voice_sessions(p_business_id UUID)
RETURNS TABLE(
    session_id UUID,
    user_id TEXT,
    agent_type agent_type,
    status voice_session_status,
    started_at TIMESTAMPTZ,
    last_activity TIMESTAMPTZ,
    emergency_mode BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        vs.id,
        vs.user_id,
        vs.agent_type,
        vs.status,
        vs.started_at,
        vs.last_activity,
        vs.emergency_mode
    FROM voice_sessions vs
    WHERE vs.business_id = p_business_id
    AND vs.status IN ('active', 'paused')
    ORDER BY vs.emergency_mode DESC, vs.started_at DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get scheduled outbound calls
CREATE OR REPLACE FUNCTION get_scheduled_outbound_calls(p_business_id UUID)
RETURNS TABLE(
    call_id UUID,
    priority INTEGER,
    scheduled_time TIMESTAMPTZ,
    purpose call_purpose,
    recipient_phone TEXT,
    current_attempt INTEGER,
    max_attempts INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        oc.id,
        oc.priority,
        oc.scheduled_time,
        oc.purpose,
        oc.recipient_data->>'phone_number' as recipient_phone,
        oc.current_attempt,
        oc.max_attempts
    FROM outbound_calls oc
    WHERE oc.business_id = p_business_id
    AND oc.status = 'scheduled'
    AND (oc.scheduled_time IS NULL OR oc.scheduled_time <= NOW())
    AND oc.current_attempt < oc.max_attempts
    ORDER BY oc.priority DESC, oc.scheduled_time ASC NULLS FIRST;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to cleanup expired voice sessions
CREATE OR REPLACE FUNCTION cleanup_expired_voice_sessions()
RETURNS INTEGER AS $$
DECLARE
    expired_count INTEGER;
BEGIN
    UPDATE voice_sessions 
    SET 
        status = 'timeout',
        ended_at = NOW()
    WHERE 
        status IN ('active', 'paused')
        AND (
            (started_at + INTERVAL '1 minute' * session_timeout_minutes) < NOW()
            OR (last_activity + INTERVAL '30 minutes') < NOW()
        );
    
    GET DIAGNOSTICS expired_count = ROW_COUNT;
    RETURN expired_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get voice session analytics
CREATE OR REPLACE FUNCTION get_voice_session_analytics(p_session_id UUID)
RETURNS TABLE(
    total_interactions BIGINT,
    successful_actions BIGINT,
    failed_actions BIGINT,
    avg_response_time_ms NUMERIC,
    total_duration_minutes NUMERIC,
    tools_used_count BIGINT,
    most_used_tools JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (vs.analytics_data->>'total_interactions')::BIGINT,
        (vs.analytics_data->>'successful_actions')::BIGINT,
        (vs.analytics_data->>'failed_actions')::BIGINT,
        (vs.analytics_data->>'average_response_time_ms')::NUMERIC,
        EXTRACT(EPOCH FROM (COALESCE(vs.ended_at, NOW()) - vs.started_at)) / 60 as total_duration_minutes,
        jsonb_array_length(vs.analytics_data->'tools_used') as tools_used_count,
        vs.analytics_data->'tool_execution_log' as most_used_tools
    FROM voice_sessions vs
    WHERE vs.id = p_session_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions to authenticated users
GRANT SELECT, INSERT, UPDATE, DELETE ON voice_sessions TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON outbound_calls TO authenticated;

-- Grant execute permissions on utility functions
GRANT EXECUTE ON FUNCTION get_active_voice_sessions(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION get_scheduled_outbound_calls(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION cleanup_expired_voice_sessions() TO authenticated;
GRANT EXECUTE ON FUNCTION get_voice_session_analytics(UUID) TO authenticated;

-- Create comments for documentation
COMMENT ON TABLE voice_sessions IS 'Voice agent sessions with LiveKit integration, conversation tracking, and tool execution analytics';
COMMENT ON TABLE outbound_calls IS 'Automated outbound call management with campaign integration and call outcome tracking';

COMMENT ON COLUMN voice_sessions.analytics_data IS 'JSON analytics including tool execution log, success rates, response times, and performance metrics';
COMMENT ON COLUMN voice_sessions.context_data IS 'JSON context including current job, contact, project, and conversation state';
COMMENT ON COLUMN outbound_calls.recipient_data IS 'JSON recipient information including contact details, preferences, and do-not-call status';
COMMENT ON COLUMN outbound_calls.script_data IS 'JSON call script including opening, main content, questions, and objection handling strategies'; 