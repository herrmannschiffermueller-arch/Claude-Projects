<?php
/**
 * claude-code-bridge.php
 *
 * PHP-Programm, das die Claude Code CLI (`claude`) per proc_open aufruft
 * und so PHP-Anwendungen die Möglichkeit gibt, Coding-Aufgaben direkt an
 * Claude Code zu delegieren.
 *
 * Voraussetzung: Claude Code CLI ist installiert und im PATH verfügbar
 * (`npm install -g @anthropic-ai/claude-code` bzw. die offizielle Installation).
 * Mehr dazu: https://docs.claude.com/en/docs/claude-code
 *
 * Nutzung (CLI):
 *   php claude-code-bridge.php "Refactoriere die Funktion foo() in src/App.php"
 *   php claude-code-bridge.php --dir=/pfad/zum/projekt "Füge Tests hinzu"
 *   php claude-code-bridge.php --interactive
 *
 * Nutzung (als Bibliothek in eigenem PHP-Code):
 *   require 'claude-code-bridge.php';
 *   $bridge = new ClaudeCodeBridge('/pfad/zum/projekt');
 *   $result = $bridge->run('Erkläre die Datei index.php');
 *   echo $result['output'];
 */

final class ClaudeCodeException extends RuntimeException {}

final class ClaudeCodeBridge
{
    private string $workingDir;
    private string $binary;
    private array $defaultArgs;

    public function __construct(
        string $workingDir = '.',
        string $binary = 'claude',
        array $defaultArgs = ['--print']
    ) {
        $resolved = realpath($workingDir);
        if ($resolved === false || !is_dir($resolved)) {
            throw new ClaudeCodeException("Arbeitsverzeichnis nicht gefunden: {$workingDir}");
        }
        $this->workingDir = $resolved;
        $this->binary = $binary;
        $this->defaultArgs = $defaultArgs;
        $this->assertBinaryAvailable();
    }

    private function assertBinaryAvailable(): void
    {
        $which = stripos(PHP_OS, 'WIN') === 0 ? 'where' : 'which';
        $check = proc_open(
            [$which, $this->binary],
            [1 => ['pipe', 'w'], 2 => ['pipe', 'w']],
            $pipes
        );
        if (!is_resource($check)) {
            throw new ClaudeCodeException("Konnte '{$this->binary}' nicht prüfen.");
        }
        stream_get_contents($pipes[1]);
        stream_get_contents($pipes[2]);
        fclose($pipes[1]);
        fclose($pipes[2]);
        $exitCode = proc_close($check);
        if ($exitCode !== 0) {
            throw new ClaudeCodeException(
                "Claude Code CLI ('{$this->binary}') wurde nicht im PATH gefunden. " .
                "Installation: npm install -g @anthropic-ai/claude-code"
            );
        }
    }

    /**
     * Führt einen einzelnen Claude-Code-Auftrag aus und gibt das Ergebnis zurück.
     *
     * @param string $prompt   Die Aufgabe / Anweisung an Claude Code.
     * @param array  $extraArgs Zusätzliche CLI-Argumente (z.B. ['--model', 'sonnet']).
     * @return array{output: string, error: string, exitCode: int}
     */
    public function run(string $prompt, array $extraArgs = []): array
    {
        if (trim($prompt) === '') {
            throw new ClaudeCodeException('Der Prompt darf nicht leer sein.');
        }

        $command = array_merge([$this->binary], $this->defaultArgs, $extraArgs, [$prompt]);

        $descriptorSpec = [
            0 => ['pipe', 'r'],
            1 => ['pipe', 'w'],
            2 => ['pipe', 'w'],
        ];

        $process = proc_open($command, $descriptorSpec, $pipes, $this->workingDir);

        if (!is_resource($process)) {
            throw new ClaudeCodeException('Konnte den Claude-Code-Prozess nicht starten.');
        }

        fclose($pipes[0]);

        $output = stream_get_contents($pipes[1]);
        $error = stream_get_contents($pipes[2]);

        fclose($pipes[1]);
        fclose($pipes[2]);

        $exitCode = proc_close($process);

        return [
            'output' => $output === false ? '' : $output,
            'error' => $error === false ? '' : $error,
            'exitCode' => $exitCode,
        ];
    }

