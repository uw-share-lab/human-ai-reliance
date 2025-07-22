# Qualtrics Integration Guide

## 🎯 **Integration Status: PRODUCTION-READY**

Complete guide for embedding the **production-tested** Chat Research Interface into Qualtrics surveys. Features **revolutionary Prolific ID persistence** and **seamless multi-scenario support**.

## ✅ Prerequisites Checklist

Before starting, ensure you have:

- ✅ **Deployed Application**: Using `DEPLOYMENT.md` guide
- ✅ **Qualtrics Account**: With survey creation permissions
- ✅ **Prolific Study**: Set up for participant recruitment
- ✅ **Testing Environment**: For end-to-end verification

## 🚀 **Revolutionary Features**

### **🎯 Why This Integration is Superior:**

- **🔄 Persistent ID System**: Users enter Prolific ID once, works across ALL embedded scenarios
- **🎯 Start Button Control**: Interactive overlay prevents accidental simultaneous interactions 
- **🎪 Direct Embedding**: Each scenario embeds directly - no landing page or navigation required
- **🔗 Automatic Data Linking**: All conversations automatically connected to participant
- **📱 Universal Compatibility**: Works on desktop, tablet, and mobile within Qualtrics
- **⏱️ Independent Sessions**: Each scenario has own 20-minute timer and data collection
- **🛡️ Built-in Safety**: Content moderation and respectful AI responses

## Survey Structure Options

### **Option 1: Multiple Scenarios in One Survey (Recommended)**

```
1. Consent & Demographics
2. Scenario 1 (embedded chat)
3. Post-Chat Questions for Scenario 1
4. Scenario 2 (embedded chat)
5. Post-Chat Questions for Scenario 2
6. ... (repeat for all scenarios)
7. Final Debriefing
```

### **Option 2: Single Scenario per Survey**

```
1. Consent & Demographics
2. Pre-Chat Questions
3. Scenario Chat (embedded)
4. Post-Chat Questions
5. Debriefing
```

## Direct Scenario Embedding

### **No URL Parameters Needed**

The new system handles Prolific ID collection automatically. You can embed scenarios using clean URLs:

```html
<div class="chat-embed-container">
  <iframe
    src="https://your-deployment.vercel.app/scenario/aita-1"
    width="100%"
    height="900px"
    frameborder="0"
    style="border: none; border-radius: 8px;"
    title="Research Chat Interface"
  >
  </iframe>
</div>
```

### **With Prolific ID (Optional Enhancement)**

If you want to pre-populate the Prolific ID to skip the entry screen:

```html
<iframe
  src="https://your-deployment.vercel.app/scenario/aita-1?PROLIFIC_PID=${e://Field/PROLIFIC_PID}"
  width="100%"
  height="900px"
  frameborder="0"
>
</iframe>
```

### **Controlled Session Flow**

1. **First Scenario**: User enters Prolific ID (stored in browser)
2. **Start Overlay**: User sees scenario title and clicks "Start Scenario" to begin
3. **Timer Starts**: 20-minute session timer begins only after start button clicked
4. **Subsequent Scenarios**: ID automatically retrieved, start overlay appears again
5. **Independent Control**: Each scenario requires explicit start, preventing accidental simultaneous interactions
6. **Data Linking**: All conversations automatically linked to same participant

## Advanced Parameter Passing

### Prolific Integration

Pass Prolific parameters automatically:

```html
<iframe
  src="https://your-deployment.vercel.app/scenario/sexism-1?PROLIFIC_PID=${e://Field/PROLIFIC_PID}&STUDY_ID=${e://Field/STUDY_ID}&SESSION_ID=${e://Field/SESSION_ID}&return_url=${e://Field/return_url}"
  width="100%"
  height="900px"
>
</iframe>
```

### Custom Parameters

Add study-specific parameters:

```html
<iframe
  src="https://your-deployment.vercel.app/scenario/aita-2?PROLIFIC_PID=${e://Field/PROLIFIC_PID}&condition=${e://Field/condition}&block=${e://Field/block_number}"
  width="100%"
  height="900px"
>
</iframe>
```

### Return URL Handling

For seamless survey flow:

```html
<iframe
  src="https://your-deployment.vercel.app/scenario/aita-3?PROLIFIC_PID=${e://Field/PROLIFIC_PID}&return_url=${e://SurveyURL}&return_response=${e://Field/ResponseID}"
  width="100%"
  height="900px"
>
</iframe>
```

