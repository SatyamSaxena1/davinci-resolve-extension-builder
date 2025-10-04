/**
 * VS Code Command Registration
 * Register command palette commands for Resolve operations
 */

import * as vscode from 'vscode';
import { ResolveChatParticipant } from './chatParticipant';

export function registerCommands(
    context: vscode.ExtensionContext,
    chatParticipant: ResolveChatParticipant
): void {
    
    // Command: Play Preview
    const previewCommand = vscode.commands.registerCommand(
        'resolve.preview',
        async () => {
            try {
                await vscode.window.withProgress(
                    {
                        location: vscode.ProgressLocation.Notification,
                        title: 'Playing preview in DaVinci Resolve...',
                        cancellable: false
                    },
                    async () => {
                        await chatParticipant.triggerPreview();
                    }
                );

                vscode.window.showInformationMessage(
                    '📺 Preview playing in DaVinci Resolve'
                );
            } catch (error: any) {
                vscode.window.showErrorMessage(
                    `Failed to play preview: ${error.message}`
                );
            }
        }
    );

    // Command: Get Context
    const contextCommand = vscode.commands.registerCommand(
        'resolve.getContext',
        async () => {
            try {
                const context = await chatParticipant.getCompositionContext();

                // Show in output channel
                const channel = vscode.window.createOutputChannel('Resolve Context');
                channel.clear();
                channel.appendLine('DaVinci Resolve Composition Context');
                channel.appendLine('='.repeat(50));
                channel.appendLine('');
                channel.appendLine(context);
                channel.show();

            } catch (error: any) {
                vscode.window.showErrorMessage(
                    `Failed to get context: ${error.message}`
                );
            }
        }
    );

    // Command: Set Render Range
    const renderRangeCommand = vscode.commands.registerCommand(
        'resolve.setRenderRange',
        async () => {
            const config = vscode.workspace.getConfiguration('resolve');
            const currentMax = config.get<number>('maxRenderSeconds', 20);

            const input = await vscode.window.showInputBox({
                prompt: 'Enter render range in seconds',
                value: currentMax.toString(),
                validateInput: (value) => {
                    const num = parseInt(value);
                    if (isNaN(num) || num < 1 || num > 120) {
                        return 'Please enter a number between 1 and 120';
                    }
                    return null;
                }
            });

            if (input) {
                const seconds = parseInt(input);
                await config.update(
                    'maxRenderSeconds',
                    seconds,
                    vscode.ConfigurationTarget.Workspace
                );

                vscode.window.showInformationMessage(
                    `⏱️ Render range set to ${seconds} seconds`
                );
            }
        }
    );

    // Command: Clear Composition
    const clearCommand = vscode.commands.registerCommand(
        'resolve.clearComposition',
        async () => {
            const confirm = await vscode.window.showWarningMessage(
                'Clear all nodes in Fusion composition?',
                { modal: true },
                'Clear'
            );

            if (confirm === 'Clear') {
                try {
                    await vscode.window.withProgress(
                        {
                            location: vscode.ProgressLocation.Notification,
                            title: 'Clearing composition...',
                            cancellable: false
                        },
                        async () => {
                            const { PythonBridge } = await import('./pythonBridge');
                            const bridge = new PythonBridge();
                            await bridge.clearComposition();
                        }
                    );

                    vscode.window.showInformationMessage(
                        '✓ Composition cleared'
                    );
                } catch (error: any) {
                    vscode.window.showErrorMessage(
                        `Failed to clear composition: ${error.message}`
                    );
                }
            }
        }
    );

    // Command: Open Chat
    const chatCommand = vscode.commands.registerCommand(
        'resolve.openChat',
        () => {
            vscode.commands.executeCommand('workbench.action.chat.open', {
                query: '@resolve '
            });
        }
    );

    // Register all commands
    context.subscriptions.push(
        previewCommand,
        contextCommand,
        renderRangeCommand,
        clearCommand,
        chatCommand
    );

    console.log('Resolve commands registered');
}
