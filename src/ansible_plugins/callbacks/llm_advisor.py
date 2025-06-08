from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: llm_advisor
    type: notification
    short_description: Uses TinyLlama 3 to provide advice during playbook execution
    description:
        - This callback plugin uses TinyLlama 3 to analyze task failures and provide advice
        - It can also analyze successful tasks and suggest optimizations
    requirements:
        - Python 3.12+
        - TinyLlama 3 components installed
    options:
      enable_failure_analysis:
        description: Whether to analyze failures 
        default: True
        type: bool
        ini:
          - section: callback_llm_advisor
            key: enable_failure_analysis
        env:
          - name: ANSIBLE_CALLBACK_LLM_ADVISOR_FAILURE_ANALYSIS
      enable_optimization:
        description: Whether to suggest optimizations for successful tasks
        default: False
        type: bool
        ini:
          - section: callback_llm_advisor
            key: enable_optimization
        env:
          - name: ANSIBLE_CALLBACK_LLM_ADVISOR_OPTIMIZATION
'''

import os
import json
import time
import traceback
import socket
from datetime import datetime

from ansible.plugins.callback import CallbackBase

try:
    # Import TinyLlama components
    # This would be the actual import in a real implementation
    TINYLLAMA_AVAILABLE = False
    TINYLLAMA_IMPORT_ERROR = "TinyLlama components not available (this is expected in the initial setup)"
except ImportError as e:
    TINYLLAMA_AVAILABLE = False
    TINYLLAMA_IMPORT_ERROR = str(e)

class CallbackModule(CallbackBase):
    """
    Ansible callback plugin that uses TinyLlama 3 to provide advice during playbook execution.
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'llm_advisor'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display=display)
        self.playbook_name = None
        self.play_name = None
        self.task_name = None
        self.host_name = None
        self.failures = 0
        self.success = 0
        self.start_time = datetime.now()
        
        # Check if TinyLlama is available
        if not TINYLLAMA_AVAILABLE:
            self._display.warning(f"TinyLlama is not available: {TINYLLAMA_IMPORT_ERROR}")
            self._display.warning("LLM advisor functionality will be limited")

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)
        self.enable_failure_analysis = self.get_option('enable_failure_analysis')
        self.enable_optimization = self.get_option('enable_optimization')
        
        self._display.vv("LLM Advisor: Failure Analysis: {}".format("Enabled" if self.enable_failure_analysis else "Disabled"))
        self._display.vv("LLM Advisor: Optimization: {}".format("Enabled" if self.enable_optimization else "Disabled"))

    def v2_playbook_on_start(self, playbook):
        self.playbook_name = os.path.basename(playbook._file_name)
        self._display.display(f"LLM Advisor: Monitoring playbook {self.playbook_name}", color="blue")

    def v2_playbook_on_play_start(self, play):
        self.play_name = play.get_name()
        
    def v2_playbook_on_task_start(self, task, is_conditional):
        self.task_name = task.get_name()
    
    def v2_runner_on_failed(self, result, ignore_errors=False):
        if not self.enable_failure_analysis:
            return
        
        self.host_name = result._host.get_name()
        self.failures += 1
        
        if ignore_errors:
            return
            
        # Extract useful information from the result
        task_args = result._task.args
        error_msg = self._get_error_message(result._result)
        
        self._display.display("LLM Advisor: Analyzing failure...", color="yellow")
        
        # In a real implementation, here we would call the LLM to analyze the failure
        # For now, we'll just show what information would be sent to the LLM
        
        analysis_data = {
            "playbook": self.playbook_name,
            "play": self.play_name,
            "task": self.task_name,
            "host": self.host_name,
            "error": error_msg,
            "task_args": task_args
        }
        
        self._display.display(f"Would send to LLM for analysis: {json.dumps(analysis_data, indent=2)}", color="yellow")
        self._display.display("LLM Advisor: This is a placeholder for actual TinyLlama analysis", color="cyan")
        
    def v2_runner_on_ok(self, result):
        self.host_name = result._host.get_name()
        self.success += 1
        
        if not self.enable_optimization:
            return
            
        # For successful tasks, we could suggest optimizations
        # This would be implemented in a real version of the plugin
        pass
        
    def v2_playbook_on_stats(self, stats):
        # Show summary at the end
        duration = (datetime.now() - self.start_time).total_seconds()
        self._display.display("LLM Advisor Summary:")
        self._display.display(f"  Duration: {duration:.2f} seconds")
        self._display.display(f"  Successful tasks: {self.success}")
        self._display.display(f"  Failed tasks: {self.failures}")
        
    def _get_error_message(self, result):
        """Extract error message from result."""
        if 'msg' in result:
            return result['msg']
        elif 'stdout' in result:
            return result['stdout']
        elif 'stderr' in result:
            return result['stderr']
        else:
            return str(result)