## Complete Scenario Implementation Examples

### **Ready-to-Use Qualtrics HTML/CSS Questions**

Copy and paste these into your Qualtrics survey questions. Replace `your-deployment.vercel.app` with your actual domain.

---

### **AITA Scenarios**

#### **AITA-1: Park Rules & Personal Responsibility**

```html
<div class="scenario-intro">
  <h3 style="color: #2c3e50; margin-bottom: 15px;">
    🏛️ Moral Reasoning Discussion
  </h3>
  <p
    style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;"
  >
    You'll discuss a situation involving park rules, dog ownership, and personal
    responsibility. Click "Start Scenario" when ready to begin - your session timer will start then.
    <strong>The conversation will last up to 20 minutes.</strong>
  </p>
</div>

<div
  class="chat-container"
  style="width: 100%; min-height: 900px; border: 1px solid #ddd; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"
>
  <iframe
    src="https://your-deployment.vercel.app/scenario/aita-1"
    width="100%"
    height="900px"
    frameborder="0"
    style="border: none;"
    title="AITA Scenario 1: Park Rules Discussion"
  >
  </iframe>
</div>

<p style="margin-top: 15px; font-size: 14px; color: #666;">
  💡
  <em
    >Your responses and conversation will be automatically saved. You can end
    the conversation early if needed.</em
  >
</p>
```

#### **AITA-2: Academic Competition & Helping Others**

```html
<div class="scenario-intro">
  <h3 style="color: #2c3e50; margin-bottom: 15px;">
    📚 Academic Ethics Discussion
  </h3>
  <p
    style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;"
  >
    You'll discuss a situation involving academic competition, curved grading,
    and the ethics of helping classmates.
    <strong>The conversation will last up to 20 minutes.</strong>
  </p>
</div>

<div
  class="chat-container"
  style="width: 100%; min-height: 900px; border: 1px solid #ddd; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"
>
  <iframe
    src="https://your-deployment.vercel.app/scenario/aita-2"
    width="100%"
    height="900px"
    frameborder="0"
    style="border: none;"
    title="AITA Scenario 2: Academic Competition Discussion"
  >
  </iframe>
</div>
```

#### **AITA-3: Family Dynamics & Respect**

```html
<div class="scenario-intro">
  <h3 style="color: #2c3e50; margin-bottom: 15px;">
    👨‍👩‍👧‍👦 Family Dynamics Discussion
  </h3>
  <p
    style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;"
  >
    You'll discuss a situation involving sibling relationships, creative
    expression, and family respect.
    <strong>The conversation will last up to 20 minutes.</strong>
  </p>
</div>

<div
  class="chat-container"
  style="width: 100%; min-height: 900px; border: 1px solid #ddd; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"
>
  <iframe
    src="https://your-deployment.vercel.app/scenario/aita-3"
    width="100%"
    height="900px"
    frameborder="0"
    style="border: none;"
    title="AITA Scenario 3: Family Dynamics Discussion"
  >
  </iframe>
</div>
```

#### **AITA-4: Privacy Rights & Parental Authority**

```html
<div class="scenario-intro">
  <h3 style="color: #2c3e50; margin-bottom: 15px;">
    🏠 Privacy & Authority Discussion
  </h3>
  <p
    style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;"
  >
    You'll discuss a situation involving adolescent privacy rights and parental
    authority.
    <strong>The conversation will last up to 20 minutes.</strong>
  </p>
</div>

<div
  class="chat-container"
  style="width: 100%; min-height: 900px; border: 1px solid #ddd; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"
>
  <iframe
    src="https://your-deployment.vercel.app/scenario/aita-4"
    width="100%"
    height="900px"
    frameborder="0"
    style="border: none;"
    title="AITA Scenario 4: Privacy Rights Discussion"
  >
  </iframe>
</div>
```

---

### **Sexism Scenarios**

#### **Sexism-1: Reproductive Autonomy**

