"""
Voice agent performance monitoring and metrics collection.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from collections import defaultdict, deque
from contextlib import asynccontextmanager
import asyncio

from ...core.config import settings

logger = logging.getLogger(__name__)


class VoiceMetricsCollector:
    """Collects and manages voice agent performance metrics."""
    
    def __init__(self, max_history_size: int = 1000):
        self.max_history_size = max_history_size
        self.metrics = defaultdict(lambda: defaultdict(list))
        self.session_metrics = {}
        self.agent_metrics = defaultdict(lambda: defaultdict(int))
        self.error_metrics = defaultdict(list)
        self.response_times = defaultdict(deque)
        self.active_sessions = set()
        self.start_time = datetime.now()
        
    def record_session_start(self, session_id: str, agent_type: str = "triage") -> None:
        """Record the start of a voice session."""
        self.active_sessions.add(session_id)
        self.session_metrics[session_id] = {
            "start_time": datetime.now(),
            "agent_type": agent_type,
            "interactions": 0,
            "tools_used": [],
            "handoffs": 0,
            "errors": 0
        }
        self.agent_metrics[agent_type]["sessions_started"] += 1
        logger.info(f"Session started: {session_id} with agent {agent_type}")
    
    def record_session_end(self, session_id: str, reason: str = "completed") -> None:
        """Record the end of a voice session."""
        if session_id in self.active_sessions:
            self.active_sessions.remove(session_id)
            
        if session_id in self.session_metrics:
            session_data = self.session_metrics[session_id]
            session_data["end_time"] = datetime.now()
            session_data["duration"] = (session_data["end_time"] - session_data["start_time"]).total_seconds()
            session_data["end_reason"] = reason
            
            # Update agent metrics
            agent_type = session_data["agent_type"]
            self.agent_metrics[agent_type]["sessions_completed"] += 1
            self.agent_metrics[agent_type]["total_duration"] += session_data["duration"]
            
            logger.info(f"Session ended: {session_id} after {session_data['duration']:.2f}s")
    
    def record_interaction(self, session_id: str, interaction_type: str, response_time: float) -> None:
        """Record a user interaction within a session."""
        if session_id in self.session_metrics:
            self.session_metrics[session_id]["interactions"] += 1
            
            # Track response times
            self.response_times[interaction_type].append(response_time)
            if len(self.response_times[interaction_type]) > self.max_history_size:
                self.response_times[interaction_type].popleft()
            
            # Update agent metrics
            agent_type = self.session_metrics[session_id]["agent_type"]
            self.agent_metrics[agent_type]["total_interactions"] += 1
            self.agent_metrics[agent_type]["total_response_time"] += response_time
    
    def record_tool_usage(self, session_id: str, tool_name: str, execution_time: float, success: bool = True) -> None:
        """Record usage of a voice tool."""
        if session_id in self.session_metrics:
            self.session_metrics[session_id]["tools_used"].append({
                "tool": tool_name,
                "timestamp": datetime.now(),
                "execution_time": execution_time,
                "success": success
            })
            
            # Update tool metrics
            self.agent_metrics["tools"][f"{tool_name}_used"] += 1
            self.agent_metrics["tools"][f"{tool_name}_total_time"] += execution_time
            
            if not success:
                self.agent_metrics["tools"][f"{tool_name}_errors"] += 1
    
    def record_handoff(self, session_id: str, from_agent: str, to_agent: str, reason: str = "") -> None:
        """Record an agent handoff."""
        if session_id in self.session_metrics:
            self.session_metrics[session_id]["handoffs"] += 1
            
            # Update handoff metrics
            self.agent_metrics["handoffs"][f"{from_agent}_to_{to_agent}"] += 1
            
            logger.info(f"Agent handoff: {from_agent} -> {to_agent} (session: {session_id})")
    
    def record_error(self, session_id: str, error_type: str, error_message: str, agent_type: str = "unknown") -> None:
        """Record an error occurrence."""
        error_data = {
            "timestamp": datetime.now(),
            "session_id": session_id,
            "error_type": error_type,
            "error_message": error_message,
            "agent_type": agent_type
        }
        
        self.error_metrics[error_type].append(error_data)
        
        # Limit error history
        if len(self.error_metrics[error_type]) > self.max_history_size:
            self.error_metrics[error_type].pop(0)
        
        if session_id in self.session_metrics:
            self.session_metrics[session_id]["errors"] += 1
        
        self.agent_metrics[agent_type]["errors"] += 1
        logger.error(f"Error recorded: {error_type} in session {session_id}")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        now = datetime.now()
        uptime = (now - self.start_time).total_seconds()
        
        # Calculate average response times
        avg_response_times = {}
        for interaction_type, times in self.response_times.items():
            if times:
                avg_response_times[interaction_type] = sum(times) / len(times)
        
        # Calculate agent performance
        agent_performance = {}
        for agent_type, metrics in self.agent_metrics.items():
            if agent_type == "tools" or agent_type == "handoffs":
                continue
                
            performance = {
                "sessions_started": metrics.get("sessions_started", 0),
                "sessions_completed": metrics.get("sessions_completed", 0),
                "total_interactions": metrics.get("total_interactions", 0),
                "total_errors": metrics.get("errors", 0),
                "avg_session_duration": 0,
                "avg_response_time": 0
            }
            
            if metrics.get("sessions_completed", 0) > 0:
                performance["avg_session_duration"] = metrics.get("total_duration", 0) / metrics["sessions_completed"]
            
            if metrics.get("total_interactions", 0) > 0:
                performance["avg_response_time"] = metrics.get("total_response_time", 0) / metrics["total_interactions"]
            
            agent_performance[agent_type] = performance
        
        return {
            "system": {
                "uptime_seconds": uptime,
                "active_sessions": len(self.active_sessions),
                "total_sessions": len(self.session_metrics),
                "last_updated": now.isoformat()
            },
            "performance": {
                "avg_response_times": avg_response_times,
                "agent_performance": agent_performance
            },
            "tools": dict(self.agent_metrics.get("tools", {})),
            "handoffs": dict(self.agent_metrics.get("handoffs", {})),
            "errors": {
                "total_errors": sum(len(errors) for errors in self.error_metrics.values()),
                "error_types": list(self.error_metrics.keys())
            }
        }
    
    def get_session_metrics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific session."""
        return self.session_metrics.get(session_id)
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent errors across all types."""
        all_errors = []
        for error_type, errors in self.error_metrics.items():
            all_errors.extend(errors)
        
        # Sort by timestamp and return most recent
        all_errors.sort(key=lambda x: x["timestamp"], reverse=True)
        return all_errors[:limit]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status of the voice agent system."""
        now = datetime.now()
        recent_errors = self.get_recent_errors(50)
        
        # Check for recent errors (last 5 minutes)
        recent_error_count = len([
            error for error in recent_errors 
            if (now - error["timestamp"]).total_seconds() < 300
        ])
        
        # Calculate error rate
        total_interactions = sum(
            metrics.get("total_interactions", 0) 
            for agent_type, metrics in self.agent_metrics.items()
            if agent_type not in ["tools", "handoffs"]
        )
        
        error_rate = 0
        if total_interactions > 0:
            total_errors = sum(len(errors) for errors in self.error_metrics.values())
            error_rate = (total_errors / total_interactions) * 100
        
        # Calculate average response time
        all_response_times = []
        for times in self.response_times.values():
            all_response_times.extend(times)
        
        avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0
        
        # Determine health status
        health_status = "healthy"
        if recent_error_count > 10:
            health_status = "unhealthy"
        elif recent_error_count > 5 or error_rate > 10:
            health_status = "degraded"
        elif avg_response_time > 5.0:  # 5 seconds
            health_status = "slow"
        
        return {
            "status": health_status,
            "active_sessions": len(self.active_sessions),
            "recent_errors": recent_error_count,
            "error_rate_percent": error_rate,
            "avg_response_time_seconds": avg_response_time,
            "uptime_seconds": (now - self.start_time).total_seconds(),
            "timestamp": now.isoformat()
        }
    
    def reset_metrics(self) -> None:
        """Reset all metrics (useful for testing)."""
        self.metrics.clear()
        self.session_metrics.clear()
        self.agent_metrics.clear()
        self.error_metrics.clear()
        self.response_times.clear()
        self.active_sessions.clear()
        self.start_time = datetime.now()
        logger.info("Voice metrics reset")


