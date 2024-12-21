"""Event handling utilities for GOAT SDK."""

import asyncio
from typing import Dict, List, Any, Callable, Awaitable
from ..telemetry import track_error

EventHandler = Callable[[Dict[str, Any]], Awaitable[None]]

class EventEmitter:
    """Event emitter implementation for handling blockchain events."""
    
    def __init__(self):
        """Initialize event emitter."""
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._running = False
        self._queue: asyncio.Queue = asyncio.Queue()
    
    def on(self, event: str, handler: EventHandler) -> None:
        """Register an event handler.
        
        Args:
            event: Event name
            handler: Event handler function
        """
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)
    
    def off(self, event: str, handler: EventHandler) -> None:
        """Remove an event handler.
        
        Args:
            event: Event name
            handler: Event handler function to remove
        """
        if event in self._handlers:
            self._handlers[event].remove(handler)
            if not self._handlers[event]:
                del self._handlers[event]
    
    async def emit(self, event: str, data: Dict[str, Any]) -> None:
        """Emit an event.
        
        Args:
            event: Event name
            data: Event data
        """
        await self._queue.put((event, data))
    
    async def start(self) -> None:
        """Start processing events."""
        self._running = True
        while self._running:
            try:
                event, data = await self._queue.get()
                if event in self._handlers:
                    for handler in self._handlers[event]:
                        try:
                            await handler(data)
                        except Exception as e:
                            track_error(type(e).__name__, str(e))
                self._queue.task_done()
            except Exception as e:
                track_error(type(e).__name__, str(e))
    
    def stop(self) -> None:
        """Stop processing events."""
        self._running = False
