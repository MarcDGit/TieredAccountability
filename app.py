import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_option_menu import option_menu
import plotly.express as px
import plotly.graph_objects as go
from database import db

# Configure Streamlit page
st.set_page_config(
    page_title="Tiered Accountability Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .urgency-high {
        background-color: #ff4444;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .urgency-critical {
        background-color: #cc0000;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-weight: bold;
        animation: blink 1s infinite;
    }
    .urgency-medium {
        background-color: #ff8800;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .urgency-low {
        background-color: #4CAF50;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .status-open {
        background-color: #2196F3;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .status-in-progress {
        background-color: #ff9800;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .status-pending-feedback {
        background-color: #9c27b0;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .status-closed {
        background-color: #4caf50;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_person' not in st.session_state:
    st.session_state.selected_person = None
if 'selected_tier' not in st.session_state:
    st.session_state.selected_tier = None

def get_urgency_color(urgency):
    colors = {
        'Low': '#4CAF50',
        'Medium': '#FF8800', 
        'High': '#FF4444',
        'Critical': '#CC0000'
    }
    return colors.get(urgency, '#999999')

def get_status_color(status):
    colors = {
        'Open': '#2196F3',
        'In Progress': '#FF9800',
        'Pending Feedback': '#9C27B0',
        'Closed': '#4CAF50'
    }
    return colors.get(status, '#999999')

def display_escalation_card(escalation):
    """Display a single escalation as a card"""
    with st.container():
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.write(f"**{escalation['title']}**")
            st.write(f"_{escalation['description'][:100]}..._" if len(escalation['description']) > 100 else f"_{escalation['description']}_")
            st.write(f"Created by: {escalation['created_by_name']} | Current Tier: {escalation['current_tier_name']}")
        
        with col2:
            urgency_class = f"urgency-{escalation['urgency'].lower()}"
            st.markdown(f"<span class='{urgency_class}'>{escalation['urgency']}</span>", unsafe_allow_html=True)
        
        with col3:
            status_class = f"status-{escalation['status'].lower().replace(' ', '-')}"
            st.markdown(f"<span class='{status_class}'>{escalation['status']}</span>", unsafe_allow_html=True)
        
        with col4:
            st.write(f"**{escalation['days_open']}** days")
        
        st.divider()

def admin_panel():
    """Admin panel for managing tiers and people"""
    st.markdown("<h1 class='main-header'>🔧 Admin Panel</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 Tier Management", "👥 People Management", "📈 Analytics"])
    
    with tab1:
        st.subheader("Tier Management")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("### Create New Tier")
            tier_name = st.text_input("Tier Name", placeholder="e.g., Level 1 Support")
            tier_level = st.number_input("Tier Level", min_value=1, value=1, step=1)
            
            # Get existing tiers for parent selection
            tiers_df = db.get_tiers()
            if not tiers_df.empty:
                tier_options = ["None"] + [(row['name'], row['id']) for _, row in tiers_df.iterrows()]
                parent_tier = st.selectbox("Parent Tier", options=[opt[0] for opt in tier_options])
                parent_tier_id = None if parent_tier == "None" else next(opt[1] for opt in tier_options if opt[0] == parent_tier)
            else:
                parent_tier_id = None
            
            tier_description = st.text_area("Description", placeholder="Describe the tier's responsibilities...")
            
            if st.button("Create Tier"):
                if tier_name:
                    tier_id = db.create_tier(tier_name, tier_level, parent_tier_id, tier_description)
                    st.success(f"Tier '{tier_name}' created successfully!")
                    st.rerun()
                else:
                    st.error("Please provide a tier name")
        
        with col2:
            st.write("### Existing Tiers")
            tiers_df = db.get_tiers()
            if not tiers_df.empty:
                for _, tier in tiers_df.iterrows():
                    with st.expander(f"Level {tier['level']}: {tier['name']}"):
                        st.write(f"**Description:** {tier['description'] or 'No description'}")
                        st.write(f"**Parent Tier:** {tier['parent_tier_name'] or 'None'}")
                        st.write(f"**Created:** {tier['created_at']}")
                        
                        # Count people in this tier
                        people_count = len(db.get_people(tier['id']))
                        st.write(f"**People in tier:** {people_count}")
            else:
                st.info("No tiers created yet.")
    
    with tab2:
        st.subheader("People Management")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("### Add New Person")
            person_name = st.text_input("Full Name", placeholder="John Doe")
            person_email = st.text_input("Email", placeholder="john.doe@company.com")
            
            # Tier selection
            tiers_df = db.get_tiers()
            if not tiers_df.empty:
                tier_options = [(row['name'], row['id']) for _, row in tiers_df.iterrows()]
                selected_tier_name = st.selectbox("Assign to Tier", options=[opt[0] for opt in tier_options])
                selected_tier_id = next(opt[1] for opt in tier_options if opt[0] == selected_tier_name)
            else:
                st.error("Please create at least one tier first!")
                selected_tier_id = None
            
            person_role = st.selectbox("Role", ["member", "lead", "manager", "admin"])
            
            if st.button("Add Person"):
                if person_name and person_email and selected_tier_id:
                    try:
                        person_id = db.create_person(person_name, person_email, selected_tier_id, person_role)
                        st.success(f"Person '{person_name}' added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating person: {str(e)}")
                else:
                    st.error("Please fill in all required fields")
        
        with col2:
            st.write("### People Directory")
            people_df = db.get_people()
            if not people_df.empty:
                # Group by tier
                for tier_name in people_df['tier_name'].unique():
                    tier_people = people_df[people_df['tier_name'] == tier_name]
                    with st.expander(f"{tier_name} ({len(tier_people)} people)"):
                        for _, person in tier_people.iterrows():
                            st.write(f"**{person['name']}** ({person['role']})")
                            st.write(f"📧 {person['email']}")
                            st.write("---")
            else:
                st.info("No people added yet.")
    
    with tab3:
        st.subheader("Analytics Dashboard")
        
        # Get escalation data for analytics
        escalations_df = db.get_escalations()
        
        if not escalations_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Escalations by urgency
                urgency_counts = escalations_df['urgency'].value_counts()
                fig_urgency = px.pie(values=urgency_counts.values, names=urgency_counts.index, 
                                   title="Escalations by Urgency",
                                   color_discrete_map={
                                       'Low': '#4CAF50', 'Medium': '#FF8800', 
                                       'High': '#FF4444', 'Critical': '#CC0000'
                                   })
                st.plotly_chart(fig_urgency, use_container_width=True)
            
            with col2:
                # Escalations by status
                status_counts = escalations_df['status'].value_counts()
                fig_status = px.bar(x=status_counts.index, y=status_counts.values,
                                  title="Escalations by Status",
                                  color=status_counts.values,
                                  color_continuous_scale='viridis')
                st.plotly_chart(fig_status, use_container_width=True)
            
            # Average resolution time by tier
            closed_escalations = escalations_df[escalations_df['status'] == 'Closed']
            if not closed_escalations.empty:
                avg_resolution_time = closed_escalations.groupby('current_tier_name')['days_open'].mean().reset_index()
                fig_resolution = px.bar(avg_resolution_time, x='current_tier_name', y='days_open',
                                      title="Average Resolution Time by Tier (Days)")
                st.plotly_chart(fig_resolution, use_container_width=True)
        else:
            st.info("No escalation data available for analytics yet.")

