"""
VS Code Bridge - Python Backend
Handles commands from VS Code extension and executes DaVinci Resolve operations
"""

import sys
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from resolve_ai.controller import ResolveAIController
    from resolve_ai.fusion_tools import FusionNodeBuilder
except ImportError as e:
    print(json.dumps({
        'success': False,
        'error': f'Failed to import resolve_ai modules: {e}'
    }))
    sys.exit(1)


class VSCodeBridge:
    """Handles commands from VS Code extension"""

    def __init__(self):
        try:
            self.controller = ResolveAIController()
            self.fusion_builder: Optional[FusionNodeBuilder] = None
        except Exception as e:
            raise RuntimeError(f"Failed to connect to DaVinci Resolve: {e}")

    def handle_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Route command to appropriate handler"""
        action = command.get('action')

        handlers = {
            'execute_step': self.execute_step,
            'play_preview': self.play_preview,
            'get_context': self.get_context,
            'parse_intent': self.parse_intent,
            'break_down_task': self.break_down_task,
            'modify_step': self.modify_step,
            'set_render_range': self.set_render_range,
            'clear_composition': self.clear_composition
        }

        handler = handlers.get(action)
        if not handler:
            return {'success': False, 'error': f'Unknown action: {action}'}

        try:
            result = handler(command)
            return {'success': True, 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def execute_step(self, command: Dict) -> Dict:
        """Execute a single step"""
        step = command['step']
        actions = step.get('actions', [])

        # Ensure we have a Fusion composition
        if not self.fusion_builder:
            comp = self.controller.get_fusion_comp()
            if not comp:
                raise RuntimeError("No Fusion composition available. Select a clip on the timeline.")
            self.fusion_builder = FusionNodeBuilder(comp)

        results = []
        details = {}

        for action in actions:
            action_type = action.get('type')
            target = action.get('target')
            params = action.get('params', {})

            if action_type == 'create_node':
                node = self._create_node(target, params)
                results.append(f"Created {target} node")
                details[target] = f"Created at ({params.get('x_pos', 0)}, {params.get('y_pos', 0)})"

            elif action_type == 'connect_nodes':
                self._connect_nodes(params)
                results.append(f"Connected nodes")

            elif action_type == 'set_parameters':
                self._set_parameters(target, params)
                results.append(f"Set parameters on {target}")

        return {
            'status': 'completed',
            'results': results,
            'details': details
        }

    def _create_node(self, node_type: str, params: Dict) -> str:
        """Create a Fusion node based on type"""
        if node_type == 'Background':
            return self.fusion_builder.create_background_node(
                name=params.get('name', 'Background'),
                color=params.get('color', (0.2, 0.4, 0.8, 1.0)),
                x_pos=params.get('x_pos', 0),
                y_pos=params.get('y_pos', 0)
            )
        elif node_type == 'Text':
            return self.fusion_builder.create_text_node(
                text=params.get('text', 'Text'),
                name=params.get('name', 'Text'),
                color=params.get('color', (1.0, 1.0, 1.0, 1.0)),
                size=params.get('size', 0.1),
                x_pos=params.get('x_pos', 1),
                y_pos=params.get('y_pos', 0)
            )
        elif node_type == 'Transform':
            return self.fusion_builder.create_transform_node(
                name=params.get('name', 'Transform'),
                x_pos=params.get('x_pos', 2),
                y_pos=params.get('y_pos', 0)
            )
        elif node_type == 'Merge':
            return self.fusion_builder.create_merge_node(
                name=params.get('name', 'Merge'),
                x_pos=params.get('x_pos', 3),
                y_pos=params.get('y_pos', 0)
            )
        else:
            raise ValueError(f"Unsupported node type: {node_type}")

    def _connect_nodes(self, params: Dict):
        """Connect two nodes"""
        from_node = params.get('from')
        to_node = params.get('to')
        input_name = params.get('input', 'Input')

        self.fusion_builder.connect_nodes(from_node, to_node, input_name)

    def _set_parameters(self, node_name: str, params: Dict):
        """Set parameters on a node"""
        self.fusion_builder.set_node_params(node_name, params)

    def play_preview(self, command: Dict) -> Dict:
        """Play 20-second preview"""
        # Set render range
        timeline = self.controller.get_current_timeline()
        if not timeline:
            raise RuntimeError("No timeline available")

        # Get frame rate
        frame_rate = float(timeline.GetSetting("timelineFrameRate") or "24")
        max_seconds = 20
        end_frame = int(max_seconds * frame_rate)

        # Set in/out points
        timeline.SetSetting("useInOutRange", "1")
        timeline.SetSetting("inFrame", "0")
        timeline.SetSetting("outFrame", str(end_frame))

        # Go to start
        timeline.SetCurrentTimecode("00:00:00:00")

        # Play (requires DaVinci Resolve UI to be visible)
        # Note: This may not work if Resolve is minimized
        project = self.controller.project
        if project:
            project.Play()

        return {
            'status': 'playing',
            'duration': max_seconds,
            'frames': f"0-{end_frame}",
            'frame_rate': frame_rate
        }

    def get_context(self, command: Dict) -> Dict:
        """Get current composition context"""
        context_lines = []

        # Project info
        status = self.controller.get_status()
        context_lines.append("Project Information:")
        context_lines.append(f"  Name: {status.get('project_name', 'N/A')}")
        context_lines.append(f"  Timeline: {status.get('timeline_name', 'N/A')}")
        context_lines.append(f"  Frame Rate: {status.get('frame_rate', 'N/A')}")
        context_lines.append("")

        # Fusion composition
        if self.fusion_builder or status.get('fusion_available'):
            if not self.fusion_builder:
                comp = self.controller.get_fusion_comp()
                if comp:
                    self.fusion_builder = FusionNodeBuilder(comp)

            if self.fusion_builder:
                nodes = self.fusion_builder.get_node_list()
                context_lines.append("Fusion Composition:")
                context_lines.append(f"  Total Nodes: {len(nodes)}")

                if nodes:
                    context_lines.append("  Nodes:")
                    for node in nodes:
                        context_lines.append(f"    - {node}")
                else:
                    context_lines.append("  (Empty composition)")
            else:
                context_lines.append("Fusion Composition: Not available")
        else:
            context_lines.append("Fusion Composition: No clip selected")

        context_lines.append("")
        context_lines.append("Ready for commands!")

        return {'context': '\n'.join(context_lines)}

    def parse_intent(self, command: Dict) -> Dict:
        """Parse user intent from natural language"""
        prompt = command['prompt'].lower()

        intent = {
            'type': 'unknown',
            'parameters': {}
        }

        # Detect common patterns
        if 'lower-third' in prompt or 'lower third' in prompt:
            intent['type'] = 'create_lower_third'
            # Extract text in quotes
            import re
            matches = re.findall(r'"([^"]*)"', command['prompt'])
            if matches:
                intent['parameters']['title'] = matches[0]
                if len(matches) > 1:
                    intent['parameters']['subtitle'] = matches[1]

        elif 'text' in prompt:
            intent['type'] = 'create_text'
            import re
            matches = re.findall(r'"([^"]*)"', command['prompt'])
            if matches:
                intent['parameters']['text'] = matches[0]

            # Detect colors
            colors = {
                'red': (1.0, 0.0, 0.0, 1.0),
                'blue': (0.0, 0.0, 1.0, 1.0),
                'green': (0.0, 1.0, 0.0, 1.0),
                'white': (1.0, 1.0, 1.0, 1.0),
                'black': (0.0, 0.0, 0.0, 1.0),
                'orange': (1.0, 0.6, 0.0, 1.0),
                'yellow': (1.0, 1.0, 0.0, 1.0),
            }
            for color_name, color_value in colors.items():
                if color_name in prompt:
                    intent['parameters']['color'] = color_value
                    break

        elif 'background' in prompt:
            intent['type'] = 'create_background'
            # Detect colors
            colors = {
                'red': (1.0, 0.0, 0.0, 1.0),
                'blue': (0.0, 0.0, 1.0, 1.0),
                'green': (0.0, 1.0, 0.0, 1.0),
                'black': (0.0, 0.0, 0.0, 1.0),
                'white': (1.0, 1.0, 1.0, 1.0),
                'orange': (1.0, 0.6, 0.0, 1.0),
            }
            for color_name, color_value in colors.items():
                if color_name in prompt:
                    intent['parameters']['color'] = color_value
                    break

        elif 'preview' in prompt or 'play' in prompt:
            intent['type'] = 'play_preview'

        elif 'clear' in prompt:
            intent['type'] = 'clear_composition'

        elif 'context' in prompt or 'show' in prompt or 'what' in prompt:
            intent['type'] = 'get_context'

        return intent

    def break_down_task(self, command: Dict) -> List[Dict]:
        """Break task into executable steps"""
        intent = command['intent']
        intent_type = intent.get('type')
        params = intent.get('parameters', {})

        steps = []

        if intent_type == 'create_lower_third':
            title = params.get('title', 'Title')
            subtitle = params.get('subtitle', '')

            steps.append({
                'id': 1,
                'description': 'Create blue background rectangle',
                'actions': [{
                    'type': 'create_node',
                    'target': 'Background',
                    'params': {
                        'name': 'LowerThird_BG',
                        'color': (0.2, 0.4, 0.8, 0.8),
                        'x_pos': 0,
                        'y_pos': 0
                    }
                }],
                'parameters': {},
                'status': 'pending'
            })

            steps.append({
                'id': 2,
                'description': f'Add title text "{title}"',
                'actions': [{
                    'type': 'create_node',
                    'target': 'Text',
                    'params': {
                        'name': 'Title',
                        'text': title,
                        'color': (1.0, 1.0, 1.0, 1.0),
                        'size': 0.08,
                        'x_pos': 1,
                        'y_pos': 0
                    }
                }],
                'parameters': {},
                'status': 'pending'
            })

            if subtitle:
                steps.append({
                    'id': 3,
                    'description': f'Add subtitle "{subtitle}"',
                    'actions': [{
                        'type': 'create_node',
                        'target': 'Text',
                        'params': {
                            'name': 'Subtitle',
                            'text': subtitle,
                            'color': (0.9, 0.9, 0.9, 1.0),
                            'size': 0.05,
                            'x_pos': 1,
                            'y_pos': 1
                        }
                    }],
                    'parameters': {},
                    'status': 'pending'
                })

        elif intent_type == 'create_text':
            text = params.get('text', 'Text')
            color = params.get('color', (1.0, 1.0, 1.0, 1.0))

            steps.append({
                'id': 1,
                'description': f'Create text node: "{text}"',
                'actions': [{
                    'type': 'create_node',
                    'target': 'Text',
                    'params': {
                        'name': 'TextNode',
                        'text': text,
                        'color': color,
                        'size': 0.1,
                        'x_pos': 0,
                        'y_pos': 0
                    }
                }],
                'parameters': {},
                'status': 'pending'
            })

        elif intent_type == 'create_background':
            color = params.get('color', (0.0, 0.0, 0.0, 1.0))

            steps.append({
                'id': 1,
                'description': 'Create background node',
                'actions': [{
                    'type': 'create_node',
                    'target': 'Background',
                    'params': {
                        'name': 'Background',
                        'color': color,
                        'x_pos': 0,
                        'y_pos': 0
                    }
                }],
                'parameters': {},
                'status': 'pending'
            })

        else:
            # Unknown intent - create generic step
            steps.append({
                'id': 1,
                'description': f'Execute: {intent_type}',
                'actions': [],
                'parameters': params,
                'status': 'pending'
            })

        return steps

    def modify_step(self, command: Dict) -> Dict:
        """Modify a step based on user feedback"""
        step = command['step']
        modification = command['modification'].lower()

        # Parse modification for color changes
        colors = {
            'red': (1.0, 0.0, 0.0, 1.0),
            'blue': (0.0, 0.0, 1.0, 1.0),
            'green': (0.0, 1.0, 0.0, 1.0),
            'orange': (1.0, 0.6, 0.0, 1.0),
            'yellow': (1.0, 1.0, 0.0, 1.0),
            'purple': (0.5, 0.0, 0.5, 1.0),
            'white': (1.0, 1.0, 1.0, 1.0),
            'black': (0.0, 0.0, 0.0, 1.0),
        }

        for color_name, color_value in colors.items():
            if color_name in modification:
                # Update color in actions
                for action in step['actions']:
                    if 'params' in action and 'color' in action['params']:
                        action['params']['color'] = color_value
                        step['description'] = step['description'].replace(
                            'blue', color_name
                        ).replace('black', color_name)

        return step

    def set_render_range(self, command: Dict) -> Dict:
        """Set render range"""
        seconds = command.get('seconds', 20)

        timeline = self.controller.get_current_timeline()
        if not timeline:
            raise RuntimeError("No timeline available")

        frame_rate = float(timeline.GetSetting("timelineFrameRate") or "24")
        end_frame = int(seconds * frame_rate)

        timeline.SetSetting("useInOutRange", "1")
        timeline.SetSetting("inFrame", "0")
        timeline.SetSetting("outFrame", str(end_frame))

        return {
            'seconds': seconds,
            'frames': f"0-{end_frame}",
            'frame_rate': frame_rate
        }

    def clear_composition(self, command: Dict) -> Dict:
        """Clear all nodes in composition"""
        if not self.fusion_builder:
            comp = self.controller.get_fusion_comp()
            if not comp:
                raise RuntimeError("No Fusion composition available")
            self.fusion_builder = FusionNodeBuilder(comp)

        self.fusion_builder.clear_composition()

        return {'status': 'cleared'}


def main():
    """Main entry point for VS Code bridge"""
    if len(sys.argv) < 2:
        print(json.dumps({'success': False, 'error': 'No command provided'}))
        sys.exit(1)

    try:
        command = json.loads(sys.argv[1])
        bridge = VSCodeBridge()
        result = bridge.handle_command(command)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({'success': False, 'error': str(e)}))
        sys.exit(1)


if __name__ == '__main__':
    main()
