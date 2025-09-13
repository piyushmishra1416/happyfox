#!/usr/bin/env python3
"""
Intelligent Support Ticket Assignment System
PyCon25 Hackathon Project

This system optimally assigns support tickets to agents based on:
- Skill matching with ticket descriptions
- Workload balancing
- Agent experience levels
- Availability status
"""

import json
import re
import math
from collections import defaultdict
from typing import Dict, List, Tuple, Any

class TicketAssignmentSystem:
    def __init__(self, dataset_file: str = "dataset.json"):
        """Initialize the assignment system with dataset."""
        self.dataset_file = dataset_file
        self.agents = []
        self.tickets = []
        self.assignments = []
        
        # Load data
        self.load_data()
        
        # Skill keyword mappings for better matching
        self.skill_keywords = self._build_skill_keywords()
        
    def load_data(self):
        """Load agents and tickets data from JSON file."""
        try:
            with open(self.dataset_file, 'r') as f:
                data = json.load(f)
                self.agents = data['agents']
                self.tickets = data['tickets']
            print(f"Loaded {len(self.agents)} agents and {len(self.tickets)} tickets")
        except FileNotFoundError:
            print(f"Error: Dataset file '{self.dataset_file}' not found")
            raise
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in dataset file '{self.dataset_file}'")
            raise
    
    def _build_skill_keywords(self) -> Dict[str, List[str]]:
        """Build keyword mappings for each skill to improve matching."""
        skill_keywords = {
            # Networking
            "Networking": ["network", "connectivity", "connection", "internet", "lan", "wan"],
            "VPN_Troubleshooting": ["vpn", "remote", "tunnel", "authentication", "dropped", "disconnection"],
            "Network_Security": ["security", "firewall", "intrusion", "attack", "breach"],
            "Network_Monitoring": ["monitoring", "performance", "bandwidth", "latency"],
            "Switch_Configuration": ["switch", "vlan", "port", "configuration"],
            "Routing_Protocols": ["routing", "protocol", "gateway", "route"],
            "Cisco_IOS": ["cisco", "ios", "router", "switch"],
            "DNS_Configuration": ["dns", "domain", "resolution", "nslookup"],
            "Network_Cabling": ["cable", "ethernet", "physical", "wiring"],
            
            # Security
            "Endpoint_Security": ["endpoint", "malware", "virus", "protection"],
            "Antivirus_Malware": ["antivirus", "malware", "virus", "threat", "infection"],
            "Phishing_Analysis": ["phishing", "email", "suspicious", "spam", "impersonating"],
            "Security_Audits": ["audit", "compliance", "security", "policy"],
            "SIEM_Logging": ["logging", "log", "siem", "monitoring", "events"],
            "Identity_Management": ["identity", "access", "permissions", "group"],
            "Firewall_Configuration": ["firewall", "port", "rule", "block", "allow"],
            
            # Windows/Microsoft
            "Windows_Server_2022": ["windows", "server", "2022", "domain"],
            "Active_Directory": ["active directory", "ad", "domain", "login", "authentication", "account", "user", "sso"],
            "Microsoft_365": ["microsoft", "365", "office", "outlook", "email", "teams"],
            "SharePoint_Online": ["sharepoint", "collaboration", "document", "site"],
            "PowerShell_Scripting": ["powershell", "script", "automation", "cmdlet"],
            "Endpoint_Management": ["endpoint", "device", "management", "policy"],
            "Windows_OS": ["windows", "desktop", "workstation", "pc"],
            
            # Hardware
            "Hardware_Diagnostics": ["hardware", "diagnostic", "component", "failure", "repair"],
            "Laptop_Repair": ["laptop", "notebook", "portable", "mobile", "boot", "repair"],
            "Printer_Troubleshooting": ["printer", "print", "queue", "toner", "paper"],
            
            # Database
            "Database_SQL": ["database", "sql", "query", "table", "performance", "slow"],
            "ETL_Processes": ["etl", "data", "extract", "transform", "load"],
            "Data_Warehousing": ["warehouse", "data", "analytics", "reporting"],
            "PowerBI_Tableau": ["powerbi", "tableau", "visualization", "dashboard"],
            
            # Cloud
            "Cloud_AWS": ["aws", "amazon", "cloud", "ec2", "s3"],
            "Cloud_Azure": ["azure", "microsoft", "cloud", "app service", "website"],
            "DevOps_CI_CD": ["devops", "jenkins", "ci", "cd", "deployment", "build"],
            "Kubernetes_Docker": ["kubernetes", "docker", "container", "orchestration"],
            
            # Linux/Unix
            "Linux_Administration": ["linux", "unix", "server", "permission", "chmod", "directory"],
            "Mac_OS": ["mac", "macos", "apple", "macbook", "samba"],
            
            # Programming/Development
            "Python_Scripting": ["python", "script", "automation", "code"],
            
            # Integration/API
            "SaaS_Integrations": ["saas", "integration", "api", "third-party"],
            "API_Troubleshooting": ["api", "rest", "web service", "integration"],
            "Web_Server_Apache_Nginx": ["web server", "apache", "nginx", "http"],
            "SSL_Certificates": ["ssl", "certificate", "https", "encryption"],
            
            # VoIP/Communication
            "Voice_VoIP": ["voice", "voip", "phone", "calling", "sip"],
            
            # Virtualization
            "Virtualization_VMware": ["vmware", "virtual", "vm", "hypervisor"],
            
            # Licensing
            "Software_Licensing": ["license", "software", "activation", "key"]
        }
        return skill_keywords
    
    def extract_keywords_from_ticket(self, ticket: Dict[str, Any]) -> List[str]:
        """Extract relevant keywords from ticket title and description."""
        text = f"{ticket['title']} {ticket['description']}".lower()
        
        # Remove common stop words and clean text
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'we', 'they', 'it', 'he', 'she', 'you', 'i', 'we', 'our', 'their', 'his', 'her', 'your', 'my'}
        
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        return keywords
    
    def has_domain_term(self, text: str, terms: List[str]) -> bool:
        """Check if text contains any of the terms using word boundaries to avoid false matches."""
        for term in terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text):
                return True
        return False
    
    def calculate_skill_match_score(self, ticket: Dict[str, Any], agent: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Calculate how well an agent's skills match a ticket's requirements."""
        ticket_keywords = self.extract_keywords_from_ticket(ticket)
        ticket_text = f"{ticket['title']} {ticket['description']}".lower()
        
        total_score = 0
        matched_skills = []
        
        # Platform/domain detection for inverse signals using word boundaries
        is_linux_ticket = self.has_domain_term(ticket_text, ['linux', 'unix', 'chmod', 'directory permissions'])
        is_windows_ticket = self.has_domain_term(ticket_text, ['windows', 'active directory', 'outlook', 'microsoft'])
        is_mac_ticket = self.has_domain_term(ticket_text, ['mac', 'macos', 'macbook', 'samba'])
        is_security_ticket = self.has_domain_term(ticket_text, ['security', 'phishing', 'attack', 'breach', 'locked', 'suspicious'])
        is_hardware_ticket = self.has_domain_term(ticket_text, ['laptop', 'hardware', 'boot', 'printer', 'diagnostic'])
        is_network_ticket = self.has_domain_term(ticket_text, ['network', 'vpn', 'connection', 'firewall', 'dns'])
        is_database_ticket = self.has_domain_term(ticket_text, ['database', 'sql', 'query', 'performance', 'slow'])
        is_cloud_ticket = self.has_domain_term(ticket_text, ['azure', 'aws', 'cloud', 'website', 'app service'])
        
        # Check each agent skill against ticket keywords
        for skill, skill_level in agent['skills'].items():
            skill_score = 0
            skill_keywords = self.skill_keywords.get(skill, [])
            
            # Domain boost/penalty system
            domain_multiplier = 1.0
            
            # Linux domain
            if 'Linux' in skill and is_linux_ticket:
                domain_multiplier = 2.0
            elif 'Linux' in skill and is_windows_ticket:
                domain_multiplier = 0.3
            
            # Windows domain
            elif any(windows_term in skill for windows_term in ['Windows', 'Active_Directory', 'Microsoft']) and is_windows_ticket:
                domain_multiplier = 2.0
            elif any(windows_term in skill for windows_term in ['Windows', 'Active_Directory', 'Microsoft']) and is_linux_ticket:
                domain_multiplier = 0.3
            
            # Mac domain
            elif 'Mac' in skill and is_mac_ticket:
                domain_multiplier = 2.0
            
            # Security domain
            elif any(sec_term in skill for sec_term in ['Security', 'Phishing', 'Antivirus', 'Firewall']) and is_security_ticket:
                domain_multiplier = 1.8
            
            # Hardware domain
            elif any(hw_term in skill for hw_term in ['Hardware', 'Laptop', 'Printer']) and is_hardware_ticket:
                domain_multiplier = 1.8
            
            # Network domain
            elif any(net_term in skill for net_term in ['Network', 'VPN', 'DNS', 'Routing']) and is_network_ticket:
                domain_multiplier = 1.8
            
            # Database domain
            elif 'Database' in skill and is_database_ticket:
                domain_multiplier = 2.0
            
            # Cloud domain
            elif any(cloud_term in skill for cloud_term in ['Cloud', 'Azure', 'AWS', 'DevOps']) and is_cloud_ticket:
                domain_multiplier = 1.8
            
            # Exact phrase matching (highest weight)
            for keyword in skill_keywords:
                if keyword in ticket_text:
                    skill_score += 3  # Highest weight for exact phrase matches
            
            # Token-level matching
            for keyword in skill_keywords:
                for ticket_keyword in ticket_keywords:
                    if keyword == ticket_keyword:  # Exact match
                        skill_score += 2
                    elif keyword in ticket_keyword or ticket_keyword in keyword:  # Partial match
                        skill_score += 1
            
            # Skill name matching
            skill_name_words = skill.lower().replace('_', ' ').split()
            for skill_word in skill_name_words:
                if skill_word in ticket_keywords:
                    skill_score += 2
            
            if skill_score > 0:
                # Apply domain multiplier and skill level weighting
                weighted_score = skill_score * skill_level * domain_multiplier
                total_score += weighted_score
                matched_skills.append(skill)
        
        # Normalize score by square root of skills count to reduce bias
        if len(agent['skills']) > 0:
            normalized_score = total_score / math.sqrt(len(agent['skills']))
        else:
            normalized_score = 0
            
        return normalized_score, matched_skills
    
    def calculate_workload_score(self, agent: Dict[str, Any], current_assignments: int = 0) -> float:
        """Calculate workload score with fairness penalty (higher score = less loaded)."""
        # Current load plus any new assignments in this session
        total_load = agent['current_load'] + current_assignments
        
        # Exponential penalty for high loads to promote fairness
        max_reasonable_load = 8
        if total_load >= max_reasonable_load:
            load_score = 0.1  # Very low score for overloaded agents
        else:
            # Exponential decay to heavily favor less loaded agents
            load_score = math.exp(-(total_load / 3.0))
        
        # Availability factor
        availability_factor = 1.0 if agent['availability_status'] == 'Available' else 0.2
        
        return load_score * availability_factor
    
    def calculate_experience_score(self, agent: Dict[str, Any]) -> float:
        """Calculate experience score based on agent's experience level."""
        # Normalize experience (assuming max experience is 15)
        max_experience = 15
        return min(agent['experience_level'], max_experience) / max_experience
    
    def calculate_ticket_priority(self, ticket: Dict[str, Any]) -> float:
        """Calculate ticket priority based on keywords and content."""
        title_lower = ticket['title'].lower()
        description_lower = ticket['description'].lower()
        
        # High priority keywords
        high_priority_keywords = [
            'critical', 'urgent', 'emergency', 'down', 'outage', 'breach', 'security',
            'production', 'business-critical', 'attack', 'locked', 'unreachable',
            'slow performance', 'phishing'
        ]
        
        # Medium priority keywords
        medium_priority_keywords = [
            'unable', 'error', 'problem', 'issue', 'failed', 'not working',
            'access denied', 'boot', 'laptop'
        ]
        
        priority_score = 1.0  # Base priority
        
        # Check for high priority indicators
        for keyword in high_priority_keywords:
            if keyword in title_lower or keyword in description_lower:
                priority_score += 2.0
        
        # Check for medium priority indicators
        for keyword in medium_priority_keywords:
            if keyword in title_lower or keyword in description_lower:
                priority_score += 1.0
        
        return min(priority_score, 5.0)  # Cap at 5.0
    
    def calculate_composite_score_with_fairness(self, ticket: Dict[str, Any], agent: Dict[str, Any], current_assignments: int) -> Tuple[float, Dict[str, Any]]:
        """Calculate composite score for agent-ticket assignment with fairness considerations."""
        skill_score, matched_skills = self.calculate_skill_match_score(ticket, agent)
        workload_score = self.calculate_workload_score(agent, current_assignments)
        experience_score = self.calculate_experience_score(agent)
        ticket_priority = self.calculate_ticket_priority(ticket)
        
        # If skill score is very low, heavily penalize to avoid mismatches
        skill_threshold = 5.0  # Minimum acceptable skill match
        if skill_score < skill_threshold:
            skill_penalty = 0.3  # Heavy penalty for poor skill matches
        else:
            skill_penalty = 1.0
        
        # Weighted combination with higher emphasis on skill matching and fairness
        composite_score = (
            skill_score * 0.6 +      # 60% weight on skill matching (increased)
            workload_score * 0.3 +   # 30% weight on workload balance
            experience_score * 0.1   # 10% weight on experience (reduced)
        ) * ticket_priority * skill_penalty  # Apply skill penalty and priority
        
        score_details = {
            'skill_score': skill_score,
            'workload_score': workload_score,
            'experience_score': experience_score,
            'ticket_priority': ticket_priority,
            'matched_skills': matched_skills,
            'current_assignments': current_assignments,
            'skill_penalty': skill_penalty,
            'composite_score': composite_score
        }
        
        return composite_score, score_details
    
    def assign_tickets(self) -> List[Dict[str, Any]]:
        """Assign all tickets to optimal agents with improved fairness."""
        assignments = []
        agent_assignment_counts = {agent['agent_id']: 0 for agent in self.agents}
        
        # Sort tickets by priority (descending)
        sorted_tickets = sorted(
            self.tickets, 
            key=lambda t: self.calculate_ticket_priority(t), 
            reverse=True
        )
        
        for ticket in sorted_tickets:
            best_agent = None
            best_score = -1
            best_details = None
            
            # Evaluate each available agent
            for agent in self.agents:
                if agent['availability_status'] != 'Available':
                    continue
                
                # Calculate current assignment count for fairness
                current_assignments = agent_assignment_counts[agent['agent_id']]
                
                score, details = self.calculate_composite_score_with_fairness(ticket, agent, current_assignments)
                
                if score > best_score:
                    best_score = score
                    best_agent = agent
                    best_details = details
            
            if best_agent and best_details:
                
                # Create assignment
                assignment = {
                    "ticket_id": ticket['ticket_id'],
                    "title": ticket['title'],
                    "assigned_agent_id": best_agent['agent_id'],
                    "rationale": self._generate_rationale(ticket, best_agent, best_details)
                }
                
                assignments.append(assignment)
                
                # Update assignment count
                agent_assignment_counts[best_agent['agent_id']] += 1
            else:
                print(f"Warning: Could not assign ticket {ticket['ticket_id']} - no available agents")
        
        return assignments
    
    def _generate_rationale(self, ticket: Dict[str, Any], agent: Dict[str, Any], score_details: Dict[str, Any]) -> str:
        """Generate human-readable rationale for the assignment."""
        matched_skills = score_details['matched_skills']
        
        # Get top skills that matched
        top_skills = []
        for skill in matched_skills[:3]:  # Top 3 matched skills
            skill_level = agent['skills'][skill]
            skill_display = skill.replace('_', ' ')
            top_skills.append(f"'{skill_display}' ({skill_level})")
        
        # Build rationale
        rationale_parts = [
            f"Assigned to {agent['name']} ({agent['agent_id']})"
        ]
        
        if top_skills:
            skills_text = " and ".join(top_skills)
            rationale_parts.append(f"based on strong skills in {skills_text}")
        
        # Add workload consideration
        if agent['current_load'] <= 2:
            rationale_parts.append("and low current workload")
        elif agent['current_load'] <= 4:
            rationale_parts.append("and moderate workload")
        
        # Add experience consideration if significant
        if agent['experience_level'] >= 9:
            rationale_parts.append("with extensive experience")
        elif agent['experience_level'] >= 7:
            rationale_parts.append("with solid experience")
        
        return ", ".join(rationale_parts) + "."
    
    def save_results(self, assignments: List[Dict[str, Any]], output_file: str = "output_result.json"):
        """Save assignment results to JSON file."""
        output_data = {"assignments": assignments}
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"Results saved to {output_file}")
        print(f"Total assignments: {len(assignments)}")
    
    def run(self):
        """Run the complete ticket assignment process."""
        print("Starting Intelligent Ticket Assignment System...")
        print("=" * 50)
        
        # Perform assignments
        assignments = self.assign_tickets()
        
        # Save results
        self.save_results(assignments)
        
        # Display summary
        self._display_summary(assignments)
        
        return assignments
    
    def _display_summary(self, assignments: List[Dict[str, Any]]):
        """Display assignment summary statistics."""
        print("\n" + "=" * 50)
        print("ASSIGNMENT SUMMARY")
        print("=" * 50)
        
        # Agent workload distribution
        agent_assignment_count = defaultdict(int)
        for assignment in assignments:
            agent_assignment_count[assignment['assigned_agent_id']] += 1
        
        print(f"\nAgent Workload Distribution:")
        for agent in self.agents:
            agent_id = agent['agent_id']
            new_assignments = agent_assignment_count[agent_id]
            total_load = agent['current_load'] + new_assignments
            print(f"  {agent['name']} ({agent_id}): {new_assignments} new tickets, {total_load} total load")
        
        print(f"\nTotal tickets processed: {len(self.tickets)}")
        print(f"Total tickets assigned: {len(assignments)}")
        print(f"Assignment success rate: {len(assignments)/len(self.tickets)*100:.1f}%")

def main():
    """Main function to run the ticket assignment system."""
    try:
        # Create and run the assignment system
        system = TicketAssignmentSystem()
        assignments = system.run()
        
        print("\n✅ Ticket assignment completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())