    /**
     * Führt einen Auftrag aus und streamt die Ausgabe live (Callback pro Zeile).
     *
     * @param callable(string):void $onOutputLine
     */
    public function runStreaming(string $prompt, callable $onOutputLine, array $extraArgs = []): int
    {
        $command = array_merge([$this->binary], $this->defaultArgs, $extraArgs, [$prompt]);

        $descriptorSpec = [
            0 => ['pipe', 'r'],
            1 => ['pipe', 'w'],
            2 => ['pipe', 'w'],
        ];

        $process = proc_open($command, $descriptorSpec, $pipes, $this->workingDir);

        if (!is_resource($process)) {
            throw new ClaudeCodeException('Konnte den Claude-Code-Prozess nicht starten.');
        }

        fclose($pipes[0]);
        stream_set_blocking($pipes[1], false);
        stream_set_blocking($pipes[2], false);

        $buffer = '';
        while (true) {
            $status = proc_get_status($process);

            $chunk = fread($pipes[1], 8192);
            if ($chunk !== false && $chunk !== '') {
                $buffer .= $chunk;
                while (($pos = strpos($buffer, "\n")) !== false) {
                    $line = substr($buffer, 0, $pos);
                    $buffer = substr($buffer, $pos + 1);
                    $onOutputLine($line);
                }
            }

            if (!$status['running'] && $chunk === '') {
                break;
            }
            usleep(20000);
        }

        if ($buffer !== '') {
            $onOutputLine($buffer);
        }

        $errOutput = stream_get_contents($pipes[2]);
        if ($errOutput) {
            foreach (explode("\n", trim($errOutput)) as $line) {
                if ($line !== '') {
                    $onOutputLine('[stderr] ' . $line);
                }
            }
        }

        fclose($pipes[1]);
        fclose($pipes[2]);

        return proc_close($process);
    }
}

// ---------------------------------------------------------------------------
// CLI-Einstiegspunkt
// ---------------------------------------------------------------------------

if (PHP_SAPI === 'cli' && realpath($argv[0]) === realpath(__FILE__)) {
    runCli($argv);
}

function runCli(array $argv): void
{
    $args = array_slice($argv, 1);
    $workingDir = '.';
    $interactive = false;
    $promptParts = [];

    foreach ($args as $arg) {
        if (str_starts_with($arg, '--dir=')) {
            $workingDir = substr($arg, 6);
        } elseif ($arg === '--interactive' || $arg === '-i') {
            $interactive = true;
        } elseif ($arg === '--help' || $arg === '-h') {
            printHelp();
            exit(0);
        } else {
            $promptParts[] = $arg;
        }
    }

    try {
        $bridge = new ClaudeCodeBridge($workingDir);
    } catch (ClaudeCodeException $e) {
        fwrite(STDERR, "Fehler: " . $e->getMessage() . PHP_EOL);
        exit(1);
    }

    if ($interactive) {
        runInteractiveSession($bridge);
        return;
    }

    $prompt = trim(implode(' ', $promptParts));
    if ($prompt === '') {
        printHelp();
        exit(1);
    }

    echo "▶ Sende Aufgabe an Claude Code …" . PHP_EOL . PHP_EOL;

    $exitCode = $bridge->runStreaming($prompt, function (string $line) {
        echo $line . PHP_EOL;
    });

    exit($exitCode);
}

function runInteractiveSession(ClaudeCodeBridge $bridge): void
{
    echo "=== Claude Code – interaktive PHP-Bridge ===" . PHP_EOL;
    echo "Gib eine Aufgabe ein und drücke Enter. 'exit' zum Beenden." . PHP_EOL . PHP_EOL;

    while (true) {
        echo "> ";
        $line = fgets(STDIN);
        if ($line === false) {
            break;
        }
        $line = trim($line);
        if ($line === '' ) {
            continue;
        }
        if (in_array(strtolower($line), ['exit', 'quit', ':q'], true)) {
            echo "Bis bald!" . PHP_EOL;
            break;
        }

        $bridge->runStreaming($line, function (string $out) {
            echo $out . PHP_EOL;
        });
        echo PHP_EOL;
    }
}

function printHelp(): void
{
    echo <<<HELP
claude-code-bridge.php – PHP-Programm zum direkten Arbeiten mit Claude Code

Verwendung:
  php claude-code-bridge.php [--dir=<pfad>] "<Aufgabe / Prompt>"
  php claude-code-bridge.php --interactive [--dir=<pfad>]

Optionen:
  --dir=<pfad>     Arbeitsverzeichnis, in dem Claude Code ausgeführt wird (Standard: aktuelles Verzeichnis)
  --interactive,-i Startet eine interaktive Eingabeschleife
  --help,-h        Zeigt diese Hilfe

Beispiele:
  php claude-code-bridge.php "Erkläre, was index.php macht"
  php claude-code-bridge.php --dir=/var/www/projekt "Schreibe Unit-Tests für UserController"
  php claude-code-bridge.php -i

Voraussetzung: Claude Code CLI muss installiert sein (npm install -g @anthropic-ai/claude-code)
und über `claude` im PATH erreichbar sein.

HELP;
}