```html
<div class="scenario-intro">
  <h3 style="color: #2c3e50; margin-bottom: 15px;">
    ⚖️ Gender & Society Discussion
  </h3>
  <div
    style="background: #fef9e7; border: 1px solid #f9ca24; padding: 15px; border-radius: 8px; margin-bottom: 20px;"
  >
    <p>
      <strong>📋 Content Notice:</strong> This conversation involves
      gender-related social expectations and reproductive choices. Please engage
      respectfully and thoughtfully.
    </p>
  </div>
  <p
    style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;"
  >
    You'll discuss societal expectations about women and childbearing decisions.
    <strong>The conversation will last up to 20 minutes.</strong>
  </p>
</div>

<div
  class="chat-container"
  style="width: 100%; min-height: 900px; border: 1px solid #ddd; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"
>
  <iframe
    src="https://your-deployment.vercel.app/scenario/sexism-1"
    width="100%"
    height="900px"
    frameborder="0"
    style="border: none;"
    title="Sexism Scenario 1: Reproductive Autonomy Discussion"
  >
  </iframe>
</div>
```

#### **Sexism-2: Gender-Based Assumptions**

```html
<div class="scenario-intro">
  <h3 style="color: #2c3e50; margin-bottom: 15px;">
    💼 Workplace Behavior Discussion
  </h3>
  <div
    style="background: #fef9e7; border: 1px solid #f9ca24; padding: 15px; border-radius: 8px; margin-bottom: 20px;"
  >
    <p>
      <strong>📋 Content Notice:</strong> This conversation involves subtle
      gender bias in social interactions.
    </p>
  </div>
  <p
    style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;"
  >
    You'll discuss gender assumptions in social situations and workplace
    dynamics.
    <strong>The conversation will last up to 20 minutes.</strong>
  </p>
</div>

<div
  class="chat-container"
  style="width: 100%; min-height: 900px; border: 1px solid #ddd; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"
>
  <iframe
    src="https://your-deployment.vercel.app/scenario/sexism-2"
    width="100%"
    height="900px"
    frameborder="0"
    style="border: none;"
    title="Sexism Scenario 2: Gender Assumptions Discussion"
  >
  </iframe>
</div>
```

#### **Sexism-3: Professional Stereotypes**

```html
<div class="scenario-intro">
  <h3 style="color: #2c3e50; margin-bottom: 15px;">
    🎯 Marketing & Gender Discussion
  </h3>
  <div
    style="background: #fef9e7; border: 1px solid #f9ca24; padding: 15px; border-radius: 8px; margin-bottom: 20px;"
  >
    <p>
      <strong>📋 Content Notice:</strong> This conversation involves workplace
      gender discrimination and professional stereotypes.
    </p>
  </div>
  <p
    style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;"
  >
    You'll discuss gender stereotypes in professional settings and media
    representation.
    <strong>The conversation will last up to 20 minutes.</strong>
  </p>
</div>

<div
  class="chat-container"
  style="width: 100%; min-height: 900px; border: 1px solid #ddd; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"
>
  <iframe
    src="https://your-deployment.vercel.app/scenario/sexism-3"
    width="100%"
    height="900px"
    frameborder="0"
    style="border: none;"
    title="Sexism Scenario 3: Professional Stereotypes Discussion"
  >
  </iframe>
</div>
```

#### **Sexism-4: Maternity & Career Bias**

```html
<div class="scenario-intro">
  <h3 style="color: #2c3e50; margin-bottom: 15px;">
    👩‍💼 Career & Family Discussion
  </h3>
  <div
    style="background: #fef9e7; border: 1px solid #f9ca24; padding: 15px; border-radius: 8px; margin-bottom: 20px;"
  >
    <p>
      <strong>📋 Content Notice:</strong> This conversation involves workplace
      discrimination based on parental status.
    </p>
  </div>
  <p
    style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;"
  >
    You'll discuss workplace bias against mothers and career-family balance
    expectations.
    <strong>The conversation will last up to 20 minutes.</strong>
  </p>
</div>

<div
  class="chat-container"
  style="width: 100%; min-height: 900px; border: 1px solid #ddd; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"
>
  <iframe
    src="https://your-deployment.vercel.app/scenario/sexism-4"
    width="100%"
    height="900px"
    frameborder="0"
    style="border: none;"
    title="Sexism Scenario 4: Maternity Career Bias Discussion"
  >
  </iframe>
</div>
```

---

## Step-by-Step Qualtrics Setup

### **1. Create New Survey**

1. Log into Qualtrics → **Create Project** → **Survey**
2. Choose **Get started from scratch**
3. Name your survey (e.g., "AI Conversation Research Study")
4. Set survey language and other preferences

