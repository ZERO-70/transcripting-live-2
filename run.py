#!/usr/bin/env python3
"""
Stream Project Runner
Main entry point for running various components of the stream project.
"""

import sys
import os
import subprocess

def run_with_path(script_path, working_dir=None):
    """Run a Python script with proper path setup."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Setup environment with proper paths
    env = os.environ.copy()
    pythonpath = [
        os.path.join(current_dir, 'src'),
        os.path.join(current_dir, 'src', 'filters'),
        os.path.join(current_dir, 'src', 'transcription'),
        os.path.join(current_dir, 'src', 'streaming'),
    ]
    
    existing_path = env.get('PYTHONPATH', '')
    if existing_path:
        pythonpath.append(existing_path)
    env['PYTHONPATH'] = os.pathsep.join(pythonpath)
    
    if working_dir:
        working_dir = os.path.join(current_dir, working_dir)
    else:
        working_dir = current_dir
    
    subprocess.run([sys.executable, script_path], cwd=working_dir, env=env)


def run_with_path_and_args(script_path, working_dir=None, extra_args=None):
    """Run a Python script with proper path setup and additional arguments."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Setup environment with proper paths
    env = os.environ.copy()
    pythonpath = [
        os.path.join(current_dir, 'src'),
        os.path.join(current_dir, 'src', 'filters'),
        os.path.join(current_dir, 'src', 'transcription'),
        os.path.join(current_dir, 'src', 'streaming'),
    ]
    
    existing_path = env.get('PYTHONPATH', '')
    if existing_path:
        pythonpath.append(existing_path)
    env['PYTHONPATH'] = os.pathsep.join(pythonpath)
    
    if working_dir:
        working_dir = os.path.join(current_dir, working_dir)
    else:
        working_dir = current_dir
    
    cmd = [sys.executable, script_path]
    if extra_args:
        cmd.extend(extra_args)
    
    subprocess.run(cmd, cwd=working_dir, env=env)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Stream Project Runner')
    parser.add_argument('component', choices=[
        'transcribe', 'transcribe-model', 'transcribe-dict', 'transcribe-nofilter',
        'demo-comparison', 'demo-model', 'demo-highlight',
        'test-comprehensive', 'test-model', 'stream', 'stream-http'
    ], help='Component to run')
    
    # Add transcription-specific arguments
    parser.add_argument('--model', default='base', help='Whisper model to use')
    parser.add_argument('--language', default='en', help='Language code')
    parser.add_argument('--stream', choices=['udp', 'http'], default='udp', help='Stream type')
    parser.add_argument('--toxicity-model', help='Toxicity detection model')
    
    args = parser.parse_args()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Handle transcription variants
    if args.component.startswith('transcribe'):
        script_path = 'src/transcription/live_transcribe.py'
        extra_args = [
            '--model', args.model,
            '--language', args.language,
            '--stream', args.stream
        ]
        
        if args.component == 'transcribe-model':
            extra_args.extend(['--filter-type', 'model'])
            if args.toxicity_model:
                extra_args.extend(['--toxicity-model', args.toxicity_model])
        elif args.component == 'transcribe-dict':
            extra_args.extend(['--filter-type', 'dictionary'])
        elif args.component == 'transcribe-nofilter':
            extra_args.append('--no-filter')
        elif args.component == 'transcribe':
            # Default to dictionary filter
            extra_args.extend(['--filter-type', 'dictionary'])
        
        print(f"🚀 Running {args.component}...")
        print(f"   Arguments: {' '.join(extra_args)}")
        run_with_path_and_args(script_path, None, extra_args)
        return
    
    # Handle other components
    component_map = {
        'demo-comparison': ('demo_filter_comparison.py', 'demos'),
        'demo-model': ('demo_model_filter.py', 'demos'),
        'demo-highlight': ('demo_red_highlighting.py', 'demos'),
        'test-comprehensive': ('test_comprehensive_filters.py', 'tests'),
        'test-model': ('test_model_filter.py', 'tests'),
        'stream': ('src/streaming/ffmpeg_stream.py', None),
        'stream-http': ('src/streaming/ffmpeg_stream.py', None),
    }
    
    script_path, working_dir = component_map[args.component]
    if working_dir:
        script_path = os.path.join(working_dir, script_path)
    
    print(f"🚀 Running {args.component}...")
    
    # Handle HTTP streaming specifically
    if args.component == 'stream-http':
        run_with_path_and_args(script_path, working_dir, ['http'])
    else:
        run_with_path(script_path, working_dir)


if __name__ == "__main__":
    main()
