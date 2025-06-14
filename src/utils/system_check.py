#!/usr/bin/env python3
"""
System check script for Ansible TinyLlama Integration.
Verifies that the current environment meets all requirements.
"""

import os
import sys
import shutil
import logging
import platform
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("system_check")

# Minimum requirements
MIN_PYTHON_VERSION = (3, 12, 0)
MIN_TORCH_VERSION = "2.0.0"
MIN_ANSIBLE_VERSION = "2.14.0"
MIN_RAM_GB = 8
MIN_DISK_GB = 10
RECOMMENDED_RAM_GB = 16
RECOMMENDED_DISK_GB = 20

def check_python_version():
    """Check if the Python version meets requirements."""
    current = sys.version_info[:3]
    if current < MIN_PYTHON_VERSION:
        logger.error(f"Python version too old: {'.'.join(map(str, current))} < {'.'.join(map(str, MIN_PYTHON_VERSION))}")
        return False
    logger.info(f"Python version: {'.'.join(map(str, current))}")
    return True

def check_pip_packages():
    """Check if required pip packages are installed."""
    try:
        import pip
        packages = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'], universal_newlines=True)
        
        # Check for key packages
        required_packages = {
            "ansible": MIN_ANSIBLE_VERSION,
            "torch": MIN_TORCH_VERSION,
            "transformers": "4.30.0",
            "fastapi": "0.100.0",
        }
        
        missing = []
        for package, version in required_packages.items():
            if not any(p.lower().startswith(f"{package.lower()}==") for p in packages.split('\n')):
                missing.append(package)
        
        if missing:
            logger.error(f"Missing required packages: {', '.join(missing)}")
            return False
        
        logger.info("All required pip packages are installed")
        return True
    except Exception as e:
        logger.error(f"Error checking pip packages: {e}")
        return False

def check_gpu():
    """Check if GPU is available for PyTorch."""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_count = torch.cuda.device_count()
            logger.info(f"GPU available: {gpu_name} (Count: {gpu_count})")
            return True
        else:
            logger.warning("No GPU detected, using CPU only (slower performance)")
            return False
    except ImportError:
        logger.warning("PyTorch not installed, skipping GPU check")
        return False
    except Exception as e:
        logger.error(f"Error checking GPU: {e}")
        return False

def check_system_resources():
    """Check system resources (RAM, disk)."""
    try:
        import psutil
    except ImportError:
        logger.warning("psutil not installed, skipping system resource check")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
            import psutil
            logger.info("Installed psutil for system checks")
        except Exception:
            return False
    
    # Check RAM
    try:
        ram_gb = psutil.virtual_memory().total / (1024 ** 3)
        if ram_gb < MIN_RAM_GB:
            logger.error(f"Insufficient RAM: {ram_gb:.1f}GB < minimum {MIN_RAM_GB}GB")
            return False
        elif ram_gb < RECOMMENDED_RAM_GB:
            logger.warning(f"RAM may be low: {ram_gb:.1f}GB < recommended {RECOMMENDED_RAM_GB}GB")
        else:
            logger.info(f"RAM: {ram_gb:.1f}GB (OK)")
    except Exception as e:
        logger.error(f"Error checking RAM: {e}")
    
    # Check disk space
    try:
        disk_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        disk_gb = psutil.disk_usage(disk_path).free / (1024 ** 3)
        if disk_gb < MIN_DISK_GB:
            logger.error(f"Insufficient disk space: {disk_gb:.1f}GB < minimum {MIN_DISK_GB}GB")
            return False
        elif disk_gb < RECOMMENDED_DISK_GB:
            logger.warning(f"Disk space may be low: {disk_gb:.1f}GB < recommended {RECOMMENDED_DISK_GB}GB")
        else:
            logger.info(f"Free disk space: {disk_gb:.1f}GB (OK)")
    except Exception as e:
        logger.error(f"Error checking disk space: {e}")
    
    return True

def check_ansible():
    """Check if Ansible is installed and meets version requirements."""
    try:
        result = subprocess.run(['ansible', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("Ansible not found or not in PATH")
            return False
        
        # Parse version
        version_line = result.stdout.splitlines()[0]
        version = version_line.split()[1]
        logger.info(f"Ansible version: {version}")
        
        # Compare with minimum required
        from packaging import version as ver_pkg
        if ver_pkg.parse(version) < ver_pkg.parse(MIN_ANSIBLE_VERSION):
            logger.error(f"Ansible version too old: {version} < {MIN_ANSIBLE_VERSION}")
            return False
        
        logger.info("Ansible check: OK")
        return True
    except Exception as e:
        logger.error(f"Error checking Ansible: {e}")
        return False

def check_directories():
    """Check if required directories exist and are writable."""
    project_root = Path(__file__).parent.parent
    directories = [
        project_root / "models",
        project_root / "logs",
        project_root / "config",
    ]
    
    ok = True
    for directory in directories:
        if not directory.exists():
            logger.warning(f"Directory {directory} does not exist, creating...")
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")
                ok = False
                continue
        
        if not os.access(directory, os.W_OK):
            logger.error(f"Directory {directory} is not writable")
            ok = False
    
    logger.info("Directory checks completed")
    return ok

def main():
    """Run all system checks."""
    logger.info("Starting system check for Ansible TinyLlama Integration")
    logger.info(f"Platform: {platform.platform()}")
    
    checks = [
        ("Python version", check_python_version),
        ("Required packages", check_pip_packages),
        ("GPU availability", check_gpu),
        ("System resources", check_system_resources),
        ("Ansible installation", check_ansible),
        ("Required directories", check_directories),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            status = "PASS" if result else "FAIL"
            results.append((name, status))
        except Exception as e:
            logger.error(f"Check '{name}' failed with error: {e}")
            results.append((name, "ERROR"))
    
    # Print summary
    logger.info("\n" + "=" * 40)
    logger.info("SYSTEM CHECK SUMMARY")
    logger.info("=" * 40)
    
    all_passed = True
    for name, status in results:
        logger.info(f"{name + ':':25} {status}")
        if status != "PASS":
            all_passed = False
    
    if all_passed:
        logger.info("\nAll checks PASSED. System is ready to run Ansible TinyLlama Integration.")
        return 0
    else:
        logger.warning("\nSome checks FAILED. Please address issues before running the application.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
