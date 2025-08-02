"""
Sample Data Initialization Script for Tiered Accountability Dashboard

This script creates sample tiers, people, and escalations to demonstrate
the application functionality. Run this after the first app startup.
"""

from database import db

def init_sample_data():
    """Initialize sample data for demonstration"""
    
    print("🔧 Initializing sample data for Tiered Accountability Dashboard...")
    
    # Create sample tiers
    print("📊 Creating sample tiers...")
    
    tier1_id = db.create_tier(
        name="Level 1 Support",
        level=1,
        description="Front-line customer support and initial issue triage"
    )
    
    tier2_id = db.create_tier(
        name="Level 2 Technical",
        level=2,
        parent_tier_id=tier1_id,
        description="Technical specialists for complex issues"
    )
    
    tier3_id = db.create_tier(
        name="Level 3 Engineering",
        level=3,
        parent_tier_id=tier2_id,
        description="Senior engineers and system architects"
    )
    
    management_id = db.create_tier(
        name="Management",
        level=4,
        parent_tier_id=tier3_id,
        description="Department managers and leadership team"
    )
    
    print(f"✅ Created 4 tiers")
    
    # Create sample people
    print("👥 Creating sample people...")
    
    # Tier 1 people
    alice_id = db.create_person("Alice Johnson", "alice.johnson@company.com", tier1_id, "lead")
    bob_id = db.create_person("Bob Smith", "bob.smith@company.com", tier1_id, "member")
    carol_id = db.create_person("Carol Wilson", "carol.wilson@company.com", tier1_id, "member")
    
    # Tier 2 people
    david_id = db.create_person("David Brown", "david.brown@company.com", tier2_id, "lead")
    emma_id = db.create_person("Emma Davis", "emma.davis@company.com", tier2_id, "member")
    
    # Tier 3 people
    frank_id = db.create_person("Frank Miller", "frank.miller@company.com", tier3_id, "member")
    grace_id = db.create_person("Grace Taylor", "grace.taylor@company.com", tier3_id, "lead")
    
    # Management
    henry_id = db.create_person("Henry Anderson", "henry.anderson@company.com", management_id, "manager")
    
    print(f"✅ Created 8 people across all tiers")
    
    # Create sample escalations
    print("📋 Creating sample escalations...")
    
    # Sample escalation 1 - Open in Tier 1
    escalation1_id = db.create_escalation(
        title="Customer login issues with new authentication system",
        description="Multiple customers reporting they cannot log in after the authentication system update. Error message shows 'Invalid credentials' even with correct passwords. Affecting approximately 15% of user base.",
        urgency="High",
        created_by=bob_id,
        source_tier_id=tier1_id
    )
    
    # Sample escalation 2 - Escalated to Tier 2
    escalation2_id = db.create_escalation(
        title="Database performance degradation during peak hours",
        description="Query response times have increased by 300% during peak hours (9-11 AM, 2-4 PM). Customer facing applications are timing out. Need immediate investigation.",
        urgency="Critical",
        created_by=alice_id,
        source_tier_id=tier1_id
    )
    
    # Escalate it to Tier 2
    db.escalate_to_next_tier(escalation2_id, tier2_id, david_id, alice_id)
    
    # Sample escalation 3 - With feedback
    escalation3_id = db.create_escalation(
        title="Email notification system not sending alerts",
        description="Automated email notifications for order confirmations and shipping updates stopped working since yesterday. Manual emails work fine.",
        urgency="Medium",
        created_by=carol_id,
        source_tier_id=tier1_id
    )
    
    # Escalate and provide feedback
    db.escalate_to_next_tier(escalation3_id, tier2_id, emma_id, carol_id)
    db.provide_feedback(escalation3_id, "Issue was caused by SMTP server configuration error after recent update. Fixed by reverting mail server settings and implementing proper configuration. System now working normally. Monitoring for 24 hours to ensure stability.", emma_id)
    
    # Sample escalation 4 - Critical escalated to Tier 3
    escalation4_id = db.create_escalation(
        title="Production server cluster showing high memory usage",
        description="All production servers in the main cluster are showing 95%+ memory usage. Risk of system crash. Need immediate scaling or optimization.",
        urgency="Critical",
        created_by=david_id,
        source_tier_id=tier2_id
    )
    
    # Escalate to Tier 3
    db.escalate_to_next_tier(escalation4_id, tier3_id, frank_id, david_id)
    
    # Sample escalation 5 - Low priority
    escalation5_id = db.create_escalation(
        title="Feature request: Dark mode for admin dashboard",
        description="Users are requesting a dark mode option for the admin dashboard to reduce eye strain during extended use. This is a nice-to-have enhancement.",
        urgency="Low",
        created_by=bob_id,
        source_tier_id=tier1_id
    )
    
    print(f"✅ Created 5 sample escalations with various statuses")
    
    print("\n🎉 Sample data initialization complete!")
    print("\n📝 Summary:")
    print("   • 4 Tiers: Level 1 Support → Level 2 Technical → Level 3 Engineering → Management")
    print("   • 8 People: Distributed across all tiers with different roles")
    print("   • 5 Escalations: Covering different urgency levels and workflow states")
    print("\n🚀 You can now:")
    print("   1. Run 'streamlit run app.py' to start the application")
    print("   2. Select any person from the sidebar to see their view")
    print("   3. Explore the Admin Panel to see the tier structure")
    print("   4. Practice the escalation workflow")
    print("\n💡 Recommended starting points:")
    print("   • Login as 'Alice Johnson' (Tier 1 Lead) to see escalations")
    print("   • Login as 'David Brown' (Tier 2 Lead) to handle escalated items")
    print("   • Visit Admin Panel to see the full organizational structure")

if __name__ == "__main__":
    init_sample_data()