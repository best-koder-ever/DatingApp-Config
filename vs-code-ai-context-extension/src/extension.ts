import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export function activate(context: vscode.ExtensionContext) {
    console.log('AI Context Preservation extension is now active!');

    let promptCounter = 0;
    let autoBackupEnabled = true;
    let backupInterval: NodeJS.Timeout | undefined;

    // Configuration
    const config = vscode.workspace.getConfiguration('aiContext');
    
    class AIContextPreservation {
        private workspaceRoot: string;
        private contextFile: string;
        private backupDir: string;

        constructor() {
            this.workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || '';
            this.contextFile = path.join(this.workspaceRoot, config.get('contextFile', 'AI_CONTEXT.md'));
            this.backupDir = path.join(this.workspaceRoot, config.get('backupDirectory', 'ai_context_backups'));
            
            // Ensure backup directory exists
            if (!fs.existsSync(this.backupDir)) {
                fs.mkdirSync(this.backupDir, { recursive: true });
            }
        }

        async createContextBackup(): Promise<void> {
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const backupPath = path.join(this.backupDir, `context-backup-${timestamp}.md`);
            
            try {
                // Gather current state
                const contextData = await this.gatherContextData();
                
                // Write backup
                fs.writeFileSync(backupPath, contextData);
                
                // Update main context file
                await this.updateMainContextFile(contextData);
                
                vscode.window.showInformationMessage(`AI Context backed up: ${path.basename(backupPath)}`);
                
            } catch (error) {
                vscode.window.showErrorMessage(`Context backup failed: ${error}`);
            }
        }

        private async gatherContextData(): Promise<string> {
            const timestamp = new Date().toISOString();
            
            let contextData = `# AI Context Backup - ${timestamp}\n\n`;
            
            // Current file information
            const activeEditor = vscode.window.activeTextEditor;
            if (activeEditor) {
                contextData += `## Current File\n`;
                contextData += `- **File**: ${activeEditor.document.fileName}\n`;
                contextData += `- **Language**: ${activeEditor.document.languageId}\n`;
                contextData += `- **Line Count**: ${activeEditor.document.lineCount}\n\n`;
            }

            // Recent terminal commands
            contextData += `## Recent Terminal Activity\n`;
            contextData += await this.getTerminalHistory();
            contextData += `\n`;

            // Git status
            contextData += `## Git Status\n`;
            contextData += await this.getGitStatus();
            contextData += `\n`;

            // Recent file changes
            contextData += `## Recent Changes\n`;
            contextData += await this.getRecentChanges();
            contextData += `\n`;

            // Project structure snapshot
            contextData += `## Project Structure\n`;
            contextData += await this.getProjectStructure();
            contextData += `\n`;

            // Session metadata
            contextData += `## Session Metadata\n`;
            contextData += `- **Prompt Count**: ${promptCounter}\n`;
            contextData += `- **Session Duration**: ${this.getSessionDuration()}\n`;
            contextData += `- **Workspace**: ${this.workspaceRoot}\n\n`;

            return contextData;
        }

        private async getTerminalHistory(): string {
            // Read bash history if available
            const historyPath = path.join(process.env.HOME || '', '.bash_history');
            if (fs.existsSync(historyPath)) {
                const history = fs.readFileSync(historyPath, 'utf8');
                const lines = history.split('\n').slice(-10); // Last 10 commands
                return lines.map(line => `- ${line}`).join('\n');
            }
            return '- Terminal history not available\n';
        }

        private async getGitStatus(): string {
            try {
                const { exec } = require('child_process');
                return new Promise((resolve) => {
                    exec('git status --short', { cwd: this.workspaceRoot }, (error: any, stdout: string) => {
                        if (error) {
                            resolve('- Git status not available\n');
                        } else {
                            resolve(stdout || '- No changes\n');
                        }
                    });
                });
            } catch {
                return '- Git status not available\n';
            }
        }

        private async getRecentChanges(): string {
            const changes: string[] = [];
            
            // Check for recently modified files
            if (vscode.workspace.workspaceFolders) {
                const files = await vscode.workspace.findFiles('**/*', '**/node_modules/**', 20);
                for (const file of files) {
                    const stat = fs.statSync(file.fsPath);
                    const ageMinutes = (Date.now() - stat.mtime.getTime()) / (1000 * 60);
                    if (ageMinutes < 60) { // Files changed in last hour
                        changes.push(`- ${path.relative(this.workspaceRoot, file.fsPath)} (${Math.round(ageMinutes)}min ago)`);
                    }
                }
            }
            
            return changes.length > 0 ? changes.join('\n') : '- No recent changes\n';
        }

        private async getProjectStructure(): string {
            const structure: string[] = [];
            const importantFiles = [
                'package.json',
                'appsettings.json',
                'AI_CONTEXT.md',
                'README.md',
                'Program.cs',
                'Dockerfile'
            ];

            for (const fileName of importantFiles) {
                if (vscode.workspace.workspaceFolders) {
                    const files = await vscode.workspace.findFiles(`**/${fileName}`, '**/node_modules/**');
                    for (const file of files) {
                        structure.push(`- ${path.relative(this.workspaceRoot, file.fsPath)}`);
                    }
                }
            }

            return structure.length > 0 ? structure.join('\n') : '- No key files found\n';
        }

        private getSessionDuration(): string {
            const startTime = context.globalState.get<number>('sessionStartTime') || Date.now();
            const duration = Date.now() - startTime;
            const minutes = Math.floor(duration / (1000 * 60));
            return `${minutes} minutes`;
        }

        private async updateMainContextFile(newData: string): Promise<void> {
            if (fs.existsSync(this.contextFile)) {
                // Read existing context
                let existing = fs.readFileSync(this.contextFile, 'utf8');
                
                // Find or create session log section
                const sessionSection = `\n## 📝 Latest Session Log\n${newData}\n`;
                
                if (existing.includes('## 📝 Latest Session Log')) {
                    // Replace existing session log
                    existing = existing.replace(
                        /## 📝 Latest Session Log[\s\S]*?(?=\n## |\n---|\n$)/,
                        sessionSection
                    );
                } else {
                    // Append session log
                    existing += sessionSection;
                }
                
                fs.writeFileSync(this.contextFile, existing);
            }
        }
    }

    const aiContext = new AIContextPreservation();

    // Initialize session tracking
    context.globalState.update('sessionStartTime', Date.now());

    // Command: Manual backup
    const backupCommand = vscode.commands.registerCommand('aiContext.backup', () => {
        aiContext.createContextBackup();
    });

    // Command: Toggle auto backup
    const toggleCommand = vscode.commands.registerCommand('aiContext.autoBackup', () => {
        autoBackupEnabled = !autoBackupEnabled;
        vscode.window.showInformationMessage(`Auto backup ${autoBackupEnabled ? 'enabled' : 'disabled'}`);
        
        if (autoBackupEnabled) {
            startAutoBackup();
        } else {
            stopAutoBackup();
        }
    });

    // Command: View stats
    const statsCommand = vscode.commands.registerCommand('aiContext.viewStats', () => {
        vscode.window.showInformationMessage(`Prompts this session: ${promptCounter}`);
    });

    // Auto backup functionality
    function startAutoBackup() {
        const interval = config.get('backupInterval', 5) * 60 * 1000; // Convert to milliseconds
        
        backupInterval = setInterval(() => {
            if (autoBackupEnabled) {
                aiContext.createContextBackup();
            }
        }, interval);
    }

    function stopAutoBackup() {
        if (backupInterval) {
            clearInterval(backupInterval);
            backupInterval = undefined;
        }
    }

    // Monitor AI interactions (heuristic based on file saves and commands)
    const saveListener = vscode.workspace.onDidSaveTextDocument((document) => {
        promptCounter++;
        
        const threshold = config.get('promptThreshold', 10);
        if (promptCounter >= threshold && autoBackupEnabled) {
            aiContext.createContextBackup();
            promptCounter = 0; // Reset counter
        }
    });

    // Backup on VS Code shutdown
    const shutdownListener = vscode.workspace.onWillSaveTextDocument(() => {
        if (config.get('backupOnShutdown', true)) {
            aiContext.createContextBackup();
        }
    });

    // Start auto backup if enabled
    if (config.get('autoBackup', true)) {
        startAutoBackup();
    }

    // Register disposables
    context.subscriptions.push(
        backupCommand,
        toggleCommand,
        statsCommand,
        saveListener,
        shutdownListener
    );
}

export function deactivate() {
    console.log('AI Context Preservation extension deactivated');
}
