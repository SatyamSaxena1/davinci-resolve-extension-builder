/**
 * Chat Participant for @resolve commands
 * Handles natural language interaction with DaVinci Resolve
 */

import * as vscode from 'vscode';
import { PythonBridge } from './pythonBridge';

interface Step {
    id: number;
    description: string;
    actions: Action[];
    parameters: Record<string, any>;
    status: 'pending' | 'executing' | 'completed' | 'failed';
}

interface Action {
    type: string;
    target: string;
    params: Record<string, any>;
}

export class ResolveChatParticipant {
    private participant: vscode.ChatParticipant | undefined;
    private bridge: PythonBridge;
    private currentPlan: Step[] = [];
    private currentStep: number = 0;
    private conversationContext: string[] = [];

    constructor(private context: vscode.ExtensionContext) {
        this.bridge = new PythonBridge();
        this.registerParticipant();
    }

    private registerParticipant() {
        try {
            this.participant = vscode.chat.createChatParticipant(
                'resolve.assistant',
                this.handleChat.bind(this)
            );

            this.participant.iconPath = vscode.Uri.file(
                this.context.asAbsolutePath('resources/resolve-icon.png')
            );

            this.context.subscriptions.push(this.participant);
            console.log('Chat participant registered: @resolve');
        } catch (error) {
            console.error('Failed to register chat participant:', error);
            throw error;
        }
    }

    private async handleChat(
        request: vscode.ChatRequest,
        context: vscode.ChatContext,
        stream: vscode.ChatResponseStream,
        token: vscode.CancellationToken
    ): Promise<void> {
        const prompt = request.prompt.trim();

        try {
            // Check for special commands
            if (this.isApproval(prompt)) {
                await this.executeCurrentStep(stream, token);
            } else if (this.isRejection(prompt)) {
                await this.handleRejection(stream);
            } else if (this.isModification(prompt)) {
                await this.modifyCurrentStep(prompt, stream, token);
            } else if (this.isContextQuery(prompt)) {
                await this.showContext(stream, token);
            } else {
                // New request - create plan
                await this.createNewPlan(prompt, stream, token);
            }
        } catch (error: any) {
            stream.markdown(`❌ **Error**: ${error.message}\n\n`);
            stream.markdown('Would you like to try something else?\n');
        }
    }

    private async createNewPlan(
        prompt: string,
        stream: vscode.ChatResponseStream,
        token: vscode.CancellationToken
    ): Promise<void> {
        stream.progress('Analyzing request...');

        // Parse user intent
        const intent = await this.bridge.parseIntent(prompt);

        if (token.isCancellationRequested) return;

        stream.progress('Breaking down into steps...');

        // Break into steps
        this.currentPlan = await this.bridge.breakDownTask(intent);
        this.currentStep = 0;

        if (token.isCancellationRequested) return;

        // Add to conversation context
        this.conversationContext.push(`User: ${prompt}`);

        // Show plan
        stream.markdown('## 📋 Plan\n\n');
        this.currentPlan.forEach((step, i) => {
            const status = i === 0 ? '→' : '□';
            stream.markdown(`${status} **Step ${i + 1}**: ${step.description}\n`);
        });

        const config = vscode.workspace.getConfiguration('resolve');
        const maxSeconds = config.get<number>('maxRenderSeconds', 20);

        stream.markdown(`\n⏱️ *Render range will be set to ${maxSeconds} seconds*\n\n`);
        stream.markdown('---\n\n');

        // Check if permission required
        if (config.get<boolean>('requirePermission', true)) {
            stream.markdown('❓ **Shall I proceed with Step 1?**\n\n');
            stream.markdown('*Reply with "yes", "no", or suggest modifications*\n');
        } else {
            // Auto-execute if permission not required
            await this.executeCurrentStep(stream, token);
        }
    }

