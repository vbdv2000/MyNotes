import logging
from datetime import datetime
from pathlib import Path

# Configurar el directorio de logs
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configurar el formato del log
log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def add_handlers(logger, filename):
    file_handler = logging.FileHandler(log_dir / filename)
    file_handler.setFormatter(log_format)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.INFO)


# Log para acciones de autenticación
auth_logger = logging.getLogger("auth")
add_handlers(auth_logger, "auth.log")

user_logger = logging.getLogger("user")
add_handlers(user_logger, "user.log")

project_logger = logging.getLogger("project")
add_handlers(project_logger, "project.log")

task_logger = logging.getLogger("task")
add_handlers(task_logger, "task.log")


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
