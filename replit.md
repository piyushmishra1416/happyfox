# Intelligent Support Ticket Assignment System

## Overview

This is a Python-based intelligent support ticket assignment system developed for a PyCon25 Hackathon project. The system automatically assigns IT support tickets to the most suitable agents based on skill matching, workload balancing, agent experience levels, and availability status. It uses machine learning-style scoring algorithms to optimize ticket assignments and improve support efficiency.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Algorithm Design
The system implements a multi-factor scoring algorithm that evaluates agents against tickets using several weighted criteria:
- **Skill Matching**: Uses keyword extraction and skill level scoring to match ticket requirements with agent capabilities
- **Workload Balancing**: Considers current agent workload to prevent overloading and ensure fair distribution
- **Experience Weighting**: Factors in agent experience levels for complex or high-priority tickets
- **Availability Filtering**: Only considers agents with "Available" status for new assignments

### Data Processing Pipeline
The architecture follows a linear processing approach:
1. **Data Loading**: Reads JSON datasets containing agent profiles and ticket information
2. **Keyword Mapping**: Builds skill-to-keyword mappings for improved text matching
3. **Score Calculation**: Applies weighted scoring algorithm to evaluate agent-ticket compatibility
4. **Assignment Output**: Generates structured assignment results with rationale explanations

### File Structure
- `ticket_assignment.py`: Main system implementation with the TicketAssignmentSystem class
- `dataset.json`: Primary data source containing agent profiles and ticket information
- `output_result.json`: Generated assignment results with explanations
- `attached_assets/`: Sample data files for testing and validation

### Algorithm Components
The system uses several key components for intelligent assignment:
- **Text Analysis**: Extracts keywords from ticket descriptions to match against agent skills
- **Weighted Scoring**: Combines multiple factors (skill match, workload, experience) into a single compatibility score
- **Constraint Handling**: Respects agent availability and capacity limits
- **Rationale Generation**: Provides human-readable explanations for each assignment decision

## External Dependencies

### Core Python Libraries
- **json**: For parsing agent and ticket data from JSON files
- **re**: For regular expression-based keyword extraction and text processing
- **math**: For mathematical operations in scoring calculations
- **collections.defaultdict**: For efficient data structure management during processing
- **typing**: For type hints and better code documentation

### Data Format Requirements
The system expects JSON input files with specific schema:
- **Agent Data**: Must include agent_id, name, skills (with proficiency levels), current_load, availability_status, and experience_level
- **Ticket Data**: Should contain ticket_id, title/description, priority level, and any relevant metadata for skill matching

No external APIs, databases, or third-party services are currently integrated, making this a self-contained Python application suitable for local deployment or integration into existing IT service management systems.