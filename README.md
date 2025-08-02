# Tiered Accountability Dashboard (TAD)

A comprehensive web application built with Streamlit and Python for managing operational excellence through tiered accountability and escalation processes.

## 🎯 Overview

The Tiered Accountability Dashboard (TAD) is designed to support lean management principles by providing a structured approach to issue escalation, accountability tracking, and operational excellence. The system enables organizations to implement a tiered hierarchy where issues can be efficiently escalated, tracked, and resolved with clear accountability at each level.

## 🏗️ Architecture

### Core Components

1. **Database Layer** (`database.py`)
   - SQLite-based persistence
   - Entity relationships for tiers, people, and escalations
   - Full audit trail and history tracking

2. **Application Layer** (`app.py`)
   - Streamlit web interface
   - Real-time dashboard updates
   - Role-based access control

3. **Data Models**
   - **Tiers**: Hierarchical levels of accountability
   - **People**: Users assigned to specific tiers with defined roles
   - **Escalations**: Issues tracked through the tier hierarchy

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone <repository_url>
cd tiered-accountability-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

4. Access the application at `http://localhost:8501`

### Initial Setup

1. **Admin Panel Setup**:
   - Navigate to "🔧 Admin Panel"
   - Create your tier hierarchy (e.g., Tier 1, Tier 2, Tier 3)
   - Add people to each tier with appropriate roles

2. **Start Using**:
   - Select your identity from the dashboard sidebar
   - Begin creating and managing escalations

## 📊 Core Features

### 1. Admin Panel
- **Tier Management**: Create and configure hierarchical accountability levels
- **People Management**: Add users and assign them to tiers with specific roles
- **Analytics Dashboard**: View system-wide metrics and performance indicators

### 2. Escalation Dashboard
- **Personal Dashboard**: View personal metrics and escalations
- **Create Escalations**: Log new issues with urgency levels
- **Manage Escalations**: Take actions on escalations (escalate, provide feedback, close)
- **Tier Overview**: Monitor tier-specific performance metrics

### 3. Workflow Management
- **Escalation Creation**: Issues start in the creator's tier
- **Tier-to-Tier Escalation**: Structured escalation to higher tiers
- **Feedback Loop**: Resolution feedback flows back to originating tier
- **Closure Process**: Original creator validates and closes escalations

## 🔄 Escalation Workflow

### Standard Process Flow

1. **Issue Creation** (Tier 1)
   - Person A creates escalation in Tier 1
   - Status: "Open"
   - Visible in Tier 1 dashboard

2. **Escalation** (Tier 1 → Tier 2)
   - Tier 1 escalates to Tier 2
   - Assigns to specific Person B in Tier 2
   - Status: "In Progress"
   - Visible in both Tier 1 and Tier 2 dashboards

3. **Resolution** (Tier 2)
   - Person B works on the issue
   - Provides feedback and resolution
   - Status: "Pending Feedback"
   - Returns to Tier 1 visibility

4. **Closure** (Tier 1)
   - Person A reviews feedback
   - Closes escalation if satisfied
   - Status: "Closed"
   - Removed from active dashboards

### Status Definitions

| Status | Description | Available Actions |
|--------|-------------|-------------------|
| **Open** | Newly created, awaiting action | Escalate to next tier |
| **In Progress** | Currently being worked on | Provide feedback |
| **Pending Feedback** | Resolved, awaiting creator review | Close escalation |
| **Closed** | Issue resolved and confirmed | View history only |

### Urgency Levels

| Level | Description | Visual Indicator | Use Case |
|-------|-------------|------------------|----------|
| **Critical** | 🚨 Emergency, system down | Red (blinking) | Production outages, safety issues |
| **High** | 📕 Urgent, affects operations | Red | Performance issues, customer impact |
| **Medium** | 📙 Standard business issues | Orange | Normal workflow problems |
| **Low** | 📗 Non-critical, can wait | Green | Enhancements, documentation |

## 📈 Key Performance Indicators (KPIs)

### Personal Metrics
- **Created by Me**: Total escalations created
- **Assigned to Me**: Escalations currently assigned
- **Pending My Feedback**: Items awaiting review
- **Average Days Open**: Mean resolution time

### Tier Metrics
- **Total Escalations**: All escalations processed
- **Open Escalations**: Currently active items
- **Average Resolution Time**: Mean time to close
- **Escalation Rate**: Percentage escalated to higher tiers
- **Critical Issues**: Count of critical urgency items

### System Analytics
- **Escalations by Urgency**: Distribution pie chart
- **Escalations by Status**: Current status breakdown
- **Resolution Time by Tier**: Performance comparison
- **Trend Analysis**: Historical patterns

## 🔐 Roles and Permissions

### Role Definitions

| Role | Permissions | Typical Responsibilities |
|------|-------------|-------------------------|
| **Member** | Create escalations, view own items | Front-line operators |
| **Lead** | Manage team escalations, escalate | Team leaders, supervisors |
| **Manager** | Cross-tier visibility, analytics | Department managers |
| **Admin** | Full system access, configuration | System administrators |

