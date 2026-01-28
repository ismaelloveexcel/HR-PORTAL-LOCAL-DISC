#!/usr/bin/env python3
"""
Seed HR Templates for Performance Evaluation and Employee Recognition

This script creates the following modern, flexible templates:
1. Performance Evaluation - Non-Managerial Positions (2025)
2. Performance Evaluation - Managerial Positions (2025)
3. Employee of the Year Nomination Form

Templates use a JSON-based schema for flexibility and programmatic manipulation.

Usage:
    cd backend
    uv run python ../scripts/seed_hr_templates.py
"""

import asyncio
import json
import os
import sys

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import get_engine, AsyncSessionLocal
from app.models.template import Template
from sqlalchemy import select


# Professional Performance Evaluation Template - Non-Managerial Positions
PERFORMANCE_EVAL_NON_MANAGERIAL = json.dumps({
    "schema_version": "2.0",
    "template_type": "performance_evaluation",
    "category": "non_managerial",
    "title": "Annual Performance Evaluation",
    "subtitle": "Non-Managerial Staff Assessment",
    "confidentiality_notice": "CONFIDENTIAL - This document contains sensitive personnel information and should be handled in accordance with company policy.",
    "evaluation_period": {
        "year": 2025,
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "configurable": True
    },
    "settings": {
        "allow_self_assessment": True,
        "require_goals": True,
        "min_goals": 1,
        "max_goals": 5,
        "enable_continuous_feedback": True,
        "enable_mid_year_review": True,
        "rating_style": "numeric",
        "display_mode": "professional",
        "show_visual_indicators": True,
        "allow_anonymous_peer_feedback": False,
        "auto_calculate_score": True
    },
    "rating_scales": {
        "default": {
            "type": "numeric",
            "min": 1,
            "max": 5,
            "labels": {
                "1": {"text": "Needs Improvement", "short": "NI", "color": "#dc2626", "description": "Performance consistently falls below expectations; immediate improvement required"},
                "2": {"text": "Developing", "short": "D", "color": "#ea580c", "description": "Performance occasionally meets expectations; development plan recommended"},
                "3": {"text": "Meets Expectations", "short": "ME", "color": "#ca8a04", "description": "Performance consistently meets job requirements and expectations"},
                "4": {"text": "Exceeds Expectations", "short": "EE", "color": "#16a34a", "description": "Performance frequently exceeds job requirements; role model in key areas"},
                "5": {"text": "Outstanding", "short": "O", "color": "#059669", "description": "Exceptional performance in all areas; consistently delivers beyond expectations"}
            }
        },
        "overall": {
            "type": "percentage_bands",
            "bands": [
                {"min": 90, "max": 100, "label": "Outstanding Performance", "code": "A"},
                {"min": 75, "max": 89, "label": "Exceeds Expectations", "code": "B"},
                {"min": 60, "max": 74, "label": "Meets Expectations", "code": "C"},
                {"min": 40, "max": 59, "label": "Developing", "code": "D"},
                {"min": 0, "max": 39, "label": "Needs Improvement", "code": "E"}
            ]
        }
    },
    "employee_info": {
        "fields": [
            {"id": "employee_name", "label": "Employee Name", "type": "text", "source": "auto", "editable": False},
            {"id": "employee_number", "label": "Employee ID", "type": "text", "source": "auto", "editable": False},
            {"id": "job_title", "label": "Job Title", "type": "text", "source": "auto", "editable": False},
            {"id": "department", "label": "Department", "type": "text", "source": "auto", "editable": False},
            {"id": "line_manager", "label": "Line Manager", "type": "text", "source": "auto", "editable": False},
            {"id": "date_of_joining", "label": "Date of Joining", "type": "date", "source": "auto", "editable": False},
            {"id": "evaluation_date", "label": "Evaluation Date", "type": "date", "source": "input", "editable": True}
        ]
    },
    "competencies": {
        "configurable": True,
        "allow_custom": True,
        "categories": [
            {
                "id": "core_competencies",
                "name": "Core Competencies",
                "description": "Essential skills for all employees",
                "items": [
                    {
                        "id": "job_knowledge",
                        "name": "Job Knowledge & Skills",
                        "description": "Understanding of role, technical skills, continuous learning",
                        "weight": 20,
                        "required": True,
                        "behaviors": [
                            "Demonstrates thorough understanding of job responsibilities",
                            "Applies technical skills effectively",
                            "Seeks opportunities for professional development"
                        ]
                    },
                    {
                        "id": "quality",
                        "name": "Quality of Work",
                        "description": "Accuracy, thoroughness, attention to detail",
                        "weight": 20,
                        "required": True,
                        "behaviors": [
                            "Produces accurate, error-free work",
                            "Meets quality standards consistently",
                            "Takes pride in deliverables"
                        ]
                    },
                    {
                        "id": "productivity",
                        "name": "Productivity & Efficiency",
                        "description": "Work volume, deadline management, time optimization",
                        "weight": 15,
                        "required": True,
                        "behaviors": [
                            "Completes tasks within deadlines",
                            "Manages workload effectively",
                            "Uses time and resources efficiently"
                        ]
                    },
                    {
                        "id": "communication",
                        "name": "Communication & Collaboration",
                        "description": "Written/verbal skills, teamwork, relationship building",
                        "weight": 15,
                        "required": True,
                        "behaviors": [
                            "Communicates clearly and professionally",
                            "Collaborates effectively with team members",
                            "Builds positive working relationships"
                        ]
                    },
                    {
                        "id": "initiative",
                        "name": "Initiative & Problem Solving",
                        "description": "Proactivity, creativity, ownership",
                        "weight": 15,
                        "required": True,
                        "behaviors": [
                            "Takes initiative without being asked",
                            "Identifies and resolves problems proactively",
                            "Brings innovative ideas and solutions"
                        ]
                    }
                ]
            },
            {
                "id": "values_alignment",
                "name": "Values & Culture",
                "description": "Alignment with company values",
                "items": [
                    {
                        "id": "integrity",
                        "name": "Integrity & Ethics",
                        "description": "Honesty, ethical behavior, compliance",
                        "weight": 10,
                        "required": True,
                        "behaviors": [
                            "Acts with honesty and transparency",
                            "Follows company policies and procedures",
                            "Demonstrates ethical decision-making"
                        ]
                    },
                    {
                        "id": "adaptability",
                        "name": "Adaptability & Growth Mindset",
                        "description": "Flexibility, learning from feedback, resilience",
                        "weight": 5,
                        "required": False,
                        "behaviors": [
                            "Adapts to changing priorities",
                            "Embraces feedback for improvement",
                            "Shows resilience in challenging situations"
                        ]
                    }
                ]
            }
        ]
    },
    "sections": [
        {
            "id": "achievements",
            "name": "Key Achievements & Accomplishments",
            "type": "dynamic_list",
            "description": "Document significant accomplishments during the evaluation period",
            "min_items": 1,
            "max_items": 10,
            "item_schema": {
                "title": {"type": "text", "label": "Achievement Title", "max_length": 200},
                "description": {"type": "textarea", "label": "Description & Context", "max_length": 1000},
                "impact": {"type": "select", "label": "Scope of Impact", "options": ["Individual Contributor", "Team Level", "Department Level", "Organization-Wide"]},
                "date": {"type": "date", "label": "Date Achieved"},
                "quantifiable_results": {"type": "text", "label": "Measurable Outcomes (if applicable)", "required": False}
            }
        },
        {
            "id": "goals",
            "name": "Professional Development Goals",
            "type": "goal_tracker",
            "description": "Establish SMART objectives for the upcoming evaluation period",
            "enable_okr_format": True,
            "item_schema": {
                "goal": {"type": "text", "label": "Objective", "required": True},
                "key_results": {"type": "dynamic_list", "label": "Key Results / Success Metrics", "max_items": 5},
                "target_date": {"type": "date", "label": "Target Completion Date", "required": True},
                "resources": {"type": "textarea", "label": "Required Resources & Support"},
                "progress": {"type": "slider", "label": "Progress (%)", "min": 0, "max": 100, "step": 5}
            }
        },
        {
            "id": "feedback",
            "name": "Continuous Performance Feedback",
            "type": "feedback_log",
            "description": "Documented feedback received throughout the evaluation period",
            "auto_populated": True,
            "item_schema": {
                "date": {"type": "date", "label": "Date"},
                "from": {"type": "text", "label": "Source"},
                "type": {"type": "select", "label": "Feedback Type", "options": ["Recognition", "Developmental", "Recommendation"]},
                "content": {"type": "textarea", "label": "Feedback Details"}
            }
        },
        {
            "id": "self_assessment",
            "name": "Employee Self-Assessment",
            "type": "rich_text",
            "description": "Provide a comprehensive reflection on your performance during this period",
            "prompts": [
                "Summarize your key contributions and achievements this evaluation period.",
                "Describe challenges you encountered and how you addressed them.",
                "Identify areas where you have demonstrated professional growth.",
                "Outline opportunities for continued development."
            ],
            "max_length": 3000
        },
        {
            "id": "manager_comments",
            "name": "Manager Assessment & Comments",
            "type": "rich_text",
            "role_restricted": ["manager", "hr"],
            "description": "Provide comprehensive feedback on employee performance",
            "max_length": 3000
        },
        {
            "id": "development_areas",
            "name": "Recommended Development Areas",
            "type": "tag_select",
            "allow_custom": True,
            "suggested_tags": [
                "Technical Proficiency", "Business Communication", "Leadership Development", 
                "Time Management", "Project Management", "Stakeholder Engagement", 
                "Analytical Skills", "Presentation Skills", "Strategic Planning", 
                "Team Collaboration", "Process Improvement", "Industry Knowledge"
            ]
        }
    ],
    "workflow": {
        "steps": [
            {"id": "self_review", "name": "Self Assessment", "actor": "employee", "deadline_days": 7},
            {"id": "manager_review", "name": "Manager Review", "actor": "manager", "deadline_days": 7},
            {"id": "calibration", "name": "Calibration", "actor": "hr", "optional": True},
            {"id": "discussion", "name": "Review Discussion", "actors": ["employee", "manager"], "deadline_days": 5},
            {"id": "acknowledgment", "name": "Employee Acknowledgment", "actor": "employee", "deadline_days": 3}
        ],
        "notifications": {
            "enabled": True,
            "channels": ["email", "in_app"],
            "reminders": [7, 3, 1]
        }
    },
    "signatures": {
        "required": ["employee", "manager"],
        "optional": ["hr"],
        "digital_signature": True
    }
}, indent=2)


