# Deployment Guide

## 🚀 Production Deployment Status: **READY**

This guide covers deploying the **production-ready** Chat Research Interface to Vercel. The application is fully tested and configured for immediate deployment.

## ✅ Pre-Deployment Checklist

Before deploying, ensure you have:

- ✅ **Supabase Database**: Set up using `SUPABASE_SETUP.md`
- ✅ **OpenAI API Key**: GPT-4 access for chat functionality
- ✅ **GitHub Repository**: All code committed and pushed
- ✅ **Vercel Account**: Free or paid plan
- ✅ **Clean Codebase**: All unnecessary files removed

## Vercel Deployment

### 1. Prepare Repository

Ensure your repository includes:

- All source code
- `vercel.json` configuration file
- Updated `.env.example` (without actual keys)
- Documentation files

```bash
# Add and commit all changes
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### 2. Connect to Vercel

1. **Sign up/Login**: Go to [vercel.com](https://vercel.com)
2. **Import Project**: Click "Import Project"
3. **Connect GitHub**: Authorize Vercel to access your repository
4. **Select Repository**: Choose your chat-research-interface repo
5. **Configure Project**: Vercel will auto-detect React settings

### 3. Configure Environment Variables

The `vercel.json` file references environment variables using Vercel's `@` syntax. You need to add the actual values in the Vercel dashboard:

**In Vercel Dashboard → Settings → Environment Variables:**

| Variable Name       | Value                              | Notes                       |
| ------------------- | ---------------------------------- | --------------------------- |
| `openai_api_key`    | `sk-proj-your-actual-key`          | ⚠️ Your OpenAI API key      |
| `supabase_url`      | `https://your-project.supabase.co` | Your Supabase project URL   |
| `supabase_anon_key` | `eyJhbGciOiJIUzI1NiIs...`          | Your Supabase anonymous key |

**The `vercel.json` file maps these to React environment variables:**

```json
{
  "build": {
    "env": {
      "REACT_APP_OPENAI_API_KEY": "@openai_api_key",
      "REACT_APP_SUPABASE_URL": "@supabase_url",
      "REACT_APP_SUPABASE_ANON_KEY": "@supabase_anon_key",
      "REACT_APP_DEFAULT_TIMEOUT": "5"
    }
  }
}
```

**Security Notes:**

- ✅ `vercel.json` is safe to commit (contains no secrets)
- ✅ Environment variable references use `@` syntax (not actual values)
- ✅ Actual secrets are stored securely in Vercel dashboard
- ⚠️ Never commit `.env` file with real API keys

### 4. Deploy

1. **Initial Deploy**: Click "Deploy" in Vercel dashboard
2. **Wait for Build**: Monitor build logs for errors
3. **Verify Success**: Check deployment URL when complete
4. **Test Application**: Visit your live URL

### 5. Custom Domain (Optional)

For professional research URLs:

1. **Domain Settings**: Vercel dashboard → Settings → Domains
2. **Add Domain**: Enter your domain (e.g., `research.youruni.edu`)
3. **Configure DNS**: Point your domain to Vercel's servers
4. **SSL Certificate**: Automatically provisioned

## Post-Deployment Testing

### 1. Basic Functionality

Test core features on your live deployment:

```bash
# Visit deployment URL
https://your-project.vercel.app

# Test scenario access
https://your-project.vercel.app/scenario/aita-1?PROLIFIC_PID=test123

# Verify database connection by completing a conversation
```

### 2. Qualtrics Integration Test

Create a test Qualtrics survey:

1. **HTML/CSS Question**: Add question type in Qualtrics
2. **Iframe Embed**:
   ```html
   <iframe
     src="https://your-project.vercel.app/scenario/aita-1?PROLIFIC_PID=${e://Field/PROLIFIC_PID}"
     width="100%"
     height="900px"
     frameborder="0"
   >
   </iframe>
   ```
3. **Test Survey**: Preview and complete a full conversation
4. **Verify Data**: Check Supabase tables for stored data

### 3. Performance Testing

Monitor key metrics:

- Page load times (should be < 3 seconds)
- AI response times (typically 2-5 seconds)
- Database connection stability
- Session timeout functionality

