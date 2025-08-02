# 🚀 Quick Start Guide - Tiered Accountability Dashboard

## Get Up and Running in 3 Steps

### Step 1: Install Dependencies
```bash
pip3 install streamlit pandas plotly streamlit-option-menu
```

### Step 2: Initialize Sample Data
```bash
python3 init_sample_data.py
```

### Step 3: Start the Application
```bash
streamlit run app.py
```

The application will be available at: `http://localhost:8501`

## 🎯 Try These Actions

### 1. **Admin Panel Tour** (2 minutes)
- Click "🔧 Admin Panel" in the sidebar
- Explore the "📊 Tier Management" tab to see the hierarchy:
  - Level 1 Support → Level 2 Technical → Level 3 Engineering → Management
- Check "👥 People Management" to see 8 sample people
- View "📈 Analytics" for system-wide metrics

### 2. **Experience the Escalation Workflow** (5 minutes)

#### As a Tier 1 Member (Bob Smith):
1. Select "Bob Smith (Level 1 Support)" from the sidebar
2. Go to "🆕 Create Escalation"
3. Create a new escalation:
   - Title: "Website loading slowly"
   - Description: "Customer reports website takes 30+ seconds to load"
   - Urgency: "High"
4. Click "Create Escalation"

#### As a Tier 1 Lead (Alice Johnson):
1. Select "Alice Johnson (Level 1 Support)" from the sidebar
2. Go to "🔄 Manage Escalations"
3. Find your escalation and click "Escalate to Next Tier"
4. Assign to "David Brown" in "Level 2 Technical"

#### As a Tier 2 Lead (David Brown):
1. Select "David Brown (Level 2 Technical)" from the sidebar
2. Go to "🔄 Manage Escalations"
3. Find the escalated item and click "Provide Feedback"
4. Add feedback: "Identified CDN caching issue. Fixed by clearing cache and optimizing image compression. Site now loads in under 3 seconds."

#### Close the Loop (Alice Johnson):
1. Switch back to "Alice Johnson"
2. Go to "🔄 Manage Escalations"
3. Find the item with "Pending Feedback" status
4. Click "Close Escalation"

### 3. **Explore Different Perspectives** (3 minutes)

Try logging in as different people to see how the dashboard changes:
- **Alice Johnson** (Tier 1 Lead): See team escalations and management overview
- **David Brown** (Tier 2 Lead): Handle escalated technical issues
- **Frank Miller** (Tier 3 Engineer): Work on complex system issues
- **Henry Anderson** (Management): High-level analytics and trends

### 4. **Use the Filtering System** (2 minutes)
- Filter escalations by:
  - **Status**: Open, In Progress, Pending Feedback, Closed
  - **Urgency**: Critical, High, Medium, Low
  - **Days Open**: Use slider to find old issues
- Watch the analytics update in real-time

## 📊 Sample Data Included

Your system comes pre-loaded with:

### Tiers
- **Level 1 Support**: Front-line customer support
- **Level 2 Technical**: Technical specialists  
- **Level 3 Engineering**: Senior engineers
- **Management**: Department leadership

### People (8 total)
- **Tier 1**: Alice Johnson (Lead), Bob Smith, Carol Wilson
- **Tier 2**: David Brown (Lead), Emma Davis
- **Tier 3**: Frank Miller, Grace Taylor (Lead)
- **Management**: Henry Anderson (Manager)

### Escalations (5 total)
1. **Customer login issues** (High, Open in Tier 1)
2. **Database performance** (Critical, In Progress in Tier 2)
3. **Email notifications** (Medium, Pending Feedback)
4. **Server memory usage** (Critical, In Progress in Tier 3)
5. **Dark mode request** (Low, Open in Tier 1)

## 🎨 Key Features to Explore

- **Real-time Metrics**: Watch counters update as you process escalations
- **Visual Analytics**: Pie charts and bar graphs showing system health
- **Audit Trail**: Click "View History" on any escalation to see the complete timeline
- **Responsive Design**: Works on desktop and mobile
- **Modern UI**: Gradient cards, color-coded urgency levels, status indicators

## 💡 Pro Tips

1. **Use Urgency Wisely**: Critical items blink red to grab attention
2. **Check Days Open**: Use this metric to identify stale issues
3. **Leverage Analytics**: Use the admin panel analytics to spot trends
4. **Follow the Workflow**: Always escalate → provide feedback → close for best results
5. **Multi-Role Testing**: Switch between different people to understand all perspectives

## 🛠️ Next Steps

Once you're comfortable with the demo:

1. **Clear Sample Data**: Delete `accountability_dashboard.db` to start fresh
2. **Create Your Organization**: Set up your real tiers and people
3. **Import Data**: Use the admin panel to bulk-create your structure
4. **Customize**: Modify colors, add fields, or integrate with your systems

## 🆘 Need Help?

- **Check README.md** for complete documentation
- **View escalation history** to understand workflow states
- **Try different user perspectives** to see the full system
- **Experiment with filters** to find specific escalations

---

**Happy Escalating!** 🎉

*Your Tiered Accountability Dashboard is ready to help you achieve operational excellence through structured escalation management.*