# Professional Performance Evaluation Template - Managerial Positions
PERFORMANCE_EVAL_MANAGERIAL = json.dumps({
    "schema_version": "2.0",
    "template_type": "performance_evaluation",
    "category": "managerial",
    "title": "Leadership Performance Evaluation",
    "subtitle": "Managerial & Supervisory Staff Assessment",
    "confidentiality_notice": "CONFIDENTIAL - This document contains sensitive personnel information and should be handled in accordance with company policy.",
    "evaluation_period": {
        "year": 2025,
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "configurable": True
    },
    "settings": {
        "allow_self_assessment": True,
        "require_goals": True,
        "min_goals": 2,
        "max_goals": 7,
        "enable_continuous_feedback": True,
        "enable_mid_year_review": True,
        "enable_360_feedback": True,
        "rating_style": "numeric",
        "display_mode": "professional",
        "auto_calculate_score": True,
        "include_team_metrics": True
    },
    "rating_scales": {
        "default": {
            "type": "numeric",
            "min": 1,
            "max": 5,
            "labels": {
                "1": {"text": "Needs Improvement", "short": "NI", "color": "#dc2626", "description": "Performance consistently falls below expectations; immediate improvement required"},
                "2": {"text": "Developing", "short": "D", "color": "#ea580c", "description": "Performance occasionally meets expectations; development plan recommended"},
                "3": {"text": "Meets Expectations", "short": "ME", "color": "#ca8a04", "description": "Performance consistently meets job requirements and expectations"},
                "4": {"text": "Exceeds Expectations", "short": "EE", "color": "#16a34a", "description": "Performance frequently exceeds job requirements; role model in key areas"},
                "5": {"text": "Outstanding", "short": "O", "color": "#059669", "description": "Exceptional performance in all areas; consistently delivers beyond expectations"}
            }
        }
    },
    "employee_info": {
        "fields": [
            {"id": "manager_name", "label": "Manager Name", "type": "text", "source": "auto"},
            {"id": "employee_number", "label": "Employee ID", "type": "text", "source": "auto"},
            {"id": "job_title", "label": "Job Title", "type": "text", "source": "auto"},
            {"id": "department", "label": "Department", "type": "text", "source": "auto"},
            {"id": "reporting_to", "label": "Reports To", "type": "text", "source": "auto"},
            {"id": "team_size", "label": "Team Size", "type": "number", "source": "auto"},
            {"id": "evaluation_date", "label": "Evaluation Date", "type": "date", "source": "input"}
        ]
    },
    "competencies": {
        "configurable": True,
        "allow_custom": True,
        "categories": [
            {
                "id": "leadership",
                "name": "Leadership Competencies",
                "items": [
                    {
                        "id": "strategic_thinking",
                        "name": "Strategic Thinking & Vision",
                        "description": "Sets direction, aligns team with organizational goals",
                        "weight": 15,
                        "required": True,
                        "behaviors": [
                            "Develops clear strategic plans",
                            "Communicates vision effectively",
                            "Aligns team objectives with company goals"
                        ]
                    },
                    {
                        "id": "people_leadership",
                        "name": "People Leadership & Development",
                        "description": "Coaching, mentoring, talent development",
                        "weight": 20,
                        "required": True,
                        "behaviors": [
                            "Develops team members' capabilities",
                            "Provides regular coaching and feedback",
                            "Builds succession pipeline"
                        ]
                    },
                    {
                        "id": "decision_making",
                        "name": "Decision Making & Judgment",
                        "description": "Analytical thinking, sound decisions under pressure",
                        "weight": 15,
                        "required": True,
                        "behaviors": [
                            "Makes timely, well-informed decisions",
                            "Considers multiple perspectives",
                            "Takes accountability for outcomes"
                        ]
                    },
                    {
                        "id": "stakeholder_management",
                        "name": "Stakeholder Management",
                        "description": "Building relationships, influencing, communication",
                        "weight": 15,
                        "required": True,
                        "behaviors": [
                            "Builds strong cross-functional relationships",
                            "Manages expectations effectively",
                            "Represents department professionally"
                        ]
                    }
                ]
            },
            {
                "id": "operational",
                "name": "Operational Excellence",
                "items": [
                    {
                        "id": "performance_management",
                        "name": "Performance Management",
                        "description": "Setting expectations, feedback, managing underperformance",
                        "weight": 10,
                        "required": True
                    },
                    {
                        "id": "operational_efficiency",
                        "name": "Operational Efficiency",
                        "description": "Process improvement, resource optimization",
                        "weight": 10,
                        "required": True
                    },
                    {
                        "id": "financial_acumen",
                        "name": "Financial Acumen",
                        "description": "Budget management, cost awareness, ROI focus",
                        "weight": 10,
                        "required": True
                    },
                    {
                        "id": "innovation",
                        "name": "Innovation & Change Leadership",
                        "description": "Driving change, fostering innovation culture",
                        "weight": 5,
                        "required": False
                    }
                ]
            }
        ]
    },
    "sections": [
        {
            "id": "kpis",
            "name": "Key Performance Indicators",
            "type": "kpi_tracker",
            "description": "Document departmental performance against established KPIs",
            "item_schema": {
                "kpi_name": {"type": "text", "label": "Performance Indicator"},
                "target": {"type": "number", "label": "Target Value"},
                "achieved": {"type": "number", "label": "Actual Value"},
                "unit": {"type": "select", "label": "Unit of Measure", "options": ["%", "AED", "Count", "Days", "Score", "Rating"]},
                "trend": {"type": "select", "label": "Performance Trend", "options": ["Improving", "Stable", "Declining"]},
                "variance_explanation": {"type": "textarea", "label": "Variance Analysis (if applicable)", "required": False}
            }
        },
        {
            "id": "team_metrics",
            "name": "Team Performance Metrics",
            "type": "metrics_dashboard",
            "description": "Automated team performance indicators",
            "auto_populated": True,
            "metrics": [
                {"id": "team_size", "label": "Current Team Size", "source": "hr_system"},
                {"id": "turnover_rate", "label": "Annual Turnover Rate", "source": "hr_system"},
                {"id": "engagement_score", "label": "Employee Engagement Score", "source": "survey"},
                {"id": "promotions", "label": "Internal Promotions", "source": "hr_system"},
                {"id": "training_hours", "label": "Average Training Hours per Employee", "source": "lms"},
                {"id": "performance_distribution", "label": "Team Performance Distribution", "source": "hr_system"}
            ]
        },
        {
            "id": "achievements",
            "name": "Key Accomplishments & Business Impact",
            "type": "dynamic_list",
            "description": "Document significant leadership accomplishments and their business impact",
            "min_items": 2,
            "max_items": 10,
            "item_schema": {
                "title": {"type": "text", "label": "Accomplishment"},
                "description": {"type": "textarea", "label": "Description & Context"},
                "metrics": {"type": "text", "label": "Quantifiable Business Impact"},
                "category": {"type": "select", "label": "Category", "options": ["Revenue Growth", "Cost Optimization", "Process Excellence", "Talent Development", "Innovation", "Customer Success", "Risk Management", "Strategic Initiative"]}
            }
        },
        {
            "id": "goals",
            "name": "Strategic Objectives & Key Results",
            "type": "okr_tracker",
            "description": "Establish strategic goals aligned with organizational priorities",
            "item_schema": {
                "objective": {"type": "text", "label": "Strategic Objective"},
                "key_results": {
                    "type": "dynamic_list",
                    "label": "Key Results",
                    "max_items": 5,
                    "item_schema": {
                        "kr": {"type": "text", "label": "Key Result"},
                        "target": {"type": "number", "label": "Target"},
                        "current": {"type": "number", "label": "Current"},
                        "unit": {"type": "text", "label": "Unit"}
                    }
                },
                "status": {"type": "select", "label": "Status", "options": ["On Track", "At Risk", "Behind Schedule", "Completed", "Deferred"]}
            }
        },
        {
            "id": "feedback_360",
            "name": "Multi-Rater Feedback Summary",
            "type": "feedback_360",
            "description": "Consolidated feedback from multiple stakeholder perspectives",
            "sources": ["direct_reports", "peers", "senior_leadership", "cross_functional_partners"],
            "anonymous": True,
            "item_schema": {
                "source_category": {"type": "text", "label": "Feedback Source"},
                "strengths": {"type": "textarea", "label": "Identified Strengths"},
                "development_areas": {"type": "textarea", "label": "Development Opportunities"},
                "themes": {"type": "tag_list", "label": "Key Themes"}
            }
        },
        {
            "id": "self_assessment",
            "name": "Leadership Self-Assessment",
            "type": "structured_reflection",
            "description": "Comprehensive reflection on leadership performance",
            "prompts": [
                {"id": "accomplishments", "text": "Summarize your most significant leadership accomplishments during this evaluation period."},
                {"id": "challenges", "text": "Describe the primary challenges you encountered and the strategies employed to address them."},
                {"id": "team_development", "text": "Detail your contributions to team development and talent growth."},
                {"id": "leadership_growth", "text": "Reflect on your own leadership development and lessons learned."},
                {"id": "strategic_priorities", "text": "Outline your strategic priorities and focus areas for the upcoming period."}
            ]
        }
    ],
    "workflow": {
        "steps": [
            {"id": "self_review", "name": "Self Assessment", "actor": "manager", "deadline_days": 10},
            {"id": "360_collection", "name": "360° Feedback Collection", "actor": "system", "deadline_days": 14},
            {"id": "supervisor_review", "name": "Supervisor Review", "actor": "supervisor", "deadline_days": 7},
            {"id": "calibration", "name": "Leadership Calibration", "actor": "hr", "optional": False},
            {"id": "discussion", "name": "Review Discussion", "actors": ["manager", "supervisor"], "deadline_days": 5},
            {"id": "acknowledgment", "name": "Acknowledgment", "actor": "manager", "deadline_days": 3}
        ]
    },
    "signatures": {
        "required": ["manager", "supervisor"],
        "optional": ["hr_director"],
        "digital_signature": True
    }
}, indent=2)


