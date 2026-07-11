# Project File Structure

```
chat-research-interface/
├── README.md                       # Main project overview
├── DEPLOYMENT.md                   # Vercel deployment guide
├── QUALTRICS_INTEGRATION.md        # Qualtrics survey embedding
├── IMPLEMENTATION_SUMMARY.md       # Feature & status overview
├── FILE_STRUCTURE.md               # This file
├── .env.example                    # Environment variables template
│
├── package.json                    # Dependencies & npm scripts
├── tsconfig.json                   # TypeScript config
├── vercel.json                     # Vercel deployment config
├── supabase-setup.sql              # Database schema + RLS policies
│
├── public/
│   └── index.html                  # HTML template
│
├── api/
│   └── chat.js                     # Vercel serverless OpenAI proxy
│                                   #   (keeps OPENAI_API_KEY off the browser)
│
└── src/
    ├── App.tsx                     # Main app component
    ├── App.css                     # Global styles
    ├── index.tsx                   # Entry point
    │
    ├── components/
    │   ├── ChatInterface.tsx       # Main chat UI
    │   ├── Home.tsx                # Scenario selection
    │   ├── ProlificIdEntry.tsx     # Persistent participant ID entry
    │   └── ScenarioRouter.tsx      # Route validation
    │
    ├── data/
    │   └── scenarios.ts            # All 8 research scenarios
    │
    ├── services/
    │   ├── conversationService.ts  # Supabase reads/writes
    │   ├── openaiService.ts        # Calls /api/chat (no key here)
    │   └── supabaseClient.ts       # Supabase client setup
    │
    ├── styles/
    │   ├── ChatInterface.css
    │   ├── Home.css
    │   └── ProlificIdEntry.css
    │
    └── types/
        └── index.ts                # TypeScript types
```

## Notes

- `api/chat.js` runs as a Vercel serverless function — never bundled into the client.
- `supabase-setup.sql` is the source of truth for the DB schema. Apply it in the Supabase SQL editor before first deploy.
- `vercel.json` pins the Node runtime so `fetch` and the Responses API call in `api/chat.js` work.
- Anything under `build/` and `node_modules/` is generated — gitignored.
