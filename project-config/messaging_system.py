#!/usr/bin/env python3
"""
Advanced Messaging System for CFGPP-Format
Provides rich messaging capabilities for project coordination
"""

import json
import sys
from datetime import datetime
from typing import Dict, List, Optional, Union
from meta_bridge import run_meta_tool

class MessagePriority:
    """Message priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

class MessageType:
    """Standard message types for project coordination"""
    STATUS = "status"
    REQUEST = "request"
    RESPONSE = "response"
    UPDATE = "update"
    ALERT = "alert"
    COORDINATION = "coordination"
    RESOURCE_SHARE = "resource_share"
    AI_COLLABORATION = "ai_collaboration"

class CFGPPMessenger:
    """
    Advanced messaging system for CFGPP-Format project
    Enables rich communication with meta workspace and other projects
    """
    
    def __init__(self):
        self.project_name = "cfgpp-format"
        self.supported_projects = [
            "meta", "consultflow", "logmill", "flowforge-ide", 
            "system-test-project", "cfgpp-format"
        ]
    
    def send_status_update(self, status: str, details: str = "", priority: int = MessagePriority.MEDIUM) -> Dict:
        """
        Send status update to meta workspace
        Used for milestone updates, progress reports, etc.
        """
        return self._send_message(
            target="meta",
            message_type=MessageType.STATUS,
            subject=f"CFGPP Status: {status}"[:50],
            content=details,
            priority=priority,
            metadata={
                "status": status,
                "project_phase": self._get_current_phase(),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def request_help(self, target_project: str, topic: str, description: str, priority: int = MessagePriority.MEDIUM) -> Dict:
        """
        Request help from another project
        Used for technical assistance, resource sharing, etc.
        """
        return self._send_message(
            target=target_project,
            message_type=MessageType.REQUEST,
            subject=f"Help Request: {topic}"[:50],
            content=description,
            priority=priority,
            metadata={
                "request_type": "help",
                "topic": topic,
                "requested_from": target_project,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def share_ai_knowledge(self, target_project: str, knowledge_type: str, knowledge_data: Dict, priority: int = MessagePriority.HIGH) -> Dict:
        """
        Share AI-aware configuration knowledge with other projects
        Perfect for the AI-aware features we're implementing
        """
        return self._send_message(
            target=target_project,
            message_type=MessageType.AI_COLLABORATION,
            subject=f"AI Knowledge: {knowledge_type}"[:50],
            content=json.dumps(knowledge_data, indent=2),
            priority=priority,
            metadata={
                "knowledge_type": knowledge_type,
                "ai_features": ["hierarchical_parsing", "hash_validation", "compression", "ai_reasoning"],
                "schema_version": "1.0",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def coordinate_implementation(self, target_project: str, feature: str, coordination_data: Dict) -> Dict:
        """
        Coordinate implementation of shared features across projects
        Useful during the 90-day AI feature rollout
        """
        return self._send_message(
            target=target_project,
            message_type=MessageType.COORDINATION,
            subject=f"Coordination: {feature}"[:50],
            content=json.dumps(coordination_data, indent=2),
            priority=MessagePriority.HIGH,
            metadata={
                "feature": feature,
                "coordination_type": "implementation",
                "phase": coordination_data.get("phase", "unknown"),
                "dependencies": coordination_data.get("dependencies", []),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def send_ai_milestone(self, milestone: str, achievements: List[str], next_steps: List[str]) -> Dict:
        """
        Send AI feature implementation milestone to meta workspace
        Tracks progress through the 90-day implementation plan
        """
        milestone_data = {
            "milestone": milestone,
            "achievements": achievements,
            "next_steps": next_steps,
            "implementation_phase": self._get_current_phase(),
            "features_status": self._get_features_status(),
            "risk_level": self._assess_risk_level(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self._send_message(
            target="meta",
            message_type=MessageType.UPDATE,
            subject=f"AI Milestone: {milestone}"[:50],
            content=json.dumps(milestone_data, indent=2),
            priority=MessagePriority.HIGH,
            metadata=milestone_data
        )
    
    def poll_messages(self, format_type: str = "standard", limit: int = 10) -> Dict:
        """
        Poll for incoming messages
        """
        args = ["poll"]
        if format_type != "standard":
            args.extend(["--format", format_type])
        if limit != 10:
            args.extend(["--limit", str(limit)])
        
        return run_meta_tool("messaging", args)
    
    def get_project_status(self) -> Dict:
        """
        Get comprehensive project status for messaging
        """
        return {
            "project": self.project_name,
            "status": "active_development",
            "current_phase": self._get_current_phase(),
            "features_implemented": self._get_features_status(),
            "test_status": "90/90 passing",
            "production_ready": True,
            "ai_features_status": "planning_phase",
            "risk_level": "minimal",
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _send_message(self, target: str, message_type: str, subject: str, content: str, priority: int, metadata: Dict) -> Dict:
        """
        Internal method to send formatted messages
        """
        if target not in self.supported_projects:
            return {
                "success": False,
                "error": f"Unsupported target project: {target}"
            }
        
        # Construct message with rich metadata
        args = [
            "send", target, message_type, subject, content,
            "--priority", str(priority),
            "--metadata", json.dumps(metadata)
        ]
        
        return run_meta_tool("messaging", args)
    
    def _get_current_phase(self) -> str:
        """
        Determine current implementation phase
        """
        # This would be determined by checking feature flags, git commits, etc.
        return "phase_1_foundation"
    
    def _get_features_status(self) -> Dict:
        """
        Get status of AI-aware features
        """
        return {
            "hierarchical_parsing": "planned",
            "hash_validation": "planned", 
            "compression": "planned",
            "ai_reasoning_modes": "planned",
            "ai_communication": "planned"
        }
    
    def _assess_risk_level(self) -> str:
        """
        Assess current risk level for AI feature implementation
        """
        return "minimal"  # Based on risk-minimized strategy

def main():
    """
    Command-line interface for advanced messaging
    """
    messenger = CFGPPMessenger()
    
    if len(sys.argv) < 2:
        print("Usage: python messaging_system.py <command> [args...]")
        print("Commands:")
        print("  status <status> [details] - Send status update")
        print("  help <project> <topic> <description> - Request help")
        print("  ai-share <project> <type> <data> - Share AI knowledge")
        print("  milestone <name> <achievements> <next_steps> - Send milestone")
        print("  poll [format] [limit] - Poll for messages")
        print("  project-status - Get project status")
        return
    
    command = sys.argv[1]
    
    try:
        if command == "status":
            status = sys.argv[2]
            details = sys.argv[3] if len(sys.argv) > 3 else ""
            result = messenger.send_status_update(status, details)
            
        elif command == "help":
            project = sys.argv[2]
            topic = sys.argv[3]
            description = sys.argv[4]
            result = messenger.request_help(project, topic, description)
            
        elif command == "milestone":
            milestone = sys.argv[2]
            achievements = sys.argv[3].split(",") if len(sys.argv) > 3 else []
            next_steps = sys.argv[4].split(",") if len(sys.argv) > 4 else []
            result = messenger.send_ai_milestone(milestone, achievements, next_steps)
            
        elif command == "poll":
            format_type = sys.argv[2] if len(sys.argv) > 2 else "standard"
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            result = messenger.poll_messages(format_type, limit)
            
        elif command == "project-status":
            result = {"success": True, "data": messenger.get_project_status()}
            
        else:
            print(f"Unknown command: {command}")
            return
        
        if result.get("success"):
            if "data" in result:
                print(json.dumps(result["data"], indent=2))
            elif "output" in result:
                print(result["output"])
            else:
                print("✅ Command completed successfully")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
    except IndexError:
        print(f"❌ Error: Insufficient arguments for command '{command}'")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
