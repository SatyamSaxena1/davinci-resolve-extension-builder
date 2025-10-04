/**
 * Python Bridge - Communication with Python backend
 * Spawns Python process and sends/receives JSON commands
 */

import * as vscode from 'vscode';
import * as child_process from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

export class PythonBridge {
    private pythonPath: string;
    private projectPath: string;

    constructor() {
        const config = vscode.workspace.getConfiguration('resolve');
        this.pythonPath = this.findPythonPath(config.get('pythonPath', ''));
        this.projectPath = this.resolveProjectPath(config.get('projectPath', ''));
    }

    private findPythonPath(configPath: string): string {
        if (configPath && fs.existsSync(configPath)) {
            return configPath;
        }

        // Try to find Poetry virtual environment
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (workspaceFolder) {
            const resolveAiPath = path.join(
                workspaceFolder.uri.fsPath,
                'resolve-ai-assistant'
            );

            // Check for Windows Poetry venv
            const windowsPoetryPaths = [
                path.join(resolveAiPath, '.venv', 'Scripts', 'python.exe'),
                path.join(process.env.APPDATA || '', 'pypoetry', 'Cache', 'virtualenvs')
            ];

            for (const pythonPath of windowsPoetryPaths) {
                if (fs.existsSync(pythonPath)) {
                    return pythonPath;
                }
            }
        }

        // Fallback to system Python
        return 'python';
    }

    private resolveProjectPath(configPath: string): string {
        // Resolve ${workspaceFolder} variable
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (workspaceFolder && configPath.includes('${workspaceFolder}')) {
            configPath = configPath.replace('${workspaceFolder}', workspaceFolder.uri.fsPath);
        }

        if (fs.existsSync(configPath)) {
            return configPath;
        }

        // Fallback to default location
        if (workspaceFolder) {
            const defaultPath = path.join(
                workspaceFolder.uri.fsPath,
                'resolve-ai-assistant'
            );
            if (fs.existsSync(defaultPath)) {
                return defaultPath;
            }
        }

        throw new Error(
            'Could not find resolve-ai-assistant project. ' +
            'Please set resolve.projectPath in settings.'
        );
    }

    async executeStep(step: any): Promise<any> {
        const command = {
            action: 'execute_step',
            step: step
        };

        return this.callPython(command);
    }

    async playPreview(): Promise<void> {
        const command = {
            action: 'play_preview'
        };

        await this.callPython(command);
    }

    async getContext(): Promise<string> {
        const command = {
            action: 'get_context'
        };

        const result = await this.callPython(command);
        return result.context || 'No context available';
    }

    async parseIntent(prompt: string): Promise<any> {
        const command = {
            action: 'parse_intent',
            prompt: prompt
        };

        return this.callPython(command);
    }

    async breakDownTask(intent: any): Promise<any[]> {
        const command = {
            action: 'break_down_task',
            intent: intent
        };

        return this.callPython(command);
    }

    async modifyStep(step: any, modification: string): Promise<any> {
        const command = {
            action: 'modify_step',
            step: step,
            modification: modification
        };

        return this.callPython(command);
    }

    async setRenderRange(seconds: number): Promise<void> {
        const command = {
            action: 'set_render_range',
            seconds: seconds
        };

        await this.callPython(command);
    }

    async clearComposition(): Promise<void> {
        const command = {
            action: 'clear_composition'
        };

        await this.callPython(command);
    }

    private async callPython(command: any): Promise<any> {
        return new Promise((resolve, reject) => {
            const scriptPath = path.join(
                this.projectPath,
                'src',
                'resolve_ai',
                'vscode_bridge.py'
            );

            if (!fs.existsSync(scriptPath)) {
                reject(new Error(
                    `Python bridge script not found at: ${scriptPath}\n` +
                    'Make sure resolve-ai-assistant project is set up correctly.'
                ));
                return;
            }

            const config = vscode.workspace.getConfiguration('resolve');
            if (config.get('verboseLogging')) {
                console.log('Calling Python:', this.pythonPath, scriptPath);
                console.log('Command:', JSON.stringify(command));
            }

            const proc = child_process.spawn(this.pythonPath, [
                scriptPath,
                JSON.stringify(command)
            ], {
                cwd: this.projectPath
            });

            let stdout = '';
            let stderr = '';

            proc.stdout.on('data', (data: Buffer) => {
                stdout += data.toString();
            });

            proc.stderr.on('data', (data: Buffer) => {
                stderr += data.toString();
            });

            proc.on('close', (code: number) => {
                if (config.get('verboseLogging')) {
                    console.log('Python exit code:', code);
                    console.log('Python stdout:', stdout);
                    if (stderr) console.log('Python stderr:', stderr);
                }

                if (code !== 0) {
                    reject(new Error(
                        `Python command failed (exit code ${code}):\n${stderr || stdout}`
                    ));
                } else {
                    try {
                        const result = JSON.parse(stdout);
                        if (result.success === false) {
                            reject(new Error(result.error || 'Unknown error'));
                        } else {
                            resolve(result.result || result);
                        }
                    } catch (e) {
                        reject(new Error(
                            `Failed to parse Python response:\n${stdout}`
                        ));
                    }
                }
            });

            proc.on('error', (err: Error) => {
                reject(new Error(
                    `Failed to spawn Python process: ${err.message}\n` +
                    `Python path: ${this.pythonPath}\n` +
                    'Make sure Python is installed and accessible.'
                ));
            });
        });
    }
}
