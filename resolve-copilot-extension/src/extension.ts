/**
 * DaVinci Resolve AI Assistant - Main Extension Entry Point
 * Integrates GitHub Copilot Chat with DaVinci Resolve Python API
 */

import * as vscode from 'vscode';
import { ResolveChatParticipant } from './chatParticipant';
import { registerCommands } from './commands';

let chatParticipant: ResolveChatParticipant | undefined;

export function activate(context: vscode.ExtensionContext) {
    console.log('DaVinci Resolve AI Assistant is activating...');

    try {
        // Register chat participant for @resolve commands
        chatParticipant = new ResolveChatParticipant(context);
        
        // Register command palette commands
        registerCommands(context, chatParticipant);

        // Show welcome message
        vscode.window.showInformationMessage(
            '🎬 DaVinci Resolve AI Assistant activated! Use @resolve in Copilot Chat.',
            'Open Chat'
        ).then(selection => {
            if (selection === 'Open Chat') {
                vscode.commands.executeCommand('workbench.action.chat.open', {
                    query: '@resolve '
                });
            }
        });

        console.log('DaVinci Resolve AI Assistant activated successfully');
    } catch (error) {
        console.error('Failed to activate extension:', error);
        vscode.window.showErrorMessage(
            `Failed to activate DaVinci Resolve AI Assistant: ${error}`
        );
    }
}

export function deactivate() {
    console.log('DaVinci Resolve AI Assistant is deactivating...');
    chatParticipant?.dispose();
}
