import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd
import hashlib

class DatabaseManager:
    def __init__(self, db_path: str = "accountability_dashboard.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize the database with all required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create admin settings table for password management
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_settings (
                    id INTEGER PRIMARY KEY,
                    setting_name TEXT UNIQUE NOT NULL,
                    setting_value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Set initial admin password if not exists
            cursor.execute('SELECT COUNT(*) FROM admin_settings WHERE setting_name = "admin_password"')
            if cursor.fetchone()[0] == 0:
                # Hash the initial password 'TA'
                password_hash = hashlib.sha256("TA".encode()).hexdigest()
                cursor.execute('''
                    INSERT INTO admin_settings (setting_name, setting_value)
                    VALUES ("admin_password", ?)
                ''', (password_hash,))
            
            # Create tiers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tiers (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    level INTEGER NOT NULL,
                    parent_tier_id TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_tier_id) REFERENCES tiers (id)
                )
            ''')
            
            # Create people table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS people (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    tier_id TEXT NOT NULL,
                    role TEXT DEFAULT 'member',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tier_id) REFERENCES tiers (id)
                )
            ''')
            
            # Create escalations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS escalations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    urgency TEXT CHECK (urgency IN ('Low', 'Medium', 'High', 'Critical')) DEFAULT 'Medium',
                    status TEXT CHECK (status IN ('Open', 'In Progress', 'Pending Feedback', 'Resolved', 'Closed')) DEFAULT 'Open',
                    created_by TEXT NOT NULL,
                    assigned_to TEXT,
                    source_tier_id TEXT NOT NULL,
                    target_tier_id TEXT,
                    current_tier_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    escalated_at TIMESTAMP,
                    resolved_at TIMESTAMP,
                    closed_at TIMESTAMP,
                    feedback TEXT,
                    FOREIGN KEY (created_by) REFERENCES people (id),
                    FOREIGN KEY (assigned_to) REFERENCES people (id),
                    FOREIGN KEY (source_tier_id) REFERENCES tiers (id),
                    FOREIGN KEY (target_tier_id) REFERENCES tiers (id),
                    FOREIGN KEY (current_tier_id) REFERENCES tiers (id)
                )
            ''')
            
            # Create escalation history table for audit trail
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS escalation_history (
                    id TEXT PRIMARY KEY,
                    escalation_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    performed_by TEXT NOT NULL,
                    from_status TEXT,
                    to_status TEXT,
                    notes TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (escalation_id) REFERENCES escalations (id),
                    FOREIGN KEY (performed_by) REFERENCES people (id)
                )
            ''')
            
            conn.commit()
    
    # Admin password management methods
    def verify_admin_password(self, password: str) -> bool:
        """Verify admin password"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT setting_value FROM admin_settings WHERE setting_name = "admin_password"')
            result = cursor.fetchone()
            return result and result[0] == password_hash
    
    def change_admin_password(self, current_password: str, new_password: str) -> bool:
        """Change admin password"""
        if not self.verify_admin_password(current_password):
            return False
        
        new_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE admin_settings 
                SET setting_value = ?, updated_at = CURRENT_TIMESTAMP
                WHERE setting_name = "admin_password"
            ''', (new_password_hash,))
            conn.commit()
        return True
    
    # Tier management methods
    def create_tier(self, name: str, level: int, parent_tier_id: Optional[str] = None, description: str = "") -> str:
        """Create a new tier"""
        tier_id = str(uuid.uuid4())
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tiers (id, name, level, parent_tier_id, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (tier_id, name, level, parent_tier_id, description))
            conn.commit()
        return tier_id
    
    def update_tier(self, tier_id: str, name: str, level: int, parent_tier_id: Optional[str] = None, description: str = "") -> bool:
        """Update an existing tier"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE tiers 
                SET name = ?, level = ?, parent_tier_id = ?, description = ?
                WHERE id = ?
            ''', (name, level, parent_tier_id, description, tier_id))
            conn.commit()
        return True
    
    def delete_tier(self, tier_id: str) -> bool:
        """Delete a tier (only if no people or escalations are associated)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if tier has people
            cursor.execute('SELECT COUNT(*) FROM people WHERE tier_id = ? AND is_active = 1', (tier_id,))
            if cursor.fetchone()[0] > 0:
                return False
            
            # Check if tier has escalations
            cursor.execute('SELECT COUNT(*) FROM escalations WHERE source_tier_id = ? OR target_tier_id = ? OR current_tier_id = ?', 
                         (tier_id, tier_id, tier_id))
            if cursor.fetchone()[0] > 0:
                return False
            
            # Check if tier has child tiers
            cursor.execute('SELECT COUNT(*) FROM tiers WHERE parent_tier_id = ?', (tier_id,))
            if cursor.fetchone()[0] > 0:
                return False
            
            # Delete the tier
            cursor.execute('DELETE FROM tiers WHERE id = ?', (tier_id,))
            conn.commit()
        return True
    
    def get_tier_by_id(self, tier_id: str) -> Optional[Dict]:
        """Get a specific tier by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT t.*, pt.name as parent_tier_name
                FROM tiers t
                LEFT JOIN tiers pt ON t.parent_tier_id = pt.id
                WHERE t.id = ?
            ''', (tier_id,))
            result = cursor.fetchone()
            if result:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, result))
        return None
    
    def get_tiers(self) -> pd.DataFrame:
        """Get all tiers"""
        with self.get_connection() as conn:
            return pd.read_sql_query('''
                SELECT t.*, pt.name as parent_tier_name
                FROM tiers t
                LEFT JOIN tiers pt ON t.parent_tier_id = pt.id
                ORDER BY t.level, t.name
            ''', conn)
    
    def get_tier_hierarchy(self) -> List[Dict]:
        """Get tier hierarchy for dropdown selection"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, level FROM tiers ORDER BY level, name')
            return [{'id': row[0], 'name': row[1], 'level': row[2]} for row in cursor.fetchall()]
    
    # People management methods
    def create_person(self, name: str, email: str, tier_id: str, role: str = 'member') -> str:
        """Create a new person"""
        person_id = str(uuid.uuid4())
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO people (id, name, email, tier_id, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (person_id, name, email, tier_id, role))
            conn.commit()
        return person_id
    
    def update_person(self, person_id: str, name: str, email: str, tier_id: str, role: str) -> bool:
        """Update an existing person"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE people 
                SET name = ?, email = ?, tier_id = ?, role = ?
                WHERE id = ?
            ''', (name, email, tier_id, role, person_id))
            conn.commit()
        return True
    
    def delete_person(self, person_id: str) -> bool:
        """Delete a person (soft delete by setting is_active to False)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE people 
                SET is_active = 0
                WHERE id = ?
            ''', (person_id,))
            conn.commit()
        return True
    
    def get_person_by_id(self, person_id: str) -> Optional[Dict]:
        """Get a specific person by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.*, t.name as tier_name
                FROM people p
                JOIN tiers t ON p.tier_id = t.id
                WHERE p.id = ? AND p.is_active = 1
            ''', (person_id,))
            result = cursor.fetchone()
            if result:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, result))
        return None
    
    def get_people(self, tier_id: Optional[str] = None) -> pd.DataFrame:
        """Get all people or people in a specific tier"""
        with self.get_connection() as conn:
            if tier_id:
                return pd.read_sql_query('''
                    SELECT p.*, t.name as tier_name
                    FROM people p
                    JOIN tiers t ON p.tier_id = t.id
                    WHERE p.tier_id = ? AND p.is_active = 1
                    ORDER BY p.name
                ''', conn, params=(tier_id,))
            else:
                return pd.read_sql_query('''
                    SELECT p.*, t.name as tier_name
                    FROM people p
                    JOIN tiers t ON p.tier_id = t.id
                    WHERE p.is_active = 1
                    ORDER BY t.level, p.name
                ''', conn)
    
    # Escalation management methods
    def create_escalation(self, title: str, description: str, urgency: str, created_by: str, source_tier_id: str) -> str:
        """Create a new escalation"""
        escalation_id = str(uuid.uuid4())
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO escalations (id, title, description, urgency, created_by, source_tier_id, current_tier_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (escalation_id, title, description, urgency, created_by, source_tier_id, source_tier_id))
            
            # Add history entry
            self._add_escalation_history(cursor, escalation_id, "Created", created_by, None, "Open")
            conn.commit()
        return escalation_id
    
    def escalate_to_next_tier(self, escalation_id: str, target_tier_id: str, assigned_to: str, performed_by: str) -> bool:
        """Escalate an escalation to the next tier"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE escalations 
                SET target_tier_id = ?, assigned_to = ?, current_tier_id = ?, 
                    status = 'In Progress', escalated_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (target_tier_id, assigned_to, target_tier_id, escalation_id))
            
            self._add_escalation_history(cursor, escalation_id, "Escalated", performed_by, "Open", "In Progress")
            conn.commit()
            return True
    
    def provide_feedback(self, escalation_id: str, feedback: str, performed_by: str) -> bool:
        """Provide feedback on an escalation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE escalations 
                SET feedback = ?, status = 'Pending Feedback', resolved_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (feedback, escalation_id))
            
            self._add_escalation_history(cursor, escalation_id, "Feedback Provided", performed_by, "In Progress", "Pending Feedback")
            conn.commit()
            return True
    
    def close_escalation(self, escalation_id: str, performed_by: str) -> bool:
        """Close an escalation"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE escalations 
                SET status = 'Closed', closed_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (escalation_id,))
            
            self._add_escalation_history(cursor, escalation_id, "Closed", performed_by, "Pending Feedback", "Closed")
            conn.commit()
            return True
    
    def delete_escalation(self, escalation_id: str, performed_by: str) -> bool:
        """Delete an escalation (only by creator/owner)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verify the user is the creator of the escalation
            cursor.execute('SELECT created_by FROM escalations WHERE id = ?', (escalation_id,))
            result = cursor.fetchone()
            if not result or result[0] != performed_by:
                return False
            
            # Delete the escalation and its history
            cursor.execute('DELETE FROM escalation_history WHERE escalation_id = ?', (escalation_id,))
            cursor.execute('DELETE FROM escalations WHERE id = ?', (escalation_id,))
            
            conn.commit()
            return True
    
    def return_escalation_to_creator(self, escalation_id: str, feedback: str, performed_by: str) -> bool:
        """Return escalation to creator with feedback"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get the source tier to return escalation to
            cursor.execute('SELECT source_tier_id FROM escalations WHERE id = ?', (escalation_id,))
            result = cursor.fetchone()
            if not result:
                return False
            
            source_tier_id = result[0]
            
            cursor.execute('''
                UPDATE escalations 
                SET feedback = ?, status = 'Pending Feedback', current_tier_id = ?, 
                    resolved_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (feedback, source_tier_id, escalation_id))
            
            self._add_escalation_history(cursor, escalation_id, "Returned to Creator", performed_by, "In Progress", "Pending Feedback", feedback)
            conn.commit()
            return True
    
    def get_escalations(self, tier_id: Optional[str] = None, person_id: Optional[str] = None, 
                       status_filter: Optional[str] = None) -> pd.DataFrame:
        """Get escalations with various filters"""
        base_query = '''
            SELECT e.*, 
                   creator.name as created_by_name,
                   assignee.name as assigned_to_name,
                   st.name as source_tier_name,
                   tt.name as target_tier_name,
                   ct.name as current_tier_name,
                   CAST((julianday('now') - julianday(e.created_at)) AS INTEGER) as days_open,
                   CASE 
                       WHEN e.escalated_at IS NOT NULL 
                       THEN CAST((julianday('now') - julianday(e.escalated_at)) AS INTEGER)
                       ELSE NULL 
                   END as days_since_escalation
            FROM escalations e
            JOIN people creator ON e.created_by = creator.id
            LEFT JOIN people assignee ON e.assigned_to = assignee.id
            JOIN tiers st ON e.source_tier_id = st.id
            LEFT JOIN tiers tt ON e.target_tier_id = tt.id
            JOIN tiers ct ON e.current_tier_id = ct.id
            WHERE 1=1
        '''
        
        params = []
        if tier_id:
            base_query += ' AND e.current_tier_id = ?'
            params.append(tier_id)
        
        if person_id:
            base_query += ' AND (e.created_by = ? OR e.assigned_to = ?)'
            params.extend([person_id, person_id])
        
        if status_filter and status_filter != 'All':
            base_query += ' AND e.status = ?'
            params.append(status_filter)
        
        base_query += ' ORDER BY e.created_at DESC'
        
        with self.get_connection() as conn:
            return pd.read_sql_query(base_query, conn, params=params)
    
    def _add_escalation_history(self, cursor, escalation_id: str, action: str, performed_by: str, 
                               from_status: Optional[str], to_status: Optional[str], notes: str = ""):
        """Add an entry to the escalation history"""
        history_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO escalation_history (id, escalation_id, action, performed_by, from_status, to_status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (history_id, escalation_id, action, performed_by, from_status, to_status, notes))
    
    def get_escalation_history(self, escalation_id: str) -> pd.DataFrame:
        """Get history for a specific escalation"""
        with self.get_connection() as conn:
            return pd.read_sql_query('''
                SELECT eh.*, p.name as performed_by_name
                FROM escalation_history eh
                JOIN people p ON eh.performed_by = p.id
                WHERE eh.escalation_id = ?
                ORDER BY eh.timestamp DESC
            ''', conn, params=(escalation_id,))

# Initialize database manager
db = DatabaseManager()