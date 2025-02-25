import numpy as np
import torch
import asyncio
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
import serial
import struct
from enum import Enum, auto
import time
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("hardware_interface")

class MotorState(Enum):
    IDLE = auto()
    MOVING = auto()
    HOLDING = auto()
    ERROR = auto()
    CALIBRATING = auto()  # Added new state for calibration

@dataclass
class JointState:
    """Physical joint state with validation and history"""
    position: float
    velocity: float
    torque: float
    current: float
    temperature: float
    state: MotorState
    timestamp: float = field(default_factory=time.time)
    
    # Add position history for derivative calculations
    position_history: List[Tuple[float, float]] = field(default_factory=list)
    
    def update_history(self, max_history: int = 10):
        """Update position history with timestamp"""
        self.position_history.append((self.timestamp, self.position))
        # Keep history limited to max_history entries
        if len(self.position_history) > max_history:
            self.position_history.pop(0)
    
    def get_position_derivative(self) -> float:
        """Calculate position derivative from history"""
        if len(self.position_history) < 2:
            return 0.0
        
        # Get last two points
        t1, p1 = self.position_history[-2]
        t2, p2 = self.position_history[-1]
        
        # Calculate derivative
        dt = t2 - t1
        if dt == 0:
            return 0.0
        
        return (p2 - p1) / dt

class CommandType(Enum):
    """Command types enum for improved type safety"""
    RESET = 0x01
    ENABLE = 0x02
    DISABLE = 0x03
    MOVE = 0x04
    CALIBRATE = 0x05  # Added calibration command
    EMERGENCY_STOP = 0x06  # Added emergency stop command

@dataclass
class SafetyConfig:
    """Centralized safety configuration"""
    max_temperature: float = 60.0  # °C
    max_current: float = 20.0  # A
    communication_timeout: float = 0.1  # seconds
    position_tolerance: float = 1.0  # degrees
    max_velocity: float = 100.0  # degrees/s
    emergency_stop_callback: Optional[Callable] = None

