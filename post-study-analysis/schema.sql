-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.conversations (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  interaction_count integer DEFAULT 0,
  completed_normally boolean DEFAULT false,
  timed_out boolean DEFAULT false,
  prolific_id text NOT NULL,
  scenario_id text NOT NULL,
  study_type text NOT NULL CHECK (study_type = ANY (ARRAY['aita'::text, 'sexism'::text])),
  session_data jsonb NOT NULL,
  start_time timestamp with time zone NOT NULL,
  end_time timestamp with time zone,
  duration_ms integer,
  user_agent text,
  ip_address inet,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT conversations_pkey PRIMARY KEY (id)
);
CREATE TABLE public.messages (
  conversation_id uuid,
  message_type text NOT NULL CHECK (message_type = ANY (ARRAY['user'::text, 'ai'::text])),
  content text NOT NULL,
  timestamp timestamp with time zone NOT NULL,
  sequence_number integer NOT NULL,
  response_time_seconds numeric,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT messages_pkey PRIMARY KEY (id),
  CONSTRAINT messages_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id)
);
CREATE TABLE public.participants (
  prolific_id text NOT NULL UNIQUE,
  metadata jsonb,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  first_seen timestamp with time zone DEFAULT now(),
  total_conversations integer DEFAULT 0,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT participants_pkey PRIMARY KEY (id)
);