class VoicePerformanceMonitor:
    """Context manager for monitoring voice agent performance."""
    
    def __init__(self, metrics_collector: VoiceMetricsCollector, session_id: str, 
                 operation_name: str, agent_type: str = "unknown"):
        self.metrics_collector = metrics_collector
        self.session_id = session_id
        self.operation_name = operation_name
        self.agent_type = agent_type
        self.start_time = None
        self.success = True
        self.error_type = None
        self.error_message = None
    
    async def __aenter__(self):
        self.start_time = time.time()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            execution_time = time.time() - self.start_time
            
            if exc_type is not None:
                self.success = False
                self.error_type = exc_type.__name__
                self.error_message = str(exc_val)
                
                # Record error
                self.metrics_collector.record_error(
                    self.session_id, 
                    self.error_type, 
                    self.error_message, 
                    self.agent_type
                )
            
            # Record the interaction/tool usage
            if self.operation_name.startswith("tool_"):
                tool_name = self.operation_name[5:]  # Remove "tool_" prefix
                self.metrics_collector.record_tool_usage(
                    self.session_id, 
                    tool_name, 
                    execution_time, 
                    self.success
                )
            else:
                self.metrics_collector.record_interaction(
                    self.session_id, 
                    self.operation_name, 
                    execution_time
                )
        
        return False  # Don't suppress exceptions


# Global metrics collector instance
voice_metrics = VoiceMetricsCollector()


@asynccontextmanager
async def monitor_voice_operation(session_id: str, operation_name: str, agent_type: str = "unknown"):
    """Context manager for monitoring voice operations."""
    async with VoicePerformanceMonitor(voice_metrics, session_id, operation_name, agent_type):
        yield 