# Professional Employee of the Year Nomination Form
EMPLOYEE_OF_YEAR_NOMINATION = json.dumps({
    "schema_version": "2.0",
    "template_type": "recognition_nomination",
    "award_type": "employee_of_the_year",
    "title": "Employee of the Year Award Nomination",
    "subtitle": "Annual Excellence Recognition Program",
    "year": 2025,
    "settings": {
        "allow_self_nomination": False,
        "require_endorsements": False,
        "min_endorsements": 0,
        "max_endorsements": 5,
        "anonymous_nominations": False,
        "multiple_nominations_allowed": True,
        "voting_enabled": False,
        "nomination_deadline": "2025-12-15",
        "display_mode": "professional"
    },
    "award_info": {
        "name": "Employee of the Year Award",
        "description": "This prestigious award recognizes an exceptional employee who has demonstrated outstanding performance, exemplified our organizational values, and made significant contributions to our company's success throughout the year.",
        "eligibility": [
            "Minimum one (1) year of continuous service as of December 31, 2025",
            "No active performance improvement plans or disciplinary actions",
            "Demonstrated excellence across multiple performance dimensions",
            "Strong record of attendance and professional conduct"
        ],
        "selection_criteria": "Nominees will be evaluated by a Selection Committee comprising senior leadership and HR representatives. The Committee's decision is final.",
        "recognition": {
            "type": "configurable",
            "components": [
                "Official Certificate of Recognition",
                "Commemorative Award Trophy",
                "Monetary Recognition Bonus",
                "Additional Paid Leave Days",
                "Recognition at Annual Company Event"
            ]
        }
    },
    "categories": [
        {
            "id": "performance",
            "name": "Professional Excellence",
            "weight": 25,
            "description": "Consistently exceeds performance expectations and delivers exceptional results",
            "rating": {"type": "numeric", "min": 1, "max": 5},
            "evidence_required": True,
            "evidence_prompt": "Provide specific examples of exceptional performance and quantifiable achievements"
        },
        {
            "id": "values",
            "name": "Values & Culture Ambassador",
            "weight": 20,
            "description": "Consistently demonstrates and promotes organizational values",
            "rating": {"type": "numeric", "min": 1, "max": 5},
            "evidence_required": True,
            "company_values": ["Integrity", "Excellence", "Innovation", "Collaboration", "Customer Focus", "Accountability"]
        },
        {
            "id": "teamwork",
            "name": "Collaboration & Team Contribution",
            "weight": 20,
            "description": "Demonstrates exceptional teamwork and supports colleagues' success",
            "rating": {"type": "numeric", "min": 1, "max": 5},
            "evidence_required": True,
            "evidence_prompt": "Describe how the nominee contributes to team success and supports colleagues"
        },
        {
            "id": "innovation",
            "name": "Innovation & Continuous Improvement",
            "weight": 20,
            "description": "Introduces innovative solutions and drives positive organizational change",
            "rating": {"type": "numeric", "min": 1, "max": 5},
            "evidence_required": True,
            "evidence_prompt": "Detail specific innovations, process improvements, or initiatives led by the nominee"
        },
        {
            "id": "impact",
            "name": "Business Impact & Results",
            "weight": 15,
            "description": "Delivers measurable positive impact on organizational objectives",
            "rating": {"type": "numeric", "min": 1, "max": 5},
            "evidence_required": True,
            "impact_categories": ["Revenue Enhancement", "Cost Optimization", "Operational Efficiency", "Customer Satisfaction", "Employee Engagement", "Risk Mitigation"]
        }
    ],
    "nominee_info": {
        "fields": [
            {"id": "nominee_name", "label": "Nominee Full Name", "type": "employee_picker", "required": True},
            {"id": "employee_number", "label": "Employee ID", "type": "text", "auto_populated": True},
            {"id": "job_title", "label": "Current Position", "type": "text", "auto_populated": True},
            {"id": "department", "label": "Department", "type": "text", "auto_populated": True},
            {"id": "tenure", "label": "Years of Service", "type": "number", "auto_populated": True},
            {"id": "line_manager", "label": "Direct Manager", "type": "text", "auto_populated": True}
        ]
    },
    "nominator_info": {
        "fields": [
            {"id": "nominator_name", "label": "Nominator Name", "type": "text", "auto_populated": True},
            {"id": "nominator_position", "label": "Nominator Position", "type": "text", "auto_populated": True},
            {"id": "nominator_department", "label": "Nominator Department", "type": "text", "auto_populated": True},
            {"id": "relationship", "label": "Professional Relationship to Nominee", "type": "select", "options": ["Direct Manager", "Senior Manager", "Peer Colleague", "Direct Report", "Cross-Functional Partner", "Executive Leadership"]},
            {"id": "nomination_date", "label": "Date of Nomination", "type": "date", "auto_populated": True}
        ]
    },
    "sections": [
        {
            "id": "achievements",
            "name": "Significant Achievements",
            "type": "achievement_cards",
            "description": "Document the nominee's most significant accomplishments during the evaluation period",
            "min_items": 1,
            "max_items": 5,
            "item_schema": {
                "title": {"type": "text", "label": "Achievement Title", "max_length": 100},
                "description": {"type": "textarea", "label": "Description of Achievement", "max_length": 500},
                "impact": {"type": "textarea", "label": "Business Impact & Results", "max_length": 300},
                "date": {"type": "month", "label": "Date of Achievement"}
            }
        },
        {
            "id": "nomination_statement",
            "name": "Nomination Rationale",
            "type": "rich_text",
            "description": "Provide a comprehensive statement explaining why this individual merits the Employee of the Year Award",
            "min_length": 100,
            "max_length": 1500,
            "guidance": [
                "Describe the unique qualities that distinguish this nominee from peers",
                "Explain how the nominee has positively influenced colleagues and the organization",
                "Articulate the lasting impact and value this individual brings to the company"
            ]
        },
        {
            "id": "endorsements",
            "name": "Professional Endorsements",
            "type": "endorsement_request",
            "optional": True,
            "description": "Request supporting statements from colleagues who can attest to the nominee's contributions",
            "item_schema": {
                "endorser": {"type": "employee_picker", "label": "Endorser"},
                "relationship": {"type": "text", "label": "Professional Relationship"},
                "statement": {"type": "textarea", "label": "Endorsement Statement", "max_length": 500},
                "status": {"type": "select", "label": "Status", "options": ["Pending Response", "Submitted", "Declined"]}
            }
        },
        {
            "id": "supporting_documentation",
            "name": "Supporting Documentation",
            "type": "media_upload",
            "optional": True,
            "description": "Attach relevant documentation supporting the nomination (e.g., project reports, customer feedback, awards)",
            "allowed_types": ["image/jpeg", "image/png", "application/pdf"],
            "max_files": 5,
            "max_file_size_mb": 10
        }
    ],
    "scoring": {
        "auto_calculate": True,
        "formula": "weighted_average",
        "display": {
            "show_score_to_nominator": False,
            "show_score_to_nominee": False,
            "show_score_to_hr": True,
            "show_score_to_committee": True
        }
    },
    "workflow": {
        "steps": [
            {"id": "draft", "name": "Draft Nomination", "actor": "nominator"},
            {"id": "submitted", "name": "Nomination Submitted", "actor": "nominator", "notification": True},
            {"id": "hr_screening", "name": "HR Eligibility Review", "actor": "hr", "deadline_days": 5},
            {"id": "committee_evaluation", "name": "Selection Committee Evaluation", "actor": "committee"},
            {"id": "final_selection", "name": "Final Selection", "actor": "committee"},
            {"id": "announcement", "name": "Award Announcement", "actor": "hr"}
        ],
        "notifications": {
            "on_submission": {"to": ["hr", "nominator"], "template": "nomination_confirmation"},
            "on_endorsement": {"to": ["nominator"], "template": "endorsement_received"},
            "on_shortlist": {"to": ["nominator"], "template": "nominee_shortlisted"},
            "on_winner": {"to": ["nominee", "nominator", "hr"], "template": "winner_announcement"}
        }
    },
    "nominator_declaration": {
        "text": "I hereby confirm that the information provided in this nomination is accurate to the best of my knowledge. I have a professional relationship with the nominee and believe they meet the eligibility criteria for this award.",
        "required": True,
        "signature_required": True
    },
    "hr_admin": {
        "section_title": "For HR Administration Use Only",
        "fields": [
            {"id": "received_date", "label": "Date Received", "type": "datetime", "auto": True},
            {"id": "reviewed_by", "label": "Reviewed By", "type": "employee_picker"},
            {"id": "eligibility_verified", "label": "Eligibility Verified", "type": "checkbox"},
            {"id": "verification_notes", "label": "Verification Notes", "type": "textarea"},
            {"id": "status", "label": "Nomination Status", "type": "select", "options": ["Pending Review", "Under Evaluation", "Shortlisted", "Selected as Winner", "Not Selected"]},
            {"id": "committee_score", "label": "Committee Score", "type": "number"},
            {"id": "internal_notes", "label": "Internal Notes", "type": "textarea", "confidential": True}
        ]
    }
}, indent=2)


