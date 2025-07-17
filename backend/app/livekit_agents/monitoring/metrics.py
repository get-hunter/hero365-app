"""
Monitoring and metrics system for Hero365 LiveKit agents.
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class EventType(Enum):
    """Types of events to track"""
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    AGENT_SWITCH = "agent_switch"
    FUNCTION_CALL = "function_call"
    VOICE_ACTIVITY = "voice_activity"
    ERROR = "error"
    PERFORMANCE = "performance"


@dataclass
class MetricEvent:
    """A single metric event"""
    event_type: EventType
    timestamp: datetime
    session_id: str
    agent_name: Optional[str] = None
    function_name: Optional[str] = None
    duration: Optional[float] = None
    value: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class SessionMetrics:
    """Metrics for a single session"""
    session_id: str
    user_id: str
    business_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration: Optional[float] = None
    agent_switches: int = 0
    function_calls: int = 0
    voice_interactions: int = 0
    errors: int = 0
    current_agent: Optional[str] = None
    agents_used: List[str] = None
    
    def __post_init__(self):
        if self.agents_used is None:
            self.agents_used = []


@dataclass
class AgentMetrics:
    """Metrics for an agent"""
    agent_name: str
    total_sessions: int = 0
    total_function_calls: int = 0
    total_duration: float = 0.0
    average_session_duration: float = 0.0
    success_rate: float = 0.0
    error_count: int = 0
    last_active: Optional[datetime] = None


@dataclass
class SystemMetrics:
    """System-wide metrics"""
    active_sessions: int = 0
    total_sessions: int = 0
    average_session_duration: float = 0.0
    total_function_calls: int = 0
    total_errors: int = 0
    uptime: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0


class LiveKitMetrics:
    """LiveKit agents metrics collector and analyzer"""
    
    def __init__(self, retention_days: int = 7, max_events_per_session: int = 1000):
        """
        Initialize the metrics system.
        
        Args:
            retention_days: Number of days to retain metrics
            max_events_per_session: Maximum events to store per session
        """
        self.retention_days = retention_days
        self.max_events_per_session = max_events_per_session
        self.start_time = datetime.now()
        
        # Storage
        self._events: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_events_per_session))
        self._session_metrics: Dict[str, SessionMetrics] = {}
        self._agent_metrics: Dict[str, AgentMetrics] = {}
        self._system_metrics = SystemMetrics()
        
        # Counters
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = defaultdict(float)
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._timers: Dict[str, List[float]] = defaultdict(list)
        
        # Locks
        self._lock = asyncio.Lock()
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start the cleanup background task"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self):
        """Background task to clean up old metrics"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self._cleanup_old_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def _cleanup_old_metrics(self):
        """Clean up old metrics data"""
        async with self._lock:
            cutoff_time = datetime.now() - timedelta(days=self.retention_days)
            
            # Clean up session metrics
            expired_sessions = []
            for session_id, metrics in self._session_metrics.items():
                if metrics.start_time < cutoff_time:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self._session_metrics[session_id]
                if session_id in self._events:
                    del self._events[session_id]
            
            logger.info(f"Cleaned up {len(expired_sessions)} expired session metrics")
    
    async def record_event(self, event: MetricEvent):
        """Record a metric event"""
        async with self._lock:
            # Add to events
            self._events[event.session_id].append(event)
            
            # Update counters
            self._counters[f"event_{event.event_type.value}"] += 1
            
            # Update session metrics
            if event.session_id not in self._session_metrics:
                # This shouldn't happen if sessions are properly tracked
                logger.warning(f"Event for unknown session: {event.session_id}")
                return
            
            session_metrics = self._session_metrics[event.session_id]
            
            # Update based on event type
            if event.event_type == EventType.AGENT_SWITCH:
                session_metrics.agent_switches += 1
                if event.agent_name:
                    session_metrics.current_agent = event.agent_name
                    if event.agent_name not in session_metrics.agents_used:
                        session_metrics.agents_used.append(event.agent_name)
            
            elif event.event_type == EventType.FUNCTION_CALL:
                session_metrics.function_calls += 1
                self._counters[f"function_{event.function_name}"] += 1
                
                if event.duration:
                    self._timers[f"function_{event.function_name}"].append(event.duration)
            
            elif event.event_type == EventType.VOICE_ACTIVITY:
                session_metrics.voice_interactions += 1
                
                if event.duration:
                    self._timers["voice_interaction"].append(event.duration)
            
            elif event.event_type == EventType.ERROR:
                session_metrics.errors += 1
                self._counters[f"error_{event.agent_name}"] += 1
            
            # Update agent metrics
            if event.agent_name:
                await self._update_agent_metrics(event.agent_name, event)
    
    async def _update_agent_metrics(self, agent_name: str, event: MetricEvent):
        """Update agent-specific metrics"""
        if agent_name not in self._agent_metrics:
            self._agent_metrics[agent_name] = AgentMetrics(agent_name=agent_name)
        
        agent_metrics = self._agent_metrics[agent_name]
        agent_metrics.last_active = event.timestamp
        
        if event.event_type == EventType.FUNCTION_CALL:
            agent_metrics.total_function_calls += 1
            if event.duration:
                agent_metrics.total_duration += event.duration
        
        elif event.event_type == EventType.ERROR:
            agent_metrics.error_count += 1
    
    async def start_session(self, session_id: str, user_id: str, business_id: str):
        """Start tracking a new session"""
        async with self._lock:
            session_metrics = SessionMetrics(
                session_id=session_id,
                user_id=user_id,
                business_id=business_id,
                start_time=datetime.now()
            )
            
            self._session_metrics[session_id] = session_metrics
            self._system_metrics.active_sessions += 1
            self._system_metrics.total_sessions += 1
            
            logger.info(f"Started tracking session {session_id}")
        
        # Record event outside of the lock to avoid deadlock
        await self.record_event(MetricEvent(
            event_type=EventType.SESSION_START,
            timestamp=datetime.now(),
            session_id=session_id
        ))
    
    async def end_session(self, session_id: str):
        """End tracking a session"""
        duration = None
        
        async with self._lock:
            if session_id not in self._session_metrics:
                logger.warning(f"Ending unknown session: {session_id}")
                return
            
            session_metrics = self._session_metrics[session_id]
            session_metrics.end_time = datetime.now()
            session_metrics.total_duration = (
                session_metrics.end_time - session_metrics.start_time
            ).total_seconds()
            
            duration = session_metrics.total_duration
            self._system_metrics.active_sessions = max(0, self._system_metrics.active_sessions - 1)
            
            logger.info(f"Ended tracking session {session_id}")
        
        # Record event outside of the lock to avoid deadlock
        await self.record_event(MetricEvent(
            event_type=EventType.SESSION_END,
            timestamp=datetime.now(),
            session_id=session_id,
            duration=duration
        ))
    
    async def record_function_call(self, session_id: str, agent_name: str, 
                                 function_name: str, duration: float, 
                                 success: bool = True, error: Optional[str] = None):
        """Record a function call"""
        event_type = EventType.FUNCTION_CALL if success else EventType.ERROR
        
        await self.record_event(MetricEvent(
            event_type=event_type,
            timestamp=datetime.now(),
            session_id=session_id,
            agent_name=agent_name,
            function_name=function_name,
            duration=duration,
            error=error
        ))
    
    async def record_voice_activity(self, session_id: str, duration: float, 
                                   confidence: Optional[float] = None):
        """Record voice activity"""
        await self.record_event(MetricEvent(
            event_type=EventType.VOICE_ACTIVITY,
            timestamp=datetime.now(),
            session_id=session_id,
            duration=duration,
            value=confidence
        ))
    
    async def record_agent_switch(self, session_id: str, from_agent: str, to_agent: str):
        """Record an agent switch"""
        await self.record_event(MetricEvent(
            event_type=EventType.AGENT_SWITCH,
            timestamp=datetime.now(),
            session_id=session_id,
            agent_name=to_agent,
            metadata={"from_agent": from_agent, "to_agent": to_agent}
        ))
    
    async def record_error(self, session_id: str, agent_name: str, error: str, 
                          function_name: Optional[str] = None):
        """Record an error"""
        await self.record_event(MetricEvent(
            event_type=EventType.ERROR,
            timestamp=datetime.now(),
            session_id=session_id,
            agent_name=agent_name,
            function_name=function_name,
            error=error
        ))
    
    async def get_session_metrics(self, session_id: str) -> Optional[SessionMetrics]:
        """Get metrics for a specific session"""
        async with self._lock:
            return self._session_metrics.get(session_id)
    
    async def get_agent_metrics(self, agent_name: str) -> Optional[AgentMetrics]:
        """Get metrics for a specific agent"""
        async with self._lock:
            agent_metrics = self._agent_metrics.get(agent_name)
            if agent_metrics:
                # Calculate derived metrics
                if agent_metrics.total_sessions > 0:
                    agent_metrics.average_session_duration = (
                        agent_metrics.total_duration / agent_metrics.total_sessions
                    )
                
                total_calls = agent_metrics.total_function_calls
                if total_calls > 0:
                    agent_metrics.success_rate = (
                        (total_calls - agent_metrics.error_count) / total_calls
                    )
            
            return agent_metrics
    
    async def get_system_metrics(self) -> SystemMetrics:
        """Get system-wide metrics"""
        async with self._lock:
            # Update derived metrics
            self._system_metrics.uptime = (datetime.now() - self.start_time).total_seconds()
            
            # Calculate average session duration
            if self._system_metrics.total_sessions > 0:
                total_duration = sum(
                    (metrics.total_duration or 0) 
                    for metrics in self._session_metrics.values()
                )
                self._system_metrics.average_session_duration = (
                    total_duration / self._system_metrics.total_sessions
                )
            
            # Update counters
            self._system_metrics.total_function_calls = sum(
                count for key, count in self._counters.items() 
                if key.startswith("function_")
            )
            
            self._system_metrics.total_errors = sum(
                count for key, count in self._counters.items() 
                if key.startswith("error_")
            )
            
            return self._system_metrics
    
    async def get_function_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for function calls"""
        async with self._lock:
            stats = {}
            
            for key, times in self._timers.items():
                if key.startswith("function_"):
                    function_name = key[9:]  # Remove "function_" prefix
                    if times:
                        stats[function_name] = {
                            "call_count": self._counters.get(key, 0),
                            "total_time": sum(times),
                            "average_time": sum(times) / len(times),
                            "min_time": min(times),
                            "max_time": max(times)
                        }
            
            return stats
    
    async def get_popular_functions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular functions"""
        async with self._lock:
            function_counts = [
                {"function": key[9:], "count": count}
                for key, count in self._counters.items()
                if key.startswith("function_")
            ]
            
            return sorted(function_counts, key=lambda x: x["count"], reverse=True)[:limit]
    
    async def get_session_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get session summary for the last N hours"""
        async with self._lock:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            recent_sessions = [
                metrics for metrics in self._session_metrics.values()
                if metrics.start_time >= cutoff_time
            ]
            
            if not recent_sessions:
                return {
                    "total_sessions": 0,
                    "average_duration": 0,
                    "total_function_calls": 0,
                    "total_errors": 0,
                    "agent_usage": {}
                }
            
            # Calculate summary
            total_duration = sum(
                (session.total_duration or 0) for session in recent_sessions
            )
            
            total_function_calls = sum(
                session.function_calls for session in recent_sessions
            )
            
            total_errors = sum(
                session.errors for session in recent_sessions
            )
            
            # Agent usage
            agent_usage = defaultdict(int)
            for session in recent_sessions:
                for agent in session.agents_used:
                    agent_usage[agent] += 1
            
            return {
                "total_sessions": len(recent_sessions),
                "average_duration": total_duration / len(recent_sessions) if recent_sessions else 0,
                "total_function_calls": total_function_calls,
                "total_errors": total_errors,
                "agent_usage": dict(agent_usage)
            }
    
    async def export_metrics(self, format: str = "json") -> str:
        """Export metrics data"""
        async with self._lock:
            data = {
                "system_metrics": asdict(await self.get_system_metrics()),
                "session_metrics": {
                    session_id: asdict(metrics) 
                    for session_id, metrics in self._session_metrics.items()
                },
                "agent_metrics": {
                    agent_name: asdict(await self.get_agent_metrics(agent_name))
                    for agent_name in self._agent_metrics.keys()
                },
                "function_statistics": await self.get_function_statistics(),
                "counters": dict(self._counters),
                "export_time": datetime.now().isoformat()
            }
            
            if format == "json":
                return json.dumps(data, indent=2, default=str)
            else:
                raise ValueError(f"Unsupported format: {format}")
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        async with self._lock:
            # Basic health checks
            error_rate = 0
            if self._system_metrics.total_function_calls > 0:
                error_rate = (
                    self._system_metrics.total_errors / 
                    self._system_metrics.total_function_calls
                )
            
            # Determine health status
            if error_rate > 0.1:  # More than 10% errors
                status = "unhealthy"
            elif error_rate > 0.05:  # More than 5% errors
                status = "degraded"
            else:
                status = "healthy"
            
            return {
                "status": status,
                "active_sessions": self._system_metrics.active_sessions,
                "error_rate": error_rate,
                "uptime": self._system_metrics.uptime,
                "total_sessions": self._system_metrics.total_sessions,
                "last_updated": datetime.now().isoformat()
            }
    
    def __del__(self):
        """Clean up resources"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()


# Global metrics instance - lazy initialization
metrics = None


async def get_metrics() -> LiveKitMetrics:
    """Get the global metrics instance"""
    global metrics
    if metrics is None:
        metrics = LiveKitMetrics()
    return metrics


def performance_timer(func: Callable) -> Callable:
    """Decorator to time function execution"""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Record performance metric
            func_name = func.__name__
            try:
                metrics_instance = await get_metrics()
                await metrics_instance.record_event(MetricEvent(
                    event_type=EventType.PERFORMANCE,
                    timestamp=datetime.now(),
                    session_id=kwargs.get('session_id', 'unknown'),
                    function_name=func_name,
                    duration=duration
                ))
            except Exception as e:
                logger.warning(f"Failed to record performance metric: {e}")
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            try:
                metrics_instance = await get_metrics()
                await metrics_instance.record_error(
                    session_id=kwargs.get('session_id', 'unknown'),
                    agent_name=kwargs.get('agent_name', 'unknown'),
                    error=str(e),
                    function_name=func.__name__
                )
            except Exception as metric_error:
                logger.warning(f"Failed to record error metric: {metric_error}")
            raise
    
    return wrapper 