class HardwareInterface:
    """Quantum-enhanced hardware control system with improved safety and performance"""

    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 115200, 
                 safety_config: Optional[SafetyConfig] = None):
        # Hardware parameters with improved documentation
        self.joints = {
            'hip_l': {'id': 1, 'limits': (-45, 45), 'max_torque': 40, 'gear_ratio': 150},
            'hip_r': {'id': 2, 'limits': (-45, 45), 'max_torque': 40, 'gear_ratio': 150},
            'knee_l': {'id': 3, 'limits': (0, 120), 'max_torque': 60, 'gear_ratio': 120},
            'knee_r': {'id': 4, 'limits': (0, 120), 'max_torque': 60, 'gear_ratio': 120},
            'ankle_l': {'id': 5, 'limits': (-20, 20), 'max_torque': 30, 'gear_ratio': 100},
            'ankle_r': {'id': 6, 'limits': (-20, 20), 'max_torque': 30, 'gear_ratio': 100}
        }

        # Safety configuration
        self.safety_config = safety_config or SafetyConfig()
        
        # Communication
        self._setup_communication(port, baudrate)
        
        # Task tracking for clean shutdown
        self.tasks = []
        
        # State tracking with improved diagnostics
        self.joint_states: Dict[str, JointState] = {}
        self.last_update = time.time()
        self.safety_flags = {
            'temperature_warning': False,
            'current_warning': False,
            'position_warning': False,
            'communication_warning': False,
            'emergency_stop': False
        }
        
        # Performance metrics
        self.metrics = {
            'command_latency': [],
            'read_frequency': [],
            'last_command_time': 0,
            'command_count': 0,
            'error_count': 0
        }

        # Initialize states
        self._initialize_states()
        
        # Create command cache for optimized repeated commands
        self._command_cache = {}
        
        logger.info("Hardware interface initialized")

    def _setup_communication(self, port: str, baudrate: int):
        """Setup serial communication with improved error handling"""
        try:
            self.serial = serial.Serial(port, baudrate, timeout=0.1)
            self.command_queue = asyncio.Queue()
            logger.info(f"Serial communication established on {port} at {baudrate} baud")
        except serial.SerialException as e:
            logger.error(f"Failed to open serial port {port}: {e}")
            raise RuntimeError(f"Failed to open serial port {port}: {e}")

    def _initialize_states(self):
        """Initialize joint states with improved defaults"""
        for joint in self.joints:
            self.joint_states[joint] = JointState(
                position=0.0,
                velocity=0.0,
                torque=0.0,
                current=0.0,
                temperature=25.0,
                state=MotorState.IDLE
            )

    @asynccontextmanager
    async def session(self):
        """Context manager for safe hardware control"""
        try:
            await self.start()
            yield self
        finally:
            await self.stop()

    async def start(self):
        """Start hardware interface with improved task management"""
        # Start communication tasks
        self.running = True
        
        # Create and track tasks for proper cleanup
        self.tasks = [
            asyncio.create_task(self._read_loop()),
            asyncio.create_task(self._write_loop()),
            asyncio.create_task(self._safety_monitor()),
            asyncio.create_task(self._metrics_collector())
        ]
        
        # Initialize hardware
        await self._initialize_hardware()
        logger.info("Hardware interface started")

    async def stop(self):
        """Stop hardware interface with proper cleanup"""
        logger.info("Stopping hardware interface")
        self.running = False

        # Safely stop all joints
        for joint in self.joints:
            await self.set_joint_state(joint, 0, 0, 0)

        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
            
        try:
            # Wait for tasks to complete
            await asyncio.gather(*self.tasks, return_exceptions=True)
        except asyncio.CancelledError:
            pass
            
        # Close serial connection
        if hasattr(self, 'serial') and self.serial.is_open:
            self.serial.close()
            
        logger.info("Hardware interface stopped")

    async def _initialize_hardware(self):
        """Initialize hardware components with improved error handling"""
        logger.info("Initializing hardware components")
        
        for joint_name, joint_info in self.joints.items():
            try:
                # Reset motor controllers
                await self._send_command(joint_info['id'], CommandType.RESET)
                await asyncio.sleep(0.1)

                # Enable motors
                await self._send_command(joint_info['id'], CommandType.ENABLE)
                await asyncio.sleep(0.1)
                
                logger.info(f"Initialized joint: {joint_name}")
            except Exception as e:
                logger.error(f"Failed to initialize joint {joint_name}: {e}")
                self.safety_flags['emergency_stop'] = True
                if self.safety_config.emergency_stop_callback:
                    await self.safety_config.emergency_stop_callback()

    async def _send_command(self, joint_id: int, command_type: CommandType, *params):
        """Send command with improved error handling"""
        command = self._create_command(joint_id, command_type, *params)
        await self.command_queue.put(command)
        self.metrics['last_command_time'] = time.time()
        self.metrics['command_count'] += 1

    async def set_joint_state(self, joint: str, position: float, 
                            velocity: float, torque: float):
        """Set joint state with improved safety checks and error handling"""
        if joint not in self.joints:
            logger.error(f"Unknown joint: {joint}")
            return False

        try:
            # Apply safety limits
            position = self._limit_position(joint, position)
            velocity = self._limit_velocity(velocity)
            torque = self._limit_torque(joint, torque)

            # Create and send command
            joint_id = self.joints[joint]['id']
            await self._send_command(
                joint_id,
                CommandType.MOVE,
                position,
                velocity,
                torque
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to set joint state for {joint}: {e}")
            self.metrics['error_count'] += 1
            return False

    async def calibrate_joint(self, joint: str):
        """Calibrate a specific joint"""
        if joint not in self.joints:
            logger.error(f"Unknown joint: {joint}")
            return False
            
        logger.info(f"Calibrating joint: {joint}")
        joint_id = self.joints[joint]['id']
        
        try:
            # Send calibration command
            await self._send_command(joint_id, CommandType.CALIBRATE)
            
            # Update joint state
            self.joint_states[joint].state = MotorState.CALIBRATING
            
            # Wait for calibration to complete (typically takes ~2s)
            for _ in range(20):  # 20 * 0.1s = 2s timeout
                await asyncio.sleep(0.1)
                
                # Check if calibration completed
                if self.joint_states[joint].state != MotorState.CALIBRATING:
                    logger.info(f"Joint {joint} calibration completed")
                    return True
                    
            logger.warning(f"Joint {joint} calibration timed out")
            return False
        except Exception as e:
            logger.error(f"Failed to calibrate joint {joint}: {e}")
            self.metrics['error_count'] += 1
            return False

    async def emergency_stop(self):
        """Emergency stop all motors"""
        logger.warning("EMERGENCY STOP triggered")
        self.safety_flags['emergency_stop'] = True
        
        try:
            # Send emergency stop to all joints
            for joint_name, joint_info in self.joints.items():
                await self._send_command(joint_info['id'], CommandType.EMERGENCY_STOP)
                
            return True
        except Exception as e:
            logger.error(f"Failed to execute emergency stop: {e}")
            return False

    def _limit_position(self, joint: str, position: float) -> float:
        """Limit joint position with improved safety margin"""
        limits = self.joints[joint]['limits']
        # Add safety margin (0.5 degrees)
        safe_min = limits[0] + 0.5
        safe_max = limits[1] - 0.5
        return np.clip(position, safe_min, safe_max)

    def _limit_velocity(self, velocity: float) -> float:
        """Limit joint velocity using safety config"""
        max_vel = self.safety_config.max_velocity
        return np.clip(velocity, -max_vel, max_vel)

    def _limit_torque(self, joint: str, torque: float) -> float:
        """Limit joint torque with improved safety factor"""
        max_torque = self.joints[joint]['max_torque'] * 0.95  # 95% safety factor
        return np.clip(torque, -max_torque, max_torque)

    def _create_command(self, joint_id: int, command_type: CommandType, 
                       *params) -> bytes:
        """Create command packet with caching for common commands"""
        # Check command cache for common commands
        cache_key = (joint_id, command_type.value, params)
        if cache_key in self._command_cache:
            return self._command_cache[cache_key]
            
        # Command structure:
        # Header (2 bytes) | Joint ID (1 byte) | Command (1 byte) | 
        # Params (4 bytes each) | Checksum (1 byte)

        # Create command packet
        packet = bytearray()
        packet.extend(b'\xFF\xFF')  # Header
        packet.append(joint_id)
        packet.append(command_type.value)

        # Add parameters
        for param in params:
            packet.extend(struct.pack('f', param))

        # Add checksum - improved with CRC-8 algorithm
        checksum = self._calculate_crc8(packet)
        packet.append(checksum)
        
        # Cache common commands (no parameters or fixed parameters)
        if len(params) == 0 or command_type in [CommandType.RESET, CommandType.ENABLE, CommandType.DISABLE]:
            self._command_cache[cache_key] = bytes(packet)

        return bytes(packet)
        
    def _calculate_crc8(self, data: bytearray) -> int:
        """Calculate CRC-8 checksum for improved error detection"""
        crc = 0
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ 0x07
                else:
                    crc <<= 1
                crc &= 0xFF
        return crc

    async def _read_loop(self):
        """Read feedback from hardware with improved error handling and timeout management"""
        last_read_time = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                read_interval = current_time - last_read_time
                last_read_time = current_time
                
                # Track read frequency for performance monitoring
                self.metrics['read_frequency'].append(1.0 / read_interval if read_interval > 0 else 0)
                if len(self.metrics['read_frequency']) > 100:
                    self.metrics['read_frequency'].pop(0)
                
                if self.serial.in_waiting >= 20:  # Expected packet size
                    data = self.serial.read(20)
                    if len(data) == 20 and data[0:2] == b'\xFF\xFF':
                        if self._validate_checksum(data):
                            self._process_feedback(data)
                        else:
                            logger.warning("Invalid checksum in feedback packet")
                            self.metrics['error_count'] += 1
                
                # Adaptive sleep based on data availability
                if self.serial.in_waiting > 0:
                    await asyncio.sleep(0.0005)  # Short sleep when data is available
                else:
                    await asyncio.sleep(0.001)  # Longer sleep when no data
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Read error: {e}")
                self.metrics['error_count'] += 1
                await asyncio.sleep(0.005)  # Longer sleep on error

    def _validate_checksum(self, data: bytes) -> bool:
        """Validate packet checksum"""
        # Last byte is checksum
        received_checksum = data[-1]
        calculated_checksum = self._calculate_crc8(bytearray(data[:-1]))
        return received_checksum == calculated_checksum

    async def _write_loop(self):
        """Write commands to hardware with improved flow control"""
        last_write_time = time.time()
        
        while self.running:
            try:
                # Get command from queue with timeout
                try:
                    command = await asyncio.wait_for(self.command_queue.get(), 0.01)
                    
                    # Calculate and track command latency
                    current_time = time.time()
                    latency = current_time - self.metrics['last_command_time']
                    self.metrics['command_latency'].append(latency)
                    if len(self.metrics['command_latency']) > 100:
                        self.metrics['command_latency'].pop(0)
                    
                    # Send command
                    self.serial.write(command)
                    self.command_queue.task_done()
                    
                    # Adaptive rate control
                    elapsed = time.time() - last_write_time
                    if elapsed < 0.001:  # Maintain max 1kHz rate
                        await asyncio.sleep(0.001 - elapsed)
                    
                    last_write_time = time.time()
                    
                except asyncio.TimeoutError:
                    # No commands in the queue
                    await asyncio.sleep(0.001)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Write error: {e}")
                self.metrics['error_count'] += 1
                await asyncio.sleep(0.005)  # Longer sleep on error

    def _process_feedback(self, data: bytes):
        """Process feedback data with improved error handling"""
        try:
            # Parse packet
            # First two bytes are header (0xFF 0xFF)
            joint_id = data[2]

            # Find joint name from ID
            joint_name = None
            for name, info in self.joints.items():
                if info['id'] == joint_id:
                    joint_name = name
                    break

            if joint_name:
                # Parse state data
                position = struct.unpack('f', data[3:7])[0]
                velocity = struct.unpack('f', data[7:11])[0]
                torque = struct.unpack('f', data[11:15])[0]
                current = struct.unpack('f', data[15:19])[0]
                
                # Last byte before checksum contains temperature and state
                temperature = (data[19] >> 3) & 0x1F  # 5 bits for temperature (0-31) + 80
                temperature += 80  # Offset for working range
                
                state_value = data[19] & 0x07  # 3 bits for state
                try:
                    state = MotorState(state_value + 1)  # +1 for enum mapping
                except ValueError:
                    state = MotorState.ERROR
                    logger.warning(f"Invalid motor state value: {state_value}")

                # Update joint state
                current_time = time.time()
                new_state = JointState(
                    position=position,
                    velocity=velocity,
                    torque=torque,
                    current=current,
                    temperature=temperature,
                    state=state,
                    timestamp=current_time,
                    position_history=self.joint_states[joint_name].position_history
                )
                new_state.update_history()
                self.joint_states[joint_name] = new_state

                self.last_update = current_time

        except Exception as e:
            logger.error(f"Feedback processing error: {e}")
            self.metrics['error_count'] += 1

    async def _safety_monitor(self):
        """Monitor system safety with improved predictive warnings"""
        while self.running:
            try:
                current_time = time.time()

                # Check communication timeout
                comm_timeout = self.safety_config.communication_timeout
                if current_time - self.last_update > comm_timeout:
                    logger.warning(f"Communication timeout detected: {current_time - self.last_update:.3f}s")
                    self.safety_flags['communication_warning'] = Tr