    private async executeCurrentStep(
        stream: vscode.ChatResponseStream,
        token: vscode.CancellationToken
    ): Promise<void> {
        if (this.currentStep >= this.currentPlan.length) {
            stream.markdown('✅ **All steps complete!**\n\n');
            stream.markdown('Would you like to make any changes or create something else?\n');
            this.resetPlan();
            return;
        }

        const step = this.currentPlan[this.currentStep];
        step.status = 'executing';

        const config = vscode.workspace.getConfiguration('resolve');

        if (config.get<boolean>('showProgress', true)) {
            stream.progress(`Executing: ${step.description}...`);
        }

        try {
            // Execute via Python backend
            const result = await this.bridge.executeStep(step);

            if (token.isCancellationRequested) return;

            step.status = 'completed';

            stream.markdown(`✓ ${step.description}\n`);

            // Show execution details if available
            if (result.details) {
                stream.markdown(`\n*Details:*\n`);
                Object.entries(result.details).forEach(([key, value]) => {
                    stream.markdown(`- ${key}: ${value}\n`);
                });
            }

            // Auto-preview if enabled
            if (config.get<boolean>('autoPreview', true)) {
                stream.markdown(`\n📺 Playing preview...\n`);
                await this.bridge.playPreview();
            }

            // Show progress
            const completed = this.currentStep + 1;
            const total = this.currentPlan.length;
            const progressBar = this.createProgressBar(completed, total);
            stream.markdown(`\n${progressBar} ${completed}/${total} steps complete\n\n`);

            // Move to next step
            this.currentStep++;

            if (this.currentStep < this.currentPlan.length) {
                const nextStep = this.currentPlan[this.currentStep];
                stream.markdown('---\n\n');
                stream.markdown(`❓ **Continue with Step ${this.currentStep + 1}**: ${nextStep.description}?\n`);
            } else {
                stream.markdown('\n✅ **All steps complete!** 🎉\n');
                this.resetPlan();
            }

        } catch (error: any) {
            step.status = 'failed';
            throw error;
        }
    }

    private async modifyCurrentStep(
        modification: string,
        stream: vscode.ChatResponseStream,
        token: vscode.CancellationToken
    ): Promise<void> {
        if (this.currentStep >= this.currentPlan.length) {
            stream.markdown('No active step to modify. Start a new request.\n');
            return;
        }

        stream.progress('Updating plan...');

        const currentStepData = this.currentPlan[this.currentStep];
        const modifiedStep = await this.bridge.modifyStep(currentStepData, modification);

        if (token.isCancellationRequested) return;

        this.currentPlan[this.currentStep] = modifiedStep;

        stream.markdown('✓ **Plan updated:**\n\n');
        stream.markdown(`- ${modifiedStep.description}\n\n`);
        stream.markdown('---\n\n');
        stream.markdown('❓ **Proceed with modified step?**\n');
    }

    private async showContext(
        stream: vscode.ChatResponseStream,
        token: vscode.CancellationToken
    ): Promise<void> {
        stream.progress('Retrieving composition context...');

        const context = await this.bridge.getContext();

        if (token.isCancellationRequested) return;

        stream.markdown('## 🎬 Current Composition State\n\n');
        stream.markdown('```\n');
        stream.markdown(context);
        stream.markdown('\n```\n\n');
        stream.markdown('What would you like to do?\n');
    }

    private async handleRejection(stream: vscode.ChatResponseStream): Promise<void> {
        stream.markdown('❌ **Cancelled**\n\n');
        stream.markdown('What would you like to do instead?\n');
        this.resetPlan();
    }

    private createProgressBar(completed: number, total: number): string {
        const width = 10;
        const filled = Math.floor((completed / total) * width);
        const empty = width - filled;
        return '[' + '■'.repeat(filled) + '□'.repeat(empty) + ']';
    }

    private isApproval(prompt: string): boolean {
        const approvalWords = ['yes', 'go', 'proceed', 'continue', 'ok', 'yeah', 'yep', 'sure'];
        const lower = prompt.toLowerCase().trim();
        return approvalWords.some(word => lower === word || lower.startsWith(word + ' '));
    }

    private isRejection(prompt: string): boolean {
        const rejectionWords = ['no', 'cancel', 'stop', 'nope'];
        const lower = prompt.toLowerCase().trim();
        return rejectionWords.some(word => lower === word || lower.startsWith(word + ' '));
    }

    private isModification(prompt: string): boolean {
        const modWords = ['change', 'modify', 'update', 'instead', 'but', 'make it', 'rather'];
        return modWords.some(word => prompt.toLowerCase().includes(word));
    }

    private isContextQuery(prompt: string): boolean {
        const contextWords = ['what', 'show', 'context', 'status', 'current', 'composition'];
        const lower = prompt.toLowerCase();
        return contextWords.filter(word => lower.includes(word)).length >= 2;
    }

    private resetPlan(): void {
        this.currentPlan = [];
        this.currentStep = 0;
    }

    dispose(): void {
        this.participant?.dispose();
    }

    // Public method for commands to trigger preview
    async triggerPreview(): Promise<void> {
        await this.bridge.playPreview();
    }

    // Public method for commands to get context
    async getCompositionContext(): Promise<string> {
        return await this.bridge.getContext();
    }
}