## Qualtrics Integration

### Survey Setup

1. **Create Survey**: New Qualtrics survey for your research
2. **Add Demographics**: Collect basic participant info first
3. **HTML/CSS Questions**: One for each scenario you want to test
4. **Piped Text**: Pass Prolific ID through survey flow

### Question Configuration

For each scenario question:

1. **Question Type**: HTML/CSS
2. **Question Text**: Brief scenario description
3. **HTML Content**:
   ```html
   <div style="width: 100%; height: 900px;">
     <iframe
       src="https://your-domain.vercel.app/scenario/aita-1?PROLIFIC_PID=${e://Field/PROLIFIC_PID}&return_url=${e://Field/ReturnURL}"
       width="100%"
       height="100%"
       frameborder="0"
       style="border: none;"
     >
     </iframe>
   </div>
   ```

### Flow Logic

Set up survey flow:

1. **Consent & Demographics**
2. **Random Assignment** to scenario order
3. **Scenario Questions** (embedded chat interface)
4. **Post-Chat Questions** (reflection, demographics)
5. **Debriefing**

### Advanced Features

- **Counterbalancing**: Randomize scenario order
- **Attention Checks**: Verify engagement
- **Data Validation**: Check completion status
- **Return URLs**: Optional parameters (sessions now lock in-place instead of redirecting)

## Monitoring & Analytics

### Application Monitoring

Vercel provides built-in analytics:

- **Function Logs**: Monitor API calls and errors
- **Performance**: Track page load and response times
- **Usage**: Monitor bandwidth and request volume

### Research Data Monitoring

Use Supabase dashboard:

- **Table Editor**: View raw conversation data
- **SQL Editor**: Run analytics queries
- **API Logs**: Monitor database performance

### Custom Analytics Queries

```sql
-- Daily participation rates
SELECT
  DATE(start_time) as date,
  COUNT(*) as total_sessions,
  COUNT(*) FILTER (WHERE completed_normally = true) as completed
FROM conversations
GROUP BY DATE(start_time)
ORDER BY date DESC;

-- Average conversation length by scenario
SELECT
  scenario_id,
  AVG(duration_ms/60000) as avg_minutes,
  COUNT(*) as total_conversations
FROM conversations
WHERE duration_ms IS NOT NULL
GROUP BY scenario_id;

-- Completion rates
SELECT
  study_type,
  ROUND(AVG(CASE WHEN completed_normally THEN 1 ELSE 0 END) * 100, 2) as completion_rate
FROM conversations
GROUP BY study_type;
```

## Troubleshooting

### Common Deployment Issues

**Build Failures:**

- Check TypeScript errors in build logs
- Verify all dependencies are listed in package.json
- Ensure environment variables are set correctly

**Runtime Errors:**

- Monitor Function logs in Vercel dashboard
- Check browser console on deployed site
- Test API endpoints directly

**Database Connection Issues:**

- Verify Supabase environment variables
- Check Supabase project status (not paused)
- Test database queries in Supabase SQL editor

### Qualtrics Embedding Issues

**Iframe Not Loading:**

- Check CORS headers in vercel.json
- Verify X-Frame-Options configuration
- Test outside of Qualtrics first

**Data Not Saving:**

- Monitor Supabase tables during test sessions
- Check browser console for JavaScript errors
- Verify Prolific ID is being passed correctly

**Session Timeout Problems:**

- Test with shorter timeouts for debugging
- Verify session locks properly when timeout occurs
- Check that chat interface disables correctly and status banner appears

## Security Considerations

### API Key Security

- Use environment variables, never hardcode keys
- Regularly rotate OpenAI API keys
- Monitor API usage for unusual patterns
- Set up usage limits and billing alerts

### Data Privacy

- Enable Supabase Row Level Security
- No PII storage beyond Prolific IDs
- Regular data export and local backups
- Comply with institutional IRB requirements

### CORS & Embedding

- Whitelist specific domains when possible
- Monitor for unauthorized usage
- Regular security updates for dependencies

## Scaling Considerations

### Vercel Limits

- **Free Tier**: 100GB bandwidth/month, 6,000 build minutes
- **Pro Tier**: 1TB bandwidth, unlimited builds
- **Function Timeout**: 10 seconds (Hobby), 60 seconds (Pro)

