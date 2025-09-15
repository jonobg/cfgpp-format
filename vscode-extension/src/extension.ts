import * as vscode from 'vscode';
import { LanguageClient, LanguageClientOptions, ServerOptions } from 'vscode-languageclient/node';
import * as path from 'path';

let client: LanguageClient;

export function activate(context: vscode.ExtensionContext) {
    // Language server setup
    const serverModule = context.asAbsolutePath(
        path.join('..', 'src', 'cfgpp', 'language_server.py')
    );
    
    const serverOptions: ServerOptions = {
        command: 'python',
        args: [serverModule],
        options: {}
    };

    const clientOptions: LanguageClientOptions = {
        documentSelector: [
            { scheme: 'file', language: 'cfgpp' },
            { scheme: 'file', language: 'cfgpp-schema' }
        ],
        synchronize: {
            fileEvents: [
                vscode.workspace.createFileSystemWatcher('**/*.cfgpp'),
                vscode.workspace.createFileSystemWatcher('**/*.cfgpp-schema')
            ]
        }
    };

    // Create and start the language client
    client = new LanguageClient(
        'cfgppLanguageServer',
        'CFG++ Language Server',
        serverOptions,
        clientOptions
    );

    // Start the client and server
    client.start();

    // Register commands
    registerCommands(context);

    // Register file system watchers
    setupFileWatchers(context);
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}

function registerCommands(context: vscode.ExtensionContext) {
    // Format document command
    const formatCommand = vscode.commands.registerCommand('cfgpp.formatDocument', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active CFG++ document found');
            return;
        }

        if (editor.document.languageId !== 'cfgpp') {
            vscode.window.showWarningMessage('Active document is not a CFG++ file');
            return;
        }

        try {
            await vscode.commands.executeCommand('editor.action.formatDocument');
            vscode.window.showInformationMessage('Document formatted successfully');
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to format document: ${error}`);
        }
    });

    // Validate schema command
    const validateCommand = vscode.commands.registerCommand('cfgpp.validateSchema', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active CFG++ document found');
            return;
        }

        if (editor.document.languageId !== 'cfgpp') {
            vscode.window.showWarningMessage('Active document is not a CFG++ file');
            return;
        }

        // Trigger diagnostics refresh
        try {
            await client.sendNotification('textDocument/didSave', {
                textDocument: {
                    uri: editor.document.uri.toString()
                }
            });
            vscode.window.showInformationMessage('Schema validation completed');
        } catch (error) {
            vscode.window.showErrorMessage(`Schema validation failed: ${error}`);
        }
    });

    // Discover schema command
    const discoverCommand = vscode.commands.registerCommand('cfgpp.discoverSchema', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active CFG++ document found');
            return;
        }

        const workspaceFolder = vscode.workspace.getWorkspaceFolder(editor.document.uri);
        if (!workspaceFolder) {
            vscode.window.showWarningMessage('No workspace folder found');
            return;
        }

        try {
            // Find schema files in workspace
            const schemaFiles = await vscode.workspace.findFiles(
                new vscode.RelativePattern(workspaceFolder, '**/*.cfgpp-schema'),
                null,
                50
            );

            if (schemaFiles.length === 0) {
                vscode.window.showInformationMessage('No schema files found in workspace');
                return;
            }

            const schemaNames = schemaFiles.map(file => 
                path.relative(workspaceFolder.uri.fsPath, file.fsPath)
            );

            const selected = await vscode.window.showQuickPick(schemaNames, {
                placeHolder: 'Select a schema file to open',
                title: 'CFG++ Schema Files'
            });

            if (selected) {
                const selectedFile = schemaFiles.find(file =>
                    path.relative(workspaceFolder.uri.fsPath, file.fsPath) === selected
                );
                
                if (selectedFile) {
                    await vscode.window.showTextDocument(selectedFile);
                }
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to discover schemas: ${error}`);
        }
    });

    context.subscriptions.push(formatCommand, validateCommand, discoverCommand);
}

function setupFileWatchers(context: vscode.ExtensionContext) {
    // Watch for changes in schema files
    const schemaWatcher = vscode.workspace.createFileSystemWatcher('**/*.cfgpp-schema');
    
    schemaWatcher.onDidCreate(() => {
        vscode.window.showInformationMessage('New schema file detected. Validation updated.');
    });
    
    schemaWatcher.onDidChange(() => {
        vscode.window.showInformationMessage('Schema file changed. Re-validating documents.');
    });
    
    schemaWatcher.onDidDelete(() => {
        vscode.window.showInformationMessage('Schema file deleted. Validation updated.');
    });

    context.subscriptions.push(schemaWatcher);
}