def escalation_dashboard():
    """Main escalation dashboard"""
    st.markdown("<h1 class='main-header'>📋 Escalation Dashboard</h1>", unsafe_allow_html=True)
    
    # Sidebar for person/tier selection
    with st.sidebar:
        st.subheader("👤 Select Your Identity")
        
        people_df = db.get_people()
        if not people_df.empty:
            person_options = [(f"{row['name']} ({row['tier_name']})", row['id'], row['tier_id']) 
                            for _, row in people_df.iterrows()]
            selected_person_display = st.selectbox("Select Person", 
                                                  options=[opt[0] for opt in person_options])
            
            if selected_person_display:
                st.session_state.selected_person = next(opt[1] for opt in person_options if opt[0] == selected_person_display)
                st.session_state.selected_tier = next(opt[2] for opt in person_options if opt[0] == selected_person_display)
                
                selected_person_name = selected_person_display.split(' (')[0]
                st.success(f"Logged in as: **{selected_person_name}**")
        else:
            st.error("No people found. Please add people in the Admin Panel first.")
            return
    
    if not st.session_state.selected_person:
        st.warning("Please select a person from the sidebar to continue.")
        return
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 My Dashboard", "🆕 Create Escalation", "🔄 Manage Escalations", "📈 Tier Overview"])
    
    with tab1:
        my_dashboard()
    
    with tab2:
        create_escalation()
    
    with tab3:
        manage_escalations()
    
    with tab4:
        tier_overview()