### **2. Configure Survey Flow**

1. Go to **Survey Flow** (left sidebar)
2. Set up **Embedded Data** at the top:
   ```
   PROLIFIC_PID = (leave empty, will be populated from URL)
   STUDY_ID = (leave empty)
   SESSION_ID = (leave empty)
   ```
3. Add your survey blocks in order

### **3. Create Survey Questions**

#### **Consent & Demographics Block**

- Add consent form
- Collect basic demographics
- Include attention check questions

#### **Scenario Questions (HTML/CSS Type)**

For each scenario you want to include:

1. **Add Question** → **HTML/CSS**
2. **Copy the appropriate HTML** from the examples above
3. **Replace `your-deployment.vercel.app`** with your actual domain
4. **Set question as required** (recommended)
5. **Add custom validation** if needed

#### **Post-Chat Reflection Questions**

After each scenario, consider adding:

- "How did the AI influence your thinking?"
- "Did you change your opinion during the conversation?"
- "How would you describe the AI's behavior?"

### **4. Survey Flow Randomization**

**For Multiple Scenarios:**

```
Survey Flow Structure:
├── Embedded Data (PROLIFIC_PID, etc.)
├── Consent & Demographics
├── Block: Pre-Study Questions
├── Randomizer (Evenly Present Elements)
│   ├── Block: AITA Scenarios
│   │   ├── AITA-1 + Post Questions
│   │   ├── AITA-2 + Post Questions
│   │   └── (etc.)
│   └── Block: Sexism Scenarios
│       ├── Sexism-1 + Post Questions
│       ├── Sexism-2 + Post Questions
│       └── (etc.)
└── Debriefing Block
```

**For Single Scenario per Survey:**

```
Survey Flow Structure:
├── Embedded Data (PROLIFIC_PID, etc.)
├── Consent & Demographics
├── Pre-Chat Questions
├── Scenario Chat (embedded)
├── Post-Chat Questions
└── Debriefing
```

### **5. Prolific Integration Setup**

#### **Study URL Configuration:**

```
https://your-survey.qualtrics.com/jfe/form/SV_XXXXXXXXX?PROLIFIC_PID={{%PROLIFIC_PID%}}&STUDY_ID={{%STUDY_ID%}}&SESSION_ID={{%SESSION_ID%}}
```

#### **Completion Redirect:**

- Go to **Survey Options** → **Survey Termination**
- Set **Redirect to URL**: `https://app.prolific.co/submissions/complete?cc=YOUR_COMPLETION_CODE`

#### **Survey Settings:**

- **Prevent ballot box stuffing**: ON (one response per participant)
- **Anonymous responses**: Configure per your IRB requirements
- **Save and continue**: OFF (to prevent partial submissions)

### **6. Testing Checklist**

Before launching:

- [ ] **Preview survey** in Qualtrics preview mode
- [ ] **Test iframe loading** - scenarios should load directly
- [ ] **Test Prolific ID entry** - should only prompt once across scenarios
- [ ] **Test start overlay** - should appear before each scenario and prevent premature interaction
- [ ] **Test conversation functionality** - messages should send/receive after clicking start
- [ ] **Test session timeout** - timer should only start after clicking "Start Scenario"
- [ ] **Check data collection** - verify data appears in Supabase
- [ ] **Test on mobile** - ensure responsive design works
- [ ] **Test completion flow** - verify redirect to Prolific works

## Advanced Configuration

### **Custom CSS Styling**

Add to your Qualtrics survey's **Look & Feel** → **Style** → **Custom CSS**:

```css
/* Improve iframe appearance */
.chat-container {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
  border-radius: 12px !important;
  overflow: hidden !important;
}

/* Responsive iframe adjustments */
@media (max-width: 768px) {
  .chat-container iframe {
    height: 700px !important;
  }
}

/* Loading indicator for slow connections */
.iframe-loading {
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  font-size: 16px;
  color: #666;
}
```

### **JavaScript Enhancements**

Add to **Survey Footer** for enhanced functionality:

```html
<script>
  // Improve iframe loading experience
  document.addEventListener("DOMContentLoaded", function () {
    // Add loading indicators
    const iframes = document.querySelectorAll('iframe[title*="Scenario"]');

    iframes.forEach(function (iframe) {
      const container = iframe.parentElement;
      const loadingDiv = document.createElement("div");
      loadingDiv.className = "iframe-loading";
      loadingDiv.innerHTML = "⏳ Loading conversation interface...";

      container.insertBefore(loadingDiv, iframe);

      iframe.onload = function () {
        loadingDiv.style.display = "none";
        iframe.style.display = "block";
      };

      iframe.style.display = "none";
    });
  });

  // Track interaction events (optional)
  window.addEventListener("message", function (event) {
    if (event.data && event.data.type === "chat_interaction") {
      console.log("Chat interaction detected:", event.data);
      // You can send this data to Qualtrics embedded data if needed
    }
  });
</script>
```

## Survey Flow Logic

### Randomization Setup

**Block Randomization:**

1. Create separate blocks for each scenario
2. Use Qualtrics randomization:
   - Survey Flow → Add Block
   - Randomize → Evenly Present Elements
   - Select blocks to randomize

**Embedded Data Setup:**

```
Survey Flow → Add Embedded Data
- scenario_order = Random(1-8)
- condition = Random(aita, sexism)
- block_number = Random(1-4)
```

### Counterbalancing

For within-subjects designs:

```
Branch Logic:
If condition = "aita_first"
  → AITA Block → Sexism Block
If condition = "sexism_first"
  → Sexism Block → AITA Block
```

## Data Collection Integration

### Pre-Chat Questions

Before each scenario:

```html
<div class="pre-chat-questions">
  <p>Before beginning the conversation, please answer:</p>

  <div class="question">
    <label>How familiar are you with this type of situation?</label>
    <select name="familiarity">
      <option value="1">Not at all familiar</option>
      <option value="2">Slightly familiar</option>
      <option value="3">Moderately familiar</option>
      <option value="4">Very familiar</option>
      <option value="5">Extremely familiar</option>
    </select>
  </div>

  <div class="question">
    <label>What is your initial reaction to this scenario?</label>
    <textarea
      name="initial_reaction"
      rows="3"
      cols="50"
      placeholder="Please describe your initial thoughts..."
    ></textarea>
  </div>
</div>
```

### Post-Chat Questions

After each scenario:

```html
<div class="post-chat-questions">
  <div class="question">
    <label
      >How much did the AI influence your thinking about this scenario?</label
    >
    <input type="radio" name="ai_influence" value="1" /> Not at all<br />
    <input type="radio" name="ai_influence" value="2" /> A little<br />
    <input type="radio" name="ai_influence" value="3" /> Moderately<br />
    <input type="radio" name="ai_influence" value="4" /> Quite a bit<br />
    <input type="radio" name="ai_influence" value="5" /> Extremely<br />
  </div>

  <div class="question">
    <label>Did you change your opinion during the conversation?</label>
    <input type="radio" name="opinion_change" value="yes" /> Yes<br />
    <input type="radio" name="opinion_change" value="no" /> No<br />
    <input type="radio" name="opinion_change" value="unsure" /> Unsure<br />
  </div>

  <div class="question">
    <label>How would you describe the AI's responses?</label>
    <textarea
      name="ai_description"
      rows="3"
      cols="50"
      placeholder="Please describe the AI's behavior and responses..."
    ></textarea>
  </div>
</div>
```

## Technical Configuration

### Iframe Optimization

**Responsive Design:**

```html
<style>
  .chat-container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
  }

  .chat-iframe {
    width: 100%;
    height: 900px;
    border: none;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }

  @media (max-width: 768px) {
    .chat-iframe {
      height: 700px;
    }
  }
</style>

<div class="chat-container">
  <iframe
    class="chat-iframe"
    src="https://your-deployment.vercel.app/scenario/aita-1?PROLIFIC_PID=${e://Field/PROLIFIC_PID}"
  >
  </iframe>
</div>
```

### Loading States

**Add Loading Indicator:**

```html
<div id="loading" style="text-align: center; padding: 40px;">
  <div
    style="border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 2s linear infinite; margin: 0 auto;"
  ></div>
  <p style="margin-top: 20px;">Loading conversation interface...</p>
</div>

<style>
  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
</style>

<iframe
  src="https://your-deployment.vercel.app/scenario/aita-1?PROLIFIC_PID=${e://Field/PROLIFIC_PID}"
  width="100%"
  height="900px"
  frameborder="0"
  onload="document.getElementById('loading').style.display='none';"
  style="display: none;"
  onload="this.style.display='block';"
>
</iframe>
```