## 📚 Definitions and Abbreviations

### Core Terms

**TAD** - Tiered Accountability Dashboard
: The complete system for managing escalations and accountability

**Tier** - Accountability Level
: A hierarchical level in the organization with specific responsibilities

**Escalation** - Issue Escalation
: A logged issue that can be escalated through the tier hierarchy

**SLA** - Service Level Agreement
: Expected timeframes for issue resolution (future enhancement)

**KPI** - Key Performance Indicator
: Measurable values demonstrating operational effectiveness

### Operational Excellence Terms

**Lean Management**
: Methodology focused on minimizing waste while maximizing productivity

**Operational Excellence** (OpEx)
: Discipline of enabling an organization to focus on growth and improvement

**Root Cause Analysis** (RCA)
: Process of identifying underlying causes of problems

**Continuous Improvement** (CI)
: Ongoing effort to improve products, services, or processes

**PDCA Cycle** - Plan-Do-Check-Act
: Four-step management method for continuous improvement

**Gemba** - The Real Place
: Japanese term for the actual place where value is created

**Kaizen** - Change for Better
: Practice of continuous improvement

**Poka-Yoke** - Error Prevention
: Technique for avoiding mistakes by design

### Status and Process Terms

**Escalation Path**
: Defined route for issue escalation through tiers

**Feedback Loop**
: System ensuring information flows back to the originator

**Escalation Matrix**
: Framework defining when and how to escalate issues

**Resolution Time**
: Duration from issue creation to closure

**First Call Resolution** (FCR)
: Percentage of issues resolved at the first tier

**Mean Time To Resolution** (MTTR)
: Average time to resolve escalations

**Time to First Response** (TTFR)
: Time from creation to first action

### System Terms

**Audit Trail**
: Complete history of all actions performed on an escalation

**Dashboard**
: Visual interface displaying key metrics and data

**Filter**
: Mechanism to narrow down displayed data based on criteria

**Real-time Updates**
: Immediate reflection of changes in the user interface

**Session State**
: User's current context and selections in the application

## 🛠️ Technical Details

### Database Schema

#### Tiers Table
- `id`: Unique identifier
- `name`: Tier name (e.g., "Level 1 Support")
- `level`: Numeric hierarchy level
- `parent_tier_id`: Reference to parent tier
- `description`: Tier responsibilities

#### People Table
- `id`: Unique identifier
- `name`: Full name
- `email`: Email address
- `tier_id`: Assigned tier
- `role`: User role (member, lead, manager, admin)
- `is_active`: Active status

#### Escalations Table
- `id`: Unique identifier
- `title`: Brief description
- `description`: Detailed information
- `urgency`: Priority level
- `status`: Current state
- `created_by`: Original creator
- `assigned_to`: Current assignee
- `source_tier_id`: Originating tier
- `target_tier_id`: Escalated to tier
- `current_tier_id`: Current tier
- `timestamps`: Created, updated, escalated, resolved, closed
- `feedback`: Resolution feedback

#### Escalation History Table
- `id`: Unique identifier
- `escalation_id`: Reference to escalation
- `action`: Action performed
- `performed_by`: User who performed action
- `from_status`/`to_status`: Status transition
- `timestamp`: When action occurred

### Dependencies

- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **SQLite3**: Database engine
- **Plotly**: Interactive visualizations
- **Streamlit-option-menu**: Enhanced navigation menus

## 🔧 Configuration

### Environment Variables

Currently, the application uses default configurations. Future versions may support:

- `DATABASE_URL`: Custom database connection
- `DEBUG_MODE`: Enable debug logging
- `SESSION_TIMEOUT`: User session duration

### Customization

The application can be customized by:

1. **Modifying CSS**: Update styling in `app.py`
2. **Adding Fields**: Extend database models
3. **Custom Reports**: Create additional analytics
4. **Integration**: Connect with external systems

## 🚀 Future Enhancements

### Planned Features

1. **SLA Management**: Define and track service level agreements
2. **Email Notifications**: Automated alerts for escalations
3. **Advanced Analytics**: Predictive analysis and trends
4. **Mobile Interface**: Responsive design for mobile devices
5. **API Integration**: REST API for external system integration
6. **Document Attachments**: File upload capabilities
7. **Advanced Reporting**: Scheduled reports and exports
8. **Multi-tenant Support**: Organization isolation

### Performance Optimizations

1. **Database Indexing**: Optimize query performance
2. **Caching**: Reduce database load
3. **Pagination**: Handle large datasets
4. **Background Jobs**: Async processing for heavy tasks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

1. Check the documentation above
2. Review existing escalations in the system
3. Contact your system administrator
4. Create an issue in the repository

---

**Built with ❤️ for Operational Excellence**

*The Tiered Accountability Dashboard promotes lean management principles through structured escalation processes, ensuring accountability and continuous improvement across all organizational levels.* 
