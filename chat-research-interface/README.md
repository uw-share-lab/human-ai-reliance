# Chat Research Interface

React + TypeScript app that runs the interactive portion of the **Human-AI Reliance** study (Ferguson lab, University of Waterloo). Participants are routed to a specific moral-reasoning (AITA) or gender-bias (sexism) scenario, hold a short timed conversation with an AI, and have the full transcript saved to Supabase for later analysis.

Stage 3 of the study pipeline:

```
AITA-Data-Analysis  →  Generating-Explanations  →  chat-research-interface  →  Post-Study-Analysis
                                                       (this repo)                  (analysis)
                                                                                          ↑
                                                                                   Data_Wrangling
```

## Features

- **8 scenarios** — 4 AITA + 4 sexism, each with an AI starting opinion (sourced from the upstream Generating-Explanations repo).
- **Persistent Prolific ID** across all embedded scenarios — participant enters it once.
- **Start-button gate** prevents accidental session start when iframed in Qualtrics.
- **3-minute session timer** with auto-save and chat lock on timeout.
- **Server-side OpenAI proxy** — the `OPENAI_API_KEY` lives only in the Vercel function (`api/chat.js`); never bundled into client JS.
- **Supabase + RLS** for storage; `participants`, `conversations`, `messages` tables (schema in `supabase-setup.sql`).
- **Content moderation** before the call to OpenAI for sensitive topics.

## Stack

- React + TypeScript (CRA)
- OpenAI `gpt-5.5-2026-04-23` via the Responses API, proxied through `api/chat.js`
- Supabase Postgres + RLS
- Vercel (functions + hosting)

## Quick Start

### Prerequisites
- Node.js 18+
- Supabase account and project
- OpenAI API key
- Vercel account (for deployment)

### Installation

1. **Clone and install**:
   ```bash
   git clone <repository-url>
   cd chat-research-interface
   npm install
   ```

2. **Environment setup**:
   Create `.env` file:
   ```env
   # Server-side only — never exposed to the browser
   OPENAI_API_KEY=your_openai_api_key_here

   # Client-side Supabase (safe to expose)
   REACT_APP_SUPABASE_URL=your_supabase_project_url
   REACT_APP_SUPABASE_PUBLISHABLE_KEY=your_supabase_publishable_key
   REACT_APP_DEFAULT_TIMEOUT=3
   ```

3. **Database setup**:
   - Run the SQL commands in `supabase-setup.sql` in your Supabase project
   - This creates all necessary tables and security policies

4. **Start development**:
   ```bash
   vercel dev
   ```
   Visit `http://localhost:3000`. Use `vercel dev` (not `npm start`) so the `/api/chat` serverless function runs locally alongside the React app.

## Usage

### For Researchers
- **Development Testing**: Use `http://localhost:3000/scenario/aita-1?PROLIFIC_PID=test123`
- **Data Analysis**: Query Supabase tables for conversation data
- **Scenario Management**: Modify scenarios in `src/data/scenarios.ts`

### For Qualtrics Integration
1. Deploy to Vercel (see deployment section)
2. Create HTML/CSS questions in Qualtrics
3. Embed scenarios directly (Prolific ID collection is handled automatically):
   ```html
   <iframe src="https://your-domain.com/scenario/aita-1" 
           width="100%" height="900px" frameborder="0"
           scrolling="no" style="border: none; overflow: hidden;"></iframe>
   ```
4. **New Feature**: Prolific ID persists across all embedded scenarios - users only enter it once!
5. **Auto-scroll Prevention**: The app automatically detects iframe embedding and prevents page jumping/centering issues in Qualtrics

## Scenarios

### AITA (Am I The Asshole) Scenarios
These focus on moral reasoning and ethical judgment:

- **aita-1**: Leash Rule Enforcement - Park safety vs. individual freedom
- **aita-2**: Competitive Grading Help - Academic competition vs. cooperation  
- **aita-3**: Brownie Photo Drama - Family dynamics and respect
- **aita-4**: Privacy Lock Controversy - Adolescent privacy vs. parental authority

### Sexism Scenarios
These explore gender dynamics and workplace bias:

- **sexism-1**: Women's Duty to Have Children - Reproductive autonomy
- **sexism-2**: Apologizing for Swearing - Gender-based assumptions
- **sexism-3**: Age Double Standards - Gender and aging stereotypes
- **sexism-4**: Gendered Caregiving Assumptions - Caretaker role assumptions

Each scenario includes:
- Detailed context and background
- AI starting opinion to initiate discussion
- Built-in conversation starters and follow-up prompts

## Technical Architecture

### Frontend (React + TypeScript)
- **Components**: Modular chat interface, scenario router, status pages
- **Routing**: React Router with scenario-specific URLs
- **State Management**: React hooks for conversation state
- **Styling**: Custom CSS with responsive design

### Backend Services
- **Database**: Supabase PostgreSQL with real-time capabilities
- **AI Integration**: OpenAI `gpt-5.5-2026-04-23` via the Responses API (`/v1/responses`), proxied through a Vercel serverless function (`api/chat.js`) — the API key never reaches the browser
- **Authentication**: Supabase anonymous access with participant tracking

### Data Model
```
conversations
├── id (UUID)
├── prolific_id (TEXT)
├── scenario_id (TEXT)  
├── study_type (aita|sexism)
├── session_data (JSONB)
├── timing and completion data
└── metadata

messages
├── conversation_id (FK)
├── message_type (user|ai)
├── content (TEXT)
├── timestamp
└── sequence_number

participants  
├── prolific_id (UNIQUE)
├── total_conversations
└── metadata
```

