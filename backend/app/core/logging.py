import logging
from datetime import datetime
from pathlib import Path

# Configurar el directorio de logs
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configurar el formato del log
log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Log para acciones de autenticación
auth_logger = logging.getLogger("auth")
auth_handler = logging.FileHandler(log_dir / "auth.log")
auth_handler.setFormatter(log_format)
auth_logger.addHandler(auth_handler)
auth_logger.setLevel(logging.INFO)

# Log para acciones de usuario
user_logger = logging.getLogger("user")
user_handler = logging.FileHandler(log_dir / "user.log")
user_handler.setFormatter(log_format)
user_logger.addHandler(user_handler)
user_logger.setLevel(logging.INFO)

# Log para acciones de proyecto
project_logger = logging.getLogger("project")
project_handler = logging.FileHandler(log_dir / "project.log")
project_handler.setFormatter(log_format)
project_logger.addHandler(project_handler)
project_logger.setLevel(logging.INFO)

# Log para acciones de tareas
task_logger = logging.getLogger("task")
task_handler = logging.FileHandler(log_dir / "task.log")
task_handler.setFormatter(log_format)
task_logger.addHandler(task_handler)
task_logger.setLevel(logging.INFO)


def log_auth_event(event_type: str, user_email: str, success: bool, ip: str = None):
    """Log eventos de autenticación"""
    auth_logger.info(
        f"Auth {event_type} - User: {user_email} - Success: {success} - IP: {ip}"
    )


def log_user_event(
    action: str, user_id: int, target_id: int = None, details: str = None
):
    """Log eventos relacionados con usuarios"""
    user_logger.info(
        f"User {action} - User ID: {user_id} - Target ID: {target_id} - Details: {details}"
    )


def log_project_event(action: str, project_id: int, user_id: int, details: str = None):
    """Log eventos relacionados con proyectos"""
    project_logger.info(
        f"Project {action} - Project ID: {project_id} - User ID: {user_id} - Details: {details}"
    )


def log_task_event(action: str, task_id: int, user_id: int, details: str = None):
    """Log eventos relacionados con tareas"""
    task_logger.info(
        f"Task {action} - Task ID: {task_id} - User ID: {user_id} - Details: {details}"
    )
