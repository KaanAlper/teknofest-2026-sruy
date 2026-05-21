"""Tek bir rclpy düğümü, ayrı thread'de spin.

CargoBot asyncio event loop'u Qt veya ana asyncio'da; rclpy executor başka bir
thread'de döner. İki dünya arasında veri akışı `asyncio.run_coroutine_threadsafe`
ile event bus'a publish çağrılır.

rclpy yüklü değilse modül `available()=False` döner. Mock adapter'lar test
için bu durumda da çalışır.
"""

from __future__ import annotations

import asyncio
import logging
import threading
from typing import Callable, Optional

log = logging.getLogger(__name__)

try:
    import rclpy
    from rclpy.executors import MultiThreadedExecutor
    from rclpy.node import Node

    _AVAILABLE = True
except ImportError:
    rclpy = None  # type: ignore
    MultiThreadedExecutor = None  # type: ignore
    Node = object  # type: ignore
    _AVAILABLE = False


def available() -> bool:
    """ROS2 ortamı kurulu mu — Jetson + ROS2 Humble = True, dev makinesi = False."""
    return _AVAILABLE


class Ros2Runtime:
    """rclpy başlat/durdur ve spin thread'ini yönet."""

    def __init__(self) -> None:
        if not _AVAILABLE:
            raise RuntimeError("rclpy yok — Jetson'da ROS2 Humble kurulumu lazım")
        self._executor: Optional[MultiThreadedExecutor] = None
        self._thread: Optional[threading.Thread] = None
        self._nodes: list[Node] = []
        self._asyncio_loop: Optional[asyncio.AbstractEventLoop] = None

    def start(self, asyncio_loop: asyncio.AbstractEventLoop) -> None:
        self._asyncio_loop = asyncio_loop
        rclpy.init()
        self._executor = MultiThreadedExecutor()
        self._thread = threading.Thread(target=self._spin, name="ros2-spin", daemon=True)
        self._thread.start()
        log.info("ROS2 runtime başladı")

    def stop(self) -> None:
        if self._executor:
            self._executor.shutdown()
        for n in self._nodes:
            n.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        if self._thread:
            self._thread.join(timeout=2.0)
        log.info("ROS2 runtime durdu")

    def add_node(self, node: Node) -> None:
        self._nodes.append(node)
        if self._executor is not None:
            self._executor.add_node(node)

    def post_to_asyncio(self, coro) -> None:
        """rclpy callback'inden asyncio event bus'a güvenli geçiş."""
        if self._asyncio_loop is None:
            log.warning("asyncio loop yok, ROS callback yutuluyor")
            return
        asyncio.run_coroutine_threadsafe(coro, self._asyncio_loop)

    def _spin(self) -> None:
        assert self._executor is not None
        try:
            self._executor.spin()
        except Exception:
            log.exception("ROS2 executor patladı")


# Ortak tek instance — adapter'lar paylaşır
_runtime: Optional[Ros2Runtime] = None


def get_runtime() -> Optional[Ros2Runtime]:
    return _runtime


def init_runtime(asyncio_loop: asyncio.AbstractEventLoop) -> Optional[Ros2Runtime]:
    """ROS2 varsa runtime'ı başlat ve döndür; yoksa None."""
    global _runtime
    if not _AVAILABLE:
        log.info("rclpy yok, ROS2 köprüsü atlanıyor (mock adapter'ler kullanılacak)")
        return None
    if _runtime is None:
        _runtime = Ros2Runtime()
        _runtime.start(asyncio_loop)
    return _runtime


def shutdown_runtime() -> None:
    global _runtime
    if _runtime is not None:
        _runtime.stop()
        _runtime = None
