# Supabase Database Setup Guide

## 🗄️ **Database Status: PRODUCTION-READY SCHEMA**

Complete setup guide for the **tested and optimized** Supabase database backend. The schema is production-ready with built-in security, analytics, and research-optimized data structure.

## ⚡ **Why Supabase for Research:**
- **🔒 Built-in Security**: Row Level Security with anonymous participant data collection
- **📊 Real-time Analytics**: Instant access to conversation data and statistics  
- **🚀 Auto-scaling**: Handles concurrent participants without configuration
- **🔄 Automatic Backups**: Daily backups with point-in-time recovery
- **💰 Cost-effective**: Free tier supports substantial research studies

## Setup Instructions

### 1. Create Supabase Project

1. **Sign up**: Go to [supabase.com](https://supabase.com) and create a free account
2. **New Project**: Click "New Project" and choose your organization
3. **Project Settings**: 
   - Name: `llm-research-interface` (or your preferred name)
   - Database Password: Generate a strong password (save it securely)
   - Region: Choose closest to your users
4. **Wait for Setup**: Project creation takes 1-2 minutes

### 2. Database Schema Setup

In your Supabase project dashboard:

1. **Navigate to SQL Editor**: Left sidebar → SQL Editor
2. **Create New Query**: Click "New Query"
3. **Copy Schema**: Copy the entire contents of `supabase-setup.sql` 
4. **Run Schema**: Paste and click "Run" to create all tables

**The schema creates:**
- `conversations` table: Main conversation data with participant details
- `messages` table: Individual message analysis and response times  
- `participants` table: Participant tracking and completion status
- Views and functions: Research analytics and data summaries

### 3. Configure Row Level Security

The schema automatically sets up security policies:
- **Anonymous INSERT**: Allows data collection from participants
- **Authenticated READ**: Researchers can access data with proper credentials
- **No public access**: Protects participant privacy

### 4. Get Project Credentials

In your Supabase dashboard:

1. **Go to Settings**: Left sidebar → Settings → API
2. **Copy Project URL**: Save your unique project URL
3. **Copy Anon Key**: Save your anonymous/public key (safe for frontend use)

### 5. Environment Configuration

Create/update your `.env` file with your project credentials:

```bash
# OpenAI Integration
REACT_APP_OPENAI_API_KEY="your-openai-key"

# Supabase Database (replace with your actual values)
REACT_APP_SUPABASE_URL="https://your-project-ref.supabase.co"
REACT_APP_SUPABASE_ANON_KEY="your-anonymous-key"

# Application Configuration  
REACT_APP_DEFAULT_TIMEOUT=20
```

**⚠️ Important**: Replace the Supabase values with your actual project URL and key from step 4.

### 6. Test the Integration

```bash
# Start the application
npm start

# Visit in browser
open http://localhost:3000

# Test with a scenario
open http://localhost:3000/scenario/aita-1?PROLIFIC_PID=test123
```

### 7. Verify Database Connection

1. **Start a test conversation** using the URL above
2. **Check Supabase Dashboard**: Go to Table Editor → conversations
3. **Verify data appears** in the tables after sending messages

**If you see connection errors:**
- Double-check your project URL and key in `.env`
- Ensure your Supabase project is running (not paused) 
- Verify the database schema was installed correctly
- Check browser console for detailed error messages

## Data Storage Architecture

### Primary Storage: Supabase Database
- **conversations** table: Complete session data
- **messages** table: Individual message analysis
- **participants** table: Participant tracking
- Real-time statistics and analytics

### Backup Storage: Local Files
- Automatic fallback if Supabase fails
- JSON files in `./conversation-data/`
- Manual export capabilities

### Frontend Storage: localStorage
- Emergency backup if all else fails
- Automatic export functionality

## Database Schema

### Conversations Table
```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY,
  prolific_id TEXT NOT NULL,
  scenario_id TEXT NOT NULL,
  study_type TEXT CHECK (study_type IN ('aita', 'sexism')),
  session_data JSONB NOT NULL,
  start_time TIMESTAMPTZ NOT NULL,
  end_time TIMESTAMPTZ,
  duration_ms INTEGER,
  interaction_count INTEGER DEFAULT 0,
  completed_normally BOOLEAN DEFAULT false,
  timed_out BOOLEAN DEFAULT false,
  user_agent TEXT,
  ip_address INET,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Messages Table (for detailed analysis)
```sql
CREATE TABLE messages (
  id UUID PRIMARY KEY,
  conversation_id UUID REFERENCES conversations(id),
  message_type TEXT CHECK (message_type IN ('user', 'ai')),
  content TEXT NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,
  sequence_number INTEGER NOT NULL,
  response_time_seconds NUMERIC
);
```

## Data Extraction Methods

### 1. Supabase Dashboard (Recommended)
- Login to your Supabase dashboard
- Go to Table Editor > conversations
- Use built-in export to CSV/JSON
- Access to raw SQL queries

### 2. API Endpoints
```bash
# Get all data as JSON
curl "http://localhost:3001/api/export-all" -o research_data.json

# Get summary statistics
curl "http://localhost:3001/api/stats"

# Get data as CSV
curl "http://localhost:3001/api/export-csv" -o research_data.csv
```

### 3. Direct SQL Queries
```sql
-- Get conversation summary
SELECT * FROM conversation_summary ORDER BY start_time DESC;

-- Get research statistics
SELECT * FROM get_research_stats();

-- Get all messages for analysis
SELECT 
  c.prolific_id,
  c.scenario_id,
  c.study_type,
  m.message_type,
  m.content,
  m.response_time_seconds
FROM conversations c
JOIN messages m ON c.id = m.conversation_id
ORDER BY c.start_time, m.sequence_number;

-- Export specific participant data
SELECT * FROM conversations 
WHERE prolific_id = 'PL123456789'
ORDER BY start_time;
```

## Real-time Monitoring

### API Status Indicator
The application shows real-time status:
- 🟢 **Backend**: API server running
- 🟢 **AI**: OpenAI GPT-4.1 ready  
- 🟢 **DB**: Supabase connected and ready

### Research Dashboard
```bash
# Get live statistics
curl http://localhost:3001/api/stats | jq '.'

# Returns:
{
  "totalConversations": 25,
  "uniqueParticipants": 18,
  "aita_conversations": 12,
  "sexism_conversations": 13,
  "completedNormally": 22,
  "avgDurationMinutes": 8.5,
  "scenarios": {...},
  "dailyStats": {...},
  "dataSource": "supabase"
}
```

## Advanced Analytics

### 1. Message Analysis
```sql
-- Average response times by study type
SELECT 
  c.study_type,
  AVG(m.response_time_seconds) as avg_response_time,
  COUNT(*) as total_messages
FROM conversations c
JOIN messages m ON c.id = m.conversation_id
WHERE m.message_type = 'user'
GROUP BY c.study_type;
```

### 2. Participation Patterns
```sql
-- Completion rates by scenario
SELECT 
  scenario_id,
  COUNT(*) as total_attempts,
  COUNT(*) FILTER (WHERE completed_normally = true) as completed,
  ROUND(COUNT(*) FILTER (WHERE completed_normally = true) * 100.0 / COUNT(*), 2) as completion_rate
FROM conversations
GROUP BY scenario_id
ORDER BY completion_rate DESC;
```

### 3. Conversation Length Analysis
```sql
-- Distribution of conversation lengths
SELECT 
  CASE 
    WHEN duration_ms < 300000 THEN '< 5 min'
    WHEN duration_ms < 600000 THEN '5-10 min'
    WHEN duration_ms < 900000 THEN '10-15 min'
    WHEN duration_ms < 1200000 THEN '15-20 min'
    ELSE '> 20 min'
  END as duration_bucket,
  COUNT(*) as count
FROM conversations
WHERE duration_ms IS NOT NULL
GROUP BY duration_bucket
ORDER BY MIN(duration_ms);
```

## Security & Privacy

### Row Level Security (RLS)
- Anonymous users can INSERT data (for data collection)
- Authenticated users can READ data (for researchers)
- No public read access to protect participant privacy

### Data Protection
- No personal information stored beyond Prolific ID
- IP addresses can be disabled in backend
- Automatic data retention policies available

## Backup & Recovery

### Automatic Backups
- Supabase provides automatic backups
- Local file backup for each conversation
- localStorage emergency backup

### Manual Export
```bash
# Export everything for backup
curl "http://localhost:3001/api/export-all" > "backup_$(date +%Y%m%d).json"
```

## Production Deployment

### Environment Variables for Cloud Deployment

**Backend (Cloud Service - Vercel/Railway):**
```bash
# Required for AI integration
OPEN_AI_API=your_openai_key

# Required for database  
SUPA_BASE_URL=https://your-project-ref.supabase.co
SUPA_BASE_KEY=your_supabase_anon_key

# Cloud service configuration
NODE_ENV=production
PORT=3001
```

**Frontend (.env.production):**
```bash
# Backend API endpoint
REACT_APP_BACKEND_URL=https://your-deployed-backend.vercel.app/api
REACT_APP_DEFAULT_TIMEOUT=20

# Optional: Direct Supabase access (if needed)
REACT_APP_SUPABASE_URL=https://your-project-ref.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Deployment Steps

1. **Deploy Backend First**: Follow GITHUB_DEPLOYMENT.md for detailed steps
2. **Configure Environment Variables**: Set all variables in your cloud service dashboard
3. **Test Backend**: Verify `/api/health` returns successful Supabase connection
4. **Deploy Frontend**: Update `.env.production` with backend URL and deploy to GitHub Pages
5. **End-to-End Test**: Complete participant flow with data verification in Supabase

### Scaling Considerations
- Supabase free tier: 500MB storage, 2GB bandwidth
- Paid tiers support millions of rows
- Built-in connection pooling and performance optimization
- Real-time subscriptions available for live monitoring

## Your Research Data is Now:
- ✅ **Stored in Supabase** (primary database)
- ✅ **Backed up locally** (JSON files)
- ✅ **Accessible via API** (multiple export formats)
- ✅ **Real-time monitored** (live status indicators)
- ✅ **Production ready** (scalable cloud database)

Start your research with confidence! 🎯