def my_dashboard():
    """Personal dashboard for the selected user"""
    person_id = st.session_state.selected_person
    tier_id = st.session_state.selected_tier
    
    # Get escalations for this person
    my_escalations = db.get_escalations(person_id=person_id)
    tier_escalations = db.get_escalations(tier_id=tier_id)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        created_count = len(my_escalations[my_escalations['created_by'] == person_id])
        st.markdown(f"""
        <div class="metric-card">
            <h3>{created_count}</h3>
            <p>Created by Me</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        assigned_count = len(my_escalations[my_escalations['assigned_to'] == person_id])
        st.markdown(f"""
        <div class="metric-card">
            <h3>{assigned_count}</h3>
            <p>Assigned to Me</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        pending_feedback = len(tier_escalations[tier_escalations['status'] == 'Pending Feedback'])
        st.markdown(f"""
        <div class="metric-card">
            <h3>{pending_feedback}</h3>
            <p>Pending My Feedback</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_days = my_escalations['days_open'].mean() if not my_escalations.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>{avg_days:.1f}</h3>
            <p>Avg Days Open</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent escalations
    st.subheader("🔔 Recent Escalations")
    
    if not my_escalations.empty:
        # Filter and sort recent escalations
        recent_escalations = my_escalations.head(10)
        
        for _, escalation in recent_escalations.iterrows():
            display_escalation_card(escalation)
    else:
        st.info("No escalations found.")

def create_escalation():
    """Form to create new escalations"""
    st.subheader("🆕 Create New Escalation")
    
    with st.form("create_escalation_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            title = st.text_input("Escalation Title*", placeholder="Brief description of the issue")
            description = st.text_area("Detailed Description*", 
                                     placeholder="Provide detailed information about the issue, including context, impact, and any steps already taken...")
        
        with col2:
            urgency = st.selectbox("Urgency Level*", ["Low", "Medium", "High", "Critical"])
            
            # Show urgency guidelines
            urgency_help = {
                "Low": "📗 Non-critical issues, can wait",
                "Medium": "📙 Standard business issues", 
                "High": "📕 Urgent, affects operations",
                "Critical": "🚨 Emergency, system down"
            }
            st.info(urgency_help[urgency])
        
        submitted = st.form_submit_button("Create Escalation", type="primary")
        
        if submitted:
            if title and description:
                escalation_id = db.create_escalation(
                    title=title,
                    description=description,
                    urgency=urgency,
                    created_by=st.session_state.selected_person,
                    source_tier_id=st.session_state.selected_tier
                )
                st.success(f"Escalation '{title}' created successfully!")
                st.rerun()
            else:
                st.error("Please fill in all required fields (*)")

def manage_escalations():
    """Manage and take actions on escalations"""
    st.subheader("🔄 Manage Escalations")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox("Filter by Status", 
                                   ["All", "Open", "In Progress", "Pending Feedback", "Closed"])
    
    with col2:
        urgency_filter = st.selectbox("Filter by Urgency", 
                                    ["All", "Critical", "High", "Medium", "Low"])
    
    with col3:
        days_filter = st.slider("Days Open", 0, 30, (0, 30))
    
    # Get escalations based on filters
    tier_escalations = db.get_escalations(tier_id=st.session_state.selected_tier)
    
    if not tier_escalations.empty:
        # Apply filters
        filtered_escalations = tier_escalations.copy()
        
        if status_filter != "All":
            filtered_escalations = filtered_escalations[filtered_escalations['status'] == status_filter]
        
        if urgency_filter != "All":
            filtered_escalations = filtered_escalations[filtered_escalations['urgency'] == urgency_filter]
        
        filtered_escalations = filtered_escalations[
            (filtered_escalations['days_open'] >= days_filter[0]) & 
            (filtered_escalations['days_open'] <= days_filter[1])
        ]
        
        st.write(f"**{len(filtered_escalations)}** escalations found")
        
        for _, escalation in filtered_escalations.iterrows():
            with st.expander(f"{escalation['title']} - {escalation['status']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Description:** {escalation['description']}")
                    st.write(f"**Created by:** {escalation['created_by_name']}")
                    st.write(f"**Days open:** {escalation['days_open']}")
                    
                    if escalation['feedback']:
                        st.write(f"**Feedback:** {escalation['feedback']}")
                
                with col2:
                    # Action buttons based on status and user role
                    if escalation['status'] == 'Open' and escalation['current_tier_id'] == st.session_state.selected_tier:
                        if st.button(f"Escalate to Next Tier", key=f"escalate_{escalation['id']}"):
                            show_escalation_form(escalation['id'])
                    
                    elif escalation['status'] == 'In Progress' and escalation['assigned_to'] == st.session_state.selected_person:
                        if st.button(f"Provide Feedback", key=f"feedback_{escalation['id']}"):
                            show_feedback_form(escalation['id'])
                    
                    elif escalation['status'] == 'Pending Feedback' and escalation['created_by'] == st.session_state.selected_person:
                        if st.button(f"Close Escalation", key=f"close_{escalation['id']}"):
                            db.close_escalation(escalation['id'], st.session_state.selected_person)
                            st.success("Escalation closed!")
                            st.rerun()
                    
                    # View history button
                    if st.button(f"View History", key=f"history_{escalation['id']}"):
                        show_escalation_history(escalation['id'])
    else:
        st.info("No escalations found for your tier.")

def show_escalation_form(escalation_id):
    """Show form to escalate to next tier"""
    st.subheader("Escalate to Next Tier")
    
    # Get available tiers (higher level)
    tiers_df = db.get_tiers()
    current_tier = tiers_df[tiers_df['id'] == st.session_state.selected_tier].iloc[0]
    higher_tiers = tiers_df[tiers_df['level'] > current_tier['level']]
    
    if higher_tiers.empty:
        st.warning("No higher tier available for escalation.")
        return
    
    with st.form(f"escalate_form_{escalation_id}"):
        target_tier_options = [(row['name'], row['id']) for _, row in higher_tiers.iterrows()]
        selected_tier_name = st.selectbox("Target Tier", options=[opt[0] for opt in target_tier_options])
        target_tier_id = next(opt[1] for opt in target_tier_options if opt[0] == selected_tier_name)
        
        # Get people in target tier
        target_people = db.get_people(target_tier_id)
        if not target_people.empty:
            people_options = [(row['name'], row['id']) for _, row in target_people.iterrows()]
            selected_person_name = st.selectbox("Assign to", options=[opt[0] for opt in people_options])
            assigned_to = next(opt[1] for opt in people_options if opt[0] == selected_person_name)
        else:
            st.error("No people found in target tier.")
            return
        
        if st.form_submit_button("Escalate"):
            db.escalate_to_next_tier(escalation_id, target_tier_id, assigned_to, st.session_state.selected_person)
            st.success(f"Escalation sent to {selected_tier_name}")
            st.rerun()

def show_feedback_form(escalation_id):
    """Show form to provide feedback"""
    st.subheader("Provide Feedback")
    
    with st.form(f"feedback_form_{escalation_id}"):
        feedback = st.text_area("Feedback", placeholder="Provide your feedback and resolution details...")
        
        if st.form_submit_button("Submit Feedback"):
            if feedback:
                db.provide_feedback(escalation_id, feedback, st.session_state.selected_person)
                st.success("Feedback provided successfully!")
                st.rerun()
            else:
                st.error("Please provide feedback before submitting.")

def show_escalation_history(escalation_id):
    """Show escalation history"""
    st.subheader("Escalation History")
    
    history_df = db.get_escalation_history(escalation_id)
    
    if not history_df.empty:
        for _, record in history_df.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**{record['action']}**")
                    st.write(f"by {record['performed_by_name']}")
                
                with col2:
                    if record['from_status'] and record['to_status']:
                        st.write(f"{record['from_status']} → {record['to_status']}")
                    if record['notes']:
                        st.write(f"_{record['notes']}_")
                
                with col3:
                    st.write(record['timestamp'][:16])
                
                st.divider()

def tier_overview():
    """Overview of the current tier's performance"""
    st.subheader("📈 Tier Overview")
    
    tier_escalations = db.get_escalations(tier_id=st.session_state.selected_tier)
    
    if not tier_escalations.empty:
        # Performance metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_escalations = len(tier_escalations)
            open_escalations = len(tier_escalations[tier_escalations['status'].isin(['Open', 'In Progress'])])
            st.metric("Total Escalations", total_escalations)
            st.metric("Open Escalations", open_escalations)
        
        with col2:
            avg_resolution = tier_escalations[tier_escalations['status'] == 'Closed']['days_open'].mean()
            st.metric("Avg Resolution Time", f"{avg_resolution:.1f} days" if pd.notna(avg_resolution) else "N/A")
            
            critical_count = len(tier_escalations[tier_escalations['urgency'] == 'Critical'])
            st.metric("Critical Issues", critical_count)
        
        with col3:
            # Escalation trend (simple calculation)
            escalation_rate = len(tier_escalations[tier_escalations['target_tier_id'].notna()]) / len(tier_escalations) * 100
            st.metric("Escalation Rate", f"{escalation_rate:.1f}%")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Urgency distribution
            urgency_counts = tier_escalations['urgency'].value_counts()
            fig_urgency = px.pie(values=urgency_counts.values, names=urgency_counts.index,
                               title="Urgency Distribution")
            st.plotly_chart(fig_urgency, use_container_width=True)
        
        with col2:
            # Status distribution
            status_counts = tier_escalations['status'].value_counts()
            fig_status = px.bar(x=status_counts.index, y=status_counts.values,
                              title="Status Distribution")
            st.plotly_chart(fig_status, use_container_width=True)
    else:
        st.info("No escalations data available for this tier.")

# Main navigation
def main():
    """Main application navigation"""
    
    # Navigation menu
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100/4CAF50/FFFFFF?text=TAD", caption="Tiered Accountability Dashboard")
        
        selected = option_menu(
            menu_title="Navigation",
            options=["🏠 Dashboard", "🔧 Admin Panel"],
            icons=["house", "gear"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "orange", "font-size": "25px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#02ab21"},
            }
        )
    
    # Route to appropriate page
    if selected == "🏠 Dashboard":
        escalation_dashboard()
    elif selected == "🔧 Admin Panel":
        admin_panel()

if __name__ == "__main__":
    main()