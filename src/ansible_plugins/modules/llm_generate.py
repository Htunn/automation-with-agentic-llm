#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2025, Your Name <your.email@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: llm_generate
short_description: Generate text using TinyLlama 3
description:
    - This module uses a TinyLlama 3 model to generate text based on prompts.
    - Can be used to generate playbooks, analyze configurations, or make decisions.
options:
    prompt:
        description:
            - The prompt to send to the LLM.
        required: true
        type: str
    max_tokens:
        description:
            - The maximum number of tokens to generate.
        required: false
        type: int
        default: 1024
    temperature:
        description:
            - Controls randomness in generation. Higher values increase randomness.
        required: false
        type: float
        default: 0.7
    endpoint:
        description:
            - The API endpoint for the LLM service. If not provided, uses local model.
        required: false
        type: str
author:
    - Your Name (@yourgithubhandle)
'''

EXAMPLES = r'''
- name: Generate an Ansible playbook to install nginx
  llm_generate:
    prompt: "Write an Ansible playbook to install and configure Nginx with a basic configuration"
    max_tokens: 2048
    temperature: 0.3
  register: generated_playbook

- name: Save the generated playbook
  copy:
    content: "{{ generated_playbook.text }}"
    dest: "/path/to/playbook.yml"

- name: Analyze a configuration file
  llm_generate:
    prompt: "Analyze this Nginx configuration file and suggest improvements: {{ lookup('file', '/etc/nginx/nginx.conf') }}"
  register: analysis_result

- name: Use remote LLM service
  llm_generate:
    prompt: "Generate a Windows automation task using SSH"
    endpoint: "http://llm-service:8000/generate"
  register: remote_generation
'''

RETURN = r'''
text:
    description: The generated text from the LLM.
    type: str
    returned: always
tokens_used:
    description: The number of tokens used in the generation.
    type: int
    returned: always
completion_time:
    description: The time taken to generate the completion in seconds.
    type: float
    returned: always
'''

import os
import time
import json
import traceback

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from ansible.module_utils.basic import AnsibleModule

def run_module():
    # Define the available arguments/parameters that a user can pass to the module
    module_args = dict(
        prompt=dict(type='str', required=True),
        max_tokens=dict(type='int', required=False, default=1024),
        temperature=dict(type='float', required=False, default=0.7),
        endpoint=dict(type='str', required=False, default=None),
    )

    # Seed the result dict
    result = dict(
        changed=False,
        text='',
        tokens_used=0,
        completion_time=0
    )

    # Create the module instance
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # Check if requests is available when endpoint is specified
    if module.params['endpoint'] and not HAS_REQUESTS:
        module.fail_json(msg='The python requests module is required for API endpoint usage.')

    # Check mode: do nothing but return an empty string
    if module.check_mode:
        module.exit_json(**result)

    # Process the prompt through the LLM
    try:
        start_time = time.time()
        
        if module.params['endpoint']:
            # Use remote API endpoint
            response = requests.post(
                module.params['endpoint'],
                json={
                    'prompt': module.params['prompt'],
                    'max_tokens': module.params['max_tokens'],
                    'temperature': module.params['temperature']
                },
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                result['text'] = response_data.get('text', '')
                result['tokens_used'] = response_data.get('tokens_used', 0)
            else:
                module.fail_json(
                    msg=f"API request failed with status code {response.status_code}: {response.text}",
                    **result
                )
        else:
            # Use local model - this is a placeholder for the actual implementation
            # In a real implementation, we would load the model and generate text
            module.warn("Local model implementation placeholder - actual model integration needed")
            result['text'] = f"This is a placeholder response for: {module.params['prompt'][:30]}..."
            result['tokens_used'] = len(module.params['prompt'].split())
        
        result['completion_time'] = time.time() - start_time
        
    except Exception as e:
        module.fail_json(msg=f"Error generating text: {str(e)}", exception=traceback.format_exc(), **result)

    # Return the results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