async def seed_templates():
    """Seed the HR templates into the database."""
    async with AsyncSessionLocal() as session:
        # Check if any of the templates already exist
        template_names = [
            "Performance Evaluation 2025 - Non-Managerial Positions",
            "Performance Evaluation 2025 - Managerial Positions",
            "Employee of the Year Nomination 2025"
        ]
        result = await session.execute(
            select(Template).where(Template.name.in_(template_names))
        )
        existing = result.scalars().all()
        if existing:
            existing_names = [t.name for t in existing]
            print(f"Templates already exist: {existing_names}. Skipping seed.")
            return

        templates = [
            Template(
                name="Performance Evaluation 2025 - Non-Managerial Positions",
                type="document",
                content=PERFORMANCE_EVAL_NON_MANAGERIAL,
                version=1,
                created_by="system",
                is_active=True,
                revision_note="Initial version for 2025 performance evaluation cycle"
            ),
            Template(
                name="Performance Evaluation 2025 - Managerial Positions",
                type="document",
                content=PERFORMANCE_EVAL_MANAGERIAL,
                version=1,
                created_by="system",
                is_active=True,
                revision_note="Initial version for 2025 performance evaluation cycle - includes leadership competencies"
            ),
            Template(
                name="Employee of the Year Nomination 2025",
                type="document",
                content=EMPLOYEE_OF_YEAR_NOMINATION,
                version=1,
                created_by="system",
                is_active=True,
                revision_note="Initial version for 2025 Employee of the Year recognition program"
            ),
        ]

        for template in templates:
            session.add(template)
            print(f"✓ Created template: {template.name}")

        await session.commit()
        print("\n✅ Successfully seeded all HR templates!")


if __name__ == "__main__":
    asyncio.run(seed_templates())