## Data Validation

### Completion Verification

**JavaScript Validation:**

```html
<script>
  window.addEventListener("message", function (event) {
    if (event.data.type === "chat_completed") {
      // Mark question as completed
      Qualtrics.SurveyEngine.setEmbeddedData("chat_completed", "true");
      Qualtrics.SurveyEngine.setEmbeddedData(
        "chat_duration",
        event.data.duration
      );

      // Enable next button
      document.getElementById("NextButton").style.display = "block";
    }
  });
</script>

<div id="next-button-container" style="display: none;">
  <button onclick="Qualtrics.SurveyEngine.clickNextButton();">
    Continue to Next Section
  </button>
</div>
```

### Attention Checks

**Post-Conversation Validation:**

```html
<div class="attention-check">
  <p>
    <strong>Attention Check:</strong> To ensure you engaged with the
    conversation, please answer:
  </p>
  <label>What topic did you discuss with the AI?</label>
  <textarea name="conversation_topic" rows="2" cols="50" required></textarea>

  <label>Approximately how many messages did you exchange?</label>
  <select name="message_count" required>
    <option value="">Select...</option>
    <option value="1-3">1-3 messages</option>
    <option value="4-6">4-6 messages</option>
    <option value="7-10">7-10 messages</option>
    <option value="10+">More than 10 messages</option>
  </select>
</div>
```

## Troubleshooting

### Common Issues

**Iframe Not Loading:**

- Check deployment URL accessibility
- Verify CORS headers in vercel.json
- Test iframe outside of Qualtrics first

**Parameters Not Passing:**

- Use Qualtrics piped text syntax: `${e://Field/PROLIFIC_PID}`
- Check embedded data field names
- Test with preview mode

**Mobile Responsiveness:**

- Test on various screen sizes
- Adjust iframe height for mobile
- Consider separate mobile-optimized versions

### Testing Checklist

Before launching:

- [ ] All scenario iframes load correctly
- [ ] Prolific ID passes through properly
- [ ] Conversations save to database
- [ ] Timeout functionality works
- [ ] Return URLs redirect properly
- [ ] Mobile compatibility verified
- [ ] Data appears in Supabase tables

## Survey Distribution

### Prolific Setup

**Study Configuration:**

```
Study URL: https://your-survey.qualtrics.com/jfe/form/SV_xxx?PROLIFIC_PID={{%PROLIFIC_PID%}}&STUDY_ID={{%STUDY_ID%}}&SESSION_ID={{%SESSION_ID%}}

Completion URL: https://app.prolific.co/submissions/complete?cc=XXXXXX
```

**Participant Requirements:**

- Fluent in English
- Age 18+
- Previous approval rate ≥ 95%
- Custom screening questions as needed

### Quality Control

**Monitoring Participation:**

- Track completion rates in real-time
- Monitor average conversation lengths
- Check for technical issues in participant messages
- Review data quality regularly

**Participant Support:**

```html
<div class="support-info">
  <p>
    <strong>Technical Issues?</strong> If you experience problems with the chat
    interface:
  </p>
  <ul>
    <li>Try refreshing the page</li>
    <li>Ensure JavaScript is enabled</li>
    <li>Contact researcher: your-email@institution.edu</li>
  </ul>
</div>
```

## Data Export & Analysis

### Linking Survey and Chat Data

Both Qualtrics and Supabase store the Prolific ID, enabling data linking:

**SQL Query for Combined Dataset:**

```sql
SELECT
  c.prolific_id,
  c.scenario_id,
  c.study_type,
  c.completed_normally,
  c.duration_ms / 60000 as duration_minutes,
  c.interaction_count,
  -- Add Qualtrics data via JOIN or manual merge
FROM conversations c
WHERE c.prolific_id IN ('PL123456', 'PL123457', ...) -- From Qualtrics export
ORDER BY c.start_time;
```

### Analysis Preparation

1. **Export Qualtrics Data**: Download as CSV with all embedded data
2. **Export Chat Data**: Use Supabase dashboard or SQL queries
3. **Merge Datasets**: Link by Prolific ID for comprehensive analysis
4. **Quality Filtering**: Remove incomplete or problematic sessions

Your Qualtrics integration is now ready for research data collection! 📊