### Supabase Limits

- **Free Tier**: 500MB storage, 2GB bandwidth
- **Pro Tier**: 8GB storage, unlimited bandwidth
- **Connection Limits**: 60 concurrent connections (free)

### OpenAI Rate Limits

- **GPT-4**: 500 requests/minute on paid plans
- **Usage Monitoring**: Set up billing alerts
- **Error Handling**: Implement retry logic and graceful degradation

## 🔍 Post-Deployment Verification

### **1. Deployment Success Check**

After deployment completes:

- ✅ Visit your Vercel deployment URL
- ✅ Home page loads without errors
- ✅ All scenario URLs work: `your-domain.com/scenario/aita-1`
- ✅ Prolific ID entry screen appears and functions
- ✅ Test conversation flow with AI responses
- ✅ Verify data saves to Supabase tables

### **2. End-to-End Testing**

```bash
# Test scenario access
curl -I https://your-domain.vercel.app/scenario/aita-1
# Should return: HTTP/2 200

# Test all 8 scenarios
for scenario in aita-1 aita-2 aita-3 aita-4 sexism-1 sexism-2 sexism-3 sexism-4; do
  echo "Testing $scenario..."
  curl -s -o /dev/null -w "%{http_code}" https://your-domain.vercel.app/scenario/$scenario
done
```

### **3. Qualtrics Integration Test**

- ✅ Create test Qualtrics survey with iframe
- ✅ Test Prolific ID persistence across scenarios
- ✅ Verify conversation data appears in Supabase
- ✅ Test timeout and session lock functionality
- ✅ Confirm mobile responsiveness

### **4. Production Monitoring Setup**

- Set up Vercel function monitoring
- Configure Supabase database alerts
- Monitor OpenAI API usage and billing
- Set up error logging and notifications

## Backup & Recovery

### Automated Backups

Supabase provides:

- Daily automated backups (7-day retention)
- Point-in-time recovery (paid plans)
- Real-time replication options

### Manual Backup Strategy

```sql
-- Export all research data
COPY (
  SELECT
    c.*,
    json_agg(
      json_build_object(
        'content', m.content,
        'type', m.message_type,
        'timestamp', m.timestamp,
        'sequence', m.sequence_number
      ) ORDER BY m.sequence_number
    ) as messages
  FROM conversations c
  LEFT JOIN messages m ON c.id = m.conversation_id
  GROUP BY c.id
) TO '/tmp/research_backup.json';
```

### Recovery Procedures

1. **Data Loss**: Restore from Supabase backup
2. **Deployment Issues**: Rollback via Vercel dashboard
3. **Configuration Problems**: Redeploy with corrected environment variables

## Production Checklist

Before launching your study:

### Technical Validation

- [ ] All scenarios load correctly
- [ ] Database connections stable
- [ ] AI responses appropriate and consistent
- [ ] Timeout functionality works
- [ ] Data appears in Supabase tables
- [ ] Qualtrics embedding functions properly

### Research Validation

- [ ] IRB approval obtained
- [ ] Consent forms integrated
- [ ] Data collection plan documented
- [ ] Backup procedures tested
- [ ] Participant support contact available

### Performance Testing

- [ ] Load testing with concurrent users
- [ ] Response time monitoring
- [ ] Error rate tracking
- [ ] Resource usage optimization

## Maintenance

### Regular Tasks

- **Weekly**: Monitor participation rates and data quality
- **Monthly**: Review API usage and costs
- **Quarterly**: Update dependencies and security patches
- **As Needed**: Scale resources based on study requirements

### Updates and Improvements

To update your deployment:

1. Make changes locally
2. Test thoroughly in development
3. Commit and push to main branch
4. Vercel automatically redeploys
5. Verify changes on live site

## Support Resources

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **Supabase Documentation**: [supabase.com/docs](https://supabase.com/docs)
- **OpenAI API Documentation**: [platform.openai.com/docs](https://platform.openai.com/docs)
- **Qualtrics Support**: [www.qualtrics.com/support](https://www.qualtrics.com/support)

Your research interface is now ready for production deployment! 🚀