## Deployment

### Vercel Deployment
1. **Connect Repository**: Link your GitHub repo to Vercel
2. **Environment Variables**: Add all `REACT_APP_*` variables in Vercel dashboard
3. **Deploy**: Automatic deployment on push to main branch
4. **Custom Domain**: Configure your research domain in Vercel

### Environment Variables for Production
Set these in the Vercel dashboard (Settings → Environment Variables):

```bash
# Server-only — set as Production + Preview, never exposed to browser
OPENAI_API_KEY=sk-proj-...

# Client-side — safe to expose, prefixed with REACT_APP_
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_PUBLISHABLE_KEY=sb_publishable_...
REACT_APP_DEFAULT_TIMEOUT=3
```

### Security Considerations
- **OpenAI API key is server-side only** — lives in `OPENAI_API_KEY` (no `REACT_APP_` prefix), proxied through `api/chat.js`. It is never bundled into client JavaScript.
- Supabase RLS (Row Level Security) enabled
- Content moderation for inappropriate messages
- No personal data stored beyond Prolific IDs
- CORS headers configured for Qualtrics embedding

## Data Collection & Privacy

### What Data is Collected
- **Conversation Data**: Complete chat history with timestamps
- **Timing Data**: Session start/end, response times, total duration
- **Participant Data**: Prolific ID, conversation count, session metadata
- **Technical Data**: User agent, interaction count (no IP addresses)

### Privacy Compliance
- Anonymous participant identification via Prolific IDs only
- No personally identifiable information collected
- Data stored in EU-compliant Supabase infrastructure
- Participants can end sessions early at any time, with chat locked but conversation history remaining accessible

### Data Analysis
Use the Supabase dashboard or connect to PostgreSQL for analysis:
```sql
-- Get conversation statistics
SELECT * FROM get_research_stats();

-- Analyze conversation length by scenario
SELECT scenario_id, AVG(duration_ms/60000) as avg_minutes
FROM conversation_summary 
GROUP BY scenario_id;

-- Export messages for qualitative analysis  
SELECT c.prolific_id, c.scenario_id, m.content, m.message_type
FROM conversations c 
JOIN messages m ON c.id = m.conversation_id
ORDER BY c.start_time, m.sequence_number;
```

## Development

### Project Structure
```
api/
└── chat.js                  # Serverless function — OpenAI proxy (key never in browser)
src/
├── components/              # React components
│   ├── ChatInterface.tsx        # Main chat interface
│   ├── Home.tsx                # Scenario selection page
│   └── ScenarioRouter.tsx      # Route validation
├── data/                    # Static data
│   └── scenarios.ts             # All scenario definitions
├── services/                # External integrations
│   ├── conversationService.ts   # Database operations
│   ├── openaiService.ts         # Calls /api/chat (no key here)
│   └── supabaseClient.ts        # Database client
├── styles/                  # CSS files
├── types/                   # TypeScript definitions
└── App.tsx                  # Main application
```

### Adding New Scenarios
1. Add scenario data to `src/data/scenarios.ts`
2. Include AI starting opinion for conversation initiation
3. Test with `http://localhost:3000/scenario/your-new-id`
4. Update documentation

### Customizing AI Behavior
- **System prompt / conversation style**: edit `buildSystemPrompt()` in `api/chat.js`
- **Safety filtering rules**: edit `isContentAppropriate()` in `src/services/openaiService.ts`
- **Response length or model**: edit `max_output_tokens` and `model` in `api/chat.js`

## Troubleshooting

### Common Issues
- **Build Errors**: Check TypeScript errors, often missing dependencies
- **Database Connection**: Verify Supabase environment variables
- **OpenAI Errors**: Check API key and rate limits
- **Qualtrics Embedding**: Ensure CORS headers and iframe dimensions

### Development Tips
- Use browser dev tools to monitor API calls
- Check Supabase logs for database issues  
- Test timeout functionality with shorter durations
- Validate participant ID handling with various formats

## Research Best Practices

### Study Design
- Test all scenarios thoroughly before launch
- Consider counterbalancing scenario order
- Monitor session completion rates
- Plan for technical support during data collection

### Data Quality
- Review AI responses for consistency
- Check for participant engagement metrics
- Monitor for unusual conversation patterns
- Validate data completeness before analysis

## Contributing

1. Fork the repository
2. Create feature branches for new functionality
3. Test thoroughly with real scenarios
4. Update documentation for any changes
5. Submit pull requests with clear descriptions

## Additional documentation

- [`DEPLOYMENT.md`](./DEPLOYMENT.md) — Vercel deployment guide
- [`QUALTRICS_INTEGRATION.md`](./QUALTRICS_INTEGRATION.md) — Qualtrics survey embedding
- [`IMPLEMENTATION_SUMMARY.md`](./IMPLEMENTATION_SUMMARY.md) — feature & status overview
- [`FILE_STRUCTURE.md`](./FILE_STRUCTURE.md) — repo layout
- [`.env.example`](./.env.example) — environment variable template
- [`supabase-setup.sql`](./supabase-setup.sql) — DB schema + RLS policies
- [`rls-fix.sql`](./rls-fix.sql) — supplemental RLS fix for anonymous upsert operations

## Support

For technical issues:
1. Check the troubleshooting section in the relevant documentation files
2. Review Supabase and OpenAI service status
3. Test with minimal scenarios first
4. Check browser console for error messages

## License

This research tool is intended for academic use. Please ensure compliance with your institution's IRB requirements and data protection regulations.